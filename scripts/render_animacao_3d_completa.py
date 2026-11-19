# -*- coding: utf-8 -*-
"""
Animação 3D Completa dos Hidrometeoros no ParaView (via pvpython + ffmpeg)
Projeto: C:\gis4wrf\projects\granizo (Seminário Final - Parte 2, FSC7116 UFSC).

Atende rigorosamente a todos os requisitos do usuário e do professor:
1. Tempestade Noturna Correta:
   - Pico severo de granizo em 22:45 UTC (19:45 Local) em 29/08/2026.
   - Refletividade 77.4 dBZ, QHAIL 5.21 g/kg, QGRAUP 8.30 g/kg, SLW 7.24 g/kg, W = 31.0 m/s.
2. Cores Fixas e Distintas para cada hidrometeoro (desvinculando do mapa de cores padrão azul):
   - Nuvem (QCLOUD): cinza claro (#d1d5db)
   - Chuva (QRAIN): azul vivo (#2563eb)
   - Graupel (QGRAUP): laranja brilhante (#f97316)
   - Granizo (QHAIL): vermelho carmesim (#dc2626)
   - Água Super-resfriada (SLW): verde esmeralda (#16a34a)
3. Rotação 360° Contínua e Suave da câmera ao redor da tempestade e do relevo
   (1.5° por frame ao longo de 240 frames).
4. Sequência Completa de Destaques:
   - Evolução temporal da tempestade noturna (21:45 a 23:15 UTC / 18:45 a 20:15 Local).
   - Camadas "despidas" (peeling de fora para dentro no pico de 22:45 UTC).
   - Camadas "vestidas" (layering back de dentro para fora no pico de 22:45 UTC).
   - Órbita 360° final da tempestade reconstituída sobre o relevo de Santa Catarina.
"""
import os
import sys
import json
import math
import shutil
import subprocess
import numpy as np
import netCDF4
import vtk
from vtk.util import numpy_support as ns
from PIL import Image, ImageDraw, ImageFont
from paraview.simple import *

