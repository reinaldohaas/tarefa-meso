# -*- coding: utf-8 -*-
"""
Animação 3D dos hidrometeoros no ParaView, no estilo "Supercell on a Carousel" (Leigh Orf), centrada na célula
que cruzou a Ilha de Santa Catarina às 12:45 UTC (o horário de metricas_wrf.json).

Duas partes, com a câmera girando sem parar em volta da coluna da célula:
  1. A evolução da onda que cruzou a Ilha, de 12:15 a 13:45 UTC, com todos os hidrometeoros.
  2. A tempestade parada às 12:45 UTC, com cada hidrometeoro apresentado sozinho (nuvem, chuva, gelo, neve,
     graupel, granizo, água super-resfriada) e, por fim, todos juntos.

- Mesma preparação das figuras estáticas (render_3d_paraview.py): altura real z = (PH + PHB)/9,81,
  exagero vertical de 4x, cores e limiares fixos, relevo e linha de costa, volume recortado em volta da célula.
- Um .vti por saída de 15 min; o TemporalInterpolator do ParaView interpola linearmente entre saídas.
- Linha vertical branca na coluna da célula, para mostrar que ela está sobre a Ilha.

Uso:
  "C:/Program Files/ParaView 6.2.0/bin/pvpython.exe" --force-offscreen-rendering animacao_3d_paraview.py
Saídas: figuras/animacao_3d_hidrometeoros.mp4 e figuras/animacao_3d_poster.png (projeto e repositório)
"""
import datetime as dt
import json
import math
import os
import shutil
import subprocess
import sys

import netCDF4
import numpy as np
import vtk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_3d_paraview as R  # noqa: E402
from paraview.simple import *  # noqa: E402,F401,F403

WRFOUT = os.path.join(R.WRF_DIR, 'wrfout_d03_2026-08-29_12_00_00')
ANTES_MIN, DEPOIS_MIN = 30, 60                                # janela em volta do horário de metricas_wrf.json
QUADROS_POR_SAIDA = 20                                        # parte 1: quadros interpolados entre saídas de 15 min
QUADROS_POR_HIDRO = 60                                        # parte 2: quadros por hidrometeoro (2,5 s)
GRAUS_POR_QUADRO = 0.9                                        # rotação contínua da câmera
FPS = 24
REUSAR = os.environ.get('REUSAR') == '1'                     # reaproveita os quadros já prontos da parte 1
QUADROS_DIR = os.path.join(R.BASE, 'figuras', 'animacao_quadros')
REPO = r'C:\Users\haas\github\tarefa-meso'
FFMPEG = shutil.which('ffmpeg') or r'C:\Users\haas\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe'
SUB = 'WRF-ARW d03 (2 km) · Milbrandt-Yau 2 momentos · célula sobre a Ilha de SC (linha branca)'


