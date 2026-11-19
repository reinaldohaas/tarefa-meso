# -*- coding: utf-8 -*-
"""
Geração das figuras 3D obrigatórias no ParaView (via pvpython) para o projeto
C:\gis4wrf\projects\granizo (Seminário Final - Parte 2, FSC7116 UFSC).

Requisitos atendidos (Seção 6 de TAREFA_WRF_HIDROMETEOROS.md):
- Coordenada vertical em altura geométrica real: z = (PH + PHB)/9,81 (km MSL), interpolada para grade estruturada.
- Projeção em km (Lambert Conformal do domínio d03).
- Unidades em g/kg (multiplicadas por 1000).
- Exagero vertical fixo e informado na legenda (VE = 4x na atmosfera e terreno).
- Limiares informados na legenda.
- Cores fixas por hidrometeoro em todas as figuras:
    * QCLOUD (nuvem): cinza claro (#b8c2cc), limiar 0,1 g/kg
    * QRAIN (chuva): azul (#1f6fd1), limiar 0,5 g/kg
    * QICE (gelo): ciano (#22b8cf), limiar 0,05 g/kg
    * QSNOW (neve): lilás (#9b72cf), limiar 0,1 g/kg
    * QGRAUP (graupel): laranja (#f08c00), limiar 0,5 g/kg
    * QHAIL (granizo): vermelho (#d62828), limiar 0,1 g/kg
    * SLW (água super-resfriada): verde (#2b9348), limiar 0,2 g/kg
- Uma imagem 3D para cada hidrometeoro no horário de maior intensidade, todas do mesmo ponto de vista,
  e uma com todos juntos (incluindo SLW), além do arquivo de sessão .pvsm.

Uso:
  "C:/Program Files/ParaView 6.2.0/bin/pvpython.exe" --force-offscreen-rendering render_3d_paraview.py
"""
import os
import sys
import json
import math
import numpy as np
import netCDF4
import vtk
from vtk.util import numpy_support as ns
from PIL import Image, ImageDraw, ImageFont
from paraview.simple import *

BASE = r'C:\gis4wrf\projects\granizo'
WRF_DIR = os.path.join(BASE, 'run_wrf')
FIG_DIR = os.path.join(BASE, 'figuras')
PV_DIR = os.path.join(BASE, 'paraview_data')
SESS_DIR = os.path.join(BASE, 'sessoes')
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(PV_DIR, exist_ok=True)
os.makedirs(SESS_DIR, exist_ok=True)

G = 9.81
RCP = 0.2854
VE = 4.0  # Exagero vertical de 4x (atmosfera e relevo)
ZS_KM = np.arange(0.0, 17.5 + 1e-4, 0.25)  # Níveis verticais físicos de 0 a 17,5 km a cada 250 m

W_IMG, H_IMG = 1600, 960
FONT = r'C:\Windows\Fonts\arial.ttf'
FONT_B = r'C:\Windows\Fonts\arialbd.ttf'

HIDROS = [
    ('QCLOUD', 'Nuvem (QCLOUD)',              '#b8c2cc', 0.10, 0.42),
    ('QRAIN',  'Chuva (QRAIN)',               '#1f6fd1', 0.50, 0.65),
    ('QICE',   'Cristais de Gelo (QICE)',     '#22b8cf', 0.05, 0.50),
    ('QSNOW',  'Neve (QSNOW)',                '#9b72cf', 0.10, 0.50),
    ('QGRAUP', 'Graupel (QGRAUP)',            '#f08c00', 0.50, 0.78),
    ('QHAIL',  'Granizo (QHAIL)',             '#d62828', 0.10, 0.95),
    ('SLW',    'Água Super-resfriada (SLW)',  '#2b9348', 0.20, 0.72),
]


def hx(s):
    s = s.lstrip('#')
    return [int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]


def to_vtk(arr, name):
    v = ns.numpy_to_vtk(np.ascontiguousarray(arr, dtype=np.float32).ravel(), deep=True)
    v.SetName(name)
    return v


