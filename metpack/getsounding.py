"""
=============================================================================
getsounding.py - Equivalente em Python de getsounding.m
Download e parsing de radiossondagens da Universidade de Wyoming (UWYO)
Disciplina: Meteorologia de Mesoescala (FSC7116 - UFSC)
=============================================================================

Uso interativo ou como módulo:
    from getsounding import getsounding
    data, header, status = getsounding(83971, 1995, 12, 24, 12)

Uso via terminal:
    python getsounding.py 83971 1995 12 24 12
"""

import sys
import os
import urllib.request
import urllib.error
import re
import math
import numpy as np

def getsounding(station_id, year, month, day, hour):
    """
    Equivalente exato da função MATLAB getsounding.m:
    [data, header, status] = getsounding(station_id, year, month, day, hour)
    
    Parâmetros:
        station_id: Código OMM da estação (ex: 83971 para Porto Alegre, 83899 para Florianópolis)
        year: Ano (ex: 1995)
        month: Mês (1-12)
        day: Dia do mês (1-31)
        hour: Hora UTC (ex: 0, 12)
        
    Retorna:
        data: Matriz NumPy com as 11 colunas padrão de Wyoming:
              [P (hPa), z (m), T (C), DWPT (C), RELH (%), MIXR (g/kg),
               DRCT (deg), SKNT (kts), THTA (K), THTE (K), THTV (K)]
        header: Lista com os nomes das colunas
        status: 1 para sucesso, 0 para falha
    """
    station_str = str(station_id)
    year_s = f"{int(year):04d}"
    month_s = f"{int(month):02d}"
    day_s = f"{int(day):02d}"
    hour_s = f"{int(hour):02d}"
    
    header = [
        'P (hPa)', 'z (m)', 'T (C)', 'DWPT (C)', 'RELH (%)',
        'MIXR (g/kg)', 'DRCT (deg)', 'SKNT (kts)', 'THTA (K)',
        'THTE (K)', 'THTV (K)'
    ]
    
    # 1. Grava header.txt (compatibilidade idêntica com getsounding.m e tcon.m)
    with open('header.txt', 'w', encoding='utf-8') as f:
        f.write(f"{station_str} {int(hour)} {int(month)} {int(day)} {int(year)}\n")
        
    raw_text = None
    
    # 2. Verifica primeiro se existe arquivo local arquivado (para uso offline)
    local_candidates = [
        f"sounding_{year_s}{month_s}{day_s}_{hour_s}Z.txt",
        f"sounding_{year_s}{month_s}{day_s}_{hour_s}.txt",
        "sounding.txt"
    ]
    for cand in local_candidates:
        if os.path.exists(cand):
            try:
                with open(cand, 'r', encoding='utf-8', errors='ignore') as f_cand:
                    content = f_cand.read()
                    if '-----------------------------------------------------------------------------' in content:
                        raw_text = content
                        print(f"-> getsounding: Usando arquivo local existente '{cand}'")
                        break
            except Exception:
                pass
                
    # 3. Se não encontrou localmente ou não corresponde, faz o download da web
    if raw_text is None:
        urls_to_try = [
            # Novo endpoint WSGI (padrão atual da Universidade de Wyoming)
            f"https://weather.uwyo.edu/wsgi/sounding?datetime={year_s}-{month_s}-{day_s}%20{hour_s}:00:00&id={station_str}&type=TEXT:LIST",
            # Endpoint clássico legado cgi-bin
            f"http://weather.uwyo.edu/cgi-bin/sounding?region=samer&TYPE=TEXT:LIST&YEAR={year_s}&MONTH={month_s}&FROM={day_s}{hour_s}&TO={day_s}{hour_s}&STNM={station_str}"
        ]
        
        for url in urls_to_try:
            print(f"-> getsounding: Conectando a {url}...")
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    raw_text = response.read().decode('utf-8', errors='ignore')
                    if len(raw_text) > 900 and '-----------------------------------------------------------------------------' in raw_text:
                        print("-> Download concluído com sucesso!")
                        break
            except Exception as e:
                print(f"   Falha na URL ({e})")
                raw_text = None

    if raw_text is None or len(raw_text) < 900:
        print("Erro: Não foi possível obter a radiossondagem (URL ou arquivo local falhou).")
        return np.nan, header, 0

    # 4. Salva sounding.txt (idêntico ao getsounding.m)
    with open('sounding.txt', 'w', encoding='utf-8') as f:
        f.write(raw_text)

    # 5. Parsing das linhas de dados contidas na tag <PRE>...</PRE>
    lines = raw_text.splitlines()
    data_rows = []
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
                    row = [
                        float(parts[0]),  # P
                        float(parts[1]),  # z
                        float(parts[2]),  # T
                        float(parts[3]),  # DWPT
                        float(parts[4]),  # RELH
                        float(parts[5]),  # MIXR
                        float(parts[6]),  # DRCT
                        float(parts[7]),  # SKNT (ou m/s convertido)
                        float(parts[8]),  # THTA
                        float(parts[9]),  # THTE
                        float(parts[10])  # THTV
                    ]
                    data_rows.append(row)
                except ValueError:
                    continue

    if not data_rows:
        print("Erro: Nenhuma linha de dados numéricos pôde ser extraída de sounding.txt.")
        return np.nan, header, 0

    data = np.array(data_rows, dtype=float)

    # 6. Grava modsound.txt (colunas P, T, Td ou P, T, RH para alimentar o tcon.m / tcon.py)
    # getsounding.m gera: P (hPa), T (°C), DWPT (°C)
    # enquanto wyoming.f / tcon.m lê: P (hPa), T (°C), RH (0 a 1)
    # Aqui calculamos a umidade relativa de saturação para máxima compatibilidade:
    with open('modsound.txt', 'w', encoding='utf-8') as f_mod:
        for row in data:
            p_val = row[0]
            t_val = row[2]
            td_val = row[3]
            # Cálculo de umidade relativa (0 a 1) a partir de T e Td
            ev = 6.112 * math.exp(17.67 * td_val / (243.5 + td_val))
            es = 6.112 * math.exp(17.67 * t_val / (243.5 + t_val))
            rh_frac = min(1.0, max(0.0, ev / es)) if es > 0 else 0.0
            f_mod.write(f"{p_val:8.2f} {t_val:8.2f} {rh_frac:8.4f}\n")

    print(f"-> Sucesso: {len(data)} níveis extraídos.")
    print("   Arquivos gerados: 'sounding.txt', 'header.txt', 'modsound.txt'.")
    return data, header, 1

if __name__ == '__main__':
    if len(sys.argv) >= 6:
        st_id = sys.argv[1]
        yr = int(sys.argv[2])
        mo = int(sys.argv[3])
        dy = int(sys.argv[4])
        hr = int(sys.argv[5])
    else:
        # Padrão: Caso Extremo de Porto Alegre (SBPA - 83971) em 24/12/1995 12Z
        st_id = 83971
        yr, mo, dy, hr = 1995, 12, 24, 12

    print(f"Executando getsounding(station={st_id}, date={yr}-{mo:02d}-{dy:02d} {hr:02d}Z)...")
    data_out, hdr, st = getsounding(st_id, yr, mo, dy, hr)
    if st == 1:
        print(f"Dimensões dos dados: {data_out.shape[0]} linhas x {data_out.shape[1]} colunas.")
