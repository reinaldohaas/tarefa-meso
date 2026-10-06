"""
Script oficial de cálculo e auditoria de integridade científica.
Calcula todos os índices termodinâmicos e cinemáticos a partir dos dados brutos,
executa controle de qualidade (QC) e teste de sensibilidade, lê os índices oficiais
da Universidade de Wyoming e salva tudo centralizadamente em metpack/metricas.json.
"""
import os
import re
import json
import numpy as np
import pandas as pd
import metpy.calc as mpcalc
from metpy.units import units

def parse_wyoming_txt(filepath):
    """
    Lê arquivo de sondagem de Wyoming (WSGI TEXT:LIST ou cgi-bin) com tratamento completo
    de unidades (SPED em m/s convertido para nós; preenchimento de níveis termodinâmicos
    estratosféricos onde o vento não foi amostrado).
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    parts = text.split('-----------------------------------------------------------------------------')
    if len(parts) >= 3:
        header_line = parts[1]
        lines = parts[2].split('</PRE>')[0].splitlines()
    else:
        lines = text.splitlines()
        header_line = ""

    is_speed_ms = ('m/s' in header_line) or ('SPED' in header_line)

    data = []
    for line in lines:
        p = line.strip().split()
        if len(p) == 11:
            try:
                pres, hght, temp, dwpt, relh, mixr, drct, sped, thta, thte, thtv = [float(x) for x in p]
                if is_speed_ms:
                    sknt = sped * 1.94384449
                    s_ms = sped
                else:
                    sknt = sped
                    s_ms = sped * 0.51444444
                data.append([pres, hght, temp, dwpt, relh, mixr, drct, sknt, s_ms, thta, thte, thtv])
            except ValueError:
                continue
        elif len(p) == 9:
            try:
                pres, hght, temp, dwpt, relh, mixr, thta, thte, thtv = [float(x) for x in p]
                data.append([pres, hght, temp, dwpt, relh, mixr, np.nan, np.nan, np.nan, thta, thte, thtv])
            except ValueError:
                continue

    cols = ['PRES', 'HGHT', 'TEMP', 'DWPT', 'RELH', 'MIXR', 'DRCT', 'SKNT', 'SPED', 'THTA', 'THTE', 'THTV']
    df = pd.DataFrame(data, columns=cols).dropna(subset=['PRES', 'HGHT', 'TEMP', 'DWPT'])
    
    # Interpolação neutra de vento na estratosfera onde apenas T/Td foram medidos
    df['DRCT'] = df['DRCT'].interpolate().ffill().bfill()
    df['SKNT'] = df['SKNT'].interpolate().ffill().bfill()
    df['SPED'] = df['SPED'].interpolate().ffill().bfill()

    # Garante ordenação estritamente decrescente de pressão
    df = df.drop_duplicates(subset=['PRES']).sort_values('PRES', ascending=False).reset_index(drop=True)
    return df

def parse_wyoming_indices_html(filepath):
    """Lê a tabela oficial de índices termodinâmicos do Wyoming (type=INDICES)."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    indices = {}
    rows = re.findall(r'<TR>\s*<TD>(.*?)</TD>\s*<TD>(.*?)</TD>\s*<TD.*?>(.*?)</TD>\s*<TD>(.*?)</TD>\s*</TR>', html, re.DOTALL)
    for tag, desc, val, unit in rows:
        tag = tag.strip()
        desc = desc.strip()
        val = val.strip()
        unit = unit.strip()
        try:
            val_num = float(val)
        except ValueError:
            val_num = val
        indices[tag] = {
            'description': desc,
            'value': val_num,
            'unit': unit
        }
    return indices

