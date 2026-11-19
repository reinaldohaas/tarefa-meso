# -*- coding: utf-8 -*-
"""
Animação 3D Completa dos Hidrometeoros no ParaView (via pvpython + ffmpeg)
Projeto: C:\gis4wrf\projects\granizo (Seminário Final - Parte 2, FSC7116 UFSC).

Atende rigorosamente às solicitações do professor:
1. Cores fixas e distintas para cada hidrometeoro (evitando o erro de tudo azul):
   - Nuvem (QCLOUD): cinza claro (#d1d5db)
   - Chuva (QRAIN): azul vivo (#2563eb)
   - Graupel (QGRAUP): laranja brilhante (#f97316)
   - Granizo (QHAIL): vermelho carmesim (#dc2626)
   - Água Super-resfriada (SLW): verde esmeralda (#16a34a)
2. Rotação 360° contínua e suave da câmera ao redor da tempestade e do relevo
   (1,5° por frame ao longo de 240 frames).
3. Sequência de destaques com camadas "despidas" (peeling de fora para dentro)
   e "vestidas" (layering back de dentro para fora), mostrando a anatomia
   tridimensional da tempestade.
"""
import os
import sys
import json
import math
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paraview.simple import *

BASE = r'C:\gis4wrf\projects\granizo'
PV_DIR = os.path.join(BASE, 'paraview_data')
SERIES_DIR = os.path.join(PV_DIR, 'series_anim')
FRAMES_DIR = os.path.join(PV_DIR, 'frames_360_peel')
FIG_DIR = os.path.join(BASE, 'figuras')
REPO_FIG = r'C:\Users\haas\github\tarefa-meso\figuras'

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(REPO_FIG, exist_ok=True)

W_IMG, H_IMG = 1600, 960
FONT = r'C:\Windows\Fonts\arial.ttf'
FONT_B = r'C:\Windows\Fonts\arialbd.ttf'
VE = 4.0

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

def fonte(sz, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, sz)

def anotar_frame(png_path, titulo, subtitulo, hora_str, frame_idx, total_frames, hidros_ativos):
    im = Image.open(png_path).convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    # 1. Barra de cabeçalho superior escura translúcida
    d.rectangle([0, 0, W_IMG, 102], fill=(11, 18, 32, 228))
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
        d.rounded_rectangle([px, py, px + box_w, py + box_h], radius=8, fill=(11, 18, 32, 215), outline=(71, 85, 105, 180))
        d.text((px + 14, py + 8), "Camadas 3D Visíveis no Quadro:", font=fonte(16, True), fill=(226, 232, 240, 255))

        y = py + 32
        for q, rot, cor_hex, lim, _ in hidros_ativos:
            rgb = tuple(int(v * 255) for v in hx(cor_hex))
            d.rounded_rectangle([px + 14, y + 4, px + 38, y + 24], radius=4, fill=rgb + (235,), outline=(255, 255, 255, 160))
            d.text((px + 48, y + 3), f"{rot} ≥ {lim:g} g/kg", font=fonte(15, True), fill=(241, 245, 249, 255))
            y += 34

    Image.alpha_composite(im, ov).convert('RGB').save(png_path)

