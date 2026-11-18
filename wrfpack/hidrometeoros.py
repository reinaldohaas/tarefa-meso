# -*- coding: utf-8 -*-
"""Diagnóstico e visualização dos hidrometeoros num wrfout (FSC7116, Seminário Final, Parte 2).

Funções usadas pelo notebook WRF_VLab_tarefa.ipynb. Leem um horário por vez (o wrfout do domínio interno
pode ter vários GB) e devolvem campos em unidades físicas:
  - altura dos níveis de massa: z = (PH + PHB)/9,81, média entre níveis vizinhos (km);
  - temperatura: T = (T + 300) * ((P + PB)/1e5)^0,2854 (°C);
  - razões de mistura em g/kg;
  - água super-resfriada (SLW) = QCLOUD + QRAIN onde T < 0 °C.

Dependências: numpy, xarray, netCDF4, matplotlib; plotly só para a figura 3D no navegador.
"""
import base64
import os

import numpy as np
import xarray as xr

G = 9.81
RCP = 0.2854

# Hidrometeoros possíveis no wrfout: nome no arquivo, rótulo, cor fixa, limiar sugerido (g/kg)
HIDROMETEOROS = {
    'QCLOUD': ('nuvem', '#b8c2cc', 0.1),
    'QRAIN': ('chuva', '#1f6fd1', 0.5),
    'QICE': ('gelo', '#22b8cf', 0.05),
    'QSNOW': ('neve', '#9b72cf', 0.1),
    'QGRAUP': ('graupel', '#f08c00', 0.5),
    'QHAIL': ('granizo', '#d62828', 0.1),
    'SLW': ('água super-resfriada', '#2b9348', 0.2),
}


def abrir(arquivo):
    """Abre o wrfout sem carregar os dados (leitura preguiçosa)."""
    return xr.open_dataset(arquivo, decode_times=False, mask_and_scale=False)


def horarios(ds):
    """Lista de horários do arquivo, como texto 'AAAA-MM-DD_hh:mm:ss'."""
    out = []
    for t in ds['Times'].values:
        if isinstance(t, (bytes, np.bytes_)):          # xarray já juntou os caracteres
            out.append(t.decode())
        elif isinstance(t, str):
            out.append(t)
        else:                                           # vetor de caracteres
            out.append(b''.join(t).decode() if isinstance(t[0], bytes) else ''.join(t))
    return out


def presentes(ds):
    """Hidrometeoros que existem neste wrfout (dependem da microfísica)."""
    return [q for q in HIDROMETEOROS if q in ds.variables or (q == 'QHAIL' and 'QH' in ds.variables)] + \
        (['SLW'] if 'QCLOUD' in ds.variables else [])


def _var(ds, nome, it):
    if nome == 'QHAIL' and 'QHAIL' not in ds.variables and 'QH' in ds.variables:
        nome = 'QH'
    return np.asarray(ds[nome].isel(Time=it).values, dtype='f4')


def campos(ds, it):
    """Campos 3D de um horário: z (km), T (°C), W (m/s), cada hidrometeoro (g/kg) e a SLW (g/kg)."""
    zst = (_var(ds, 'PH', it) + _var(ds, 'PHB', it)) / G
    out = {'z': 0.5 * (zst[:-1] + zst[1:]) / 1000.0}
    out['T'] = (_var(ds, 'T', it) + 300.0) * ((_var(ds, 'P', it) + _var(ds, 'PB', it)) / 1e5) ** RCP - 273.15
    ww = _var(ds, 'W', it)
    out['W'] = 0.5 * (ww[:-1] + ww[1:])
    for q in presentes(ds):
        if q != 'SLW':
            out[q] = _var(ds, q, it) * 1000.0
    if 'QCLOUD' in out:
        liq = out['QCLOUD'] + out.get('QRAIN', 0.0)
        out['SLW'] = np.where(out['T'] < 0.0, liq, 0.0).astype('f4')
    out['hgt'] = np.asarray(ds['HGT'].isel(Time=it).values) / 1000.0
    out['lat'] = np.asarray(ds['XLAT'].isel(Time=it).values)
    out['lon'] = np.asarray(ds['XLONG'].isel(Time=it).values)
    return out


def refl_composta(ds, it):
    """Refletividade máxima na coluna (dBZ). Usa REFL_10CM (do_radar_ref = 1)."""
    if 'REFL_10CM' not in ds.variables:
        raise KeyError('REFL_10CM não está no wrfout: ligue do_radar_ref = 1 no namelist.input')
    return np.asarray(ds['REFL_10CM'].isel(Time=it).max('bottom_top').values)


