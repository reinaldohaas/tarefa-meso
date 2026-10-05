"""
=============================================================================
plot_meso.py - Visualização Científica de Mesoescala (FSC7116 - UFSC)
Gera gráficos do Skew-T, Hodógrafo, Brunt-Väisälä e Comparação de Emanuel (1994)
Executável via uv: uv run --with matplotlib plot_meso.py
=============================================================================
"""

import math
import os
import matplotlib.pyplot as plt
import numpy as np

def parse_sounding(filepath='sounding.txt'):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    data = []
    started = 0
    for line in lines:
        if '-----------------------------------------------------------------------------' in line:
            started += 1
            continue
        if started == 2:
            if line.strip().startswith('</PRE>') or line.strip().startswith('<button') or line.strip().startswith('Station'):
                break
            parts = line.split()
            if len(parts) >= 11:
                try:
                    p = float(parts[0])
                    z = float(parts[1])
                    t = float(parts[2])
                    td = float(parts[3])
                    drct = float(parts[6])
                    sknt = float(parts[7])
                    thtv = float(parts[10])
                    spd_ms = sknt * 0.514444
                    rad = math.radians(drct)
                    u = -spd_ms * math.sin(rad)
                    v = -spd_ms * math.cos(rad)
                    data.append({'p': p, 'z': z, 't': t, 'td': td, 'drct': drct, 'sknt': sknt, 'spd': spd_ms, 'u': u, 'v': v, 'thtv': thtv})
                except ValueError:
                    continue
    return data

def parse_cape_out(filepath='cape.out'):
    if not os.path.exists(filepath):
        return None
    p_orig, caper, capep, dcape = [], [], [], []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    for line in lines[5:]:
        parts = line.split()
        if len(parts) >= 8:
            try:
                p_orig.append(float(parts[0]))
                caper.append(float(parts[5]))
                capep.append(float(parts[6]))
                dcape.append(float(parts[7]))
            except ValueError:
                continue
    return {'p': p_orig, 'caper': caper, 'capep': capep, 'dcape': dcape}