def construir_roteiro(total_quadros=240):
    """
    Constrói a lista com os 240 frames da animação:
    - Rotação de 360° contínua (1.5° por frame).
    - 4 fases: Evolução temporal -> Despindo -> Vestindo -> Órbita final completa.
    """
    roteiro = []
    graus_por_quadro = 360.0 / total_quadros

    # Fase 1: Evolução temporal inicial (0 a 39 = 40 frames, 12:45 a 14:00 UTC)
    n_fase1 = 40
    for f in range(n_fase1):
        t_val = (f / n_fase1) * 5.0  # avança pelas saídas 0 a 5
        # Interpolação de horário
        min_tot = 45 + int(f * (75.0 / n_fase1))
        hh = 12 + min_tot // 60
        mm = min_tot % 60
        h_str = f"{hh:02d}:{mm:02d} UTC ({(hh - 3) % 24:02d}:{mm:02d} Local)"
        roteiro.append({
            'frame': f,
            'time_val': t_val,
            'azimuth': -45.0 + f * graus_por_quadro,
            'visiveis': ['QCLOUD', 'QRAIN', 'QGRAUP', 'QHAIL', 'SLW'],
            'opacidades': {'QCLOUD': 0.20, 'QRAIN': 0.60, 'QGRAUP': 0.85, 'QHAIL': 0.95, 'SLW': 0.75},
            'titulo': "1. Evolução Temporal da Tempestade sobre a Ilha de Santa Catarina",
            'subtitulo': "WRF-ARW d03 (2 km) · Convecção Explícita · Milbrandt-Yau 2 Momentos",
            'hora_str': h_str,
        })

    # Fase 2: "Despindo" a Tempestade (Pico Convectivo em 12:45 UTC, frames 40 a 129 = 90 frames)
    # Mantém o tempo fixo em 12:45 UTC (time_val = 0.0) e a câmera gira continuamente 360°!
    sub_fases_despindo = [
        # 40 a 54: Todas as camadas juntas no pico
        (15, ['QCLOUD', 'QRAIN', 'QGRAUP', 'QHAIL', 'SLW'],
         {'QCLOUD': 0.20, 'QRAIN': 0.60, 'QGRAUP': 0.85, 'QHAIL': 0.95, 'SLW': 0.75},
         "2. Estrutura 3D Completa no Pico: Nuvem, Chuva e Núcleo Congelado",
         "Tempestade sobre a Ilha de Santa Catarina (12:45 UTC / 09:45 Local)"),

        # 55 a 69: Despe a nuvem (revela chuva e interior)
        (15, ['QRAIN', 'QGRAUP', 'QHAIL', 'SLW'],
         {'QRAIN': 0.65, 'QGRAUP': 0.85, 'QHAIL': 0.95, 'SLW': 0.75},
         "3. Despindo a Nuvem: Revela o Eixo de Chuva e a Coluna Convectiva",
         "Nuvem (QCLOUD) removida · Precipitação líquida e núcleos congelados visíveis"),

        # 70 a 84: Despe a chuva (revela carga de gelo e SLW)
        (15, ['QGRAUP', 'QHAIL', 'SLW'],
         {'QGRAUP': 0.85, 'QHAIL': 0.95, 'SLW': 0.80},
         "4. Despindo a Chuva: Revela a Carga de Gelo e Água Super-resfriada",
         "Chuva (QRAIN) removida · Graupel (laranja), Granizo (vermelho) e SLW (verde)"),

        # 85 a 99: Destaque da Água Super-resfriada (SLW)
        (15, ['SLW'],
         {'SLW': 0.95},
         "5. Destaque: Água Líquida Super-resfriada (SLW, verde)",
         "SLW presente até -20 °C ao redor da ascendente (combustível para formação de granizo)"),

        # 100 a 114: Destaque da Coluna de Graupel (QGRAUP)
        (15, ['QGRAUP'],
         {'QGRAUP': 0.95},
         "6. Destaque: Coluna de Graupel (QGRAUP, laranja)",
         "Partículas de gelo de densidade intermediária crescendo por acreção na ascendente"),

        # 115 a 129: Destaque do Núcleo de Granizo (QHAIL)
        (15, ['QHAIL'],
         {'QHAIL': 1.0},
         "7. Destaque: Núcleo de Granizo de Alta Densidade (QHAIL, vermelho)",
         "Pedras de granizo formadas no centro da corrente ascendente vigorosa"),
    ]

    curr_f = n_fase1
    for dur, vis, opacs, tit, sub in sub_fases_despindo:
        for _ in range(dur):
            roteiro.append({
                'frame': curr_f,
                'time_val': 0.0,
                'azimuth': -45.0 + curr_f * graus_por_quadro,
                'visiveis': vis,
                'opacidades': opacs,
                'titulo': tit,
                'subtitulo': sub,
                'hora_str': "12:45 UTC (09:45 Local)",
            })
            curr_f += 1

    # Fase 3: "Vestindo" a Tempestade (Layering back de dentro para fora, frames 130 a 204 = 75 frames)
    sub_fases_vestindo = [
        # 130 a 144: Inicia com o granizo
        (15, ['QHAIL'],
         {'QHAIL': 1.0},
         "8. Vestindo a Tempestade: Núcleo Inicial de Granizo (vermelho)",
         "Iniciando a recomposição tridimensional a partir do núcleo de granizo"),

        # 145 a 159: Veste o graupel ao redor
        (15, ['QHAIL', 'QGRAUP'],
         {'QHAIL': 1.0, 'QGRAUP': 0.80},
         "9. Vestindo: Adiciona a Coluna de Graupel (laranja)",
         "Graupel envolve o granizo na zona mista de congelamento"),

        # 160 a 174: Veste a água super-resfriada
        (15, ['QHAIL', 'QGRAUP', 'SLW'],
         {'QHAIL': 1.0, 'QGRAUP': 0.80, 'SLW': 0.75},
         "10. Vestindo: Adiciona a Água Super-resfriada (verde)",
         "Gotículas super-resfriadas circundando o núcleo de gelo"),

        # 175 a 189: Veste a chuva
        (15, ['QHAIL', 'QGRAUP', 'SLW', 'QRAIN'],
         {'QHAIL': 0.95, 'QGRAUP': 0.85, 'SLW': 0.75, 'QRAIN': 0.65},
         "11. Vestindo: Adiciona o Eixo de Chuva (azul)",
         "Precipitação líquida abaixo do nível de congelamento (isoterma de 0 °C)"),

        # 190 a 204: Veste a nuvem (reconstituição completa)
        (15, ['QHAIL', 'QGRAUP', 'SLW', 'QRAIN', 'QCLOUD'],
         {'QHAIL': 0.95, 'QGRAUP': 0.85, 'SLW': 0.75, 'QRAIN': 0.65, 'QCLOUD': 0.22},
         "12. Vestindo: Reconstituição do Envelope Completo de Nuvem",
         "Nuvem e bigorna de gelo envolvendo toda a estrutura convectiva"),
    ]

    for dur, vis, opacs, tit, sub in sub_fases_vestindo:
        for _ in range(dur):
            roteiro.append({
                'frame': curr_f,
                'time_val': 0.0,
                'azimuth': -45.0 + curr_f * graus_por_quadro,
                'visiveis': vis,
                'opacidades': opacs,
                'titulo': tit,
                'subtitulo': sub,
                'hora_str': "12:45 UTC (09:45 Local)",
            })
            curr_f += 1

    # Fase 4: Órbita final completa da tempestade reconstituída (frames 205 a 239 = 35 frames)
    while curr_f < total_quadros:
        roteiro.append({
            'frame': curr_f,
            'time_val': 0.0,
            'azimuth': -45.0 + curr_f * graus_por_quadro,
            'visiveis': ['QCLOUD', 'QRAIN', 'QGRAUP', 'QHAIL', 'SLW'],
            'opacidades': {'QCLOUD': 0.22, 'QRAIN': 0.65, 'QGRAUP': 0.85, 'QHAIL': 0.95, 'SLW': 0.75},
            'titulo': "13. Estrutura 3D Final Reconstituída sobre o Relevo de SC",
            'subtitulo': "Visão 360° Completa: Relevo, Linha de Costa e Todos os Hidrometeoros",
            'hora_str': "12:45 UTC (09:45 Local)",
        })
        curr_f += 1

    return roteiro