def interp_z(f3d, z3d, hgt2d):
    """Interpola campo 3D dos níveis eta (z3d em km MSL) para níveis regulares ZS_KM."""
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


def preparar_vtk():
    """Lê metricas_wrf.json e grava os arquivos VTK (.vts do relevo e .vti dos hidrometeoros em altura real)."""
    meta_path = os.path.join(BASE, 'metricas_wrf.json')
    meta = json.load(open(meta_path, encoding='utf-8'))
    wrfout = meta['wrfout_d03']
    it = meta['it_pico']
    t_str = meta['tempo_pico_utc']

    with netCDF4.Dataset(wrfout) as ds:
        V = ds.variables
        dx = float(ds.getncattr('DX')) / 1000.0
        hgt_m = np.array(V['HGT'][it], dtype=np.float32)
        hgt_km = hgt_m / 1000.0
        land = np.array(V['LANDMASK'][it], dtype=np.float32)
        lat = np.array(V['XLAT'][it], dtype=np.float32)
        lon = np.array(V['XLONG'][it], dtype=np.float32)
        ny, nx = hgt_km.shape

        xs = (np.arange(nx) - (nx - 1) / 2.0) * dx
        ys = (np.arange(ny) - (ny - 1) / 2.0) * dx

        ph = np.array(V['PH'][it], dtype=np.float32)
        phb = np.array(V['PHB'][it], dtype=np.float32)
        zst = (ph + phb) / G / 1000.0
        zm = 0.5 * (zst[:-1] + zst[1:])

        t_pert = np.array(V['T'][it], dtype=np.float32)
        p_tot = np.array(V['P'][it], dtype=np.float32) + np.array(V['PB'][it], dtype=np.float32)
        T_C = (t_pert + 300.0) * ((p_tot / 100000.0) ** RCP) - 273.15

        raw = {}
        for q, _, _, _, _ in HIDROS:
            if q == 'SLW':
                continue
            if q in V:
                raw[q] = np.array(V[q][it], dtype=np.float32) * 1000.0
            else:
                raw[q] = np.zeros_like(T_C, dtype=np.float32)
        raw['SLW'] = np.where(T_C < 0.0, raw['QCLOUD'] + raw['QRAIN'], 0.0).astype(np.float32)

    # 1. Relevo e Linha de Costa em VTK
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

    relevo_vts = os.path.join(PV_DIR, 'relevo_d03.vts')
    w_sg = vtk.vtkXMLStructuredGridWriter()
    w_sg.SetFileName(relevo_vts)
    w_sg.SetInputData(sg)
    w_sg.Write()

    # 2. Grade 3D de hidrometeoros com coordenada z = VE * z_real_km
    img = vtk.vtkImageData()
    img.SetDimensions(nx, ny, len(ZS_KM))
    img.SetOrigin(float(xs[0]), float(ys[0]), 0.0)
    img.SetSpacing(dx, dx, float((ZS_KM[1] - ZS_KM[0]) * VE))

    limiares_usados = {}
    maximos_grade = {}
    for q, rotulo, cor, lim_padrao, _ in HIDROS:
        g = interp_z(raw[q], zm, hgt_km)
        img.GetPointData().AddArray(to_vtk(g, q))
        vmax = float(g.max())
        maximos_grade[q] = vmax
        # Se o máximo da grade for menor que o limiar padrão, ajustar o limiar para 35% do máximo (e informar na legenda)
        if vmax > lim_padrao * 1.15:
            limiares_usados[q] = lim_padrao
        elif vmax > 0.005:
            limiares_usados[q] = round(max(0.01, vmax * 0.35), 3)
        else:
            limiares_usados[q] = lim_padrao

    hidro_vti = os.path.join(PV_DIR, 'hidrometeoros_d03.vti')
    w_im = vtk.vtkXMLImageDataWriter()
    w_im.SetFileName(hidro_vti)
    w_im.SetInputData(img)
    w_im.Write()

    # Posição do núcleo convectivo em coordenadas de cena (km)
    jc, ic = meta['j_celula'], meta['i_celula']
    focal = [float(xs[ic]), float(ys[jc]), float(6.0 * VE)]
    return relevo_vts, hidro_vti, t_str, focal, limiares_usados, maximos_grade