def horario_mais_intenso(ds, inicio=0, fim=None):
    """Índice do horário com a maior refletividade composta (ou o maior W, se não houver REFL_10CM)."""
    fim = ds.sizes['Time'] if fim is None else fim
    nome = 'REFL_10CM' if 'REFL_10CM' in ds.variables else 'W'
    maxs = [float(ds[nome].isel(Time=i).max().values) for i in range(inicio, fim)]
    return inicio + int(np.argmax(maxs)), maxs


def tabela_maximos(c):
    """Máximo de cada hidrometeoro, com altura (km) e temperatura (°C) onde ocorre."""
    linhas = []
    for q in HIDROMETEOROS:
        if q not in c:
            continue
        k, j, i = np.unravel_index(np.argmax(c[q]), c[q].shape)
        linhas.append(dict(variavel=q, nome=HIDROMETEOROS[q][0], max_g_kg=round(float(c[q][k, j, i]), 2),
                           altura_km=round(float(c['z'][k, j, i]), 1), temperatura_C=round(float(c['T'][k, j, i]), 1),
                           j=int(j), i=int(i)))
    return linhas


def ponto_mais_forte(c):
    """(j, i) da coluna com a maior corrente ascendente."""
    k, j, i = np.unravel_index(np.argmax(c['W']), c['W'].shape)
    return int(j), int(i)


def corte_vertical(c, j, i, dx_km, meia_largura_km=40.0, direcao='oeste-leste', topo_km=18.0, ax=None):
    """Corte vertical pela coluna (j, i): graupel e granizo sombreados, SLW, W e isotermas de 0, -20 e -40 °C."""
    import matplotlib.pyplot as plt
    n = int(round(meia_largura_km / dx_km))
    if direcao == 'oeste-leste':
        sl = (slice(None), j, slice(max(i - n, 0), i + n + 1))
        x = (np.arange(sl[2].start, min(i + n + 1, c['z'].shape[2])) - i) * dx_km
        hgt = c['hgt'][j, sl[2]]
        rot = 'distância oeste-leste (km)'
    else:
        sl = (slice(None), slice(max(j - n, 0), j + n + 1), i)
        x = (np.arange(sl[1].start, min(j + n + 1, c['z'].shape[1])) - j) * dx_km
        hgt = c['hgt'][sl[1], i]
        rot = 'distância sul-norte (km)'
    z = c['z'][sl]
    X = np.broadcast_to(x, z.shape)
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 5.5))
    gelo = c.get('QGRAUP', 0.0)
    if 'QHAIL' in c:
        gelo = gelo + c['QHAIL']
    gelo = np.asarray(gelo)[sl] if np.ndim(gelo) else np.zeros_like(z)
    rotulo = 'graupel + granizo (g/kg)' if 'QHAIL' in c else 'QGRAUP (g/kg)'
    m = ax.pcolormesh(X, z, np.ma.masked_less(gelo, 0.05), cmap='Oranges', shading='nearest', vmin=0)
    plt.colorbar(m, ax=ax, label=rotulo, pad=0.01)
    cs = ax.contour(X, z, c['SLW'][sl], levels=[0.2, 0.5, 1, 2], colors='#2b9348', linewidths=1.4)
    ax.clabel(cs, fmt='%.1f', fontsize=7)
    ax.contour(X, z, c['W'][sl], levels=[5, 10, 20, 30, 40], colors='k', linewidths=0.9)
    ax.contour(X, z, c['W'][sl], levels=[-10, -5], colors='k', linewidths=0.9, linestyles='--')
    ci = ax.contour(X, z, c['T'][sl], levels=[-40, -20, 0], colors=['#7b2cbf', '#1971c2', '#1971c2'],
                    linewidths=[1.4, 1.4, 2.2], linestyles=['-', '--', '-'])
    ax.clabel(ci, fmt='%d °C', fontsize=8)
    ax.fill_between(x, 0, hgt, color='#8d6e63', zorder=3)
    ax.set_ylim(0, topo_km)
    ax.set_xlabel(rot)
    ax.set_ylabel('altura (km)')
    ax.set_title('Corte vertical: graupel/granizo (cor), SLW (verde, g/kg), W (preto, m/s), isotermas')
    return ax


def para_alturas(c, nomes, j0, j1, i0, i1, dz_km=0.25, topo_km=18.0):
    """Interpola os campos de um recorte para níveis de altura regulares (necessário para a isosuperfície)."""
    zt = np.arange(dz_km, topo_km + 1e-6, dz_km)
    z = c['z'][:, j0:j1, i0:i1]
    out = {}
    for nome in nomes:
        v = c[nome][:, j0:j1, i0:i1]
        r = np.zeros((zt.size,) + v.shape[1:], 'f4')
        for jj in range(v.shape[1]):
            for ii in range(v.shape[2]):
                r[:, jj, ii] = np.interp(zt, z[:, jj, ii], v[:, jj, ii], left=0.0, right=0.0)
        out[nome] = r
    return zt, out


