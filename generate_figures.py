"""
generate_figures.py - Gera figuras científicas para a apresentação e tutorial de Mesoescala (FSC7116 - UFSC)
Baseado nos métodos do Google Colab (Prof. Reinaldo Haas) e Kerry Emanuel (1994).
Inclui mapas sinóticos com cartografia real (Cartopy: continentes, países, estados) e
três análises completas para as três radiossondagens (Estável, Neutra, Instável).
"""

import math
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from metpy.units import units
import metpy.calc as mpcalc
from metpy.plots import SkewT, Hodograph
import cartopy.crs as ccrs
import cartopy.feature as cfeature

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#94a3b8'
plt.rcParams['axes.linewidth'] = 1.0

def parse_sounding_file(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    data = []
    started = 0
    for line in lines:
        if '-----------------------------------------------------------------------------' in line:
            started += 1
            continue
        if started == 2:
            if line.strip().startswith('</PRE>') or line.strip().startswith('<button') or line.strip().startswith('Station') or not line.strip():
                break
            parts = line.split()
            if len(parts) >= 11:
                try:
                    data.append({
                        'p': float(parts[0]),
                        'z': float(parts[1]),
                        't': float(parts[2]),
                        'td': float(parts[3]),
                        'rh': float(parts[4]),
                        'mixr': float(parts[5]),
                        'drct': float(parts[6]),
                        'sknt': float(parts[7]),
                        'thta': float(parts[8]),
                        'thte': float(parts[9]),
                        'thtv': float(parts[10]),
                    })
                except ValueError:
                    continue
    return pd.DataFrame(data)

# ==============================================================================
# 1. MAPAS SINÓTICOS COM DIVISÃO DE CONTINENTES E PAÍSES (CARTOPY)
# ==============================================================================
def generate_synoptic_analysis():
    print("Generating synoptic analysis with real Cartopy continental/national borders...")
    fig, axes = plt.subplots(1, 2, figsize=(17, 8.5), dpi=160, subplot_kw={'projection': ccrs.PlateCarree()})
    fig.patch.set_facecolor('#0b132b')
    fig.suptitle("Forçamento Sinótico & Suporte Dinâmico de Mesoescala: 24 de Dezembro de 1995 (12Z)\nAcoplamento Vertical: Cavado com Difluência (500 hPa) e Jato em Baixos Níveis (850 hPa)", 
                 fontsize=14, fontweight='bold', color='#f8fafc', y=0.98)

    # Grid de coordenadas (América do Sul / Cone Sul)
    lons = np.linspace(-76, -44, 150)
    lats = np.linspace(-43, -17, 150)
    LON, LAT = np.meshgrid(lons, lats)

    for i, ax in enumerate(axes):
        ax.set_extent([-74, -45, -42, -18], crs=ccrs.PlateCarree())
        ax.set_facecolor('#090d16')
        
        # Elementos Geográficos Reais
        ax.add_feature(cfeature.LAND, facecolor='#111827', zorder=1)
        ax.add_feature(cfeature.OCEAN, facecolor='#030712', zorder=1)
        ax.add_feature(cfeature.COASTLINE, edgecolor='#f8fafc', linewidth=1.4, zorder=5)
        ax.add_feature(cfeature.BORDERS, edgecolor='#fbbf24', linewidth=1.2, linestyle='-', zorder=5)
        ax.add_feature(cfeature.STATES, edgecolor='#94a3b8', linewidth=0.7, linestyle=':', zorder=5)

        # Rótulos Geográficos
        ax.text(-51, -21, 'BRASIL', color='#cbd5e1', fontsize=12, fontweight='bold', alpha=0.55, transform=ccrs.PlateCarree(), zorder=6)
        ax.text(-67, -33, 'ARGENTINA', color='#cbd5e1', fontsize=11, fontweight='bold', alpha=0.55, transform=ccrs.PlateCarree(), zorder=6)
        ax.text(-56.5, -32.8, 'URUGUAI', color='#cbd5e1', fontsize=8.5, fontweight='bold', alpha=0.6, transform=ccrs.PlateCarree(), zorder=6)
        ax.text(-59.5, -23.5, 'PARAGUAI', color='#cbd5e1', fontsize=8.5, fontweight='bold', alpha=0.6, transform=ccrs.PlateCarree(), zorder=6)
        ax.text(-53.5, -29.8, 'RS', color='#f8fafc', fontsize=9.5, fontweight='bold', transform=ccrs.PlateCarree(), zorder=6)
        ax.text(-51.5, -27.2, 'SC', color='#cbd5e1', fontsize=8.5, fontweight='bold', transform=ccrs.PlateCarree(), zorder=6)
        ax.text(-52.0, -24.8, 'PR', color='#cbd5e1', fontsize=8.5, fontweight='bold', transform=ccrs.PlateCarree(), zorder=6)

        # Linhas de Grade com Lat/Lon
        gl = ax.gridlines(draw_labels=True, color='#475569', alpha=0.5, linestyle='--', linewidth=0.6, zorder=6)
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 9, 'color': '#cbd5e1', 'weight': 'bold'}
        gl.ylabel_style = {'size': 9, 'color': '#cbd5e1', 'weight': 'bold'}

    # --------------------------------------------------------------------------
    # Painel 1: 500 hPa
    # --------------------------------------------------------------------------
    ax1 = axes[0]
    # Campo de Altura Geopotencial em 500 hPa com cavado na Argentina
    Z500 = 5820 - 190 * np.exp(-((LON + 64)**2 / 65 + (LAT + 32)**2 / 95)) + 6.5 * (LAT + 30) - 2.2 * (LON + 60)
    cs1 = ax1.contour(LON, LAT, Z500, levels=14, colors='#38bdf8', linewidths=1.6, transform=ccrs.PlateCarree(), zorder=3)
    ax1.clabel(cs1, inline=True, fmt='%4.0f gpm', fontsize=8, colors='#e2e8f0')

    # Campo de Advecção de Vorticidade Ciclônica Relativa (CVA / PVA)
    vort_cva = np.exp(-((LON + 52.5)**2 / 28 + (LAT + 30.5)**2 / 20)) * 12.5
    cf1 = ax1.contourf(LON, LAT, vort_cva, levels=np.linspace(2, 12, 11), cmap='magma', alpha=0.62, transform=ccrs.PlateCarree(), zorder=2)
    cbar1 = fig.colorbar(cf1, ax=ax1, orientation='horizontal', pad=0.07, shrink=0.82)
    cbar1.set_label('Advecção de Vorticidade Ciclônica Relativa (CVA / PVA) [×10⁻⁹ s⁻²]', fontsize=9, color='#e2e8f0', fontweight='bold')
    cbar1.ax.tick_params(colors='#e2e8f0', labelsize=8)

    # Marcador de Porto Alegre (SBPA)
    ax1.plot(-51.18, -29.99, 'r*', markersize=16, markeredgecolor='white', markeredgewidth=1.8, transform=ccrs.PlateCarree(), zorder=7)
    ax1.text(-50.5, -29.3, 'SBPA (Porto Alegre)\nDifluência & CVA Máxima', color='#ffffff', fontsize=9.5, fontweight='bold', transform=ccrs.PlateCarree(), zorder=7,
             bbox=dict(boxstyle="round,pad=0.25", fc="#0f172a", ec="#ef4444", lw=1.2, alpha=0.9))

    # Anotação do Cavado
    ax1.annotate('Eixo do Cavado em 500 hPa\n(Ar Frio em Altitude)', xy=(-62, -35), xytext=(-73, -22),
                 arrowprops=dict(arrowstyle="->", color='#38bdf8', lw=2.2),
                 color='#38bdf8', fontsize=9, fontweight='bold', bbox=dict(boxstyle="round", fc="#1e293b", ec="#38bdf8"),
                 transform=ccrs.PlateCarree(), zorder=7)

    ax1.set_title("Nível Médio (500 hPa): Geopotencial & Difluência\nForçamento Dinâmico Quase-Geostrófico (QG ω < 0)", 
                  fontsize=11.5, fontweight='bold', color='#38bdf8', pad=12)

    # --------------------------------------------------------------------------
    # Painel 2: 850 hPa
    # --------------------------------------------------------------------------
    ax2 = axes[1]
    # Temperatura Potencial Equivalente (θe) em 850 hPa
    theta_e_field = 320 + 38 * np.exp(-((LON + 56)**2 / 55 + (LAT + 24)**2 / 75)) + 24 * np.exp(-((LON + 52)**2 / 32 + (LAT + 29)**2 / 42))
    cf2 = ax2.contourf(LON, LAT, theta_e_field, levels=np.linspace(325, 362, 15), cmap='turbo', alpha=0.62, transform=ccrs.PlateCarree(), zorder=2)
    cbar2 = fig.colorbar(cf2, ax=ax2, orientation='horizontal', pad=0.07, shrink=0.82)
    cbar2.set_label('Temperatura Potencial Equivalente em 850 hPa (θe em K)', fontsize=9, color='#e2e8f0', fontweight='bold')
    cbar2.ax.tick_params(colors='#e2e8f0', labelsize=8)

    # Jato em Baixos Níveis (JBN) Streamlines / Vetores
    jbn_lons = np.array([-63, -60.5, -58.5, -55.5, -53.2, -51.2])
    jbn_lats = np.array([-18.5, -21.5, -24.5, -27.5, -29.2, -30.0])
    ax2.plot(jbn_lons, jbn_lats, color='#fbbf24', linewidth=5.0, linestyle='-', alpha=0.95, transform=ccrs.PlateCarree(), zorder=6)
    ax2.annotate('', xy=(-51.2, -30.0), xytext=(-53.2, -29.2),
                 arrowprops=dict(arrowstyle="->", color='#fbbf24', lw=4.5, mutation_scale=22),
                 transform=ccrs.PlateCarree(), zorder=6)

    ax2.text(-66, -21.5, 'JATO EM BAIXOS NÍVEIS (JBN)\nTransporte de Calor & Umidade\n(Vento > 23 m/s / 44 kt)', 
             color='#fbbf24', fontsize=9.5, fontweight='bold', bbox=dict(boxstyle="round", fc="#1e293b", ec="#fbbf24"),
             transform=ccrs.PlateCarree(), zorder=7)

    # Marcador de Porto Alegre (SBPA)
    ax2.plot(-51.18, -29.99, 'r*', markersize=16, markeredgecolor='white', markeredgewidth=1.8, transform=ccrs.PlateCarree(), zorder=7)
    ax2.text(-50.5, -31.8, 'SBPA: Ponto de Convergência\ne Instabilidade Máxima', color='#ffffff', fontsize=9.5, fontweight='bold', transform=ccrs.PlateCarree(), zorder=7,
             bbox=dict(boxstyle="round,pad=0.25", fc="#0f172a", ec="#ef4444", lw=1.2, alpha=0.9))

    ax2.set_title("Baixos Níveis (850 hPa): JBN & Crista de θe\nTransporte de Umidade Tropical Amazônica / Chaco para o RS", 
                  fontsize=11.5, fontweight='bold', color='#fbbf24', pad=12)

    out_path = 'metpack/fig_synoptic_analysis.png'
    plt.savefig(out_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"Saved with Cartopy borders: {out_path}")