def analyze_lapse_rates_and_qc(df):
    """
    Analisa taxas de lapso vertical (Γ = -dT/dz) e gradientes de θ e θe camada a camada.
    Identifica camadas superadiabáticas e variações acentuadas.
    """
    layers = []
    p = df['PRES'].values
    z = df['HGHT'].values
    T = df['TEMP'].values
    Td = df['DWPT'].values
    theta = df['THTA'].values
    theta_e = df['THTE'].values

    for i in range(len(df) - 1):
        dz = z[i+1] - z[i]
        dT = T[i+1] - T[i]
        dth = theta[i+1] - theta[i]
        dthe = theta_e[i+1] - theta_e[i]

        gamma = - (dT / dz) * 1000.0 if dz > 0 else 0.0
        dth_dz = (dth / dz) * 1000.0 if dz > 0 else 0.0

        is_superadiabatic = (gamma > 10.5 or dth_dz < -1.0)
        is_large_dthe = abs(dthe) > 15.0

        if is_superadiabatic or is_large_dthe or (Td[i] > T[i] + 0.1):
            layers.append({
                'layer_p_bottom': float(p[i]),
                'layer_p_top': float(p[i+1]),
                'dz_m': float(dz),
                'dT_C': round(float(dT), 2),
                'gamma_K_km': round(float(gamma), 2),
                'dtheta_dz_K_km': round(float(dth_dz), 2),
                'dtheta_e_K': round(float(dthe), 2),
                'is_superadiabatic': bool(is_superadiabatic),
                'is_large_dthe': bool(is_large_dthe)
            })
    return layers

def parse_emanuel_cape_out(filepath):
    """Extrai os dados de CAPE e DCAPE reversível e pseudoadiabático de cape.out."""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        lines = f.readlines()
    data = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 8:
            try:
                row = [float(p) for p in parts[:8]]
                data.append(row)
            except ValueError:
                continue
    if not data:
        return None
    arr = np.array(data)
    # Colunas: p(0), Rev PA(1), P.A. PA(2), Rev NA(3), P.A. NA(4), Rev CAPE(5), P.A. CAPE(6), DCAPE(7)
    return {
        'surface_p_hPa': float(arr[0, 0]),
        'surface_cape_rev_Jkg': round(float(arr[0, 5]), 1),
        'surface_cape_pseudo_Jkg': round(float(arr[0, 6]), 1),
        'surface_cin_rev_Jkg': round(float(arr[0, 3]), 1),
        'surface_cin_pseudo_Jkg': round(float(arr[0, 4]), 1),
        'surface_dcape_emanuel_Jkg': round(float(arr[0, 7]), 1),
        'max_cape_rev_Jkg': round(float(np.max(arr[:, 5])), 1),
        'max_cape_pseudo_Jkg': round(float(np.max(arr[:, 6])), 1),
        'max_cape_p_hPa': float(arr[np.argmax(arr[:, 6]), 0]),
        'max_dcape_emanuel_Jkg': round(float(np.max(arr[:, 7])), 1),
        'max_dcape_p_hPa': float(arr[np.argmax(arr[:, 7]), 0])
    }

