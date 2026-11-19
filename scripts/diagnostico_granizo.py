# -*- coding: utf-8 -*-
"""
Script de diagnóstico e geração das figuras 2D e tabelas para a simulação WRF
do projeto C:\gis4wrf\projects\granizo (Seminário Final - Parte 2, FSC7116 UFSC).

Gera:
  1. figuras/dominios.png               - Mapa dos 3 domínios aninhados (18 / 6 / 2 km) e relevo
  2. figuras/corte_vertical.png         - Corte vertical pela célula mais vigorosa (QGRAUP, QHAIL, SLW, W e isotermas 0, -20, -40 °C)
  3. figuras/refletividade.png          - REFL_10CM máxima na coluna e série temporal de evolução
  4. figuras/comparacao_obs.png         - Painel lado a lado: WRF REFL_10CM vs. Observação (relatos e núcleos convectivos)
  5. tabela_maximos.csv e metricas_wrf.json - Tabela com o máximo de cada hidrometeoro (g/kg), altura (km) e T (°C)
"""
import os
import sys
import json
import glob
import datetime as dt
import numpy as np
import netCDF4
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap

BASE = r'C:\gis4wrf\projects\granizo'
WPS_DIR = os.path.join(BASE, 'run_wps')
WRF_DIR = os.path.join(BASE, 'run_wrf')
FIG_DIR = os.path.join(BASE, 'figuras')
os.makedirs(FIG_DIR, exist_ok=True)

G = 9.81
RCP = 0.2854

# Cores e limiares padronizados (Seção 6.1 de TAREFA_WRF_HIDROMETEOROS.md)
HIDROMETEOROS = {
    'QCLOUD': ('Nuvem (QCLOUD)', '#b8c2cc', 0.1),
    'QRAIN':  ('Chuva (QRAIN)', '#1f6fd1', 0.5),
    'QICE':   ('Gelo (QICE)', '#22b8cf', 0.05),
    'QSNOW':  ('Neve (QSNOW)', '#9b72cf', 0.1),
    'QGRAUP': ('Graupel (QGRAUP)', '#f08c00', 0.5),
    'QHAIL':  ('Granizo (QHAIL)', '#d62828', 0.1),
    'SLW':    ('Água Super-resfriada (SLW)', '#2b9348', 0.2),
}

RELATOS = [
    {'nome': 'Biguaçu',                'lon': -48.657, 'lat': -27.494, 'hora': '22:00-22:30Z'},
    {'nome': 'Jurerê / Canasvieiras',  'lon': -48.480, 'lat': -27.432, 'hora': '22:00-22:30Z'},
    {'nome': 'Cachoeira do Bom Jesus', 'lon': -48.437, 'lat': -27.425, 'hora': '22:50Z'},
    {'nome': 'Ingleses / Vargem',      'lon': -48.402, 'lat': -27.432, 'hora': '22:40-23:00Z'},
]

NORTE_LON = (-48.60, -48.37)
NORTE_LAT = (-27.52, -27.35)