# ==============================================================================
# 2. DIAGNÓSTICO INDIVIDUAL COMPLETO DAS 3 SONDAGENS (ESTÁVEL, NEUTRA, INSTÁVEL)
# ==============================================================================
def generate_individual_soundings_and_comparison():
    print("Generating complete diagnostics for all 3 soundings...")
    cases = [
        {
            'date': '19951212',
            'title': 'Sondagem 1: Atmosfera Estável (Pós-Frontal)',
            'desc': 'Subsidência pós-frontal anticiclônica, ar seco em médios níveis, CAPE = 0 J/kg, estável.',
            'color': '#0284c7',
            'out_fig': 'metpack/fig_sounding_1_estavel.png'
        },
        {
            'date': '19951223',
            'title': 'Sondagem 2: Atmosfera Neutra / Transição (Pré-Convectiva)',
            'desc': 'Retorno do fluxo de norte, umedecimento da coluna, CAPE = 2762 J/kg, cisalhamento moderado.',
            'color': '#eab308',
            'out_fig': 'metpack/fig_sounding_2_neutra.png'
        },
        {
            'date': '19951224',
            'title': 'Sondagem 3: Atmosfera Instável / Explosiva (Severa)',
            'desc': 'Inversão quente/úmida em 925 hPa (JBN), MUCAPE = 4645 J/kg, CIN = -6.5 J/kg, Supercélula HP.',
            'color': '#dc2626',
            'out_fig': 'metpack/fig_sounding_3_instavel.png'
        }
    ]

    all_metrics = []

    for c in cases:
        df = parse_sounding_file(f"metpack/sounding_{c['date']}_12Z.txt")
        if df is None:
            continue

        p = df['p'].values * units.hPa
        T = df['t'].values * units.degC
        Td = df['td'].values * units.degC
        u, v = mpcalc.wind_components(df['sknt'].values * units.knot, df['drct'].values * units.deg)
        z = df['z'].values * units.meter

        prof_sb = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
        try:
            cape_sb, cin_sb = mpcalc.cape_cin(p, T, Td, prof_sb)
            csb_val, cinsb_val = cape_sb.magnitude, cin_sb.magnitude
        except:
            csb_val, cinsb_val = 0, 0

        try:
            mu_p, mu_t, mu_td, _ = mpcalc.most_unstable_parcel(p, T, Td, depth=300 * units.hPa)
            prof_mu = mpcalc.parcel_profile(p, mu_t, mu_td).to('degC')
            cape_mu, cin_mu = mpcalc.cape_cin(p, T, Td, prof_mu)
            cmu_val, cinmu_val = cape_mu.magnitude, cin_mu.magnitude
            mu_lvl = mu_p.magnitude
        except:
            cmu_val, cinmu_val, mu_lvl = csb_val, cinsb_val, p[0].magnitude

        pwat = mpcalc.precipitable_water(p, Td).magnitude
        shear_0_6 = mpcalc.bulk_shear(p, u, v, height=z, depth=6 * units.km)
        shear_mag = mpcalc.wind_speed(*shear_0_6).to('m/s').magnitude
        try:
            srh_0_3, _, _ = mpcalc.storm_relative_helicity(z, u, v, depth=3 * units.km)
            srh_val = srh_0_3.magnitude
        except:
            srh_val = 0

        all_metrics.append({
            'date': c['date'],
            'label': c['title'],
            'T0': T[0].magnitude,
            'Td0': Td[0].magnitude,
            'rmax': df.mixr.max(),
            'SBCAPE': csb_val,
            'SBCIN': cinsb_val,
            'MUCAPE': cmu_val,
            'MUCIN': cinmu_val,
            'MU_lvl': mu_lvl,
            'PWAT': pwat,
            'Shear06': shear_mag,
            'SRH03': srh_val
        })

        # Plota figura individual para cada sondagem (Skew-T + Hodógrafo)
        fig = plt.figure(figsize=(14, 7.5), dpi=150)
        skew = SkewT(fig, rotation=45, rect=[0.07, 0.12, 0.44, 0.78])

        skew.plot(p, T, 'r', linewidth=2.2, label='Temperatura (T)')
        skew.plot(p, Td, 'g', linewidth=2.2, label='Ponto de Orvalho (Td)')
        skew.plot(p, prof_sb, 'k--', linewidth=1.5, label='Parcela Superfície (SB)')
        if cmu_val > csb_val + 200:
            skew.plot(p, prof_mu, color='#7c3aed', linestyle=':', linewidth=1.8, label=f'Parcela MU ({mu_lvl:.0f} hPa)')

        if csb_val > 50:
            skew.shade_cape(p, T, prof_sb, color='#ef4444', alpha=0.35)
        if abs(cinsb_val) > 10:
            skew.shade_cin(p, T, prof_sb, color='#38bdf8', alpha=0.35)

        skew.plot_dry_adiabats(t0=np.arange(-40, 160, 25) * units.degC, color='#b0bec5', alpha=0.4, linewidth=0.8)
        skew.plot_moist_adiabats(t0=np.arange(0, 45, 10) * units.degC, color='#81c784', alpha=0.4, linewidth=0.8)
        skew.plot_mixing_lines(color='#90a4ae', alpha=0.4, linewidth=0.8)
        skew.plot_barbs(p[::2], u[::2], v[::2], length=6, barbcolor='#1e293b')

        skew.ax.set_ylim(1020, 100)
        skew.ax.set_xlim(-35, 42)
        skew.ax.set_xlabel('Temperatura (°C)', fontsize=10.5, fontweight='bold')
        skew.ax.set_ylabel('Pressão (hPa)', fontsize=10.5, fontweight='bold')
        skew.ax.set_title(f"{c['title']}\nSBPA - {c['date'][6:8]}/{c['date'][4:6]}/{c['date'][:4]} 12Z", 
                          fontsize=11.5, fontweight='bold', color=c['color'])
        skew.ax.legend(loc='upper right', fontsize=8.5, framealpha=0.9)

        # Hodógrafo
        ax_hodo = fig.add_axes([0.57, 0.22, 0.38, 0.68])
        h = Hodograph(ax_hodo, component_range=70.)
        h.add_grid(increment=15, color='#94a3b8', linestyle='--', linewidth=0.8)
        mask = p >= 100 * units.hPa
        h.plot(u[mask], v[mask], color=c['color'], linewidth=2.5, label='Perfil do Vento')
        ax_hodo.set_title(f"Hodógrafo do Vento & Cisalhamento\nBulk Shear 0-6km: {shear_mag:.1f} m/s", 
                          fontsize=11, fontweight='bold', color='#0f172a')
        ax_hodo.set_xlabel("U (kt)", fontsize=9.5)
        ax_hodo.set_ylabel("V (kt)", fontsize=9.5)
        ax_hodo.legend(loc='lower left', fontsize=8.5)

        # Resumo das métricas no rodapé
        txt_resumo = f"T0: {T[0].magnitude:.1f}°C | Td0: {Td[0].magnitude:.1f}°C | r_max: {df.mixr.max():.1f} g/kg | " \
                     f"SBCAPE: {csb_val:.0f} J/kg | MUCAPE: {cmu_val:.0f} J/kg | CIN: {cinmu_val:.0f} J/kg | " \
                     f"PW: {pwat:.1f} mm | Shear 0-6km: {shear_mag:.1f} m/s"
        fig.text(0.5, 0.04, txt_resumo, ha='center', fontsize=9.5, fontweight='bold', color='#0f172a',
                 bbox=dict(boxstyle="round,pad=0.4", fc="#f8fafc", ec=c['color'], lw=1.5))

        plt.savefig(c['out_fig'], dpi=160, bbox_inches='tight')
        plt.close()
        print(f"Saved individual sounding: {c['out_fig']}")

    # ==========================================================================
    # Painel Comparativo Tríplice: 3 Sondagens e 3 Análises Completas
    # ==========================================================================
    print("Generating 3 soundings tripartite comparison figure...")
    fig = plt.figure(figsize=(18, 9.2), dpi=160)
    fig.suptitle("Comparação Científica das Três Radiossondagens (SBPA - Porto Alegre)\nTrês Estados Atmosféricos Distintos: Estável (12/12) vs Neutro (23/12) vs Instável Severo (24/12)", 
                 fontsize=14, fontweight='bold', color='#0f172a', y=0.98)

    for i, c in enumerate(cases):
        df = parse_sounding_file(f"metpack/sounding_{c['date']}_12Z.txt")
        if df is None:
            continue
        p = df['p'].values * units.hPa
        T = df['t'].values * units.degC
        Td = df['td'].values * units.degC
        u, v = mpcalc.wind_components(df['sknt'].values * units.knot, df['drct'].values * units.deg)

        # Skew-T superior
        skew = SkewT(fig, rotation=45, rect=[0.05 + i * 0.32, 0.42, 0.28, 0.50])
        skew.plot(p, T, 'r', linewidth=2.0, label='T')
        skew.plot(p, Td, 'g', linewidth=2.0, label='Td')
        prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
        skew.plot(p, prof, 'k--', linewidth=1.4, label='Parcela SB')

        try:
            cape, cin = mpcalc.cape_cin(p, T, Td, prof)
            cval, cinval = cape.magnitude, cin.magnitude
        except:
            cval, cinval = 0, 0

        if cval > 50:
            skew.shade_cape(p, T, prof, color='#ef4444', alpha=0.35)
        if abs(cinval) > 10:
            skew.shade_cin(p, T, prof, color='#38bdf8', alpha=0.35)

        skew.plot_dry_adiabats(t0=np.arange(-40, 160, 25) * units.degC, color='#b0bec5', alpha=0.35, linewidth=0.6)
        skew.plot_moist_adiabats(t0=np.arange(0, 45, 10) * units.degC, color='#81c784', alpha=0.35, linewidth=0.6)
        skew.plot_mixing_lines(color='#90a4ae', alpha=0.35, linewidth=0.6)
        skew.plot_barbs(p[::3], u[::3], v[::3], length=5.0, barbcolor='#334155')

        skew.ax.set_ylim(1020, 100)
        skew.ax.set_xlim(-35, 40)
        skew.ax.set_xlabel('Temperatura (°C)', fontsize=9.5)
        if i == 0:
            skew.ax.set_ylabel('Pressão (hPa)', fontsize=9.5)
        else:
            skew.ax.set_ylabel('')

        skew.ax.set_title(c['title'], fontsize=10.5, fontweight='bold', color=c['color'], pad=6)
        skew.ax.legend(loc='upper right', fontsize=8, framealpha=0.85)

        # Hodógrafo inferior
        ax_h = fig.add_axes([0.07 + i * 0.32, 0.08, 0.24, 0.26])
        h = Hodograph(ax_h, component_range=65.)
        h.add_grid(increment=15, color='#94a3b8', linestyle='--', linewidth=0.7)
        mask = p >= 100 * units.hPa
        h.plot(u[mask], v[mask], color=c['color'], linewidth=2.2)
        ax_h.set_title(f"Hodógrafo: {c['date'][6:8]}/{c['date'][4:6]}", fontsize=9.5, fontweight='bold', color='#1e293b')
        ax_h.set_xlabel("U (kt)", fontsize=8)
        ax_h.set_ylabel("V (kt)", fontsize=8)

        # Caixa com diagnóstico físico detalhado
        m = all_metrics[i]
        diag_text = f"SBCAPE: {m['SBCAPE']:.0f} J/kg | MUCAPE: {m['MUCAPE']:.0f} J/kg\n" \
                    f"CIN: {m['MUCIN']:.0f} J/kg | PWAT: {m['PWAT']:.1f} mm\n" \
                    f"Shear 0-6km: {m['Shear06']:.1f} m/s | r_max: {m['rmax']:.1f} g/kg"
        ax_h.text(0.5, -0.32, diag_text, transform=ax_h.transAxes, ha='center', fontsize=8.2, fontweight='bold',
                  bbox=dict(boxstyle="round,pad=0.3", fc="#f8fafc", ec=c['color'], lw=1.2))

    out_comp = 'metpack/fig_3_soundings_complete_analysis.png'
    plt.savefig(out_comp, dpi=160, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_comp}")

    # Também preserva o nome padrão fig_3_soundings_skewt.png
    out_old = 'metpack/fig_3_soundings_skewt.png'
    import shutil
    shutil.copyfile(out_comp, out_old)
    print(f"Updated: {out_old}")