def gravar_series():
    """Um .vti por saída da janela, com os hidrometeoros interpolados para altura real (g/kg)."""
    pasta = os.path.join(R.PV_DIR, 'serie')
    os.makedirs(pasta, exist_ok=True)
    for f in os.listdir(pasta):
        os.remove(os.path.join(pasta, f))
    arquivos, horas, maximos = [], [], {q: 0.0 for q, *_ in R.HIDROS}
    meta = json.load(open(os.path.join(R.BASE, 'metricas_wrf.json'), encoding='utf-8'))
    nc = int(round(R.MEIA_CAIXA_KM / meta['dx_km']))
    jc, ic = meta['j_celula'], meta['i_celula']
    max_foco = {}                                               # máximos às 12:45 na caixa da célula (parte 2)
    with netCDF4.Dataset(WRFOUT) as ds:
        V = ds.variables
        tempos = [b''.join(t).decode() for t in V['Times'][:]]
        foco = dt.datetime.strptime(meta['tempo_pico_utc'][:16], '%Y-%m-%d_%H:%M')
        ini = (foco - dt.timedelta(minutes=ANTES_MIN)).strftime('%Y-%m-%d_%H:%M')
        fim = (foco + dt.timedelta(minutes=DEPOIS_MIN + 1)).strftime('%Y-%m-%d_%H:%M')
        idx = [i for i, t in enumerate(tempos) if ini <= t[:16] <= fim]
        dx = float(ds.getncattr('DX')) / 1000.0
        ny, nx = V['HGT'].shape[1:]
        xs = (np.arange(nx) - (nx - 1) / 2.0) * dx
        ys = (np.arange(ny) - (ny - 1) / 2.0) * dx
        for n, it in enumerate(idx):
            hgt_km = np.array(V['HGT'][it], dtype=np.float32) / 1000.0
            zst = (np.array(V['PH'][it], dtype=np.float32) + np.array(V['PHB'][it], dtype=np.float32)) / R.G / 1000.0
            zm = 0.5 * (zst[:-1] + zst[1:])
            p = np.array(V['P'][it], dtype=np.float32) + np.array(V['PB'][it], dtype=np.float32)
            T_C = (np.array(V['T'][it], dtype=np.float32) + 300.0) * (p / 1e5) ** R.RCP - 273.15
            raw = {q: (np.array(V[q][it], dtype=np.float32) * 1000.0 if q in V else np.zeros_like(T_C))
                   for q, *_ in R.HIDROS if q != 'SLW'}
            raw['SLW'] = np.where(T_C < 0.0, raw['QCLOUD'] + raw['QRAIN'], 0.0).astype(np.float32)
            img = vtk.vtkImageData()
            img.SetDimensions(nx, ny, len(R.ZS_KM))
            img.SetOrigin(float(xs[0]), float(ys[0]), 0.0)
            img.SetSpacing(dx, dx, float((R.ZS_KM[1] - R.ZS_KM[0]) * R.VE))
            for q, *_ in R.HIDROS:
                g = R.interp_z(raw[q], zm, hgt_km)
                maximos[q] = max(maximos[q], float(g.max()))
                if tempos[it][:16] == meta['tempo_pico_utc'][:16]:
                    max_foco[q] = float(g[:, max(jc - nc, 0):jc + nc + 1, max(ic - nc, 0):ic + nc + 1].max())
                img.GetPointData().AddArray(R.to_vtk(g, q))
            arq = os.path.join(pasta, f'hidro_{n:03d}.vti')
            w = vtk.vtkXMLImageDataWriter()
            w.SetFileName(arq)
            w.SetInputData(img)
            w.Write()
            arquivos.append(arq)
            horas.append(dt.datetime.strptime(tempos[it][:16], '%Y-%m-%d_%H:%M'))
            print('saída', tempos[it], flush=True)
    limiares = {}
    for q, _, _, lim, _ in R.HIDROS:
        limiares[q] = lim if maximos[q] > lim * 1.15 else round(max(0.01, maximos[q] * 0.35), 3)
    # Parte 2: limiar de cada hidrometeoro às 12:45 na caixa da célula, para nenhum trecho sair vazio
    lim_foco = {}
    for q, _, _, lim, _ in R.HIDROS:
        m = max_foco.get(q, 0.0)
        lim_foco[q] = lim if m > lim * 1.15 else round(max(0.005, m * 0.35), 3)
    print('limiares às 12:45:', lim_foco, '| máximos:', {k: round(v, 2) for k, v in max_foco.items()}, flush=True)
    return arquivos, horas, limiares, maximos, lim_foco, max_foco