def isosuperficies_html(c, j, i, dx_km, arquivo, nomes=None, meia_largura_km=40.0, passo=1, exagero=3.0,
                        limiares=None, titulo=''):
    """Figura 3D interativa (plotly) com uma isosuperfície por hidrometeoro, gravada em HTML.

    Cada hidrometeoro vira um traço que o leitor liga e desliga na legenda. passo > 1 reduz a grade."""
    import plotly.graph_objects as go
    nomes = nomes or [q for q in HIDROMETEOROS if q in c]
    limiares = limiares or {}
    n = int(round(meia_largura_km / dx_km))
    ny, nx = c['hgt'].shape
    j0, j1, i0, i1 = max(j - n, 0), min(j + n + 1, ny), max(i - n, 0), min(i + n + 1, nx)
    zt, reg = para_alturas(c, nomes, j0, j1, i0, i1)
    s = (slice(None), slice(None, None, passo), slice(None, None, passo))
    yy = (np.arange(j0, j1) - j)[::passo] * dx_km
    xx = (np.arange(i0, i1) - i)[::passo] * dx_km
    Z, Y, X = np.meshgrid(zt, yy, xx, indexing='ij')
    fig = go.Figure()
    for q in nomes:
        nome, cor, lim = HIDROMETEOROS[q]
        lim = limiares.get(q, lim)
        v = reg[q][s]
        if float(v.max()) <= lim:
            continue
        fig.add_trace(go.Isosurface(x=X.ravel(), y=Y.ravel(), z=Z.ravel(), value=v.ravel(), isomin=lim,
                                    isomax=float(v.max()), surface_count=1, caps=dict(x_show=False, y_show=False, z_show=False),
                                    colorscale=[[0, cor], [1, cor]], showscale=False, opacity=0.45,
                                    name=f'{nome} ≥ {lim:g} g/kg', showlegend=True))
    hg = c['hgt'][j0:j1:passo, i0:i1:passo]
    fig.add_trace(go.Surface(x=xx, y=yy, z=hg, colorscale=[[0, '#8d6e63'], [1, '#d7ccc8']], showscale=False,
                             name='relevo', opacity=1.0))
    lado = max(np.ptp(xx), np.ptp(yy))
    fig.update_layout(title=titulo, legend=dict(itemsizing='constant'), margin=dict(l=0, r=0, t=40, b=0),
                      scene=dict(xaxis_title='x (km)', yaxis_title='y (km)', zaxis_title='altura (km)',
                                 aspectmode='manual',
                                 aspectratio=dict(x=np.ptp(xx) / lado, y=np.ptp(yy) / lado, z=exagero * zt[-1] / lado)))
    fig.write_html(arquivo, include_plotlyjs='cdn', full_html=True)
    return fig


def gravar_vts(c, arquivo, nomes=None, passo=1):
    """Grava o domínio como grade estruturada VTK (.vts) para o ParaView: x e y em km, z da altura real (km).

    No ParaView: Contour em cada variável e Transform (escala em z) para o exagero vertical."""
    nomes = nomes or [q for q in HIDROMETEOROS if q in c] + ['W', 'T']
    z = c['z'][:, ::passo, ::passo]
    nz, ny, nx = z.shape
    dx = c.get('dx_km', 1.0) * passo
    X, Y = np.meshgrid(np.arange(nx) * dx, np.arange(ny) * dx)
    pts = np.stack([np.broadcast_to(X, z.shape), np.broadcast_to(Y, z.shape), z], axis=-1).astype('f4').reshape(-1, 3)

    def bloco(a):
        b = np.ascontiguousarray(a, dtype='f4').tobytes()
        return base64.b64encode(np.uint32(len(b)).tobytes() + b).decode()

    with open(arquivo, 'w') as f:
        ext = f'0 {nx - 1} 0 {ny - 1} 0 {nz - 1}'
        f.write('<?xml version="1.0"?>\n<VTKFile type="StructuredGrid" version="0.1" byte_order="LittleEndian" '
                'header_type="UInt32">\n')
        f.write(f'<StructuredGrid WholeExtent="{ext}"><Piece Extent="{ext}">\n<PointData>\n')
        for q in nomes:
            f.write(f'<DataArray type="Float32" Name="{q}" format="binary">{bloco(c[q][:, ::passo, ::passo])}</DataArray>\n')
        f.write('</PointData>\n<Points><DataArray type="Float32" NumberOfComponents="3" format="binary">')
        f.write(bloco(pts))
        f.write('</DataArray></Points>\n</Piece></StructuredGrid>\n</VTKFile>\n')
    return os.path.getsize(arquivo)