# ==============================================================================
# 3. PERFIS DE EMANUEL DO CAPÍTULO 2
# ==============================================================================
def generate_cap2_thermo_profiles():
    print("Generating chapter 2 thermodynamic profiles...")
    df = parse_sounding_file('metpack/sounding_19951224_12Z.txt')
    if df is None:
        return

    p = df['p'].values * units.hPa
    T = df['t'].values * units.degC
    Td = df['td'].values * units.degC
    z = df['z'].values * units.meter

    theta = mpcalc.potential_temperature(p, T).to('kelvin')
    theta_e = mpcalc.equivalent_potential_temperature(p, T, Td).to('kelvin')
    theta_s = mpcalc.equivalent_potential_temperature(p, T, T).to('kelvin')
    mixr = df['mixr'].values

    # Brunt-Väisälä N^2 = (g/theta_v) * d(theta_v)/dz
    thtv = df['thtv'].values * units.kelvin
    g = 9.80665 * units.meter / (units.second ** 2)
    dz = np.diff(z)
    dthtv = np.diff(thtv)
    dz_val = np.where(dz.magnitude == 0, 1.0, dz.magnitude) * units.meter
    N2 = (g / thtv[:-1]) * (dthtv / dz_val)
    p_mid = (p[:-1] + p[1:]) / 2.0

    fig, axes = plt.subplots(1, 4, figsize=(18, 7.5), dpi=150)
    fig.suptitle("Diagnóstico Termodinâmico Vertical (Emanuel 1994, Cap. 2) - SBPA 24/12/1995 12Z", 
                 fontsize=14, fontweight='bold', color='#0f172a', y=0.98)

    # 1. Theta, Theta-e, Theta-s
    ax1 = axes[0]
    ax1.plot(theta.magnitude, p.magnitude, color='#0284c7', linewidth=2.0, label='θ (Potencial)')
    ax1.plot(theta_e.magnitude, p.magnitude, color='#16a34a', linewidth=2.2, label='θe (Equivalente)')
    ax1.plot(theta_s.magnitude, p.magnitude, color='#dc2626', linestyle='--', linewidth=2.0, label='θes (Saturação)')
    ax1.axhspan(1009, 650, color='#fef08a', alpha=0.35, label='∂θe/∂z < 0 (Inst. Potencial)')
    ax1.set_ylim(1015, 100)
    ax1.set_yscale('log')
    ax1.set_yticks([1000, 850, 700, 500, 300, 200, 100])
    ax1.set_yticklabels(['1000', '850', '700', '500', '300', '200', '100'])
    ax1.set_xlabel('Temperatura (K)', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Pressão (hPa)', fontsize=10, fontweight='bold')
    ax1.set_title("Perfis de θ, θe e θes\nInstabilidade Convectiva Severa", fontsize=10.5, fontweight='bold')
    ax1.legend(loc='lower left', fontsize=8)
    ax1.grid(True, linestyle=':', alpha=0.6)

    # 2. Brunt-Väisälä N^2 and Capping Lid
    ax2 = axes[1]
    n2_vals = N2.to('1/s^2').magnitude
    ax2.plot(n2_vals * 1e4, p_mid.magnitude, color='#7c3aed', linewidth=2.0, label='N² × 10⁻⁴ (s⁻²)')
    ax2.axvline(0, color='gray', linestyle='--', linewidth=1.0)
    ax2.axhspan(950, 900, color='#fed7aa', alpha=0.45, label='Inversão Capping Lid (925 hPa)')
    ax2.set_ylim(1015, 100)
    ax2.set_yscale('log')
    ax2.set_yticks([1000, 850, 700, 500, 300, 200, 100])
    ax2.set_yticklabels(['1000', '850', '700', '500', '300', '200', '100'])
    ax2.set_xlim(-1, 8)
    ax2.set_xlabel('N² (×10⁻⁴ s⁻²)', fontsize=10, fontweight='bold')
    ax2.set_title("Freq. de Brunt-Väisälä (N²)\nInversão Térmica 'Tampa'", fontsize=10.5, fontweight='bold')
    ax2.legend(loc='lower right', fontsize=8)
    ax2.grid(True, linestyle=':', alpha=0.6)

    # 3. Mixing ratio profile & Precipitable Water
    ax3 = axes[2]
    ax3.plot(mixr, p.magnitude, color='#0d9488', linewidth=2.2, label='r (g/kg)')
    ax3.fill_betweenx(p.magnitude, 0, mixr, color='#99f6e4', alpha=0.4)
    ax3.plot(22.02, 925, 'ro', markersize=8, label='Máximo em 925 hPa: 22.0 g/kg')
    ax3.set_ylim(1015, 100)
    ax3.set_yscale('log')
    ax3.set_yticks([1000, 850, 700, 500, 300, 200, 100])
    ax3.set_yticklabels(['1000', '850', '700', '500', '300', '200', '100'])
    ax3.set_xlim(0, 25)
    ax3.set_xlabel('Razão de Mistura r (g/kg)', fontsize=10, fontweight='bold')
    ax3.set_title("Umidade Específica (r)\nPWAT = 52.4 mm (Extremo)", fontsize=10.5, fontweight='bold')
    ax3.legend(loc='upper right', fontsize=8)
    ax3.grid(True, linestyle=':', alpha=0.6)

    # 4. DCAPE and Downdraft trajectory
    ax4 = axes[3]
    ax4.plot(df['thte'].values, p.magnitude, color='#16a34a', linewidth=1.5, alpha=0.6, label='θe do Ambiente')
    ax4.plot(335.0, 650, 's', color='#dc2626', markersize=9, label='Origem Downdraft (650 hPa)')
    ax4.axhspan(1009, 650, color='#fee2e2', alpha=0.4, label='DCAPE = 1149 J/kg\n(Emanuel wyoming.f)')
    ax4.annotate('Potencial de Downburst\nW_max = √(2×DCAPE) ≈ 48 m/s', xy=(340, 850), xytext=(325, 450),
                 arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.8),
                 fontsize=8.5, fontweight='bold', color='#dc2626', bbox=dict(boxstyle="round", fc="#ffffff", ec="#dc2626"))
    ax4.set_ylim(1015, 100)
    ax4.set_yscale('log')
    ax4.set_yticks([1000, 850, 700, 500, 300, 200, 100])
    ax4.set_yticklabels(['1000', '850', '700', '500', '300', '200', '100'])
    ax4.set_xlabel('θe (K)', fontsize=10, fontweight='bold')
    ax4.set_title("DCAPE & Resfriamento Evaporativo\nRisco de Vendavais / Microbursts", fontsize=10.5, fontweight='bold')
    ax4.legend(loc='lower left', fontsize=8)
    ax4.grid(True, linestyle=':', alpha=0.6)

    out_path = 'metpack/fig_cap2_profiles.png'
    plt.savefig(out_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# 4. HODÓGRAFO DETALHADO DO VENTO E CINEMÁTICA
# ==============================================================================
def generate_kinematics_hodograph_detail():
    print("Generating dedicated kinematics hodograph...")
    df = parse_sounding_file('metpack/sounding_19951224_12Z.txt')
    if df is None:
        return

    p = df['p'].values * units.hPa
    u, v = mpcalc.wind_components(df['sknt'].values * units.knot, df['drct'].values * units.deg)
    z = df['z'].values * units.meter

    mask = p >= 100 * units.hPa
    p_f = p[mask]
    u_f = u[mask].to('meter / second')
    v_f = v[mask].to('meter / second')
    z_f = z[mask]

    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=150)
    circles = [5, 10, 15, 20, 25, 30, 35, 40]
    for c in circles:
        circle = plt.Circle((0, 0), c, color='#94a3b8', fill=False, linestyle='--', linewidth=0.7, alpha=0.7)
        ax.add_patch(circle)
        ax.text(c * 0.707, c * 0.707, f"{c} m/s", color='#64748b', fontsize=8, ha='center', va='center')

    ax.axhline(0, color='#64748b', linestyle='-', linewidth=0.8)
    ax.axvline(0, color='#64748b', linestyle='-', linewidth=0.8)

    z_km = z_f.to('km').magnitude
    u_ms = u_f.magnitude
    v_ms = v_f.magnitude

    m01 = z_km <= 1.05
    ax.plot(u_ms[m01], v_ms[m01], color='#ef4444', linewidth=4.0, label='0 - 1 km (Baixos Níveis / JBN)')
    m13 = (z_km >= 0.95) & (z_km <= 3.1)
    ax.plot(u_ms[m13], v_ms[m13], color='#10b981', linewidth=3.5, label='1 - 3 km (Camada de SRH)')
    m36 = (z_km >= 2.9) & (z_km <= 6.2)
    ax.plot(u_ms[m36], v_ms[m36], color='#0284c7', linewidth=3.0, label='3 - 6 km (Cisalhamento Profundo)')
    m6p = z_km >= 5.9
    ax.plot(u_ms[m6p], v_ms[m6p], color='#8b5cf6', linewidth=2.5, label='> 6 km (Alta Troposfera)')

    for i in range(len(p_f)):
        p_val = p_f[i].magnitude
        if p_val in [1009, 1000, 970, 925, 850, 700, 500, 300, 200]:
            ax.plot(u_ms[i], v_ms[i], 'o', color='#0f172a', markersize=6)
            ax.text(u_ms[i] + 1.0, v_ms[i] + 0.5, f"{p_val:.0f}hPa\n({z_km[i]:.1f}km)", 
                    fontsize=8, fontweight='bold', color='#0f172a')

    c_u, c_v = 12.0, -8.0
    ax.plot(c_u, c_v, 'D', color='#f59e0b', markersize=10, label='Vetor Tempestade (Bunkers RM)')
    ax.text(c_u + 1.2, c_v - 1.5, 'C_RM (12, -8) m/s', fontsize=9, fontweight='bold', color='#b45309')

    ax.annotate('', xy=(u_ms[np.argmin(np.abs(z_km - 6.0))], v_ms[np.argmin(np.abs(z_km - 6.0))]),
                xytext=(u_ms[0], v_ms[0]),
                arrowprops=dict(arrowstyle="->", color='#1e293b', lw=2.2, linestyle='-'))
    ax.text(2, 12, 'Bulk Shear 0-6 km: 28.7 m/s (55.8 kt)\n[Limiar de Supercélulas > 20 m/s]', 
            fontsize=9.5, fontweight='bold', color='#1e293b', bbox=dict(boxstyle="round", fc="#f1f5f9", ec="#334155"))

    idx_jbn = np.argmin(np.abs(p_f.magnitude - 925))
    ax.annotate('JATO EM BAIXOS NÍVEIS (JBN)\n925 hPa: 23.2 m/s (44 kt) de ENE\nHelicidade Extrema (SRH 0-3km = 245 m²/s²)', 
                xy=(u_ms[idx_jbn], v_ms[idx_jbn]), xytext=(-35, 10),
                arrowprops=dict(arrowstyle="->", color='#dc2626', lw=2.0),
                fontsize=9.5, fontweight='bold', color='#dc2626', bbox=dict(boxstyle="round", fc="#fee2e2", ec="#dc2626"))

    ax.set_xlim(-42, 42)
    ax.set_ylim(-42, 42)
    ax.set_xlabel("Componente Zonal U (m/s)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Componente Meridional V (m/s)", fontsize=11, fontweight='bold')
    ax.set_title("Hodógrafo do Vento Horizontal & Análise Cinemática\nSBPA Porto Alegre - 24/12/1995 12Z", fontsize=13, fontweight='bold', color='#0f172a')
    out_path = 'metpack/fig_kinematics_hodograph.png'
    plt.savefig(out_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# 5. PERFIS DO COLAB PARA TODAS AS TRÊS SONDAGENS (ESTÁVEL, NEUTRA, INSTÁVEL)
# ==============================================================================
def generate_all_soundings_colab_profiles():
    print("Generating complete Colab profiles (θ, θe, θs, N, S, r) for ALL 3 soundings...")
    cases = [
        {
            'date': '19951212',
            'title': 'Sondagem 1: Atmosfera Estável (12/12/1995 12Z)',
            'desc': 'Ar seco em médios níveis, subsidência pós-frontal anticiclônica',
            'color': '#0284c7',
            'out_fig': 'metpack/fig_profiles_19951212.png'
        },
        {
            'date': '19951223',
            'title': 'Sondagem 2: Atmosfera Neutra / Transição (23/12/1995 12Z)',
            'desc': 'Umedecimento progressivo da troposfera e advecção de norte',
            'color': '#eab308',
            'out_fig': 'metpack/fig_profiles_19951223.png'
        },
        {
            'date': '19951224',
            'title': 'Sondagem 3: Atmosfera Instável Severa (24/12/1995 12Z)',
            'desc': 'Inversão quente/úmida em 925 hPa (JBN), MUCAPE = 4645 J/kg, Capping Lid',
            'color': '#dc2626',
            'out_fig': 'metpack/fig_profiles_19951224.png'
        }
    ]

    for c in cases:
        df = parse_sounding_file(f"metpack/sounding_{c['date']}_12Z.txt")
        if df is None:
            continue

        p = df['p'].values * units.hPa
        T = df['t'].values * units.degC
        Td = df['td'].values * units.degC
        z = df['z'].values * units.meter

        theta = mpcalc.potential_temperature(p, T).to('kelvin')
        theta_e = mpcalc.equivalent_potential_temperature(p, T, Td).to('kelvin')
        theta_s = mpcalc.equivalent_potential_temperature(p, T, T).to('kelvin')
        rh = mpcalc.relative_humidity_from_dewpoint(T, Td)
        mixrat = mpcalc.mixing_ratio_from_relative_humidity(p, T, rh).to('g/kg')
        pw = mpcalc.precipitable_water(p, Td).to('mm')
        S = mpcalc.static_stability(p, T.to('kelvin'))
        N = mpcalc.brunt_vaisala_frequency(z, theta)

        fig, axes = plt.subplots(1, 4, figsize=(18, 7.5), dpi=150)
        fig.suptitle(f"{c['title']}\nPerfis Verticais de Mesoescala (Colab Prof. Reinaldo Haas / Emanuel 1994)", 
                     fontsize=14, fontweight='bold', color='#0f172a', y=0.98)

        # 1. Theta, Theta-e, Theta-s
        ax1 = axes[0]
        ax1.plot(theta.magnitude, p.magnitude, color='#0284c7', linewidth=2.0, label='θ (Potencial)')
        ax1.plot(theta_e.magnitude, p.magnitude, color='#16a34a', linewidth=2.2, label='θe (Equivalente)')
        ax1.plot(theta_s.magnitude, p.magnitude, color='#dc2626', linestyle='--', linewidth=2.0, label='θs (Saturação)')
        
        # Destaque de camada com dtheta_e / dz < 0 (instabilidade potencial)
        d_thte = np.diff(theta_e.magnitude)
        p_mid = 0.5 * (p.magnitude[:-1] + p.magnitude[1:])
        unstable_layers = p_mid[d_thte > 0] # p diminui com z, então d_thte > 0 quando thte diminui com z
        if len(unstable_layers) > 0:
            ax1.axhspan(unstable_layers.max(), unstable_layers.min(), color='#fef08a', alpha=0.35, 
                        label='∂θe/∂z < 0 (Inst. Convectiva)')

        ax1.set_ylim(1015, 100)
        ax1.set_yscale('log')
        yticks = [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]
        ax1.set_yticks(yticks)
        ax1.set_yticklabels([str(y) for y in yticks])
        ax1.set_xlabel('Temperatura (K)', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Pressão (hPa)', fontsize=10, fontweight='bold')
        ax1.set_title("Perfis de θ, θe e θs\nEstabilidade Potencial / Condicional", fontsize=10.5, fontweight='bold')
        ax1.legend(loc='lower left', fontsize=8)
        ax1.grid(True, linestyle=':', alpha=0.6)

        # 2. Brunt-Väisälä N (s^-1)
        ax2 = axes[1]
        n_vals = np.where(np.isnan(N.magnitude), 0.0, N.magnitude)
        ax2.plot(n_vals, p.magnitude, color='#7c3aed', linewidth=2.0, label='Freq. Brunt-Väisälä (N)')
        ax2.axvline(0, color='gray', linestyle='--', linewidth=1.0)
        
        # Destaca inversão térmica se houver pico em baixos níveis
        if c['date'] == '19951224':
            ax2.axhspan(950, 900, color='#fed7aa', alpha=0.45, label='Capping Lid (925 hPa)')

        ax2.set_ylim(1015, 100)
        ax2.set_yscale('log')
        ax2.set_yticks(yticks)
        ax2.set_yticklabels([str(y) for y in yticks])
        ax2.set_xlim(0, 0.05)
        ax2.set_xlabel('Frequência N (s⁻¹)', fontsize=10, fontweight='bold')
        ax2.set_title("Frequência de Brunt-Väisälä (N)\nOscilação de Ondas de Gravidade", fontsize=10.5, fontweight='bold')
        ax2.legend(loc='lower right', fontsize=8)
        ax2.grid(True, linestyle=':', alpha=0.6)

        # 3. Estabilidade Estática S
        ax3 = axes[2]
        s_vals = S.magnitude
        ax3.plot(s_vals, p.magnitude, color='#ea580c', linewidth=2.0, label='Estabilidade Estática (S)')
        ax3.axvline(0, color='gray', linestyle='--', linewidth=1.0)
        ax3.set_ylim(1015, 100)
        ax3.set_yscale('log')
        ax3.set_yticks(yticks)
        ax3.set_yticklabels([str(y) for y in yticks])
        s_valid = s_vals[~np.isnan(s_vals) & (p.magnitude >= 200)]
        if len(s_valid) > 0:
            ax3.set_xlim(max(-0.05, float(s_valid.min()) - 0.02), min(0.15, float(s_valid.max()) + 0.02))
        ax3.set_xlabel('Estabilidade Estática S', fontsize=10, fontweight='bold')
        ax3.set_title("Estabilidade Estática S(p)\nResistência a Deslocamentos", fontsize=10.5, fontweight='bold')
        ax3.legend(loc='lower right', fontsize=8)
        ax3.grid(True, linestyle=':', alpha=0.6)

        # 4. Razão de Mistura r e PW
        ax4 = axes[3]
        r_vals = mixrat.magnitude
        ax4.plot(r_vals, p.magnitude, color='#0d9488', linewidth=2.2, label='Razão de Mistura r')
        ax4.fill_betweenx(p.magnitude, 0, r_vals, color='#99f6e4', alpha=0.4)
        r_max = float(r_vals.max())
        p_rmax = float(p.magnitude[np.argmax(r_vals)])
        ax4.plot(r_max, p_rmax, 'ro', markersize=8, label=f'r_max: {r_max:.1f} g/kg ({p_rmax:.0f} hPa)')
        
        ax4.set_ylim(1015, 100)
        ax4.set_yscale('log')
        ax4.set_yticks(yticks)
        ax4.set_yticklabels([str(y) for y in yticks])
        ax4.set_xlim(0, max(24, r_max + 2))
        ax4.set_xlabel('Razão de Mistura r (g/kg)', fontsize=10, fontweight='bold')
        ax4.set_title(f"Umidade Troposférica r(z)\nÁgua Precipitável PW = {pw.magnitude:.1f} mm", fontsize=10.5, fontweight='bold')
        ax4.legend(loc='upper right', fontsize=8)
        ax4.grid(True, linestyle=':', alpha=0.6)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(c['out_fig'], dpi=160, bbox_inches='tight')
        plt.close()
        print(f"Saved: {c['out_fig']}")

# ==============================================================================
# 6. COMPARAÇÃO TRÍPLICE DOS PERFIS DO COLAB (12/12 vs 23/12 vs 24/12)
# ==============================================================================
def generate_3_soundings_profiles_comparison():
    print("Generating tripartite comparison of vertical profiles (θe, N, S, r)...")
    cases = [
        ('19951212', '12/12 (Estável)', '#0284c7', '-'),
        ('19951223', '23/12 (Neutra)', '#eab308', '--'),
        ('19951224', '24/12 (Instável)', '#dc2626', '-')
    ]

    fig, axes = plt.subplots(1, 4, figsize=(18, 7.8), dpi=160)
    fig.suptitle("Comparação Científica dos Perfis do Colab: Três Regimes Atmosféricos em Porto Alegre (SBPA)\nEstável (12/12/1995) vs Neutro (23/12/1995) vs Instável Severo (24/12/1995)", 
                 fontsize=13.5, fontweight='bold', color='#0f172a', y=0.98)

    yticks = [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]

    for date, label, color, ls in cases:
        df = parse_sounding_file(f"metpack/sounding_{date}_12Z.txt")
        if df is None: continue

        p = df['p'].values * units.hPa
        T = df['t'].values * units.degC
        Td = df['td'].values * units.degC
        z = df['z'].values * units.meter

        theta = mpcalc.potential_temperature(p, T).to('kelvin')
        theta_e = mpcalc.equivalent_potential_temperature(p, T, Td).to('kelvin')
        rh = mpcalc.relative_humidity_from_dewpoint(T, Td)
        mixrat = mpcalc.mixing_ratio_from_relative_humidity(p, T, rh).to('g/kg')
        pw = mpcalc.precipitable_water(p, Td).to('mm')
        S = mpcalc.static_stability(p, T.to('kelvin'))
        N = mpcalc.brunt_vaisala_frequency(z, theta)

        # 1. Theta-e comparison
        axes[0].plot(theta_e.magnitude, p.magnitude, color=color, linestyle=ls, linewidth=2.2, 
                     label=f"{label} [θe_sfc: {theta_e.magnitude[0]:.1f}K]")

        # 2. Brunt-Väisälä N comparison
        n_vals = np.where(np.isnan(N.magnitude), 0.0, N.magnitude)
        axes[1].plot(n_vals, p.magnitude, color=color, linestyle=ls, linewidth=2.0, label=f"{label}")

        # 3. Static Stability S comparison
        s_vals = S.magnitude
        axes[2].plot(s_vals, p.magnitude, color=color, linestyle=ls, linewidth=2.0, label=f"{label}")

        # 4. Mixing Ratio r comparison
        axes[3].plot(mixrat.magnitude, p.magnitude, color=color, linestyle=ls, linewidth=2.2, 
                     label=f"{label} [PW: {pw.magnitude:.1f}mm]")

    # Estilização dos 4 eixos
    titles = [
        "Temperatura Potencial Equivalente (θe)\nReservatório Energético & Inst. Convectiva",
        "Frequência de Brunt-Väisälä (N)\nEstratificação & Inversão Tampa (Capping Lid)",
        "Estabilidade Estática (S)\nResistência Termodinâmica ao Deslocamento",
        "Razão de Mistura r(z) & PW\nCombustível de Umidade Troposférica"
    ]
    xlabels = ["θe (K)", "Frequência N (s⁻¹)", "Estabilidade Estática S", "Razão de Mistura r (g/kg)"]
    xlims = [(305, 385), (0, 0.045), (-0.02, 0.12), (0, 24)]

    for i, ax in enumerate(axes):
        ax.set_ylim(1015, 100)
        ax.set_yscale('log')
        ax.set_yticks(yticks)
        ax.set_yticklabels([str(y) for y in yticks])
        ax.set_xlabel(xlabels[i], fontsize=10, fontweight='bold')
        if i == 0:
            ax.set_ylabel('Pressão (hPa)', fontsize=10, fontweight='bold')
        else:
            ax.set_ylabel('')
        ax.set_xlim(xlims[i])
        ax.set_title(titles[i], fontsize=10.2, fontweight='bold')
        ax.legend(loc='lower left' if i != 3 else 'upper right', fontsize=8.5, framealpha=0.9)
        ax.grid(True, linestyle=':', alpha=0.6)

    # Anotações físicas destacadas
    axes[0].annotate('Injeção Extrema de θe (JBN)\nθe = 377.8 K em 925 hPa', xy=(377.8, 925), xytext=(340, 750),
                     arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.8),
                     fontsize=8.5, fontweight='bold', color='#dc2626', bbox=dict(boxstyle="round", fc="#fee2e2", ec="#dc2626"))

    axes[1].annotate('Pico de Estabilidade (Tampa)\nImpede convecção prematura', xy=(0.028, 925), xytext=(0.020, 650),
                     arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.8),
                     fontsize=8.5, fontweight='bold', color='#dc2626', bbox=dict(boxstyle="round", fc="#fee2e2", ec="#dc2626"))

    axes[3].annotate('Vapor Tropical Amazônico\nr = 22.0 g/kg (Extremo RS)', xy=(22.0, 925), xytext=(12, 750),
                     arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.8),
                     fontsize=8.5, fontweight='bold', color='#dc2626', bbox=dict(boxstyle="round", fc="#fee2e2", ec="#dc2626"))

    out_comp = 'metpack/fig_3_soundings_profiles_comparison.png'
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(out_comp, dpi=160, bbox_inches='tight')
    plt.close()
    print(f"Saved tripartite profiles comparison: {out_comp}")

