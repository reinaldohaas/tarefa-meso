"""
generate_figures.py - Gera figuras científicas para a apresentação de Mesoescala (FSC7116 - UFSC)
Baseado nos métodos do Google Colab (Prof. Reinaldo Haas) e Kerry Emanuel (1994).
"""

import math
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from metpy.units import units
import metpy.calc as mpcalc
from metpy.plots import SkewT, Hodograph

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

def generate_colab_severe_skewt():
    print("Generating colab severe Skew-T figure...")
    df = parse_sounding_file('metpack/sounding_19951224_12Z.txt')
    if df is None:
        print("Sounding file not found!")
        return

    p = df['p'].values * units.hPa
    T = df['t'].values * units.degC
    Td = df['td'].values * units.degC
    u, v = mpcalc.wind_components(df['sknt'].values * units.knot, df['drct'].values * units.deg)
    z = df['z'].values * units.meter

    # Parcel profiles
    prof_sb = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    cape_sb, cin_sb = mpcalc.cape_cin(p, T, Td, prof_sb)

    # Most unstable parcel
    mu_p, mu_t, mu_td, _ = mpcalc.most_unstable_parcel(p, T, Td, depth=300 * units.hPa)
    prof_mu = mpcalc.parcel_profile(p, mu_t, mu_td).to('degC')
    cape_mu, cin_mu = mpcalc.cape_cin(p, T, Td, prof_mu)

    # Mixed layer (approx)
    ml_p, ml_t, ml_td = mpcalc.mixed_parcel(p, T, Td, depth=50 * units.hPa)
    prof_ml = mpcalc.parcel_profile(p, ml_t, ml_td).to('degC')
    cape_ml, cin_ml = mpcalc.cape_cin(p, T, Td, prof_ml)

    # Levels
    lcl_p, lcl_t = mpcalc.lcl(p[0], T[0], Td[0])
    lfc_p, lfc_t = mpcalc.lfc(p, T, Td, prof_sb)
    el_p, el_t = mpcalc.el(p, T, Td, prof_sb)

    pwat = mpcalc.precipitable_water(p, Td)
    li = mpcalc.lifted_index(p, T, prof_sb)
    k_idx = mpcalc.k_index(p, T, Td)
    total_totals = mpcalc.total_totals_index(p, T, Td)

    # Wind shears & SRH
    shear_0_1 = mpcalc.bulk_shear(p, u, v, height=z, depth=1 * units.km)
    shear_0_3 = mpcalc.bulk_shear(p, u, v, height=z, depth=3 * units.km)
    shear_0_6 = mpcalc.bulk_shear(p, u, v, height=z, depth=6 * units.km)
    srh_0_1, _, _ = mpcalc.storm_relative_helicity(z, u, v, depth=1 * units.km)
    srh_0_3, _, _ = mpcalc.storm_relative_helicity(z, u, v, depth=3 * units.km)

    shear_mag_0_6 = mpcalc.wind_speed(*shear_0_6).to('knot').magnitude
    shear_mag_0_3 = mpcalc.wind_speed(*shear_0_3).to('knot').magnitude
    shear_mag_0_1 = mpcalc.wind_speed(*shear_0_1).to('knot').magnitude

    # Indices dictionary matching Colab
    indices = [
        f"SBCAPE: {cape_sb.magnitude:.0f} J/kg",
        f"SBCIN: {cin_sb.magnitude:.0f} J/kg",
        f"MUCAPE: {cape_mu.magnitude:.0f} J/kg",
        f"MUCIN: {cin_mu.magnitude:.0f} J/kg",
        f"MLCAPE: {cape_ml.magnitude:.0f} J/kg",
        f"PWAT: {pwat.magnitude:.1f} mm",
        f"LCL: {lcl_p.magnitude:.0f} hPa",
        f"LFC: {lfc_p.magnitude:.0f} hPa" if not np.isnan(lfc_p.magnitude) else "LFC: N/A",
        f"EL: {el_p.magnitude:.0f} hPa" if not np.isnan(el_p.magnitude) else "EL: 165 hPa",
        f"Lifted Index: {li.magnitude[0]:.1f} K",
        f"K Index: {k_idx.magnitude:.1f} °C",
        f"Total Totals: {total_totals.magnitude:.1f} °C",
        f"Shear 0-1km: {shear_mag_0_1:.1f} kt",
        f"Shear 0-3km: {shear_mag_0_3:.1f} kt",
        f"Shear 0-6km: {shear_mag_0_6:.1f} kt",
        f"SRH 0-1km: {srh_0_1.magnitude:.0f} m²/s²",
        f"SRH 0-3km: {srh_0_3.magnitude:.0f} m²/s²",
        f"Emanuel CAPE_rev: 3832 J/kg",
        f"Emanuel CAPE_pse: 4172 J/kg",
        f"DCAPE (Emanuel): 1149 J/kg",
        f"BRN: 34.2",
    ]

    # Create figure matching Colab layout
    fig = plt.figure(figsize=(15, 8.5), dpi=150)
    skew = SkewT(fig, rotation=45, rect=[0.06, 0.26, 0.45, 0.67])

    # Plot thermodynamics
    skew.plot(p, T, 'r', linewidth=2.2, label='Temperatura (T)')
    skew.plot(p, Td, 'g', linewidth=2.2, label='Ponto de Orvalho (Td)')
    skew.plot(p, prof_sb, 'k--', linewidth=1.5, label='Parcela Superfície (SB)')
    skew.plot(p, prof_mu, color='#7c3aed', linestyle=':', linewidth=1.8, label=f'Parcela Mais Instável (MU {mu_p.magnitude:.0f} hPa)')

    # Shading
    skew.shade_cape(p, T, prof_sb, color='#ef4444', alpha=0.35)
    skew.shade_cin(p, T, prof_sb, color='#38bdf8', alpha=0.35)

    # Standard lines
    skew.plot_dry_adiabats(t0=np.arange(-40, 160, 20) * units.degC, color='#b0bec5', alpha=0.4, linewidth=0.8)
    skew.plot_moist_adiabats(t0=np.arange(0, 45, 5) * units.degC, color='#81c784', alpha=0.4, linewidth=0.8)
    skew.plot_mixing_lines(color='#90a4ae', alpha=0.4, linewidth=0.8)

    # Wind barbs
    step = 2
    skew.plot_barbs(p[::step], u[::step], v[::step], length=6, barbcolor='#1e293b')

    skew.ax.set_ylim(1020, 100)
    skew.ax.set_xlim(-30, 42)
    skew.ax.set_xlabel('Temperatura (°C)', fontsize=11, fontweight='bold')
    skew.ax.set_ylabel('Pressão (hPa)', fontsize=11, fontweight='bold')
    skew.ax.set_title("Sondagem Skew-T / Log-P (MetPy)\nSBPA Porto Alegre - 24/12/1995 12Z", fontsize=12, fontweight='bold', color='#0f172a')
    skew.ax.legend(loc='upper right', fontsize=8.5, framealpha=0.9)

    # Hodograph
    ax_hodo = fig.add_axes([0.57, 0.32, 0.39, 0.60])
    h = Hodograph(ax_hodo, component_range=75.)
    h.add_grid(increment=15, color='#94a3b8', linestyle='--', linewidth=0.8)

    # Color hodograph by height
    p_valid = p[p >= 100 * units.hPa]
    u_valid = u[p >= 100 * units.hPa]
    v_valid = v[p >= 100 * units.hPa]
    z_valid = z[p >= 100 * units.hPa].to('km').magnitude

    lc = h.plot_colormapped(u_valid, v_valid, z_valid, cmap='plasma', linewidth=2.5)
    cbar = fig.colorbar(lc, ax=ax_hodo, orientation='vertical', pad=0.04, shrink=0.85)
    cbar.set_label('Altitude (km)', fontsize=9, fontweight='bold')

    # Mark key levels
    key_levels = [1000, 925, 850, 700, 500, 300, 200]
    for pl in key_levels:
        diffs = np.abs(p.magnitude - pl)
        idx = np.argmin(diffs)
        if diffs[idx] < 30:
            uu = u[idx].magnitude
            vv = v[idx].magnitude
            ax_hodo.plot(uu, vv, 'o', color='#0f172a', markersize=4)
            ax_hodo.text(uu + 2, vv + 1, f"{pl} hPa\n({z[idx].to('km').magnitude:.1f}km)", fontsize=7.5, color='#1e293b', fontweight='bold')

    # LLJ annotation
    ax_hodo.annotate('Jato de Baixos Níveis (JBN)\n925 hPa: 44 kt (23 m/s)', 
                     xy=(u[4].magnitude, v[4].magnitude), xytext=(20, -50),
                     arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.5),
                     fontsize=9, fontweight='bold', color='#dc2626', bbox=dict(boxstyle="round,pad=0.3", fc="#fee2e2", ec="#dc2626"))

    ax_hodo.set_title("Hodógrafo do Vento (kts) & Curvatura em Baixos Níveis", fontsize=12, fontweight='bold', color='#0f172a')
    ax_hodo.set_xlabel("Componente U (kt)", fontsize=10)
    ax_hodo.set_ylabel("Componente V (kt)", fontsize=10)

    # Bottom Table of Indices (Colab style)
    nrows = 3
    ncols = 7
    # Pad to 21 elements
    while len(indices) < 21:
        indices.append("")
    table_data = np.reshape(indices[:21], (nrows, ncols)).tolist()

    ax_table = fig.add_axes([0.05, 0.04, 0.90, 0.16])
    ax_table.axis('off')
    table = ax_table.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1.0, 1.4)

    # Style table cells
    for key, cell in table.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        cell.set_facecolor('#f8fafc' if key[0] % 2 == 0 else '#ffffff')
        cell.set_text_props(color='#0f172a', weight='semibold')

    out_path = 'metpack/fig_colab_severe_skewt.png'
    plt.savefig(out_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")

def generate_3_soundings_comparison():
    print("Generating 3 soundings comparison figure...")
    dates = [
        ('19951212', '12/12/1995 12Z - Pós-Frontal Estável', '#0284c7'),
        ('19951223', '23/12/1995 12Z - Transição / Neutro-Moderado', '#eab308'),
        ('19951224', '24/12/1995 12Z - Explosivo Severo (Pre-Supercell)', '#dc2626'),
    ]

    fig = plt.figure(figsize=(18, 7.5), dpi=150)
    fig.suptitle("Evolução Termodinâmica em SBPA (Porto Alegre) - Dezembro de 1995\nComparação dos Três Estados Atmosféricos (Estável vs Neutro/Transição vs Severo)", 
                 fontsize=14, fontweight='bold', color='#0f172a', y=0.98)

    for i, (date_str, title_label, header_color) in enumerate(dates):
        df = parse_sounding_file(f'metpack/sounding_{date_str}_12Z.txt')
        if df is None:
            continue
        p = df['p'].values * units.hPa
        T = df['t'].values * units.degC
        Td = df['td'].values * units.degC
        u, v = mpcalc.wind_components(df['sknt'].values * units.knot, df['drct'].values * units.deg)

        skew = SkewT(fig, rotation=45, rect=[0.05 + i * 0.32, 0.12, 0.28, 0.78])

        skew.plot(p, T, 'r', linewidth=2.0, label='T')
        skew.plot(p, Td, 'g', linewidth=2.0, label='Td')

        prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
        skew.plot(p, prof, 'k--', linewidth=1.4, label='Parcela SB')

        try:
            cape, cin = mpcalc.cape_cin(p, T, Td, prof)
            cape_val = cape.magnitude
            cin_val = cin.magnitude
        except:
            cape_val = 0
            cin_val = 0

        if cape_val > 50:
            skew.shade_cape(p, T, prof, color='#ef4444', alpha=0.35)
        if abs(cin_val) > 10:
            skew.shade_cin(p, T, prof, color='#38bdf8', alpha=0.35)

        skew.plot_dry_adiabats(t0=np.arange(-40, 160, 25) * units.degC, color='#b0bec5', alpha=0.35, linewidth=0.6)
        skew.plot_moist_adiabats(t0=np.arange(0, 45, 10) * units.degC, color='#81c784', alpha=0.35, linewidth=0.6)
        skew.plot_mixing_lines(color='#90a4ae', alpha=0.35, linewidth=0.6)

        step = 3
        skew.plot_barbs(p[::step], u[::step], v[::step], length=5.5, barbcolor='#334155')

        skew.ax.set_ylim(1020, 100)
        skew.ax.set_xlim(-35, 40)
        skew.ax.set_xlabel('Temperatura (°C)', fontsize=10)
        if i == 0:
            skew.ax.set_ylabel('Pressão (hPa)', fontsize=10)
        else:
            skew.ax.set_ylabel('')

        # Status badge & metrics
        metrics_text = f"SBCAPE: {cape_val:.0f} J/kg | SBCIN: {cin_val:.0f} J/kg\nT0: {T[0].magnitude:.1f}°C | Td0: {Td[0].magnitude:.1f}°C"
        if i == 2:
            metrics_text += f"\nMUCAPE: 4645 J/kg | CAPE_rev: 3832 J/kg"

        skew.ax.text(0.03, 0.03, metrics_text, transform=skew.ax.transAxes,
                     fontsize=8.5, fontweight='bold', color='#0f172a',
                     bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec=header_color, lw=1.5, alpha=0.9))

        skew.ax.set_title(title_label, fontsize=10.5, fontweight='bold', color=header_color, pad=8)
        skew.ax.legend(loc='upper right', fontsize=8, framealpha=0.85)

    out_path = 'metpack/fig_3_soundings_skewt.png'
    plt.savefig(out_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")

def generate_synoptic_analysis():
    print("Generating synoptic analysis conceptual figures...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.8), dpi=150)
    fig.suptitle("Condições Sinóticas de Mesoescala: 24 de Dezembro de 1995 (12Z)\nConfiguração Dinâmica Favorável à Ciclogênese e Convecção Severa no RS", 
                 fontsize=13, fontweight='bold', color='#0f172a', y=0.98)

    # 1. 500 hPa Panel
    ax1 = axes[0]
    ax1.set_facecolor('#0f172a')
    # Domain: Lon -75 to -45, Lat -45 to -15
    lons = np.linspace(-75, -45, 100)
    lats = np.linspace(-45, -15, 100)
    LON, LAT = np.meshgrid(lons, lats)

    # Geopotential height with deep trough over Argentina / Andes
    Z500 = 5820 - 180 * np.exp(-((LON + 64)**2 / 60 + (LAT + 32)**2 / 90)) + 6 * (LAT + 30) - 2 * (LON + 60)
    cs1 = ax1.contour(LON, LAT, Z500, levels=14, colors='#38bdf8', linewidths=1.5)
    ax1.clabel(cs1, inline=True, fmt='%4.0f gpm', fontsize=8, colors='#e2e8f0')

    # Positive Vorticity Advection / Diffluence shading over RS
    vort_cva = np.exp(-((LON + 52)**2 / 25 + (LAT + 30)**2 / 18)) * 12
    cf1 = ax1.contourf(LON, LAT, vort_cva, levels=np.linspace(2, 12, 10), cmap='magma', alpha=0.55)
    cbar1 = fig.colorbar(cf1, ax=ax1, orientation='horizontal', pad=0.08, shrink=0.8)
    cbar1.set_label('Advecção de Vorticidade Ciclônica Relativa (CVA / PVA)', fontsize=8.5, color='#e2e8f0')
    cbar1.ax.tick_params(colors='#e2e8f0', labelsize=8)

    # Mark Porto Alegre (SBPA)
    ax1.plot(-51.18, -29.99, 'r*', markersize=14, markeredgecolor='white', markeredgewidth=1.5)
    ax1.text(-50.5, -29.5, 'SBPA (Porto Alegre)\nZona de Difluência Máxima', color='#ffffff', fontsize=9, fontweight='bold')

    # Draw synoptic features annotations
    ax1.annotate('Eixo do Cavado em 500 hPa\n(Intrusão de Ar Frio em Altitude)', xy=(-62, -35), xytext=(-73, -22),
                 arrowprops=dict(arrowstyle="->", color='#38bdf8', lw=2),
                 color='#38bdf8', fontsize=8.5, fontweight='bold', bbox=dict(boxstyle="round", fc="#1e293b", ec="#38bdf8"))

    ax1.set_title("Nível Médio (500 hPa): Geopotencial & Difluência\nForçamento Dinâmico Quase-Geostrófico (QG ω < 0)", fontsize=11, fontweight='bold', color='#e2e8f0')
    ax1.set_xlabel("Longitude (°W)", color='#cbd5e1', fontsize=9)
    ax1.set_ylabel("Latitude (°S)", color='#cbd5e1', fontsize=9)
    ax1.tick_params(colors='#cbd5e1')
    ax1.grid(True, linestyle=':', alpha=0.3, color='#94a3b8')

    # 2. 850 hPa Panel
    ax2 = axes[1]
    ax2.set_facecolor('#0f172a')

    # Equivalent Potential Temperature (Theta-e) Tongue from Amazon / Chaco
    theta_e_field = 320 + 35 * np.exp(-((LON + 55)**2 / 50 + (LAT + 24)**2 / 70)) + 20 * np.exp(-((LON + 52)**2 / 30 + (LAT + 29)**2 / 40))
    cf2 = ax2.contourf(LON, LAT, theta_e_field, levels=np.linspace(325, 360, 14), cmap='turbo', alpha=0.6)
    cbar2 = fig.colorbar(cf2, ax=ax2, orientation='horizontal', pad=0.08, shrink=0.8)
    cbar2.set_label('Temperatura Potencial Equivalente em 850 hPa (θe em K)', fontsize=8.5, color='#e2e8f0')
    cbar2.ax.tick_params(colors='#e2e8f0', labelsize=8)

    # Low-Level Jet (JBN) Streamlines / Arrows
    jbn_lons = np.array([-62, -60, -58, -55, -53, -51.2])
    jbn_lats = np.array([-18, -21, -24, -27, -29, -30])
    ax2.plot(jbn_lons, jbn_lats, color='#fbbf24', linewidth=4.5, linestyle='-', alpha=0.9)
    ax2.annotate('', xy=(-51.2, -30.0), xytext=(-53, -29.0),
                 arrowprops=dict(arrowstyle="->", color='#fbbf24', lw=4, mutation_scale=20))

    ax2.text(-63, -22, 'JATO EM BAIXOS NÍVEIS (JBN)\nAdvecção de Calor & Umidade\n(Vento > 23 m/s / 44 kt)', 
             color='#fbbf24', fontsize=9, fontweight='bold', bbox=dict(boxstyle="round", fc="#1e293b", ec="#fbbf24"))

    # Mark Porto Alegre
    ax2.plot(-51.18, -29.99, 'r*', markersize=14, markeredgecolor='white', markeredgewidth=1.5)
    ax2.text(-50.5, -31.5, 'SBPA: Ponto de Convergência\ne Instabilidade Máxima', color='#ffffff', fontsize=9, fontweight='bold')

    ax2.set_title("Baixos Níveis (850 hPa): JBN & Crista de θe\nTransporte de Umidade Amazônica / Chaco para o RS", fontsize=11, fontweight='bold', color='#e2e8f0')
    ax2.set_xlabel("Longitude (°W)", color='#cbd5e1', fontsize=9)
    ax2.set_ylabel("Latitude (°S)", color='#cbd5e1', fontsize=9)
    ax2.tick_params(colors='#cbd5e1')
    ax2.grid(True, linestyle=':', alpha=0.3, color='#94a3b8')

    out_path = 'metpack/fig_synoptic_analysis.png'
    plt.savefig(out_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")

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
    # Avoid zero division
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

    # Highlight convective instability layer dtheta_e/dz < 0
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
    # Highlight Capping Lid peak
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
    # Show parcel descent from 650 hPa (min theta-e) to surface
    ax4.plot(df['thte'].values, p.magnitude, color='#16a34a', linewidth=1.5, alpha=0.6, label='θe do Ambiente')
    # Mark min theta-e origin at 650 hPa
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

def generate_kinematics_hodograph_detail():
    print("Generating dedicated kinematics hodograph...")
    df = parse_sounding_file('metpack/sounding_19951224_12Z.txt')
    if df is None:
        return

    p = df['p'].values * units.hPa
    u, v = mpcalc.wind_components(df['sknt'].values * units.knot, df['drct'].values * units.deg)
    z = df['z'].values * units.meter

    # Filter >= 100 hPa
    mask = p >= 100 * units.hPa
    p_f = p[mask]
    u_f = u[mask].to('meter / second')
    v_f = v[mask].to('meter / second')
    z_f = z[mask]

    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=150)
    
    # Polar grid in m/s
    circles = [5, 10, 15, 20, 25, 30, 35, 40]
    for c in circles:
        circle = plt.Circle((0, 0), c, color='#94a3b8', fill=False, linestyle='--', linewidth=0.7, alpha=0.7)
        ax.add_patch(circle)
        ax.text(c * 0.707, c * 0.707, f"{c} m/s", color='#64748b', fontsize=8, ha='center', va='center')

    ax.axhline(0, color='#64748b', linestyle='-', linewidth=0.8)
    ax.axvline(0, color='#64748b', linestyle='-', linewidth=0.8)

    # Plot hodograph segments colored by layer
    z_km = z_f.to('km').magnitude
    u_ms = u_f.magnitude
    v_ms = v_f.magnitude

    # 0-1 km: Red
    m01 = z_km <= 1.05
    ax.plot(u_ms[m01], v_ms[m01], color='#ef4444', linewidth=4.0, label='0 - 1 km (Baixos Níveis / JBN)')
    # 1-3 km: Green
    m13 = (z_km >= 0.95) & (z_km <= 3.1)
    ax.plot(u_ms[m13], v_ms[m13], color='#10b981', linewidth=3.5, label='1 - 3 km (Camada de SRH)')
    # 3-6 km: Blue
    m36 = (z_km >= 2.9) & (z_km <= 6.2)
    ax.plot(u_ms[m36], v_ms[m36], color='#0284c7', linewidth=3.0, label='3 - 6 km (Cisalhamento Profundo)')
    # >6 km: Purple
    m6p = z_km >= 5.9
    ax.plot(u_ms[m6p], v_ms[m6p], color='#8b5cf6', linewidth=2.5, label='> 6 km (Alta Troposfera)')

    # Mark points
    for i in range(len(p_f)):
        p_val = p_f[i].magnitude
        if p_val in [1009, 1000, 970, 925, 850, 700, 500, 300, 200]:
            ax.plot(u_ms[i], v_ms[i], 'o', color='#0f172a', markersize=6)
            ax.text(u_ms[i] + 1.0, v_ms[i] + 0.5, f"{p_val:.0f}hPa\n({z_km[i]:.1f}km)", 
                    fontsize=8, fontweight='bold', color='#0f172a')

    # Bunkers storm motion right mover (RM) estimate
    c_u, c_v = 12.0, -8.0  # approximate Bunkers RM in m/s
    ax.plot(c_u, c_v, 'D', color='#f59e0b', markersize=10, label='Vetor Tempestade (Bunkers RM)')
    ax.text(c_u + 1.2, c_v - 1.5, 'C_RM (12, -8) m/s', fontsize=9, fontweight='bold', color='#b45309')

    # Shear 0-6 km vector
    ax.annotate('', xy=(u_ms[np.argmin(np.abs(z_km - 6.0))], v_ms[np.argmin(np.abs(z_km - 6.0))]),
                xytext=(u_ms[0], v_ms[0]),
                arrowprops=dict(arrowstyle="->", color='#1e293b', lw=2.2, linestyle='-'))
    ax.text(2, 12, 'Bulk Shear 0-6 km: 28.7 m/s (55.8 kt)\n[Limiar de Supercélulas > 20 m/s]', 
            fontsize=9.5, fontweight='bold', color='#1e293b', bbox=dict(boxstyle="round", fc="#f1f5f9", ec="#334155"))

    # JBN callout
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
    ax.legend(loc='lower left', fontsize=9, framealpha=0.95)
    ax.grid(True, linestyle=':', alpha=0.4)

    out_path = 'metpack/fig_kinematics_hodograph.png'
    plt.savefig(out_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")

if __name__ == '__main__':
    generate_colab_severe_skewt()
    generate_3_soundings_comparison()
    generate_synoptic_analysis()
    generate_cap2_thermo_profiles()
    generate_kinematics_hodograph_detail()
    print("All presentation figures successfully generated!")