def executar():
    print("Iniciando configuração do ParaView para Renderização 360° com Despir/Vestir...")

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

    # 1. Carregar Relevo e Linha de Costa
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

    # 2. Carregar Série Temporal de Hidrometeoros
    storm = XMLImageDataReader(registrationName='Tempestade_3D', FileName=[series_path])

    # 3. Criar Contornos para Cada Hidrometeoro COM CORES FIXAS DESVINCULADAS DO MAPA ESCALAR
    contornos = {}
    for q, rot, cor_hex, lim, op_padrao in HIDROS_DEF:
        c = Contour(registrationName=f'C_{q}', Input=storm)
        c.ContourBy = ['POINTS', q]
        c.Isosurfaces = [lim]
        c.ComputeNormals = 1

        disp = Show(c, view)
        disp.Representation = 'Surface'
        disp.ColorArrayName = ['POINTS', '']  # ESSENCIAL: desvincula o mapa de cor padrão azul
        ColorBy(disp, None)                  # Garante coloração pura por DiffuseColor
        disp.AmbientColor = hx(cor_hex)
        disp.DiffuseColor = hx(cor_hex)
        disp.Opacity = op_padrao
        disp.Specular = 0.30
        disp.SpecularPower = 28.0
        disp.Interpolation = 'Gouraud'

        contornos[q] = (c, disp, rot, cor_hex, lim)

    total_quadros = 240
    roteiro = construir_roteiro(total_quadros)
    print(f"Roteiro construído com {len(roteiro)} quadros.")

    focal = [4.0, 6.0, 24.0]
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

        # Atualiza a visibilidade e opacidade das camadas
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

        # Anotação com PIL
        anotar_frame(png_path, item['titulo'], item['subtitulo'], item['hora_str'], idx, total_quadros, hidros_ativos)

        if idx % 20 == 0 or idx == total_quadros - 1:
            print(f"  Progresso: {idx + 1}/{total_quadros} quadros renderizados ({item['titulo'][:40]}...)")

    print("Renderização de todos os quadros concluída! Iniciando compilação do vídeo e GIF...")

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