def plot_dominios():
    """Gera figuras/dominios.png com os 3 domínios aninhados e o relevo."""
    fig, ax = plt.subplots(figsize=(8.5, 7.2), dpi=150)
    cores = {1: '#111827', 2: '#c2410c', 3: '#0284c7'}
    dxs = {1: 18, 2: 6, 3: 2}
    for k in (1, 2, 3):
        arq = os.path.join(WPS_DIR, f'geo_em.d0{k}.nc')
        with netCDF4.Dataset(arq) as g:
            la = np.array(g.variables['XLAT_M'][0])
            lo = np.array(g.variables['XLONG_M'][0])
            hgt = np.array(g.variables['HGT_M'][0])
            land = np.array(g.variables['LANDMASK'][0])
            if k == 1:
                hgt_plot = np.where(land > 0.5, hgt, -50.0)
                m = ax.pcolormesh(lo, la, hgt_plot, cmap='terrain', vmin=-100, vmax=1400, shading='auto')
                cb = plt.colorbar(m, ax=ax, fraction=0.04, pad=0.02)
                cb.set_label('Altitude do terreno HGT_M (m)')
            ax.contour(lo, la, land, levels=[0.5], colors='#334155', linewidths=0.7)
            borda = np.concatenate([
                np.c_[lo[0, :], la[0, :]],
                np.c_[lo[:, -1], la[:, -1]],
                np.c_[lo[-1, ::-1], la[-1, ::-1]],
                np.c_[lo[::-1, 0], la[::-1, 0]]
            ])
            ny, nx = la.shape
            ax.plot(borda[:, 0], borda[:, 1], color=cores[k], lw=2.2,
                    label=f'd0{k}: dx = {dxs[k]} km ({nx}×{ny} pts)')
            ax.annotate(f'd0{k} ({dxs[k]} km)', xy=(lo[0, 2], la[0, 2]),
                        xytext=(4, 4), textcoords='offset points',
                        fontsize=9, fontweight='bold', color=cores[k],
                        bbox=dict(boxstyle='round,pad=0.2', fc='#ffffffdd', ec=cores[k], lw=0.8))

    ax.plot(-48.55, -27.50, 'r*', ms=13, mec='k', mew=0.8, label='Norte da Ilha de SC (-27,50°S, -48,55°W)')
    ax.set_xlabel('Longitude (°)')
    ax.set_ylabel('Latitude (°)')
    ax.set_title('Domínios Aninhados do WRF-ARW (18 / 6 / 2 km) — Projeto Granizo SC', fontsize=12, fontweight='bold')
    ax.legend(loc='lower right', framealpha=0.92, fontsize=9)
    ax.grid(color='#00000022', linestyle=':', lw=0.5)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, 'dominios.png')
    fig.savefig(out, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('Salvo:', out)


def ler_tempos(ds):
    out = []
    for t in ds.variables['Times'][:]:
        s = b''.join(t).decode() if isinstance(t[0], (bytes, np.bytes_)) else ''.join(t)
        out.append(s[:19])
    return out


def extrair_campos(ds, it):
    """Extrai campos 3D em unidades físicas no índice de tempo it."""
    V = ds.variables
    ph = np.array(V['PH'][it], dtype=np.float32)
    phb = np.array(V['PHB'][it], dtype=np.float32)
    zst = (ph + phb) / G / 1000.0  # km MSL nos níveis staggered
    z = 0.5 * (zst[:-1] + zst[1:]) # km MSL no centro da célula

    t_pert = np.array(V['T'][it], dtype=np.float32)
    p_tot = np.array(V['P'][it], dtype=np.float32) + np.array(V['PB'][it], dtype=np.float32)
    T_C = (t_pert + 300.0) * ((p_tot / 100000.0) ** RCP) - 273.15

    w_st = np.array(V['W'][it], dtype=np.float32)
    W = 0.5 * (w_st[:-1] + w_st[1:])

    out = {
        'z': z,
        'T': T_C,
        'W': W,
        'p_hPa': p_tot / 100.0,
        'hgt': np.array(V['HGT'][it], dtype=np.float32) / 1000.0,
        'land': np.array(V['LANDMASK'][it], dtype=np.float32),
        'lat': np.array(V['XLAT'][it], dtype=np.float32),
        'lon': np.array(V['XLONG'][it], dtype=np.float32),
        'REFL_10CM': np.array(V['REFL_10CM'][it], dtype=np.float32),
    }
    if 'HAILCAST_DIAM_MAX' in V:
        out['HAILCAST'] = np.array(V['HAILCAST_DIAM_MAX'][it], dtype=np.float32)
    else:
        out['HAILCAST'] = np.zeros_like(out['hgt'])

    for q in ('QCLOUD', 'QRAIN', 'QICE', 'QSNOW', 'QGRAUP', 'QHAIL'):
        if q in V:
            out[q] = np.array(V[q][it], dtype=np.float32) * 1000.0  # g/kg

    # Água super-resfriada (SLW) = QCLOUD + QRAIN onde T < 0 °C (item 5.1)
    liq = out.get('QCLOUD', 0.0) + out.get('QRAIN', 0.0)
    out['SLW'] = np.where(T_C < 0.0, liq, 0.0).astype(np.float32)
    return out


def escala_dbz():
    cores = ['#04e9e7', '#019ff4', '#0300f4', '#02fd02', '#01c501', '#008e00',
             '#fdf802', '#e5bc00', '#fd9500', '#fd0000', '#d40000', '#bc0000',
             '#f800fd', '#9854c6']
    limites = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]
    return ListedColormap(cores), BoundaryNorm(limites, len(cores))