def calc_diagnostics(df, label=""):
    """Calcula todos os índices termodinâmicos e cinemáticos via MetPy."""
    p = df['PRES'].values * units.hPa
    z = df['HGHT'].values * units.meter
    T = df['TEMP'].values * units.degC
    Td = df['DWPT'].values * units.degC
    spd = df['SKNT'].values * units.knot
    drct = df['DRCT'].values * units.deg

    u, v = mpcalc.wind_components(spd, drct)

    res = {}
    
    # 1. Termodinâmica básica
    pw = mpcalc.precipitable_water(p, Td)
    res['pw_mm'] = round(float(pw.to('mm').magnitude), 2)
    
    # LCL
    lcl_p, lcl_t = mpcalc.lcl(p[0], T[0], Td[0])
    res['lcl_p_hPa'] = round(float(lcl_p.to('hPa').magnitude), 1)
    res['lcl_t_C'] = round(float(lcl_t.to('degC').magnitude), 1)

    # Surface-Based CAPE / CIN
    try:
        sbcape, sbcin = mpcalc.surface_based_cape_cin(p, T, Td)
        res['sbcape_Jkg'] = round(float(sbcape.magnitude), 1)
        res['sbcin_Jkg'] = round(float(sbcin.magnitude), 1)
    except Exception as e:
        res['sbcape_Jkg'] = f"Erro: {str(e)}"
        res['sbcin_Jkg'] = f"Erro: {str(e)}"

    # Most-Unstable CAPE / CIN
    try:
        mucape, mucin = mpcalc.most_unstable_cape_cin(p, T, Td)
        res['mucape_Jkg'] = round(float(mucape.magnitude), 1)
        res['mucin_Jkg'] = round(float(mucin.magnitude), 1)
    except Exception as e:
        res['mucape_Jkg'] = f"Erro: {str(e)}"
        res['mucin_Jkg'] = f"Erro: {str(e)}"

    # Mixed-Layer CAPE / CIN (100 hPa)
    try:
        mlcape, mlcin = mpcalc.mixed_layer_cape_cin(p, T, Td, depth=100 * units.hPa)
        res['mlcape_Jkg'] = round(float(mlcape.magnitude), 1)
        res['mlcin_Jkg'] = round(float(mlcin.magnitude), 1)
    except Exception as e:
        res['mlcape_Jkg'] = f"Erro: {str(e)}"
        res['mlcin_Jkg'] = f"Erro: {str(e)}"

    # LFC e EL
    try:
        lfc_p, lfc_t = mpcalc.lfc(p, T, Td)
        res['lfc_p_hPa'] = round(float(lfc_p.to('hPa').magnitude), 1) if not np.isnan(lfc_p.magnitude) else None
    except Exception:
        res['lfc_p_hPa'] = None

    try:
        el_p, el_t = mpcalc.el(p, T, Td)
        res['el_p_hPa'] = round(float(el_p.to('hPa').magnitude), 1) if not np.isnan(el_p.magnitude) else None
    except Exception:
        res['el_p_hPa'] = None

    # Lifted Index
    try:
        parcel_prof = mpcalc.parcel_profile(p, T[0], Td[0])
        li = mpcalc.lifted_index(p, T, parcel_prof)
        res['lifted_index_K'] = round(float(li.magnitude[0]), 2)
    except Exception as e:
        res['lifted_index_K'] = f"Erro: {str(e)}"

    # Downdraft CAPE (MetPy)
    try:
        dcape_tuple = mpcalc.downdraft_cape(p, T, Td)
        res['dcape_metpy_Jkg'] = round(float(dcape_tuple[0].magnitude), 1)
    except Exception as e:
        res['dcape_metpy_Jkg'] = f"Erro: {str(e)}"

    # 2. Cinemática
    z_agl = z - z[0]

    # Bulk shear 0-1km, 0-3km, 0-6km
    try:
        bs_1 = mpcalc.bulk_shear(p, u, v, height=z_agl, depth=1000 * units.meter)
        bs_3 = mpcalc.bulk_shear(p, u, v, height=z_agl, depth=3000 * units.meter)
        bs_6 = mpcalc.bulk_shear(p, u, v, height=z_agl, depth=6000 * units.meter)

        shear_0_1 = np.hypot(bs_1[0], bs_1[1])
        shear_0_3 = np.hypot(bs_3[0], bs_3[1])
        shear_0_6 = np.hypot(bs_6[0], bs_6[1])

        res['bulk_shear_0_1km_ms'] = round(float(shear_0_1.to('m/s').magnitude), 2)
        res['bulk_shear_0_1km_kt'] = round(float(shear_0_1.to('knot').magnitude), 1)
        res['bulk_shear_0_3km_ms'] = round(float(shear_0_3.to('m/s').magnitude), 2)
        res['bulk_shear_0_3km_kt'] = round(float(shear_0_3.to('knot').magnitude), 1)
        res['bulk_shear_0_6km_ms'] = round(float(shear_0_6.to('m/s').magnitude), 2)
        res['bulk_shear_0_6km_kt'] = round(float(shear_0_6.to('knot').magnitude), 1)
    except Exception as e:
        res['bulk_shear_0_6km_ms'] = f"Erro: {str(e)}"

    # Bunkers Storm Motion
    try:
        bunkers_rm, bunkers_lm, mean_wind = mpcalc.bunkers_storm_motion(p, u, v, z_agl)
        res['bunkers_lm_u_ms'] = round(float(bunkers_lm[0].to('m/s').magnitude), 2)
        res['bunkers_lm_v_ms'] = round(float(bunkers_lm[1].to('m/s').magnitude), 2)
        res['bunkers_rm_u_ms'] = round(float(bunkers_rm[0].to('m/s').magnitude), 2)
        res['bunkers_rm_v_ms'] = round(float(bunkers_rm[1].to('m/s').magnitude), 2)
        res['mean_wind_u_ms'] = round(float(mean_wind[0].to('m/s').magnitude), 2)
        res['mean_wind_v_ms'] = round(float(mean_wind[1].to('m/s').magnitude), 2)

        lm_spd = np.hypot(bunkers_lm[0], bunkers_lm[1])
        res['bunkers_lm_spd_kt'] = round(float(lm_spd.to('knot').magnitude), 1)
        res['bunkers_lm_spd_ms'] = round(float(lm_spd.to('m/s').magnitude), 2)
        lm_dir = mpcalc.wind_direction(bunkers_lm[0], bunkers_lm[1])
        res['bunkers_lm_dir_deg'] = round(float(lm_dir.magnitude), 1)

        # SRH com Left-Mover (Hemisfério Sul)
        srh_0_1_lm = mpcalc.storm_relative_helicity(z_agl, u, v, depth=1000 * units.meter,
                                                    storm_u=bunkers_lm[0], storm_v=bunkers_lm[1])
        srh_0_3_lm = mpcalc.storm_relative_helicity(z_agl, u, v, depth=3000 * units.meter,
                                                    storm_u=bunkers_lm[0], storm_v=bunkers_lm[1])

        res['srh_0_1km_lm_m2s2'] = round(float(srh_0_1_lm[2].magnitude), 1)
        res['srh_0_3km_lm_m2s2'] = round(float(srh_0_3_lm[2].magnitude), 1)

        # SRH com Right-Mover (para comparação técnica)
        srh_0_3_rm = mpcalc.storm_relative_helicity(z_agl, u, v, depth=3000 * units.meter,
                                                    storm_u=bunkers_rm[0], storm_v=bunkers_rm[1])
        res['srh_0_3km_rm_m2s2'] = round(float(srh_0_3_rm[2].magnitude), 1)
    except Exception as e:
        res['srh_0_3km_lm_m2s2'] = f"Erro: {str(e)}"

    # Vento em 925 hPa
    idx_925 = (df['PRES'] - 925).abs().idxmin()
    res['p_level_near_925'] = float(df.loc[idx_925, 'PRES'])
    res['wind_925_spd_kt'] = round(float(df.loc[idx_925, 'SKNT']), 1)
    res['wind_925_spd_ms'] = round(float(df.loc[idx_925, 'SPED']), 1)
    res['wind_925_dir_deg'] = round(float(df.loc[idx_925, 'DRCT']), 0)
    res['t_925_C'] = float(df.loc[idx_925, 'TEMP'])
    res['td_925_C'] = float(df.loc[idx_925, 'DWPT'])
    res['theta_e_925_K'] = float(df.loc[idx_925, 'THTE'])

    return res