BASE = r'C:\gis4wrf\projects\granizo'
WRF_DIR = os.path.join(BASE, 'run_wrf')
PV_DIR = os.path.join(BASE, 'paraview_data')
SERIES_DIR = os.path.join(PV_DIR, 'series_anim')
FRAMES_DIR = os.path.join(PV_DIR, 'frames_360_peel')
FIG_DIR = os.path.join(BASE, 'figuras')
REPO_FIG = r'C:\Users\haas\github\tarefa-meso\figuras'

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(SERIES_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(REPO_FIG, exist_ok=True)

G = 9.81
RCP = 0.2854
VE = 4.0
ZS_KM = np.arange(0.0, 17.5 + 1e-4, 0.25)
W_IMG, H_IMG = 1600, 960
FONT = r'C:\Windows\Fonts\arial.ttf'
FONT_B = r'C:\Windows\Fonts\arialbd.ttf'

relevo_vts = os.path.join(PV_DIR, 'relevo_d03.vts')
series_path = os.path.join(SERIES_DIR, 'tempestade.vti.series')

def hx(s):
    s = s.lstrip('#')
    return [int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]

HIDROS_DEF = [
    ('QCLOUD', 'Nuvem (QCLOUD)',              '#d1d5db', 0.10, 0.22),
    ('QRAIN',  'Chuva (QRAIN)',               '#2563eb', 0.50, 0.65),
    ('QGRAUP', 'Graupel (QGRAUP)',            '#f97316', 0.50, 0.85),
    ('QHAIL',  'Granizo (QHAIL)',             '#dc2626', 0.10, 0.95),
    ('SLW',    'Água Super-resfriada (SLW)',  '#16a34a', 0.20, 0.80),
]

def to_vtk(arr, name):
    v = ns.numpy_to_vtk(np.ascontiguousarray(arr, dtype=np.float32).ravel(), deep=True)
    v.SetName(name)
    return v

def interp_z(f3d, z3d, hgt2d):
    nk = z3d.shape[0]
    out = np.zeros((len(ZS_KM),) + z3d.shape[1:], dtype=np.float32)
    for idx, zt in enumerate(ZS_KM):
        k1 = np.clip((z3d < zt).sum(axis=0), 1, nk - 1)
        k0 = k1 - 1
        z0 = np.take_along_axis(z3d, k0[None], 0)[0]
        z1 = np.take_along_axis(z3d, k1[None], 0)[0]
        f0 = np.take_along_axis(f3d, k0[None], 0)[0]
        f1 = np.take_along_axis(f3d, k1[None], 0)[0]
        w = np.clip((zt - z0) / np.maximum(z1 - z0, 1e-5), 0.0, 1.0)
        val = f0 + (f1 - f0) * w
        val[zt < hgt2d] = 0.0
        out[idx] = val
    return out

def preparar_series_noturna(indices_tempo):
    meta_path = os.path.join(BASE, 'metricas_wrf.json')
    meta = json.load(open(meta_path, encoding='utf-8'))
    wrfout = meta['wrfout_d03']

    series_info = []
    print(f"Lendo dados de {wrfout} para {len(indices_tempo)} instantes noturnos...")

    with netCDF4.Dataset(wrfout) as ds:
        V = ds.variables
        dx = float(ds.getncattr('DX')) / 1000.0
        hgt_m = np.array(V['HGT'][0], dtype=np.float32)
        hgt_km = hgt_m / 1000.0
        land = np.array(V['LANDMASK'][0], dtype=np.float32)
        ny, nx = hgt_km.shape
        xs = (np.arange(nx) - (nx - 1) / 2.0) * dx
        ys = (np.arange(ny) - (ny - 1) / 2.0) * dx

        if not os.path.exists(relevo_vts):
            X, Y = np.meshgrid(xs, ys)
            surf_pts = np.column_stack([X.ravel(), Y.ravel(), (VE * hgt_km).ravel()]).astype(np.float32)
            elev = np.where(land > 0.5, np.maximum(hgt_m, 1.0), -100.0).astype(np.float32)
            sg = vtk.vtkStructuredGrid()
            sg.SetDimensions(nx, ny, 1)
            pts = vtk.vtkPoints()
            pts.SetData(ns.numpy_to_vtk(surf_pts, deep=True))
            sg.SetPoints(pts)
            sg.GetPointData().AddArray(to_vtk(elev, 'Elevacao_m'))
            sg.GetPointData().AddArray(to_vtk(land, 'Landmask'))
            w_sg = vtk.vtkXMLStructuredGridWriter()
            w_sg.SetFileName(relevo_vts)
            w_sg.SetInputData(sg)
            w_sg.Write()

        all_times = [''.join([c.decode('utf-8') for c in t]) for t in V['Times'][:]]

        for seq, it in enumerate(indices_tempo):
            t_str = all_times[it]
            ph = np.array(V['PH'][it], dtype=np.float32)
            phb = np.array(V['PHB'][it], dtype=np.float32)
            zst = (ph + phb) / G / 1000.0
            zm = 0.5 * (zst[:-1] + zst[1:])

            t_pert = np.array(V['T'][it], dtype=np.float32)
            p_tot = np.array(V['P'][it], dtype=np.float32) + np.array(V['PB'][it], dtype=np.float32)
            T_C = (t_pert + 300.0) * ((p_tot / 100000.0) ** RCP) - 273.15

            raw = {}
            for q, _, _, _, _ in HIDROS_DEF:
                if q == 'SLW':
                    continue
                if q in V:
                    raw[q] = np.array(V[q][it], dtype=np.float32) * 1000.0
                else:
                    raw[q] = np.zeros_like(T_C, dtype=np.float32)
            raw['SLW'] = np.where(T_C < 0.0, raw['QCLOUD'] + raw['QRAIN'], 0.0).astype(np.float32)

            img = vtk.vtkImageData()
            img.SetDimensions(nx, ny, len(ZS_KM))
            img.SetOrigin(float(xs[0]), float(ys[0]), 0.0)
            img.SetSpacing(dx, dx, float((ZS_KM[1] - ZS_KM[0]) * VE))

            for q, _, _, _, _ in HIDROS_DEF:
                g = interp_z(raw[q], zm, hgt_km)
                img.GetPointData().AddArray(to_vtk(g, q))

            fn = f'tempestade_{seq:03d}.vti'
            fpath = os.path.join(SERIES_DIR, fn)
            w_im = vtk.vtkXMLImageDataWriter()
            w_im.SetFileName(fpath)
            w_im.SetInputData(img)
            w_im.Write()

            series_info.append({'name': fn, 'time': float(seq), 't_str': t_str})
            print(f"  Frame {seq:02d} [{t_str}] gravado (it={it}).")

    with open(series_path, 'w', encoding='utf-8') as f:
        json.dump({'file-series-version': '1.0', 'files': series_info}, f, indent=1)

    return series_info

def fonte(sz, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, sz)

def anotar_frame(png_path, titulo, subtitulo, hora_str, frame_idx, total_frames, hidros_ativos):
    im = Image.open(png_path).convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    # 1. Barra de cabeçalho superior escura translúcida
    d.rectangle([0, 0, W_IMG, 102], fill=(11, 18, 32, 230))
    d.text((28, 14), titulo, font=fonte(27, True), fill=(248, 250, 252, 255))
    d.text((28, 56), subtitulo, font=fonte(18, False), fill=(195, 208, 226, 255))

    # Canto direito
    tw = d.textlength(hora_str, font=fonte(26, True))
    d.text((W_IMG - 28 - tw, 14), hora_str, font=fonte(26, True), fill=(255, 255, 255, 255))
    info_dir = f"Rotação 360° · Quadro {frame_idx + 1}/{total_frames}"
    tw2 = d.textlength(info_dir, font=fonte(17))
    d.text((W_IMG - 28 - tw2, 56), info_dir, font=fonte(17), fill=(148, 163, 184, 255))

    # 2. Caixa de Legenda Dinâmica no canto inferior esquerdo
    n_it = len(hidros_ativos)
    if n_it > 0:
        box_h = 32 + n_it * 34
        box_w = 460
        px, py = 24, H_IMG - box_h - 24
        d.rounded_rectangle([px, py, px + box_w, py + box_h], radius=8, fill=(11, 18, 32, 218), outline=(71, 85, 105, 180))
        d.text((px + 14, py + 8), "Camadas 3D Visíveis no Quadro:", font=fonte(16, True), fill=(226, 232, 240, 255))

        y = py + 32
        for q, rot, cor_hex, lim, _ in hidros_ativos:
            rgb = tuple(int(v * 255) for v in hx(cor_hex))
            d.rounded_rectangle([px + 14, y + 4, px + 38, y + 24], radius=4, fill=rgb + (235,), outline=(255, 255, 255, 160))
            d.text((px + 48, y + 3), f"{rot} ≥ {lim:g} g/kg", font=fonte(15, True), fill=(241, 245, 249, 255))
            y += 34

    Image.alpha_composite(im, ov).convert('RGB').save(png_path)

def construir_roteiro(total_quadros=240, pico_time_val=4.0):
    """
    Constrói a lista com os 240 frames da animação:
    - Rotação de 360° contínua (1.5° por frame).
    - 4 fases:
      1. Evolução temporal da tempestade noturna (21:45 a 23:15 UTC) -> frames 0 a 47
      2. "Despindo" a tempestade no pico (22:45 UTC, time_val=4.0) -> frames 48 a 137
      3. "Vestindo" a tempestade no pico (22:45 UTC, time_val=4.0) -> frames 138 a 207
      4. Órbita 360° final reconstituída no pico -> frames 208 a 239
    """
    roteiro = []
    graus_por_quadro = 360.0 / total_quadros

    # Fase 1: Evolução temporal noturna (0 a 47 = 48 frames, 21:45 a 23:15 UTC)
    n_fase1 = 48
    # 7 timesteps: 0=21:45, 1=22:00, 2=22:15, 3=22:30, 4=22:45 (pico), 5=23:00, 6=23:15
    for f in range(n_fase1):
        t_val = (f / float(n_fase1 - 1)) * 6.0
        # Mapeamento do horário real
        min_tot = 45 + int(f * (90.0 / (n_fase1 - 1)))
        hh = 21 + min_tot // 60
        mm = min_tot % 60
        h_str = f"{hh:02d}:{mm:02d} UTC ({(hh - 3) % 24:02d}:{mm:02d} Local)"
        roteiro.append({
            'frame': f,
            'time_val': t_val,
            'azimuth': -60.0 + f * graus_por_quadro,
            'visiveis': ['QCLOUD', 'QRAIN', 'QGRAUP', 'QHAIL', 'SLW'],
            'opacidades': {'QCLOUD': 0.22, 'QRAIN': 0.65, 'QGRAUP': 0.85, 'QHAIL': 0.95, 'SLW': 0.80},
            'titulo': "1. Evolução Temporal da Tempestade Severa Noturna (21:45 a 23:15 UTC)",
            'subtitulo': "WRF-ARW d03 (2 km) · Convecção Noturna Explícita · Milbrandt-Yau 2 Momentos",
            'hora_str': h_str,
        })

    # Fase 2: "Despindo" a Tempestade Noturna no Pico Convectivo (22:45 UTC / 19:45 Local, 90 frames: 48 a 137)
    sub_fases_despindo = [
        # 48 a 62: Todas as camadas juntas no pico noturno
        (15, ['QCLOUD', 'QRAIN', 'QGRAUP', 'QHAIL', 'SLW'],
         {'QCLOUD': 0.22, 'QRAIN': 0.65, 'QGRAUP': 0.85, 'QHAIL': 0.95, 'SLW': 0.80},
         "2. Estrutura 3D Completa no Pico Noturno (22:45 UTC / 19:45 Local)",
         "Tempestade severa sobre Florianópolis · Refletividade 77.4 dBZ · W = 31.0 m/s"),

        # 63 a 77: Despe a nuvem (revela chuva e interior congelado)
        (15, ['QRAIN', 'QGRAUP', 'QHAIL', 'SLW'],
         {'QRAIN': 0.65, 'QGRAUP': 0.85, 'QHAIL': 0.95, 'SLW': 0.80},
         "3. Despindo a Nuvem: Revela o Eixo de Chuva e a Coluna Convectiva",
         "Nuvem (QCLOUD) removida · Precipitação líquida e núcleos congelados visíveis"),

        # 78 a 92: Despe a chuva (revela carga de gelo e água super-resfriada)
        (15, ['QGRAUP', 'QHAIL', 'SLW'],
         {'QGRAUP': 0.85, 'QHAIL': 0.95, 'SLW': 0.85},
         "4. Despindo a Chuva: Revela a Carga de Gelo e Água Super-resfriada",
         "Chuva removida · Graupel (laranja), Granizo (vermelho) e SLW (verde)"),

        # 93 a 107: Destaque da Água Super-resfriada (SLW)
        (15, ['SLW'],
         {'SLW': 0.95},
         "5. Destaque: Água Líquida Super-resfriada (SLW = 7.24 g/kg, verde)",
         "SLW abundante até -20 °C ao redor da ascendente (combustível da granizogênese)"),

        # 108 a 122: Destaque da Coluna de Graupel (QGRAUP)
        (15, ['QGRAUP'],
         {'QGRAUP': 0.95},
         "6. Destaque: Coluna Massiva de Graupel (QGRAUP = 8.30 g/kg, laranja)",
         "Partículas de gelo em rápida acreção térmica entre 6 km e 12 km de altitude"),

        # 123 a 137: Destaque do Núcleo de Granizo (QHAIL)
        (15, ['QHAIL'],
         {'QHAIL': 1.0},
         "7. Destaque: Núcleo de Granizo Severo (QHAIL = 5.21 g/kg, vermelho)",
         "Pedras gigantes no núcleo ascendente sobre a Ilha de Santa Catarina"),
    ]

    curr_f = n_fase1
    for dur, vis, opacs, tit, sub in sub_fases_despindo:
        for _ in range(dur):
            roteiro.append({
                'frame': curr_f,
                'time_val': pico_time_val,
                'azimuth': -60.0 + curr_f * graus_por_quadro,
                'visiveis': vis,
                'opacidades': opacs,
                'titulo': tit,
                'subtitulo': sub,
                'hora_str': "22:45 UTC (19:45 Local)",
            })
            curr_f += 1

    # Fase 3: "Vestindo" a Tempestade Noturna (Layering back de dentro para fora, 70 frames: 138 a 207)
    sub_fases_vestindo = [
        # 138 a 151: Inicia com o granizo
        (14, ['QHAIL'],
         {'QHAIL': 1.0},
         "8. Vestindo a Tempestade: Núcleo Inicial de Granizo Severo (vermelho)",
         "Recomposição tridimensional a partir do núcleo de granizo (5.21 g/kg)"),

        # 152 a 165: Veste o graupel ao redor
        (14, ['QHAIL', 'QGRAUP'],
         {'QHAIL': 1.0, 'QGRAUP': 0.85},
         "9. Vestindo: Adiciona a Coluna de Graupel (laranja, 8.30 g/kg)",
         "Graupel envolve o granizo na zona mista de congelamento da nuvem"),

        # 166 a 179: Veste a água super-resfriada
        (14, ['QHAIL', 'QGRAUP', 'SLW'],
         {'QHAIL': 1.0, 'QGRAUP': 0.85, 'SLW': 0.80},
         "10. Vestindo: Adiciona a Água Super-resfriada (verde, 7.24 g/kg)",
         "Gotículas super-resfriadas circundando o núcleo de gelo ascendente"),

        # 180 a 193: Veste a chuva
        (14, ['QHAIL', 'QGRAUP', 'SLW', 'QRAIN'],
         {'QHAIL': 0.95, 'QGRAUP': 0.85, 'SLW': 0.80, 'QRAIN': 0.65},
         "11. Vestindo: Adiciona o Eixo de Chuva Líquida Intensa (azul)",
         "Precipitação líquida abaixo do nível de fusão (isoterma de 0 °C em 4.7 km)"),

        # 194 a 207: Veste a nuvem (reconstituição completa)
        (14, ['QHAIL', 'QGRAUP', 'SLW', 'QRAIN', 'QCLOUD'],
         {'QHAIL': 0.95, 'QGRAUP': 0.85, 'SLW': 0.80, 'QRAIN': 0.65, 'QCLOUD': 0.22},
         "12. Vestindo: Reconstituição do Envelope Completo de Nuvem (cinza)",
         "Nuvem e bigorna envolvendo toda a supercélula noturna de Santa Catarina"),
    ]

    for dur, vis, opacs, tit, sub in sub_fases_vestindo:
        for _ in range(dur):
            roteiro.append({
                'frame': curr_f,
                'time_val': pico_time_val,
                'azimuth': -60.0 + curr_f * graus_por_quadro,
                'visiveis': vis,
                'opacidades': opacs,
                'titulo': tit,
                'subtitulo': sub,
                'hora_str': "22:45 UTC (19:45 Local)",
            })
            curr_f += 1

    # Fase 4: Órbita final completa da tempestade reconstituída (frames 208 a 239 = 32 frames)
    while curr_f < total_quadros:
        roteiro.append({
            'frame': curr_f,
            'time_val': pico_time_val,
            'azimuth': -60.0 + curr_f * graus_por_quadro,
            'visiveis': ['QCLOUD', 'QRAIN', 'QGRAUP', 'QHAIL', 'SLW'],
            'opacidades': {'QCLOUD': 0.22, 'QRAIN': 0.65, 'QGRAUP': 0.85, 'QHAIL': 0.95, 'SLW': 0.80},
            'titulo': "13. Estrutura 3D Final Reconstituída sobre o Relevo de SC",
            'subtitulo': "Visão 360° Completa: Relevo, Linha de Costa e Todos os Hidrometeoros",
            'hora_str': "22:45 UTC (19:45 Local)",
        })
        curr_f += 1

    return roteiro

def executar():
    print("=== INICIANDO PIPELINE DE ANIMAÇÃO 3D DA TEMPESTADE NOTURNA ===")

    # 1. Preparar dados da tempestade noturna (timesteps 39 a 45)
    # Timestep 43 é o pico absoluto (22:45:06 UTC), mapeado como índice 4 (time_val = 4.0)
    indices_noturnos = [39, 40, 41, 42, 43, 44, 45]
    pico_time_val = 4.0
    series_info = preparar_series_noturna(indices_noturnos)
    print(f"Série noturna preparada com {len(series_info)} instantes.")

    # 2. Configurar Cena no ParaView
    print("Configurando cena 3D no ParaView...")
    view = CreateView('RenderView')
    view.ViewSize = [W_IMG, H_IMG]
    view.OrientationAxesVisibility = 0
    view.UseColorPaletteForBackground = 0
    view.BackgroundColorMode = 'Gradient'
    view.Background2 = hx('#0b1324')
    view.Background = hx('#243247')
    view.KeyLightWarmth = 0.55
    view.KeyLightIntensity = 0.88
    view.KeyLightElevation = 48
    view.KeyLightAzimuth = -32
    view.FillLightKFRatio = 3.2

    # Carregar Relevo e Linha de Costa
    relevo = XMLStructuredGridReader(registrationName='Relevo_d03', FileName=[relevo_vts])
    rd = Show(relevo, view)
    rd.Representation = 'Surface'
    ColorBy(rd, ('POINTS', 'Elevacao_m'))
    lut = GetColorTransferFunction('Elevacao_m')
    lut.ColorSpace = 'Lab'
    lut.RGBPoints = [
        -100.0, *hx('#172a3f'),
        -1.0,   *hx('#1e3a5a'),
        0.5,    *hx('#4a5e42'),
        150.0,  *hx('#5c6f4b'),
        500.0,  *hx('#787854'),
        900.0,  *hx('#94876b'),
        1300.0, *hx('#aa9b82'),
        1700.0, *hx('#d1cbc0'),
    ]
    lut.AutomaticRescaleRangeMode = 'Never'
    rd.SetScalarBarVisibility(view, False)

    # Carregar Série Temporal de Hidrometeoros
    storm = XMLImageDataReader(registrationName='Tempestade_3D', FileName=[series_path])

    # Criar Contornos para Cada Hidrometeoro com Cores Fixas Desvinculadas do Mapa de Cor
    contornos = {}
    for q, rot, cor_hex, lim, op_padrao in HIDROS_DEF:
        c = Contour(registrationName=f'C_{q}', Input=storm)
        c.ContourBy = ['POINTS', q]
        c.Isosurfaces = [lim]
        c.ComputeNormals = 1

        disp = Show(c, view)
        disp.Representation = 'Surface'
        disp.ColorArrayName = ['POINTS', '']  # Desvincula mapa de cores escalar padrão (evita tudo azul)
        ColorBy(disp, None)                  # Garante cor sólida DiffuseColor
        disp.AmbientColor = hx(cor_hex)
        disp.DiffuseColor = hx(cor_hex)
        disp.Opacity = op_padrao
        disp.Specular = 0.35
        disp.SpecularPower = 28.0
        disp.Interpolation = 'Gouraud'

        contornos[q] = (c, disp, rot, cor_hex, lim)

    total_quadros = 240
    roteiro = construir_roteiro(total_quadros, pico_time_val)
    print(f"Roteiro construído com {len(roteiro)} quadros.")

    # Ponto focal centrado na célula noturna sobre Florianópolis
    focal = [-10.0, -18.0, 22.0]
    dist = 135.0
    elev = 22.0
    rad_e = math.radians(elev)

    for item in roteiro:
        idx = item['frame']
        t_val = item['time_val']
        az = item['azimuth']
        vis_list = item['visiveis']
        opacs = item['opacidades']

        # Atualiza o tempo do modelo
        view.ViewTime = t_val

        # Atualiza visibilidade e opacidade das camadas
        hidros_ativos = []
        for q, rot, cor_hex, lim, _ in HIDROS_DEF:
            c, disp, _, _, _ = contornos[q]
            if q in vis_list:
                disp.Visibility = 1
                disp.Opacity = opacs.get(q, 0.85)
                hidros_ativos.append((q, rot, cor_hex, lim, opacs.get(q, 0.85)))
            else:
                disp.Visibility = 0

        # Atualiza a câmera para órbita 360° contínua
        rad_a = math.radians(az)
        cx = focal[0] + dist * math.cos(rad_e) * math.sin(rad_a)
        cy = focal[1] - dist * math.cos(rad_e) * math.cos(rad_a)
        cz = focal[2] + dist * math.sin(rad_e)

        view.CameraFocalPoint = focal
        view.CameraPosition = [cx, cy, cz]
        view.CameraViewUp = [0, 0, 1]

        Render(view)

        png_path = os.path.join(FRAMES_DIR, f'frame_{idx:04d}.png')
        SaveScreenshot(png_path, view, ImageResolution=[W_IMG, H_IMG])

        # Anotação de alta resolução com PIL
        anotar_frame(png_path, item['titulo'], item['subtitulo'], item['hora_str'], idx, total_quadros, hidros_ativos)

        if idx % 20 == 0 or idx == total_quadros - 1:
            print(f"  Progresso: {idx + 1}/{total_quadros} quadros renderizados ({item['titulo'][:38]}...)")

    print("Renderização de todos os quadros concluída! Iniciando compilação de vídeo e GIF...")

    ffmpeg_exe = shutil.which('ffmpeg') or r'C:\Users\haas\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe'
    mp4_out = os.path.join(FIG_DIR, 'granizo_3d_evolucao.mp4')
    gif_out = os.path.join(FIG_DIR, 'granizo_3d_evolucao.gif')

    # Compila MP4 a 15 fps (16 segundos de animação suave)
    print("Compilando MP4...")
    cmd_mp4 = [
        ffmpeg_exe, '-y', '-loglevel', 'error',
        '-framerate', '15',
        '-i', os.path.join(FRAMES_DIR, 'frame_%04d.png'),
        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
        '-pix_fmt', 'yuv420p',
        mp4_out
    ]
    subprocess.run(cmd_mp4, check=True)

    # Compila GIF a 15 fps otimizado
    print("Compilando GIF animado...")
    cmd_gif = [
        ffmpeg_exe, '-y', '-loglevel', 'error',
        '-framerate', '15',
        '-i', os.path.join(FRAMES_DIR, 'frame_%04d.png'),
        '-vf', 'scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=192[p];[b][p]paletteuse=dither=sierra2_4a',
        '-loop', '0',
        gif_out
    ]
    subprocess.run(cmd_gif, check=True)

    # Copiar para o repositório tarefa-meso
    for f in [mp4_out, gif_out]:
        dest = os.path.join(REPO_FIG, os.path.basename(f))
        shutil.copy2(f, dest)
        print(f"Copiado para {dest} ({os.path.getsize(dest)} bytes)")

    print("=== ANIMAÇÃO CONCLUÍDA COM SUCESSO! ===")

if __name__ == '__main__':
    executar()
