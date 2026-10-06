"""
getsounding_wyoming.py - versão Python de getsounding_wyoming.m

Baixa uma radiossondagem do Wyoming (interface atual "wsgi") e prepara os arquivos de
entrada do programa de Kerry Emanuel (wyoming.f): sounding.txt, header.txt e modsound.txt.

Adaptado de getsounding.m (A. Rhines / K. Emanuel, https://texmex.mit.edu/pub/emanuel/soundings/):
  - usa o endereço atual: https://weather.uwyo.edu/wsgi/sounding?...&type=TEXT:LIST
  - lê as colunas pela posição do cabeçalho (campos vazios -> NaN)
  - converte o vento SPED (m/s, formato atual) para nós (coluna 8 = SKNT, como no original)

Uso:
    from getsounding_wyoming import getsounding_wyoming
    data, header, status, fonte = getsounding_wyoming(83971, 1995, 12, 24, 12)
    # colunas: P (hPa), z (m), T (C), Td (C), UR (%), r (g/kg), DIR (graus), VEL (nós),
    #          THETA (K), THETA_E (K), THETA_V (K)

Se o Wyoming não responder, tenta a cópia local sounding_AAAAMMDD_HHZ.txt (na pasta atual
ou em metpack/) e a cópia guardada no repositório (só existe para os casos do exemplo).
"""
import os
import re
import urllib.request

import numpy as np

URL_REPOSITORIO = 'https://raw.githubusercontent.com/reinaldohaas/tarefa-meso/master/metpack'
HEADER = ['P (hPa)', 'z (m)', 'T (C)', 'DWPT (C)', 'RELH (%)', 'MIXR (g/kg)',
          'DRCT (deg)', 'SKNT (kts)', 'THTA (K)', 'THTE (K)', 'THTV (K)']
ORDEM = ['PRES', 'HGHT', 'TEMP', 'DWPT', 'RELH', 'MIXR', 'DRCT', 'SKNT', 'THTA', 'THTE', 'THTV']


def _baixa(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode('utf-8', errors='ignore')


def getsounding_wyoming(station_id, year, month, day, hour, src='FM35', pasta_saida='.'):
    station = str(station_id)
    url = (f'https://weather.uwyo.edu/wsgi/sounding?datetime={year:04d}-{month:02d}-{day:02d}%20{hour:02d}:00:00'
           f'&id={station}&src={src}&type=TEXT:LIST')
    arq_local = f'sounding_{year:04d}{month:02d}{day:02d}_{hour:02d}Z.txt'
    pasta_m = os.path.dirname(os.path.abspath(__file__))
    fontes = [('url', url), ('arquivo', arq_local), ('arquivo', os.path.join(pasta_m, arq_local)),
              ('url', f'{URL_REPOSITORIO}/{arq_local}')]
    texto, fonte = '', ''
    for tipo, f in fontes:
        try:
            if tipo == 'url':
                texto = _baixa(f)
            elif os.path.exists(f):
                texto = open(f, encoding='utf-8', errors='ignore').read()
        except Exception as e:
            print(f'  falhou {f}: {type(e).__name__}')
            texto = ''
        if texto and re.search(r'PRES\s+HGHT', texto):
            fonte = f
            break
        texto = ''
    if not texto:
        print(f'Erro: sondagem {station} {year:04d}-{month:02d}-{day:02d} {hour:02d}Z não encontrada.')
        return np.nan, HEADER, 0, ''
    print(f'Sondagem {station} {year:04d}-{month:02d}-{day:02d} {hour:02d}Z obtida de: {fonte}')
    with open(os.path.join(pasta_saida, arq_local), 'w', encoding='utf-8') as fh:   # cópia local
        fh.write(texto)

    # --- leitura da tabela pelas posições do cabeçalho ---
    linhas = re.sub(r'<[^>]+>', '', texto).splitlines()
    i0 = next(i for i, l in enumerate(linhas) if re.search(r'PRES\s+HGHT', l))
    nomes = linhas[i0].split()
    fins = [m.end() for m in re.finditer(r'\S+', linhas[i0])]
    k = i0 + 1
    while k < len(linhas) and (not linhas[k].strip() or linhas[k].strip().startswith('-') or 'hPa' in linhas[k]):
        k += 1
    tab = []
    while k < len(linhas) and re.match(r'^\s*-?\d', linhas[k]):
        l, ini, vals = linhas[k], 0, []
        for fim in fins:
            campo = l[ini:fim].strip()
            vals.append(float(campo) if campo else np.nan)
            ini = fim
        tab.append(vals)
        k += 1
    tab = np.array(tab, dtype=float)
    data = np.full((len(tab), 11), np.nan)
    for j, nome in enumerate(ORDEM):
        if nome in nomes:
            data[:, j] = tab[:, nomes.index(nome)]
    if 'SKNT' not in nomes and 'SPED' in nomes:
        data[:, 7] = tab[:, nomes.index('SPED')] * 1.943844      # m/s -> nós

    # --- arquivos de entrada do wyoming.f ---
    d = data[np.all(np.isfinite(data[:, :4]), axis=1)]
    _, iu = np.unique(d[:, 0], return_index=True)
    d = d[np.sort(iu)]
    d = d[np.argsort(-d[:, 0])]
    with open(os.path.join(pasta_saida, 'sounding.txt'), 'w', encoding='latin1') as fh:
        fh.write('\n' * 10)                      # 10 linhas de cabeçalho (puladas pelo wyoming.f)
        for r in d:
            fh.write(f'{r[0]:7.1f}{r[1]:7.0f}{r[2]:7.1f}{r[3]:7.1f}\n')
        fh.write('</PRE>\n')
        fh.write(f'Station identifier: {station}\n')
        fh.write(f'Station number: {station}\n')
        fh.write(f'Observation time: {year % 100:02d}{month:02d}{day:02d} {hour:02d}00\n')
    with open(os.path.join(pasta_saida, 'header.txt'), 'w') as fh:
        fh.write(f'{station} {hour} {month} {day} {year}')
    with open(os.path.join(pasta_saida, 'modsound.txt'), 'w') as fh:
        for r in d:
            fh.write(f'{r[0]:f} {r[2]:f} {np.clip(r[4] / 100, 0, 1):f}\n')
    return data, HEADER, 1, fonte