def fonte(sz, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, sz)


def anotar_png(png_path, titulo_principal, subtitulo, itens_legenda, t_str):
    im = Image.open(png_path).convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    # Cabeçalho escuro translúcido
    d.rectangle([0, 0, W_IMG, 102], fill=(11, 18, 32, 215))
    d.text((28, 16), titulo_principal, font=fonte(30, True), fill=(248, 250, 252, 255))
    d.text((28, 58), subtitulo, font=fonte(19, False), fill=(195, 208, 226, 255))

    ft_h = fonte(28, True)
    tw = d.textlength(t_str + ' UTC', font=ft_h)
    d.text((W_IMG - 28 - tw, 18), t_str + ' UTC', font=ft_h, fill=(255, 255, 255, 255))
    sub_dir = f'Altura real z=(PH+PHB)/g · Exagero vertical: {VE:g}×'
    tw2 = d.textlength(sub_dir, font=fonte(18))
    d.text((W_IMG - 28 - tw2, 58), sub_dir, font=fonte(18), fill=(148, 163, 184, 255))

    # Caixa de legenda no canto inferior esquerdo
    n_it = len(itens_legenda)
    box_h = 34 + n_it * 42
    box_w = 470
    px, py = 24, H_IMG - box_h - 24
    d.rounded_rectangle([px, py, px + box_w, py + box_h], radius=10, fill=(11, 18, 32, 210), outline=(71, 85, 105, 180))
    d.text((px + 16, py + 8), 'Isosuperfícies 3D (cores fixas e limiares):', font=fonte(17, True), fill=(226, 232, 240, 255))

    y = py + 34
    for rotulo, cor_hex, lim, vmax in itens_legenda:
        rgb = tuple(int(v * 255) for v in hx(cor_hex))
        d.rounded_rectangle([px + 16, y + 4, px + 46, y + 30], radius=5, fill=rgb + (235,), outline=(255, 255, 255, 140))
        d.text((px + 58, y + 2), f'{rotulo}', font=fonte(17, True), fill=(241, 245, 249, 255))
        d.text((px + 58, y + 21), f'Limiar: {lim:g} g/kg  (máx na grade: {vmax:.2f} g/kg)', font=fonte(14), fill=(165, 180, 202, 255))
        y += 40

    Image.alpha_composite(im, ov).convert('RGB').save(png_path)