def distancia_km(lon1, lat1, lon2, lat2):
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return float(2 * r * np.arcsin(np.sqrt(a)))


def main():
    plot_dominios()

    arqs = sorted(glob.glob(os.path.join(WRF_DIR, 'wrfout_d03_*')))
    if not arqs:
        sys.exit('Nenhum wrfout_d03 encontrado em ' + WRF_DIR)
    wrfout = arqs[0]
    print('Lendo:', wrfout)

    with netCDF4.Dataset(wrfout) as ds:
        tempos = ler_tempos(ds)
        dx_km = float(ds.getncattr('DX')) / 1000.0
        lat = np.array(ds.variables['XLAT'][0])
        lon = np.array(ds.variables['XLONG'][0])
        norte_mask = ((lon >= NORTE_LON[0]) & (lon <= NORTE_LON[1]) &
                      (lat >= NORTE_LAT[0]) & (lat <= NORTE_LAT[1]))

        serie = []
        # Analisar evolução temporal
        for it, t_str in enumerate(tempos):
            refl3d = np.array(ds.variables['REFL_10CM'][it], dtype=np.float32)
            refl_col = np.nanmax(refl3d, axis=0)
            w3d = np.array(ds.variables['W'][it], dtype=np.float32)
            qg3d = np.array(ds.variables['QGRAUP'][it], dtype=np.float32) * 1000.0
            qh3d = np.array(ds.variables['QHAIL'][it], dtype=np.float32) * 1000.0 if 'QHAIL' in ds.variables else np.zeros_like(qg3d)
            hail2d = np.array(ds.variables['HAILCAST_DIAM_MAX'][it], dtype=np.float32) if 'HAILCAST_DIAM_MAX' in ds.variables else np.zeros_like(refl_col)
            hail2d_ok = np.where(hail2d > 150.0, 0.0, hail2d)

            j_max, i_max = np.unravel_index(np.nanargmax(refl_col), refl_col.shape)
            serie.append({
                'it': it,
                'tempo': t_str,
                'refl_max_dbz': round(float(np.nanmax(refl_col)), 2),
                'refl_norte_dbz': round(float(np.nanmax(refl_col[norte_mask])), 2) if norte_mask.any() else 0.0,
                'refl_max_lat': round(float(lat[j_max, i_max]), 3),
                'refl_max_lon': round(float(lon[j_max, i_max]), 3),
                'w_max_ms': round(float(np.nanmax(w3d)), 2),
                'qgraup_max_gkg': round(float(np.nanmax(qg3d)), 2),
                'qhail_max_gkg': round(float(np.nanmax(qh3d)), 2),
                'hailcast_max_mm': round(float(np.nanmax(hail2d_ok)), 2),
            })

        # Selecionar o horário de maior atividade convectiva (após spin-up inicial de 2h, it >= 8)
        candidatos = [s for s in serie if s['it'] >= 8] or serie
        # Priorizar janela com maior refletividade/hidrometeoros de gelo
        pico = max(candidatos, key=lambda s: (s['qgraup_max_gkg'] + 2.0 * s['qhail_max_gkg'], s['refl_max_dbz']))
        it_pico = pico['it']
        t_pico_str = pico['tempo']
        print(f'Horário de pico selecionado: it={it_pico} ({t_pico_str} UTC) | '
              f'REFL={pico["refl_max_dbz"]} dBZ | QGRAUP={pico["qgraup_max_gkg"]} g/kg | QHAIL={pico["qhail_max_gkg"]} g/kg')

        c = extrair_campos(ds, it_pico)
        c['dx_km'] = dx_km

        # Também extrair no horário do Episódio 1 observado (22:15 ou 22:30 UTC, ou último horário se menor)
        it_obs = min(range(len(tempos)), key=lambda i: abs(
            (dt.datetime.strptime(tempos[i], '%Y-%m-%d_%H:%M:%S') - dt.datetime(2026, 8, 29, 22, 30)).total_seconds()
        ))
        c_obs = extrair_campos(ds, it_obs)
        t_obs_str = tempos[it_obs]

    # 1. Tabela de máximos (item 6.3.4)
    tabela = []
    for q, (rotulo, cor, lim) in HIDROMETEOROS.items():
        if q not in c:
            continue
        arr = c[q]
        k, j, i = np.unravel_index(np.argmax(arr), arr.shape)
        tabela.append({
            'variavel': q,
            'nome': rotulo,
            'cor': cor,
            'limiar_g_kg': lim,
            'max_g_kg': round(float(arr[k, j, i]), 3),
            'altura_km': round(float(c['z'][k, j, i]), 2),
            'temperatura_C': round(float(c['T'][k, j, i]), 1),
            'pressao_hPa': round(float(c['p_hPa'][k, j, i]), 1),
            'lat': round(float(c['lat'][j, i]), 3),
            'lon': round(float(c['lon'][j, i]), 3),
            'j': int(j),
            'i': int(i),
            'k': int(k),
        })

    csv_tab = os.path.join(BASE, 'tabela_maximos.csv')
    with open(csv_tab, 'w', encoding='utf-8') as f:
        f.write('variavel,nome,max_g_kg,altura_km,temperatura_C,pressao_hPa,lat,lon,limiar_g_kg\n')
        for r in tabela:
            f.write(f"{r['variavel']},{r['nome']},{r['max_g_kg']},{r['altura_km']},"
                    f"{r['temperatura_C']},{r['pressao_hPa']},{r['lat']},{r['lon']},{r['limiar_g_kg']}\n")
    print('Salvo:', csv_tab)

    # 2. Coluna da célula mais vigorosa (maior QGRAUP + QHAIL ou maior W)
    gelo_tot = c.get('QGRAUP', 0.0) + c.get('QHAIL', 0.0)
    _, j_cel, i_cel = np.unravel_index(np.argmax(gelo_tot), gelo_tot.shape)
    w_col_max = float(c['W'][:, j_cel, i_cel].max())
    # Nível da isoterma de 0 °C na célula
    t_col = c['T'][:, j_cel, i_cel]
    z_col = c['z'][:, j_cel, i_cel]
    idx_0c = np.where(t_col <= 0.0)[0]
    z_0c_km = float(z_col[idx_0c[0]]) if len(idx_0c) else 4.0

    # 3. Corte vertical pela célula mais vigorosa (item 6.3.2)
    fig, ax = plt.subplots(figsize=(10.5, 5.8), dpi=150)
    sl = (slice(None), j_cel, slice(None))
    x_km = (np.arange(c['z'].shape[2]) - i_cel) * dx_km
    z_slice = c['z'][sl]
    X = np.broadcast_to(x_km, z_slice.shape)

    qg_slice = c['QGRAUP'][sl]
    qh_slice = c.get('QHAIL', np.zeros_like(c['QGRAUP']))[sl]
    slw_slice = c['SLW'][sl]
    w_slice = c['W'][sl]
    t_slice = c['T'][sl]
    hgt_slice = c['hgt'][j_cel, :]

    m = ax.pcolormesh(X, z_slice, np.ma.masked_less(qg_slice, 0.05),
                      cmap='Oranges', shading='nearest', vmin=0, vmax=max(1.0, float(qg_slice.max())))
    cb = plt.colorbar(m, ax=ax, pad=0.015, fraction=0.035)
    cb.set_label('Graupel QGRAUP (g/kg)')

    # Contornos de QHAIL (Granizo separado pelo Milbrandt-Yau)
    qh_max = float(qh_slice.max())
    if qh_max >= 0.05:
        niv_qh = sorted(list({round(v, 2) for v in [0.05, 0.1, 0.25, 0.5, 1.0, 2.0] if v < qh_max})) or [round(qh_max * 0.5, 2)]
        cqh = ax.contour(X, z_slice, qh_slice, levels=niv_qh, colors='#d62828', linewidths=1.8)
        ax.clabel(cqh, fmt='QHAIL %.2f', fontsize=7.5)

    # Contornos de SLW (Água super-resfriada)
    slw_max = float(slw_slice.max())
    if slw_max >= 0.1:
        niv_slw = [v for v in [0.1, 0.2, 0.5, 1.0, 2.0] if v < slw_max] or [round(slw_max * 0.5, 2)]
        cslw = ax.contour(X, z_slice, slw_slice, levels=niv_slw, colors='#2b9348', linewidths=1.6)
        ax.clabel(cslw, fmt='SLW %.1f', fontsize=7.5)

    # Contornos de W (corrente ascendente e descendente)
    w_max_s = float(w_slice.max())
    if w_max_s >= 1.0:
        niv_w = [v for v in [1, 2, 5, 10, 15, 25] if v < w_max_s] or [round(w_max_s * 0.5, 1)]
        cw = ax.contour(X, z_slice, w_slice, levels=niv_w, colors='k', linewidths=1.0)
        ax.clabel(cw, fmt='W=%g', fontsize=7)
    if float(w_slice.min()) <= -1.0:
        ax.contour(X, z_slice, w_slice, levels=[-10, -5, -2, -1], colors='k', linewidths=0.8, linestyles='--')

    # Isotermas de 0 °C, -20 °C e -40 °C
    ci = ax.contour(X, z_slice, t_slice, levels=[-40, -20, 0],
                    colors=['#7b2cbf', '#1d4ed8', '#0284c7'],
                    linewidths=[1.5, 1.5, 2.4], linestyles=['-', '--', '-'])
    ax.clabel(ci, fmt='%d °C', fontsize=8.5)

    ax.fill_between(x_km, 0, hgt_slice, color='#57534e', zorder=5, label='Terreno (HGT)')
    ax.set_ylim(0, 16.5)
    ax.set_xlim(x_km.min(), x_km.max())
    ax.set_xlabel('Distância Oeste–Leste a partir do núcleo da célula (km)')
    ax.set_ylabel('Altura Geométrica Real z = (PH + PHB)/g (km MSL)')
    ax.set_title(f'Corte Vertical Oeste–Leste pela Célula Mais Vigorosa ({t_pico_str} UTC)\n'
                 f'Lat {c["lat"][j_cel, i_cel]:.2f}°, Lon {c["lon"][j_cel, i_cel]:.2f}° — '
                 f'QGRAUP (sombreado), QHAIL (vermelho), SLW (verde), W (preto) e Isotermas',
                 fontsize=10.5, fontweight='bold')
    ax.grid(color='#00000018', linestyle=':', lw=0.5)
    fig.tight_layout()
    out_cv = os.path.join(FIG_DIR, 'corte_vertical.png')
    fig.savefig(out_cv, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('Salvo:', out_cv)

    # 4. Refletividade máxima na coluna e série temporal (item 6.3.3)
    cmap_dbz, norm_dbz = escala_dbz()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.8), dpi=150)

    refl_pico = np.nanmax(c['REFL_10CM'], axis=0)
    m1 = ax1.pcolormesh(c['lon'], c['lat'], np.ma.masked_less(refl_pico, 5.0),
                        cmap=cmap_dbz, norm=norm_dbz, shading='auto')
    cb1 = plt.colorbar(m1, ax=ax1, fraction=0.045, pad=0.02)
    cb1.set_label('REFL_10CM máxima na coluna (dBZ)')
    if float(refl_pico.max()) >= 50.0:
        ax1.contour(c['lon'], c['lat'], refl_pico, levels=[50.0], colors='k', linewidths=1.3)
    ax1.contour(c['lon'], c['lat'], c['land'], levels=[0.5], colors='#1e293b', linewidths=0.9)
    for n, r in enumerate(RELATOS, 1):
        ax1.plot(r['lon'], r['lat'], 'rv', ms=8, mec='k', mew=0.7)
        ax1.annotate(str(n), xy=(r['lon'], r['lat']), xytext=(3, 3), textcoords='offset points',
                     fontsize=8, fontweight='bold', color='#991b1b')
    ax1.plot(c['lon'][j_cel, i_cel], c['lat'][j_cel, i_cel], 'k+', ms=12, mew=2, label='Núcleo do corte vertical')
    ax1.set_xlabel('Longitude (°)')
    ax1.set_ylabel('Latitude (°)')
    ax1.set_title(f'Refletividade Composta REFL_10CM (d03, 2 km)\nPico Simulado: {t_pico_str} UTC', fontsize=10.5, fontweight='bold')
    ax1.grid(color='#00000020', linestyle=':', lw=0.5)

    # Série temporal no painel direito
    t_dt = [dt.datetime.strptime(s['tempo'], '%Y-%m-%d_%H:%M:%S') for s in serie]
    ax2.plot(t_dt, [s['refl_max_dbz'] for s in serie], '-o', ms=3.5, lw=1.8, color='#1d4ed8', label='REFL_10CM máx domínio (dBZ)')
    ax2.plot(t_dt, [s['refl_norte_dbz'] for s in serie], '-s', ms=3.5, lw=1.6, color='#dc2626', label='REFL_10CM máx Norte da Ilha (dBZ)')
    ax2.axhline(50.0, color='#475569', ls='--', lw=1.0, label='Limiar 50 dBZ (eco severo)')
    ax2.axvspan(dt.datetime(2026, 8, 29, 22, 0), dt.datetime(2026, 8, 29, 23, 0),
                color='#fecaca', alpha=0.45, label='Janela dos relatos (22:00–23:00 UTC)')
    ax2.set_xlabel('Horário (UTC) em 29–30/08/2026')
    ax2.set_ylabel('Refletividade Equivalente (dBZ)')
    ax2.set_title('Evolução Temporal da Convecção no Domínio Interno (d03)', fontsize=10.5, fontweight='bold')
    ax2.legend(loc='lower right', fontsize=8.5)
    ax2.grid(color='#00000020', linestyle=':', lw=0.5)
    fig.autofmt_xdate()
    fig.tight_layout()
    out_refl = os.path.join(FIG_DIR, 'refletividade.png')
    fig.savefig(out_refl, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('Salvo:', out_refl)

    # 5. Painel lado a lado: Comparação com a Observação no horário dos relatos (item 7)
    fig, (ax_obs, ax_wrf) = plt.subplots(1, 2, figsize=(13.5, 6.0), dpi=150)

    # Painel esquerdo: Síntese observacional (Relatos de granizo + área norte da ilha + contorno costeiro)
    ax_obs.contourf(c_obs['lon'], c_obs['lat'], c_obs['land'], levels=[-0.5, 0.5, 1.5],
                    colors=['#e0f2fe', '#f1f5f9'])
    ax_obs.contour(c_obs['lon'], c_obs['lat'], c_obs['land'], levels=[0.5], colors='#334155', linewidths=1.0)
    ax_obs.contour(c_obs['lon'], c_obs['lat'], c_obs['hgt'] * 1000.0, levels=[200, 500, 800],
                   colors='#94a3b8', linewidths=0.6, linestyles=':')
    rect = plt.Rectangle((NORTE_LON[0], NORTE_LAT[0]), NORTE_LON[1] - NORTE_LON[0], NORTE_LAT[1] - NORTE_LAT[0],
                         fill=True, facecolor='#fee2e2', edgecolor='#dc2626', lw=1.5, ls='--', alpha=0.6,
                         label='Caixa Norte da Ilha (GOES-19 Tb = -62,9 °C às 22:20Z)')
    ax_obs.add_patch(rect)
    for n, r in enumerate(RELATOS, 1):
        ax_obs.plot(r['lon'], r['lat'], 'rv', ms=11, mec='k', mew=1.0)
        ax_obs.annotate(f"{n}. {r['nome']} ({r['hora']})", xy=(r['lon'], r['lat']),
                        xytext=(6, -4 if n % 2 == 0 else 6), textcoords='offset points',
                        fontsize=8.5, fontweight='bold', color='#7f1d1d',
                        bbox=dict(boxstyle='round,pad=0.2', fc='#ffffffdd', ec='#dc2626', lw=0.6))
    # Núcleo do radar Morro da Igreja observado às 22:16Z e 22:36Z
    ax_obs.plot([-48.606, -48.316], [-27.496, -27.411], '-o', color='#7c3aed', lw=2.2, ms=8,
                label='Trajetória Radar Morro da Igreja (22:16Z → 22:36Z)')
    ax_obs.set_xlim(c_obs['lon'].min(), c_obs['lon'].max())
    ax_obs.set_ylim(c_obs['lat'].min(), c_obs['lat'].max())
    ax_obs.set_xlabel('Longitude (°)')
    ax_obs.set_ylabel('Latitude (°)')
    ax_obs.set_title('Observação: Radar MI, GOES-19 e Relatos (22:00–23:00 UTC)\nGranizo observado até 60 mm no Norte da Ilha',
                     fontsize=10.5, fontweight='bold')
    ax_obs.legend(loc='lower left', fontsize=8, framealpha=0.92)
    ax_obs.grid(color='#00000020', linestyle=':', lw=0.5)

    # Painel direito: Refletividade simulada no horário dos relatos (t_obs_str)
    refl_obs_t = np.nanmax(c_obs['REFL_10CM'], axis=0)
    m2 = ax_wrf.pcolormesh(c_obs['lon'], c_obs['lat'], np.ma.masked_less(refl_obs_t, 5.0),
                           cmap=cmap_dbz, norm=norm_dbz, shading='auto')
    cb2 = plt.colorbar(m2, ax=ax_wrf, fraction=0.045, pad=0.02)
    cb2.set_label('REFL_10CM simulada (dBZ)')
    ax_wrf.contour(c_obs['lon'], c_obs['lat'], c_obs['land'], levels=[0.5], colors='#1e293b', linewidths=1.0)
    ax_wrf.add_patch(plt.Rectangle((NORTE_LON[0], NORTE_LAT[0]), NORTE_LON[1] - NORTE_LON[0], NORTE_LAT[1] - NORTE_LAT[0],
                                   fill=False, edgecolor='#dc2626', lw=1.4, ls='--'))
    for n, r in enumerate(RELATOS, 1):
        ax_wrf.plot(r['lon'], r['lat'], 'rv', ms=9, mec='k', mew=0.8)

    j_o, i_o = np.unravel_index(np.nanargmax(refl_obs_t), refl_obs_t.shape)
    dist_erro_km = distancia_km(-48.480, -27.432, float(c_obs['lon'][j_o, i_o]), float(c_obs['lat'][j_o, i_o]))
    ax_wrf.plot(c_obs['lon'][j_o, i_o], c_obs['lat'][j_o, i_o], 'k*', ms=13,
                label=f'Máx WRF ({refl_obs_t[j_o, i_o]:.1f} dBZ) a {dist_erro_km:.1f} km de Jurerê')
    ax_wrf.set_xlim(c_obs['lon'].min(), c_obs['lon'].max())
    ax_wrf.set_ylim(c_obs['lat'].min(), c_obs['lat'].max())
    ax_wrf.set_xlabel('Longitude (°)')
    ax_wrf.set_ylabel('Latitude (°)')
    ax_wrf.set_title(f'Simulação WRF-ARW d03 (2 km, Milbrandt-Yau) — {t_obs_str} UTC\n'
                     f'Deslocamento espacial do núcleo: {dist_erro_km:.1f} km',
                     fontsize=10.5, fontweight='bold')
    ax_wrf.legend(loc='lower left', fontsize=8.5, framealpha=0.92)
    ax_wrf.grid(color='#00000020', linestyle=':', lw=0.5)

    fig.tight_layout()
    out_comp = os.path.join(FIG_DIR, 'comparacao_obs.png')
    fig.savefig(out_comp, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('Salvo:', out_comp)

    # Salvar resumo JSON para alimentar a renderização 3D no ParaView e a página HTML
    resumo = {
        'projeto': BASE,
        'wrfout_d03': wrfout,
        'dx_km': dx_km,
        'it_pico': it_pico,
        'tempo_pico_utc': t_pico_str,
        'it_obs': it_obs,
        'tempo_obs_utc': t_obs_str,
        'j_celula': int(j_cel),
        'i_celula': int(i_cel),
        'lat_celula': round(float(c['lat'][j_cel, i_cel]), 3),
        'lon_celula': round(float(c['lon'][j_cel, i_cel]), 3),
        'w_max_celula_ms': round(w_col_max, 2),
        'z_isoterma_0C_km': round(z_0c_km, 2),
        'erro_distancia_obs_km': round(dist_erro_km, 1),
        'tabela_maximos': tabela,
        'serie_temporal': serie,
    }
    json_out = os.path.join(BASE, 'metricas_wrf.json')
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)
    print('Salvo:', json_out)


if __name__ == '__main__':
    main()