def main():
    print("=== INICIANDO AUDITORIA E CÁLCULO DE INTEGRIDADE CIENTÍFICA (REVISÃO 2) ===")
    
    files = {
        '19951212': 'metpack/sounding_19951212_12Z.txt',
        '19951223': 'metpack/sounding_19951223_12Z.txt',
        '19951224': 'metpack/sounding_19951224_12Z.txt'
    }
    indices_files = {
        '19951212': 'metpack/indices_19951212_12Z.txt',
        '19951223': 'metpack/indices_19951223_12Z.txt',
        '19951224': 'metpack/indices_19951224_12Z.txt'
    }

    out_json = {}

    # 1. Leitura e Análise da Sondagem de 24/12/1995
    df_24 = parse_wyoming_txt(files['19951224'])
    qc_flags_24 = analyze_lapse_rates_and_qc(df_24)
    out_json['qc_camadas_superadiabaticas_19951224'] = qc_flags_24

    # Camadas específicas de 925 hPa
    # 925.0 -> 910.5 hPa e 910.5 -> 850.0 hPa
    idx_925 = df_24[df_24['PRES'] == 925.0].index[0]
    idx_910 = df_24[df_24['PRES'] == 910.5].index[0]
    idx_850 = df_24[df_24['PRES'] == 850.0].index[0]

    dz_925_910 = df_24.loc[idx_910, 'HGHT'] - df_24.loc[idx_925, 'HGHT']
    dT_925_910 = df_24.loc[idx_910, 'TEMP'] - df_24.loc[idx_925, 'TEMP']
    gamma_925_910 = - (dT_925_910 / dz_925_910) * 1000.0
    dth_dz_925_910 = ((df_24.loc[idx_910, 'THTA'] - df_24.loc[idx_925, 'THTA']) / dz_925_910) * 1000.0

    dz_910_850 = df_24.loc[idx_850, 'HGHT'] - df_24.loc[idx_910, 'HGHT']
    dT_910_850 = df_24.loc[idx_850, 'TEMP'] - df_24.loc[idx_910, 'TEMP']
    gamma_910_850 = - (dT_910_850 / dz_910_850) * 1000.0
    dth_dz_910_850 = ((df_24.loc[idx_850, 'THTA'] - df_24.loc[idx_910, 'THTA']) / dz_910_850) * 1000.0

    out_json['gradientes_camadas_925'] = {
        'camada_925_910': {
            'dz_m': round(float(dz_925_910), 1),
            'dT_C': round(float(dT_925_910), 2),
            'gamma_K_km': round(float(gamma_925_910), 2),
            'dtheta_dz_K_km': round(float(dth_dz_925_910), 2),
            'dtheta_e_K': round(float(df_24.loc[idx_910, 'THTE'] - df_24.loc[idx_925, 'THTE']), 2)
        },
        'camada_910_850': {
            'dz_m': round(float(dz_910_850), 1),
            'dT_C': round(float(dT_910_850), 2),
            'gamma_K_km': round(float(gamma_910_850), 2),
            'dtheta_dz_K_km': round(float(dth_dz_910_850), 2),
            'dtheta_e_K': round(float(df_24.loc[idx_850, 'THTE'] - df_24.loc[idx_910, 'THTE']), 2)
        }
    }

    # Teste de sensibilidade: sondagem sem os níveis próximos a 925 hPa
    low_level_near_925 = [942.5, 925.0, 910.5]
    df_24_sens = df_24[~df_24['PRES'].isin(low_level_near_925)].reset_index(drop=True)

    # 2. Diagnóstico de 12/12/1995 (Oficial)
    df_12 = parse_wyoming_txt(files['19951212'])
    diag_12 = calc_diagnostics(df_12, "19951212")
    emanuel_12 = parse_emanuel_cape_out('metpack/19951212_cape.out')
    if not emanuel_12:
        emanuel_12 = parse_emanuel_cape_out('metpack/testes/19951212_py_corte_cape.out')
    if not emanuel_12:
        emanuel_12 = parse_emanuel_cape_out('metpack/testes/cape_19951212_f.out')
    diag_12['emanuel'] = emanuel_12
    ind_12 = parse_wyoming_indices_html(indices_files['19951212'])
    if not ind_12:
        ind_12 = parse_wyoming_indices_html('metpack/testes/indices_19951212_12Z.txt')
    diag_12['indices_wyoming'] = ind_12
    out_json['19951212'] = diag_12

    # 3. Diagnóstico de 23/12/1995 (Oficial)
    df_23 = parse_wyoming_txt(files['19951223'])
    diag_23 = calc_diagnostics(df_23, "19951223")
    emanuel_23 = parse_emanuel_cape_out('metpack/19951223_cape.out')
    if not emanuel_23:
        emanuel_23 = parse_emanuel_cape_out('metpack/testes/19951223_py_corte_cape.out')
    if not emanuel_23:
        emanuel_23 = parse_emanuel_cape_out('metpack/testes/cape_19951223_f.out')
    diag_23['emanuel'] = emanuel_23
    ind_23 = parse_wyoming_indices_html(indices_files['19951223'])
    if not ind_23:
        ind_23 = parse_wyoming_indices_html('metpack/testes/indices_19951223_12Z.txt')
    diag_23['indices_wyoming'] = ind_23
    out_json['19951223'] = diag_23

    # 4. Diagnóstico de 24/12/1995 (Oficial - Sondagem Completa como publicada)
    diag_24_raw = calc_diagnostics(df_24, "19951224_raw")
    emanuel_24 = parse_emanuel_cape_out('metpack/19951224_cape.out')
    if not emanuel_24:
        emanuel_24 = parse_emanuel_cape_out('metpack/testes/19951224_py_corte_cape.out')
    if not emanuel_24:
        emanuel_24 = parse_emanuel_cape_out('metpack/testes/cape_19951224_f.out')
    diag_24_raw['emanuel'] = emanuel_24
    ind_24 = parse_wyoming_indices_html(indices_files['19951224'])
    if not ind_24:
        ind_24 = parse_wyoming_indices_html('metpack/testes/indices_19951224_12Z.txt')
    diag_24_raw['indices_wyoming'] = ind_24
    out_json['19951224_raw'] = diag_24_raw

    # 5. Diagnóstico de 24/12/1995 (Teste de Sensibilidade sem os níveis próximos a 925 hPa)
    diag_24_sens = calc_diagnostics(df_24_sens, "19951224_sensibilidade")
    diag_24_sens['emanuel'] = "Teste de sensibilidade com níveis de 925 hPa removidos da ascensão"
    diag_24_sens['indices_wyoming'] = None
    out_json['19951224_sensibilidade'] = diag_24_sens
    # Mantém compatibilidade com a chave 19951224_qc para scripts que a leem
    out_json['19951224_qc'] = diag_24_sens

    # Comparativo Padronizado dos Três Métodos de DCAPE (Item 4 da Revisão 3)
    out_json['dcape_comparativo'] = {
        '19951212': {
            'data': '12/12/1995',
            'regime': 'Estável',
            'wyoming_Jkg': (ind_12.get('DCAPE', {}).get('value') if ind_12 else None),
            'metpy_Jkg': diag_12.get('dcape_metpy_Jkg'),
            'emanuel_max_Jkg': (emanuel_12.get('max_dcape_emanuel_Jkg') if emanuel_12 else None),
            'emanuel_max_p_hPa': (emanuel_12.get('max_dcape_p_hPa') if emanuel_12 else None)
        },
        '19951223': {
            'data': '23/12/1995',
            'regime': 'Transição',
            'wyoming_Jkg': (ind_23.get('DCAPE', {}).get('value') if ind_23 else None),
            'metpy_Jkg': diag_23.get('dcape_metpy_Jkg'),
            'emanuel_max_Jkg': (emanuel_23.get('max_dcape_emanuel_Jkg') if emanuel_23 else None),
            'emanuel_max_p_hPa': (emanuel_23.get('max_dcape_p_hPa') if emanuel_23 else None)
        },
        '19951224_raw': {
            'data': '24/12/1995',
            'regime': 'Instável (Oficial)',
            'wyoming_Jkg': (ind_24.get('DCAPE', {}).get('value') if ind_24 else None),
            'metpy_Jkg': diag_24_raw.get('dcape_metpy_Jkg'),
            'emanuel_max_Jkg': (emanuel_24.get('max_dcape_emanuel_Jkg') if emanuel_24 else None),
            'emanuel_max_p_hPa': (emanuel_24.get('max_dcape_p_hPa') if emanuel_24 else None)
        },
        '19951224_sensibilidade': {
            'data': '24/12/1995',
            'regime': 'Instável (Sensibilidade)',
            'wyoming_Jkg': None,
            'metpy_Jkg': diag_24_sens.get('dcape_metpy_Jkg'),
            'emanuel_max_Jkg': None,
            'emanuel_max_p_hPa': None
        }
    }

    # Tabela comparativa estruturada para relatórios, HTML e roteiro
    comp_dict = {}
    for dt_key, dt_label, diag in [('19951212', '12/12/1995', diag_12), ('19951223', '23/12/1995', diag_23), ('19951224', '24/12/1995', diag_24_raw)]:
        w = diag.get('indices_wyoming', {}) or {}
        items = [
            ('PW (mm)', w.get('PWAT', {}).get('value'), diag.get('pw_mm')),
            ('MUCAPE (J/kg)', w.get('MUCAPE', {}).get('value'), diag.get('mucape_Jkg')),
            ('MUCIN (J/kg)', w.get('MUCIN', {}).get('value'), diag.get('mucin_Jkg')),
            ('LCL (hPa)', w.get('LCLP', {}).get('value'), diag.get('lcl_p_hPa')),
            ('DCAPE (J/kg)', w.get('DCAPE', {}).get('value'), diag.get('dcape_metpy_Jkg')),
            ('Showalter (K)', w.get('SHOW', {}).get('value'), None),
            ('Lifted Index (K)', w.get('LFVT', {}).get('value'), diag.get('lifted_index_K')),
            ('K Index (C)', w.get('KINX', {}).get('value'), None),
            ('Total Totals (K)', w.get('TOTL', {}).get('value'), None)
        ]
        row_list = []
        for name, val_w, val_calc in items:
            diff = round(val_calc - val_w, 2) if (val_w is not None and val_calc is not None) else None
            row_list.append({
                'indice': name,
                'wyoming': val_w,
                'calculado': val_calc,
                'diferenca': diff
            })
        comp_dict[dt_key] = {
            'data': dt_label,
            'linhas': row_list
        }
    out_json['comparativo_wyoming_metpy'] = comp_dict

    # Gravação do JSON mestre único
    with open('metpack/metricas.json', 'w', encoding='utf-8') as f:
        json.dump(out_json, f, indent=2, ensure_ascii=False)
    print("\n-> Arquivo metpack/metricas.json gravado com sucesso!")

    # Exibição da Tabela de Conferência Oficial com Wyoming
    print("\n" + "="*85)
    print("TABELA DE CONFERÊNCIA: ÍNDICES OFICIAIS DO WYOMING vs NOSSO CÁLCULO")
    print("="*85)
    for dt, diag in [('12/12/1995', diag_12), ('23/12/1995', diag_23), ('24/12/1995', diag_24_raw)]:
        w = diag.get('indices_wyoming', {})
        print(f"\n--- DATA: {dt} ---")
        print(f"{'Índice':<22} | {'Wyoming':<15} | {'Nosso Cálculo (MetPy)':<22} | {'Diferença':<15}")
        print("-" * 80)
        
        items = [
            ('PW (mm)', w.get('PWAT', {}).get('value'), diag.get('pw_mm')),
            ('MUCAPE (J/kg)', w.get('MUCAPE', {}).get('value'), diag.get('mucape_Jkg')),
            ('MUCIN (J/kg)', w.get('MUCIN', {}).get('value'), diag.get('mucin_Jkg')),
            ('LCL (hPa)', w.get('LCLP', {}).get('value'), diag.get('lcl_p_hPa')),
            ('DCAPE (J/kg)', w.get('DCAPE', {}).get('value'), diag.get('dcape_metpy_Jkg')),
            ('Showalter (K)', w.get('SHOW', {}).get('value'), None),
            ('Lifted Index (K)', w.get('LFVT', {}).get('value'), diag.get('lifted_index_K')),
            ('K Index (C)', w.get('KINX', {}).get('value'), None),
            ('Total Totals (K)', w.get('TOTL', {}).get('value'), None)
        ]
        for name, val_w, val_calc in items:
            str_w = f"{val_w}" if val_w is not None else "N/A"
            str_c = f"{val_calc}" if val_calc is not None else "N/A"
            if val_w is not None and val_calc is not None and isinstance(val_w, (int, float)) and isinstance(val_calc, (int, float)):
                diff = round(val_calc - val_w, 2)
                str_diff = f"{diff:+}"
            else:
                str_diff = "-"
            print(f"{name:<22} | {str_w:<15} | {str_c:<22} | {str_diff:<15}")

if __name__ == '__main__':
    main()