def main():
    relevo_vts, hidro_vti, t_str, focal, limiares, maximos = preparar_vtk()

    view = CreateView('RenderView')
    view.ViewSize = [W_IMG, H_IMG]
    view.OrientationAxesVisibility = 1
    view.UseColorPaletteForBackground = 0
    view.BackgroundColorMode = 'Gradient'
    view.Background2 = hx('#0b1324')
    view.Background = hx('#243247')
    view.KeyLightWarmth = 0.55
    view.KeyLightIntensity = 0.88
    view.KeyLightElevation = 48
    view.KeyLightAzimuth = -32
    view.FillLightKFRatio = 3.2

    relevo = XMLStructuredGridReader(registrationName='Relevo_d03', FileName=[relevo_vts])
    rd = Show(relevo, view)
    rd.Representation = 'Surface'
    ColorBy(rd, ('POINTS', 'Elevacao_m'))
    lut = GetColorTransferFunction('Elevacao_m')
    lut.ColorSpace = 'Lab'
    lut.RGBPoints = [
        -100.0, *hx('#172a3f'),
        -1.0,   *hx('#1e3650'),
        0.5,    *hx('#4d5e47'),
        200.0,  *hx('#677352'),
        600.0,  *hx('#8c8265'),
        1200.0, *hx('#b8ad99'),
    ]
    lut.AutomaticRescaleRangeMode = 'Never'
    rd.SetScalarBarVisibility(view, False)
    rd.Ambient, rd.Diffuse, rd.Specular = 0.22, 0.85, 0.0

    # Contorno da linha de costa sobre o terreno
    costa = Contour(registrationName='Linha_de_Costa', Input=relevo)
    costa.ContourBy = ['POINTS', 'Landmask']
    costa.Isosurfaces = [0.5]
    cd_costa = Show(costa, view)
    cd_costa.ColorArrayName = ['POINTS', '']
    cd_costa.AmbientColor = cd_costa.DiffuseColor = hx('#f8fafc')
    cd_costa.LineWidth = 2.0

    hidro = XMLImageDataReader(registrationName='Hidrometeoros_WRF_d03', FileName=[hidro_vti])

    # Criar um filtro Contour para cada hidrometeoro
    contornos = {}
    for q, rotulo, cor_hex, _, opac in HIDROS:
        lim = limiares[q]
        c = Contour(registrationName=f'Iso_{q}', Input=hidro)
        c.ContourBy = ['POINTS', q]
        c.Isosurfaces = [lim]
        c.ComputeNormals = 1
        disp = Show(c, view)
        disp.ColorArrayName = ['POINTS', '']
        disp.AmbientColor = disp.DiffuseColor = hx(cor_hex)
        disp.Opacity = opac
        disp.Specular = 0.25
        disp.SpecularPower = 28.0
        disp.Interpolation = 'Gouraud'
        Hide(c, view)
        contornos[q] = (c, disp, rotulo, cor_hex, lim, opac)

    Render(view)

    # Posicionar câmera fixa para todas as imagens (mesmo ponto de vista, item 6.3.1)
    azim, elev_ang, dist = -38.0, 21.0, 185.0
    a, e = math.radians(azim), math.radians(elev_ang)
    view.CameraFocalPoint = focal
    view.CameraPosition = [
        focal[0] + dist * math.cos(e) * math.sin(a),
        focal[1] - dist * math.cos(e) * math.cos(a),
        focal[2] + dist * math.sin(e)
    ]
    view.CameraViewUp = [0, 0, 1]
    view.CameraViewAngle = 30.0

    # 1. Uma figura 3D individual para cada hidrometeoro
    for q, rotulo, cor_hex, _, opac in HIDROS:
        for qq in contornos:
            Hide(contornos[qq][0], view)
        c_obj, disp, _, _, lim, _ = contornos[q]
        disp.Opacity = max(0.78, opac)
        Show(c_obj, view)
        Render(view)
        png = os.path.join(FIG_DIR, f'3d_{q}.png')
        SaveScreenshot(png, view, ImageResolution=[W_IMG, H_IMG])
        anotar_png(
            png,
            f'Hidrometeoro 3D: {rotulo}',
            'WRF-ARW d03 (2 km) · Microfísica Milbrandt-Yau 2-momentos (mp_physics = 9)',
            [(rotulo, cor_hex, lim, maximos[q])],
            t_str
        )
        print('Salvo 3D individual:', png)

    # 2. Figura combinada com todos os hidrometeoros juntos (incluindo SLW)
    itens_todos = []
    for q, rotulo, cor_hex, _, opac in HIDROS:
        c_obj, disp, _, _, lim, _ = contornos[q]
        disp.Opacity = opac
        Show(c_obj, view)
        itens_todos.append((rotulo, cor_hex, lim, maximos[q]))

    Render(view)
    png_todos = os.path.join(FIG_DIR, '3d_todos.png')
    SaveScreenshot(png_todos, view, ImageResolution=[W_IMG, H_IMG])
    anotar_png(
        png_todos,
        'Estrutura 3D Combinada dos Hidrometeoros e Água Super-resfriada (SLW)',
        'WRF-ARW d03 (2 km) · Milbrandt-Yau 2-momentos · Graupel (QGRAUP) e Granizo (QHAIL) separados',
        itens_todos,
        t_str
    )
    print('Salvo 3D combinado:', png_todos)

    # Salvar estado do ParaView (.pvsm) para entrega no repositório (item 9.1)
    pvsm_path = os.path.join(SESS_DIR, 'granizo_hidrometeoros_3d.pvsm')
    SaveState(pvsm_path)
    print('Salvo estado ParaView:', pvsm_path)


if __name__ == '__main__':
    main()