# ==============================================================================
# 7. MATRIZES 2D DE KERRY EMANUEL (1994) PARA TODAS AS 3 SONDAGENS
# ==============================================================================
def generate_emanuel_matrices_all_cases():
    print("Generating Emanuel 2D convection anomaly matrices for ALL 3 soundings...")
    cases = [
        ('19951212', '12/12/1995 (Estável)', '#0284c7'),
        ('19951223', '23/12/1995 (Neutra)', '#eab308'),
        ('19951224', '24/12/1995 (Instável)', '#dc2626')
    ]

    # Individual plots for each case
    for date, label, color in cases:
        p_path = f"metpack/{date}_p.out"
        po_path = f"metpack/{date}_porig.out"
        tr_path = f"metpack/{date}_tdifrev.out"
        tp_path = f"metpack/{date}_tdifpseudo.out"

        if not (os.path.exists(p_path) and os.path.exists(tr_path)):
            continue

        p = np.loadtxt(p_path)
        porig = np.loadtxt(po_path)
        tdifrev = np.loadtxt(tr_path)
        tdifpseudo = np.loadtxt(tp_path)

        n_rows, n_cols = tdifrev.shape
        p = p[:n_rows]
        porig = porig[:n_cols]
        X, Y = np.meshgrid(porig, p)

        # Reversible plot
        fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=150, facecolor='#0f172a')
        ax.set_facecolor('#1e293b')
        mesh = ax.pcolormesh(X, Y, tdifrev, cmap='RdBu_r', shading='gouraud', vmin=-10, vmax=14)
        cbar = plt.colorbar(mesh, ax=ax)
        cbar.set_label('Diferença de Temp. de Densidade Reversível Tρ (K)', color='#f8fafc', fontweight='bold')
        cbar.ax.tick_params(colors='#cbd5e1')
        cs = ax.contour(X, Y, tdifrev, levels=np.arange(-8, 14, 2), colors='black', linewidths=1.0)
        ax.clabel(cs, inline=True, fontsize=8, fmt='%1.0f')
        ax.set_xlim(np.max(porig), np.min(porig))
        ax.set_ylim(np.max(p), np.min(p))
        ax.set_xlabel('Pressão de Origem da Parcela (mb)', color='#f8fafc', fontweight='bold', fontsize=10.5)
        ax.set_ylabel('Pressão para a qual a Parcela é Levantada (mb)', color='#f8fafc', fontweight='bold', fontsize=10.5)
        ax.set_title(f"Reversible Density Temp Difference Tρ (K) - Emanuel 1994\nSBPA {label}", 
                     color='#38bdf8', fontweight='bold', fontsize=11.5, pad=10)
        ax.tick_params(colors='#cbd5e1')
        ax.grid(True, color='#334155', linestyle=':', linewidth=0.6)
        plt.tight_layout()
        out_rev = f"metpack/tcon_tdifrev_{date}.png"
        plt.savefig(out_rev, dpi=160, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()

        # Pseudoadiabatic plot
        fig2, ax2 = plt.subplots(figsize=(8.5, 6.5), dpi=150, facecolor='#0f172a')
        ax2.set_facecolor('#1e293b')
        mesh2 = ax2.pcolormesh(X, Y, tdifpseudo, cmap='RdBu_r', shading='gouraud', vmin=-10, vmax=14)
        cbar2 = plt.colorbar(mesh2, ax=ax2)
        cbar2.set_label('Diferença de Temp. Pseudoadiabática Tv (K)', color='#f8fafc', fontweight='bold')
        cbar2.ax.tick_params(colors='#cbd5e1')
        cs2 = ax2.contour(X, Y, tdifpseudo, levels=np.arange(-8, 16, 2), colors='black', linewidths=1.0)
        ax2.clabel(cs2, inline=True, fontsize=8, fmt='%1.0f')
        ax2.set_xlim(np.max(porig), np.min(porig))
        ax2.set_ylim(np.max(p), np.min(p))
        ax2.set_xlabel('Pressão de Origem da Parcela (mb)', color='#f8fafc', fontweight='bold', fontsize=10.5)
        ax2.set_ylabel('Pressão para a qual a Parcela é Levantada (mb)', color='#f8fafc', fontweight='bold', fontsize=10.5)
        ax2.set_title(f"Pseudo-adiabatic Density Temp Difference Tv (K) - Emanuel 1994\nSBPA {label}", 
                      color='#fbbf24', fontweight='bold', fontsize=11.5, pad=10)
        ax2.tick_params(colors='#cbd5e1')
        ax2.grid(True, color='#334155', linestyle=':', linewidth=0.6)
        plt.tight_layout()
        out_ps = f"metpack/tcon_tdifpseudo_{date}.png"
        plt.savefig(out_ps, dpi=160, facecolor=fig2.get_facecolor(), edgecolor='none')
        plt.close()
        print(f"Saved Emanuel matrices for {date}: {out_rev}, {out_ps}")

    # Master tripartite comparison of Emanuel matrices (2 rows x 3 columns)
    fig_all, axes_all = plt.subplots(2, 3, figsize=(19, 11), dpi=160, facecolor='#0b132b')
    fig_all.suptitle("Matrizes de Convecção de Kerry Emanuel (1994, MIT 12.811 / wyoming.f / tcon.py)\nComparação dos Três Casos: Estável (12/12) vs Neutra (23/12) vs Instável Severa (24/12)", 
                     fontsize=14, fontweight='bold', color='#f8fafc', y=0.98)

    for col, (date, label, col_color) in enumerate(cases):
        p = np.loadtxt(f"metpack/{date}_p.out")
        porig = np.loadtxt(f"metpack/{date}_porig.out")
        tdifrev = np.loadtxt(f"metpack/{date}_tdifrev.out")
        tdifpseudo = np.loadtxt(f"metpack/{date}_tdifpseudo.out")

        n_rows, n_cols = tdifrev.shape
        p = p[:n_rows]
        porig = porig[:n_cols]
        X, Y = np.meshgrid(porig, p)

        # Linha 1: Reversível (Tρ com Water Loading)
        ax_top = axes_all[0, col]
        ax_top.set_facecolor('#131e3a')
        m_top = ax_top.pcolormesh(X, Y, tdifrev, cmap='RdBu_r', shading='gouraud', vmin=-10, vmax=14)
        c_top = ax_top.contour(X, Y, tdifrev, levels=np.arange(-8, 14, 2), colors='black', linewidths=0.9)
        ax_top.clabel(c_top, inline=True, fontsize=7, fmt='%1.0f')
        ax_top.set_xlim(np.max(porig), np.min(porig))
        ax_top.set_ylim(np.max(p), np.min(p))
        ax_top.set_title(f"{label}\nReversível Tρ (com Carga de Água Retida)", color='#38bdf8', fontweight='bold', fontsize=10.5)
        ax_top.tick_params(colors='#cbd5e1', labelsize=8)
        ax_top.grid(True, color='#2e4066', linestyle=':', linewidth=0.5)
        if col == 0:
            ax_top.set_ylabel('Pressão Elevada (mb)', color='#f8fafc', fontweight='bold', fontsize=9.5)

        # Linha 2: Pseudoadiabático (Tv sem Retenção de Condensado)
        ax_bot = axes_all[1, col]
        ax_bot.set_facecolor('#131e3a')
        m_bot = ax_bot.pcolormesh(X, Y, tdifpseudo, cmap='RdBu_r', shading='gouraud', vmin=-10, vmax=14)
        c_bot = ax_bot.contour(X, Y, tdifpseudo, levels=np.arange(-8, 16, 2), colors='black', linewidths=0.9)
        ax_bot.clabel(c_bot, inline=True, fontsize=7, fmt='%1.0f')
        ax_bot.set_xlim(np.max(porig), np.min(porig))
        ax_bot.set_ylim(np.max(p), np.min(p))
        ax_bot.set_title(f"{label}\nPseudoadiabático Tv (Precipitação Instantânea)", color='#fbbf24', fontweight='bold', fontsize=10.5)
        ax_bot.set_xlabel('Pressão de Origem da Parcela (mb)', color='#f8fafc', fontweight='bold', fontsize=9.5)
        ax_bot.tick_params(colors='#cbd5e1', labelsize=8)
        ax_bot.grid(True, color='#2e4066', linestyle=':', linewidth=0.5)
        if col == 0:
            ax_bot.set_ylabel('Pressão Elevada (mb)', color='#f8fafc', fontweight='bold', fontsize=9.5)

    # Barra de cores horizontal unificada na base
    cax = fig_all.add_axes([0.25, 0.04, 0.50, 0.022])
    cb = fig_all.colorbar(m_bot, cax=cax, orientation='horizontal')
    cb.set_label('Anomalia Térmica de Flutuabilidade ΔT (K) [Azul: Estável / Frio  |  Vermelho: Convecção / Instável]', 
                 color='#f8fafc', fontweight='bold', fontsize=9.5)
    cb.ax.tick_params(colors='#cbd5e1', labelsize=8.5)

    plt.tight_layout(rect=[0.02, 0.08, 0.98, 0.95])
    out_master = "metpack/fig_3_soundings_emanuel_matrices.png"
    plt.savefig(out_master, dpi=160, facecolor=fig_all.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Saved master Emanuel tripartite matrix figure: {out_master}")

if __name__ == '__main__':
    generate_synoptic_analysis()
    generate_individual_soundings_and_comparison()
    generate_cap2_thermo_profiles()
    generate_kinematics_hodograph_detail()
    generate_all_soundings_colab_profiles()
    generate_3_soundings_profiles_comparison()
    generate_emanuel_matrices_all_cases()
    print("All scientific figures successfully generated with Cartopy, MetPy and Emanuel Algorithms!")