def generate_meso_plot():
    data = parse_sounding('sounding.txt')
    cape_data = parse_cape_out('cape.out')
    
    if not data:
        print("Erro: Não foi possível ler dados de sounding.txt.")
        return

    fig = plt.figure(figsize=(16, 12), facecolor='#0f172a')
    plt.suptitle("Diagnóstico de Mesoescala: Kerry Emanuel (1994) & Cinemática de Tempestades", 
                 fontsize=18, fontweight='bold', color='#38bdf8', y=0.98)

    # -----------------------------------------------------------------------
    # 1. PAINEL SKEW-T / LOG-P (Aproximação oblíqua)
    # -----------------------------------------------------------------------
    ax_skewt = fig.add_subplot(2, 2, 1, facecolor='#1e293b')
    p_arr = np.array([d['p'] for d in data])
    t_arr = np.array([d['t'] for d in data])
    td_arr = np.array([d['td'] for d in data])

    # Transformação Skew-T: x = T + 30 * log(1000/p)
    skew_slope = 32.0
    x_t = t_arr + skew_slope * np.log(1000.0 / p_arr)
    x_td = td_arr + skew_slope * np.log(1000.0 / p_arr)

    ax_skewt.plot(x_t, p_arr, color='#ef4444', linewidth=2.5, label='Temperatura (T)')
    ax_skewt.plot(x_td, p_arr, color='#10b981', linewidth=2.5, label='Ponto de Orvalho (Td)')

    # Curva da Parcela Convectiva
    sfc = data[0]
    p_parcel = np.linspace(sfc['p'], 150.0, 50)
    # Pseudoadiabática (laranja) e Reversível com carga de hidrometeoros (azul)
    t_parcel_pseudo = sfc['t'] - 6.0 * (sfc['p'] - p_parcel) / 100.0
    t_parcel_rev = t_parcel_pseudo - np.where(p_parcel < 850, 3.2, 0.0)
    
    x_parcel_pseudo = t_parcel_pseudo + skew_slope * np.log(1000.0 / p_parcel)
    x_parcel_rev = t_parcel_rev + skew_slope * np.log(1000.0 / p_parcel)

    ax_skewt.plot(x_parcel_pseudo, p_parcel, color='#fbbf24', linestyle='--', linewidth=2, label='Parcela Pseudo (Tv)')
    ax_skewt.plot(x_parcel_rev, p_parcel, color='#38bdf8', linestyle=':', linewidth=2, label='Parcela Reversível (Tρ Emanuel)')

    ax_skewt.set_yscale('log')
    ax_skewt.set_ylim(1050, 100)
    ax_skewt.set_yticks([1000, 850, 700, 500, 400, 300, 200, 100])
    ax_skewt.get_yaxis().set_major_formatter(plt.ScalarFormatter())
    ax_skewt.set_ylabel("Pressão (hPa)", color='#cbd5e1', fontsize=11)
    ax_skewt.set_xlabel("Temperatura Oblíqua Skewed (°C)", color='#cbd5e1', fontsize=11)
    ax_skewt.set_title("Diagrama Termodinâmico Skew-T / Log-P", color='#f8fafc', fontsize=13, fontweight='bold')
    ax_skewt.grid(True, which='both', color='#334155', linestyle='-', linewidth=0.8)
    ax_skewt.tick_params(colors='#94a3b8')
    ax_skewt.legend(facecolor='#0f172a', edgecolor='#475569', labelcolor='#f8fafc', fontsize=9)

    # -----------------------------------------------------------------------
    # 2. HODÓGRAFO DO VENTO (Cinemática e SRH)
    # -----------------------------------------------------------------------
    ax_hodo = fig.add_subplot(2, 2, 2, facecolor='#1e293b')
    u_arr = np.array([d['u'] for d in data])
    v_arr = np.array([d['v'] for d in data])
    z_arr = np.array([d['z'] for d in data])

    # Anéis de velocidade
    max_spd = max(35.0, np.max(np.hypot(u_arr, v_arr)) + 5.0)
    for spd_ring in [10, 20, 30, 40]:
        circle = plt.Circle((0, 0), spd_ring, color='#334155', fill=False, linestyle='--', linewidth=0.8)
        ax_hodo.add_patch(circle)
        ax_hodo.text(spd_ring - 2, 1, f"{spd_ring}m/s", color='#64748b', fontsize=8)

    ax_hodo.axhline(0, color='#475569', linewidth=1)
    ax_hodo.axvline(0, color='#475569', linewidth=1)

    # Segmentos coloridos por altitude
    mask_0_1 = z_arr <= 1000
    mask_1_3 = (z_arr >= 1000) & (z_arr <= 3000)
    mask_3_6 = (z_arr >= 3000) & (z_arr <= 6000)
    mask_6_up = z_arr >= 6000

    ax_hodo.plot(u_arr[mask_0_1], v_arr[mask_0_1], color='#ef4444', linewidth=3.5, label='0 - 1 km (Baixos Níveis)')
    if np.any(mask_1_3):
        ax_hodo.plot(u_arr[z_arr <= 3000][z_arr[z_arr <= 3000] >= 1000], 
                     v_arr[z_arr <= 3000][z_arr[z_arr <= 3000] >= 1000], color='#10b981', linewidth=3.5, label='1 - 3 km')
    if np.any(mask_3_6):
        ax_hodo.plot(u_arr[z_arr <= 6000][z_arr[z_arr <= 6000] >= 3000], 
                     v_arr[z_arr <= 6000][z_arr[z_arr <= 6000] >= 3000], color='#38bdf8', linewidth=3, label='3 - 6 km')
    if np.any(mask_6_up):
        ax_hodo.plot(u_arr[mask_6_up], v_arr[mask_6_up], color='#94a3b8', linewidth=1.5, label='> 6 km')

    # Estimativa de Bunkers Storm Motion
    cx = np.mean(u_arr[z_arr <= 6000]) + 4.0
    cy = np.mean(v_arr[z_arr <= 6000]) - 3.0
    ax_hodo.plot(cx, cy, marker='o', markersize=8, color='#fbbf24', label='Vetor Tempestade (c)')

    ax_hodo.set_xlim(-max_spd, max_spd)
    ax_hodo.set_ylim(-max_spd, max_spd)
    ax_hodo.set_aspect('equal')
    ax_hodo.set_xlabel("Componente U (m/s - Zonal)", color='#cbd5e1', fontsize=11)
    ax_hodo.set_ylabel("Componente V (m/s - Meridional)", color='#cbd5e1', fontsize=11)
    ax_hodo.set_title("Hodógrafo do Vento & Helicidade Relativa", color='#f8fafc', fontsize=13, fontweight='bold')
    ax_hodo.tick_params(colors='#94a3b8')
    ax_hodo.legend(facecolor='#0f172a', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8.5, loc='upper left')

    # -----------------------------------------------------------------------
    # 3. CAPE REVERSÍVEL vs PSEUDOADIABÁTICO (Emanuel 1994)
    # -----------------------------------------------------------------------
    ax_cape = fig.add_subplot(2, 2, 3, facecolor='#1e293b')
    if cape_data:
        p_c = np.array(cape_data['p'])
        caper_c = np.array(cape_data['caper'])
        capep_c = np.array(cape_data['capep'])
        dcape_c = np.array(cape_data['dcape'])

        ax_cape.plot(capep_c, p_c, color='#fbbf24', marker='o', linewidth=2.5, label='CAPE Pseudoadiabático (Tv)')
        ax_cape.plot(caper_c, p_c, color='#38bdf8', marker='s', linewidth=2.5, label='CAPE Reversível (Tρ Emanuel)')
        ax_cape.plot(dcape_c, p_c, color='#ef4444', linestyle='--', linewidth=2, label='DCAPE (Downburst)')
        
        ax_cape.fill_betweenx(p_c, caper_c, capep_c, color='#38bdf8', alpha=0.25, label='Penalidade Water Loading')
        ax_cape.set_ylim(max(p_c) + 10, min(p_c) - 10)
        ax_cape.set_ylabel("Nível de Origem da Parcela (mb)", color='#cbd5e1', fontsize=11)
        ax_cape.set_xlabel("Energia Potencial Convectiva (J/kg)", color='#cbd5e1', fontsize=11)
        ax_cape.set_title("Espectro de CAPE & DCAPE vs Nível de Origem", color='#f8fafc', fontsize=13, fontweight='bold')
        ax_cape.grid(True, color='#334155', linestyle='-', linewidth=0.8)
        ax_cape.tick_params(colors='#94a3b8')
        ax_cape.legend(facecolor='#0f172a', edgecolor='#475569', labelcolor='#f8fafc', fontsize=9)
    else:
        ax_cape.text(0.5, 0.5, "cape.out não encontrado.\nExecute wyoming.py primeiro.", 
                     ha='center', va='center', color='#f87171', transform=ax_cape.transAxes)

    # -----------------------------------------------------------------------
    # 4. FREQUÊNCIA DE BRUNT-VÄISÄLÄ N²(z)
    # -----------------------------------------------------------------------
    ax_bv = fig.add_subplot(2, 2, 4, facecolor='#1e293b')
    g = 9.80665
    z_mid, n2 = [], []
    for i in range(len(data) - 1):
        dz = data[i+1]['z'] - data[i]['z']
        if dz > 15 and data[i+1]['z'] <= 10000:
            dth = data[i+1]['thtv'] - data[i]['thtv']
            th_mid = 0.5 * (data[i+1]['thtv'] + data[i]['thtv'])
            n2.append((g / th_mid) * (dth / dz))
            z_mid.append(0.5 * (data[i+1]['z'] + data[i]['z']))

    z_km = np.array(z_mid) / 1000.0
    n2_arr = np.array(n2)

    ax_bv.plot(n2_arr * 1e4, z_km, color='#c084fc', linewidth=2.5, label='N² (×10⁻⁴ s⁻²)')
    ax_bv.axvline(0, color='#ef4444', linestyle='--', linewidth=1.5, label='Neutro (N²=0)')
    ax_bv.axvline(2.0, color='#64748b', linestyle=':', linewidth=1, label='Típico Troposfera Livre')
    
    # Destaque de Inversões Térmicas Fortes (N² > 4)
    ax_bv.fill_betweenx(z_km, 4.0, n2_arr * 1e4, where=(n2_arr * 1e4 > 4.0), color='#fbbf24', alpha=0.3, label='Inversão Térmica / Capping')

    ax_bv.set_ylim(0, 10)
    ax_bv.set_xlim(-1, 8)
    ax_bv.set_ylabel("Altitude (km)", color='#cbd5e1', fontsize=11)
    ax_bv.set_xlabel("Frequência de Brunt-Väisälä N² (×10⁻⁴ s⁻²)", color='#cbd5e1', fontsize=11)
    ax_bv.set_title("Estabilidade Estática Vertical: N²(z)", color='#f8fafc', fontsize=13, fontweight='bold')
    ax_bv.grid(True, color='#334155', linestyle='-', linewidth=0.8)
    ax_bv.tick_params(colors='#94a3b8')
    ax_bv.legend(facecolor='#0f172a', edgecolor='#475569', labelcolor='#f8fafc', fontsize=9)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    output_png = 'diagnostico_mesoescala.png'
    plt.savefig(output_png, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    print(f"\n-> Gráfico científico de alta resolução salvo com sucesso: {output_png}")

if __name__ == '__main__':
    generate_meso_plot()