def main():
    meta = json.load(open(os.path.join(R.BASE, 'metricas_wrf.json'), encoding='utf-8'))
    relevo_vts, _, _, focal_cel, _, _ = R.preparar_vtk()
    arquivos, horas, limiares, maximos, lim_foco, max_foco = gravar_series()
    t_foco = dt.datetime.strptime(meta['tempo_pico_utc'][:16], '%Y-%m-%d_%H:%M')
    t_foco_idx = (t_foco - horas[0]).total_seconds() / 900.0     # 12:45 em unidades de saída

    view = CreateView('RenderView')
    view.ViewSize = [R.W_IMG, R.H_IMG]
    view.OrientationAxesVisibility = 0
    view.UseColorPaletteForBackground = 0
    view.BackgroundColorMode = 'Gradient'
    view.Background2 = R.hx('#0b1324')
    view.Background = R.hx('#243247')
    view.KeyLightWarmth, view.KeyLightIntensity = 0.55, 0.88
    view.KeyLightElevation, view.KeyLightAzimuth = 48, -32
    view.FillLightKFRatio = 3.2

    relevo = XMLStructuredGridReader(FileName=[relevo_vts])
    rd = Show(relevo, view)
    ColorBy(rd, ('POINTS', 'Elevacao_m'))
    lut = GetColorTransferFunction('Elevacao_m')
    lut.RGBPoints = [-100.0, *R.hx('#172a3f'), -1.0, *R.hx('#1e3650'), 0.5, *R.hx('#4d5e47'),
                     200.0, *R.hx('#677352'), 600.0, *R.hx('#8c8265'), 1200.0, *R.hx('#b8ad99')]
    lut.AutomaticRescaleRangeMode = 'Never'
    rd.SetScalarBarVisibility(view, False)
    costa = Contour(Input=relevo)
    costa.ContourBy = ['POINTS', 'Landmask']
    costa.Isosurfaces = [0.5]
    cd = Show(costa, view)
    cd.ColorArrayName = ['POINTS', '']
    cd.AmbientColor = cd.DiffuseColor = R.hx('#f8fafc')
    cd.LineWidth = 2.0
    R.marcar_coluna(view, focal_cel)

    serie = XMLImageDataReader(FileName=arquivos)                # tempo 0, 1, 2... (uma saída por unidade)
    interp = TemporalInterpolator(Input=serie)
    volume = R.recorte_celula(interp, ref=serie)
    disp = {}
    for q, rotulo, cor, _, opac in R.HIDROS:
        c = Contour(Input=volume)
        c.ContourBy = ['POINTS', q]
        c.Isosurfaces = [limiares[q]]
        c.ComputeNormals = 1
        d = Show(c, view)
        d.ColorArrayName = ['POINTS', '']
        d.AmbientColor = d.DiffuseColor = R.hx(cor)
        d.Opacity = opac
        d.Specular, d.SpecularPower = 0.25, 28.0
        disp[q] = (c, d, rotulo, cor, opac)
    todos = [(rot, cor, limiares[q], maximos[q]) for q, (c, d, rot, cor, op) in disp.items()]

    os.makedirs(QUADROS_DIR, exist_ok=True)
    if not REUSAR:
        for f in os.listdir(QUADROS_DIR):
            os.remove(os.path.join(QUADROS_DIR, f))

    # Roteiro: (tempo em unidades de saída, hidrometeoros visíveis, título, itens da legenda)
    roteiro = []
    n1 = (len(arquivos) - 1) * QUADROS_POR_SAIDA + 1
    for f in range(n1):
        roteiro.append((f / QUADROS_POR_SAIDA, list(disp), f'A tempestade sobre a Ilha: {horas[0]:%H:%M} a {horas[-1]:%H:%M} UTC', todos))
    ordem = ['QCLOUD', 'QRAIN', 'QICE', 'QSNOW', 'QGRAUP', 'QHAIL', 'SLW']
    for q in ordem + ['todos']:
        vis = list(disp) if q == 'todos' else [q]
        titulo = f'Às {t_foco:%H:%M} UTC, todos os hidrometeoros juntos' if q == 'todos' else f'Às {t_foco:%H:%M} UTC, só {disp[q][2]}'
        todos_foco = [(disp[k][2], disp[k][3], lim_foco[k], max_foco.get(k, 0.0)) for k in disp]
        itens = todos_foco if q == 'todos' else [(disp[q][2], disp[q][3], lim_foco[q], max_foco.get(q, 0.0))]
        for _ in range(QUADROS_POR_HIDRO):
            roteiro.append((t_foco_idx, vis, titulo, itens))
    if os.environ.get('TESTE'):
        roteiro = [roteiro[k] for k in (n1 // 2, n1 + 5 * QUADROS_POR_HIDRO + 10, len(roteiro) - 5)]

    cena = GetAnimationScene()
    cena.UpdateAnimationUsingDataTimeSteps()
    dist, elev = 150.0, 24.0
    focal = [focal_cel[0], focal_cel[1], 5.0 * R.VE]
    visiveis = None
    ja_foco = False
    for f, (t, vis, titulo, itens) in enumerate(roteiro):
        parte2 = f >= n1 or os.environ.get('TESTE')
        if REUSAR and not parte2 and os.path.exists(os.path.join(QUADROS_DIR, f'q_{f:04d}.png')):
            continue                                            # parte 1 já renderizada (REUSAR=1)
        if parte2 and not ja_foco:
            for q, (c, *_r) in disp.items():
                c.Isosurfaces = [lim_foco[q]]
            ja_foco = True
        if vis != visiveis:
            for q, (c, d, *_r) in disp.items():
                d.Visibility = 1 if q in vis else 0
                d.Opacity = disp[q][4] if len(vis) > 1 else max(0.85, disp[q][4])
            visiveis = vis
        cena.AnimationTime = t
        view.ViewTime = t
        az = math.radians(-40.0 + GRAUS_POR_QUADRO * f)
        e = math.radians(elev)
        view.CameraFocalPoint = focal
        view.CameraPosition = [focal[0] + dist * math.cos(e) * math.sin(az),
                               focal[1] - dist * math.cos(e) * math.cos(az),
                               focal[2] + dist * math.sin(e)]
        view.CameraViewUp = [0, 0, 1]
        view.CameraViewAngle = 30.0
        Render(view)
        png = os.path.join(QUADROS_DIR, f'q_{f:04d}.png')
        SaveScreenshot(png, view, ImageResolution=[R.W_IMG, R.H_IMG])
        hora = horas[0] + dt.timedelta(minutes=15 * t)
        R.anotar_png(png, titulo, SUB, itens, hora.strftime('%Y-%m-%d %H:%M'))
        if f % 48 == 0:
            print(f'quadro {f}/{len(roteiro)}', titulo, flush=True)

    if os.environ.get('TESTE'):
        return
    mp4 = os.path.join(R.BASE, 'figuras', 'animacao_3d_hidrometeoros.mp4')
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(QUADROS_DIR, 'q_%04d.png'),
                    '-vf', 'scale=1280:-2', '-c:v', 'libx264', '-crf', '24', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', mp4], check=True)
    poster = os.path.join(R.BASE, 'figuras', 'animacao_3d_poster.png')
    shutil.copy2(os.path.join(QUADROS_DIR, f'q_{len(roteiro) - 10:04d}.png'), poster)
    for arq in (mp4, poster):
        shutil.copy2(arq, os.path.join(REPO, 'figuras', os.path.basename(arq)))
    print('MP4:', mp4, f'{os.path.getsize(mp4) / 1e6:.1f} MB', len(roteiro), 'quadros')


if __name__ == '__main__':
    main()
