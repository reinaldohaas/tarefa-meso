"""
=============================================================================
wyoming.py - Emulação Fiel do Algoritmo Termodinâmico de Kerry Emanuel (MIT)
Tradução do programa clássico wyoming.f (Emanuel 1994 / MIT OCW 12.811)
Disciplina: Meteorologia de Mesoescala (FSC7116 - UFSC)
=============================================================================

Este script executa exatamente o mesmo algoritmo numérico de wyoming.f:
1. Lê o arquivo sounding.txt (formato University of Wyoming).
2. Interpola verticalmente a sondagem a cada 5 hPa (mb).
3. Calcula a ascensão convectiva para diferentes níveis de origem (NK=20):
   - Ascensão Reversível: conserva entropia úmida total (s) e calcula a 
     Temperatura de Densidade (TLVR = T_rho) subtraindo o carregamento de
     água líquida retida (water loading, r_l = r_t - r_v).
   - Ascensão Pseudoadiabática: conserva entropia pseudoadiabática (sp) e
     assume perda instantânea de condensado (TLVP = T_v).
4. Simula o ramo descendente (downdraft saturado) e calcula o DCAPE.
5. Gera os mesmos arquivos de saída de wyoming.f:
   - cape.out (Tabela com PA, NA, CAPE reversível, CAPE pseudoadiabático, DCAPE)
   - p.out, porig.out, tdifrev.out, tdifpseudo.out
=============================================================================
"""

import math
import os
import sys

# ---------------------------------------------------------------------------
# CONSTANTES TERMODINÂMICAS IDÊNTICAS AO wyoming.f (Emanuel 1994)
# ---------------------------------------------------------------------------
CPD = 1005.7       # Calor específico do ar seco a pressão constante (J/kg/K)
CPV = 1870.0       # Calor específico do vapor de água a pressão constante (J/kg/K)
CL = 2500.0        # Calor específico da água líquida (J/kg/K)
CPVMCL = 2320.0    # Diferença efetiva cl - cpv usada por Emanuel
RV = 461.5         # Constante dos gases para vapor d'água (J/kg/K)
RD = 287.04        # Constante dos gases para ar seco (J/kg/K)
EPS = RD / RV      # Razão das constantes dos gases (~0.622)
ALV0 = 2.501E6     # Calor latente de vaporização a 0 °C (J/kg)

NA = 800
NK = 20
NS = 1000

def run_wyoming(sounding_file='sounding.txt'):
    if not os.path.exists(sounding_file):
        print(f"Erro: Arquivo '{sounding_file}' não encontrado no diretório atual.")
        return

    # -----------------------------------------------------------------------
    # 1. LEITURA DA SONDAGEM BRUTA DE WYOMING
    # -----------------------------------------------------------------------
    with open(sounding_file, 'r', encoding='utf-8', errors='ignore') as f:
        raw_lines = f.readlines()

    # wyoming.f pula os primeiros cabeçalhos e procura as linhas de dados numéricos
    ptem = []
    ttem = []
    rtem = []
    evtem = []
    estem = []

    header_skipped = 0
    data_started = False
    
    for line in raw_lines:
        # Detecta separador da tabela de Wyoming
        if '-----------------------------------------------------------------------------' in line:
            header_skipped += 1
            if header_skipped == 2:
                data_started = True
            continue
        
        if not data_started:
            continue

        if line.strip().startswith('</PRE>') or line.strip().startswith('<button') or line.strip().startswith('Station'):
            break

        parts = line.split()
        if len(parts) >= 4:
            try:
                pk = float(parts[0])
                tk = float(parts[2])
                rk = float(parts[3]) # Ponto de orvalho (Td em °C)
                
                if pk < 78.0 or tk > 100.0 or rk > 100.0:
                    continue
                
                if tk < -200.0: tk = -200.0

                # Pressão de vapor segundo Tetens
                ev = 6.112 * math.exp(17.67 * rk / (243.5 + rk))
                es = 6.112 * math.exp(17.67 * tk / (243.5 + tk))
                ev = min(ev, es)
                
                # Razão de mistura (kg/kg)
                r_mix = EPS * ev / (pk - ev)
                t_kelvin = tk + 273.15

                ptem.append(pk)
                ttem.append(t_kelvin)
                rtem.append(r_mix)
                evtem.append(ev)
                estem.append(es)
            except ValueError:
                continue

    n_raw = len(ptem)
    if n_raw < 5:
        print("Erro: Não foram encontrados dados numéricos suficientes em sounding.txt.")
        return

    print(f"-> Lido {sounding_file}: {n_raw} níveis de pressão identificados.")
    print(f"   Superfície: {ptem[0]:.1f} hPa | Topo: {ptem[-1]:.1f} hPa")

    # -----------------------------------------------------------------------
    # 2. INTERPOLAÇÃO VERTICAL EM INTERVALOS REGULARES DE 5 hPa (mb)
    # -----------------------------------------------------------------------
    p = [ptem[0]]
    t = [ttem[0]]
    r = [rtem[0]]
    ev = [evtem[0]]
    es = [estem[0]]

    nl = int((1005.0 - ptem[-1]) / 5.0 + 0.001)
    for i in range(1, nl):
        pi = 1005.0 - 5.0 * float(i + 1)
        for j in range(1, n_raw):
            if ptem[j] <= pi:
                dp = ptem[j-1] - ptem[j]
                weight_j = (ptem[j-1] - pi) / dp
                weight_jm1 = (pi - ptem[j]) / dp
                
                ti = ttem[j] * weight_j + ttem[j-1] * weight_jm1
                ri = rtem[j] * weight_j + rtem[j-1] * weight_jm1
                evi = evtem[j] * weight_j + evtem[j-1] * weight_jm1
                esi = estem[j] * weight_j + estem[j-1] * weight_jm1
                
                p.append(pi)
                t.append(ti)
                r.append(ri)
                ev.append(evi)
                es.append(esi)
                break

    n = len(p)
    actual_nk = min(NK, n)

    # Matrizes de trabalho
    tlr = [[0.0]*n for _ in range(actual_nk)]
    tlp = [[0.0]*n for _ in range(actual_nk)]
    tlvr = [[0.0]*n for _ in range(actual_nk)]
    tlvp = [[0.0]*n for _ in range(actual_nk)]
    tvrdif = [[0.0]*n for _ in range(actual_nk)]
    tvpdif = [[0.0]*n for _ in range(actual_nk)]
    lw = [[0.0]*n for _ in range(actual_nk)]
    tvd = [0.0]*actual_nk
    pl = [p[i] for i in range(actual_nk)]

    # -----------------------------------------------------------------------
    # 3. CICLO PRINCIPAL: ASCENSÃO E DESCENSÃO CONVECTIVA (Emanuel 1994)
    # -----------------------------------------------------------------------
    for i in range(actual_nk):
        rs = EPS * es[i] / (p[i] - es[i])
        alv = ALV0 - CPVMCL * (t[i] - 273.15)
        em = max(ev[i], 1.0e-6)

        # Entropia Reversível (S) e Pseudoadiabática (SP)
        s = (CPD + r[i] * CL) * math.log(t[i]) - RD * math.log(p[i] - ev[i]) + \
            alv * r[i] / t[i] - r[i] * RV * math.log(em / es[i])

        sp = CPD * math.log(t[i]) - RD * math.log(p[i] - ev[i]) + \
             alv * r[i] / t[i] - r[i] * RV * math.log(em / es[i])

        ah = (CPD + r[i] * CL) * t[i] + alv * r[i]

        # Nível de Bulbo Úmido para Downdraft
        slope = CPD + alv * alv * rs / (RV * t[i] * t[i])
        tg = t[i]
        rg = rs
        for _ in range(20):
            alv1 = ALV0 - CPVMCL * (tg - 273.15)
            ahg = (CPD + CL * rg) * tg + alv1 * rg
            tg = tg + (ah - ahg) / slope
            tc = tg - 273.15
            enew = 6.112 * math.exp(17.67 * tc / (243.5 + tc))
            rg = EPS * enew / (p[i] - enew)

        eg = rg * p[i] / (EPS + rg)
        alv1 = ALV0 - CPVMCL * (tg - 273.15)
        spd = CPD * math.log(tg) - RD * math.log(p[i] - eg) + alv1 * rg / tg
        tvd[i] = tg * (1.0 + rg / EPS) / (1.0 + rg) - t[i] * (1.0 + r[i] / EPS) / (1.0 + r[i])
        if p[i] < 100.0: tvd[i] = 0.0

        # Pressão do NCL (LCL) segundo Kerry Emanuel
        rh = r[i] / rs
        rh = min(rh, 1.0)
        chi = t[i] / (1669.0 - 122.0 * rh - t[i])
        plcl = p[i] * (rh**chi) if rh > 0.0 else 1.0

        # Ascensão da Corrente Ascendente (Updraft)
        sum_cw = 0.0
        rg0 = r[i]
        tg0 = t[i]

        for j in range(i, n):
            rs_j = EPS * es[j] / (p[j] - es[j])
            alv_j = ALV0 - CPVMCL * (t[j] - 273.15)
            sl = (CPD + r[i] * CL + alv_j * alv_j * rs_j / (RV * t[j] * t[j])) / t[j]
            slp = (CPD + rs_j * CL + alv_j * alv_j * rs_j / (RV * t[j] * t[j])) / t[j]

            if p[j] >= plcl:
                # Abaixo do LCL: adiabática seca
                tlr_val = t[i] * ((p[j] / p[i]) ** (RD / CPD))
                tlr[i][j] = tlr_val
                tlp[i][j] = tlr_val
                lw[i][j] = 0.0
                tlvr_val = tlr_val * (1.0 + r[i] / EPS) / (1.0 + r[i])
                tlvr[i][j] = tlvr_val
                tlvp[i][j] = tlvr_val
                tvrdif[i][j] = tlvr_val - t[j] * (1.0 + r[j] / EPS) / (1.0 + r[j])
                tvpdif[i][j] = tvrdif[i][j]
            else:
                # Acima do LCL: iteração de Newton-Raphson
                # 3.1. Ascensão Reversível (conserva S e água total r[i])
                tg = t[j]
                rg = rs_j
                for _ in range(20):
                    em = rg * p[j] / (EPS + rg)
                    alv_k = ALV0 - CPVMCL * (tg - 273.15)
                    sg = (CPD + r[i] * CL) * math.log(tg) - RD * math.log(p[j] - em) + alv_k * rg / tg
                    tg = tg + (s - sg) / sl
                    tc = tg - 273.15
                    enew = 6.112 * math.exp(17.67 * tc / (243.5 + tc))
                    rg = EPS * enew / (p[j] - enew)

                tlr[i][j] = tg
                # TEMPERATURA DE DENSIDADE (Emanuel 1994, Eq. 4.3.4):
                tlvr[i][j] = tg * (1.0 + rg / EPS) / (1.0 + r[i])
                lw[i][j] = max(0.0, r[i] - rg)
                tvrdif[i][j] = tlvr[i][j] - t[j] * (1.0 + r[j] / EPS) / (1.0 + r[j])

                # 3.2. Ascensão Pseudoadiabática (conserva Sp, r_l = 0)
                tg = t[j]
                rg = rs_j
                for _ in range(20):
                    cpw = 0.0
                    if j > 0:
                        cpw = sum_cw + CL * 0.5 * (rg0 + rg) * (math.log(tg) - math.log(tg0))
                    em = rg * p[j] / (EPS + rg)
                    alv_k = ALV0 - CPVMCL * (tg - 273.15)
                    spg = CPD * math.log(tg) - RD * math.log(p[j] - em) + cpw + alv_k * rg / tg
                    tg = tg + (sp - spg) / slp
                    tc = tg - 273.15
                    enew = 6.112 * math.exp(17.67 * tc / (243.5 + tc))
                    rg = EPS * enew / (p[j] - enew)

                tlp[i][j] = tg
                # TEMPERATURA VIRTUAL PURA:
                tlvp[i][j] = tg * (1.0 + rg / EPS) / (1.0 + rg)
                tvpdif[i][j] = tlvp[i][j] - t[j] * (1.0 + r[j] / EPS) / (1.0 + r[j])
                rg0 = rg
                tg0 = tg
                sum_cw = cpw

    # -----------------------------------------------------------------------
    # 4. INTEGRAÇÃO DE CAPE, CIN (NA/PA) E DCAPE
    # -----------------------------------------------------------------------
    par = [0.0] * actual_nk
    nar = [0.0] * actual_nk
    caper = [0.0] * actual_nk
    pap = [0.0] * actual_nk
    nap = [0.0] * actual_nk
    capep = [0.0] * actual_nk
    dcape = [0.0] * actual_nk

    for i in range(actual_nk):
        # Determina o nível de flutuabilidade neutra (EL)
        inbr = 1
        inbp = 1
        for j in range(n - 1, i, -1):
            if tvrdif[i][j] > 0.0: inbr = max(inbr, j)
            if tvpdif[i][j] > 0.0: inbp = max(inbp, j)

        # Integração Reversível
        if inbr > i:
            for j in range(i + 1, inbr + 1):
                tvm = 0.5 * (tvrdif[i][j] + tvrdif[i][j - 1])
                pm = 0.5 * (p[j] + p[j - 1])
                dp_val = (p[j - 1] - p[j]) / pm
                if tvm <= 0.0:
                    nar[i] -= RD * tvm * dp_val
                else:
                    par[i] += RD * tvm * dp_val
            caper[i] = par[i] - nar[i]

        # Integração Pseudoadiabática
        if inbp > i:
            for j in range(i + 1, inbp + 1):
                tvm = 0.5 * (tvpdif[i][j] + tvpdif[i][j - 1])
                pm = 0.5 * (p[j] + p[j - 1])
                dp_val = (p[j - 1] - p[j]) / pm
                if tvm <= 0.0:
                    nap[i] -= RD * tvm * dp_val
                else:
                    pap[i] += RD * tvm * dp_val
            capep[i] = pap[i] - nap[i]

        # DCAPE (Downdraft)
        if i > 0:
            for j in range(i - 1, -1, -1):
                tvdifm = tvpdif[i][j + 1] if i != (j + 1) else tvd[i]
                tvm = 0.5 * (tvpdif[i][j] + tvdifm)
                pm = 0.5 * (p[j] + p[j + 1])
                dp_val = (p[j] - p[j + 1]) / pm
                if tvm < 0.0:
                    dcape[i] -= RD * tvm * dp_val

    # -----------------------------------------------------------------------
    # 5. GRAVAÇÃO DO ARQUIVO cape.out (FORMATO IDÊNTICO AO wyoming.f)
    # -----------------------------------------------------------------------
    with open('cape.out', 'w') as f_out:
        f_out.write("     Number of soundings =    1\n")
        f_out.write("                    ALL AREAS IN UNITS OF J/kg\n\n")
        f_out.write(" Origin    Rev.    P.A.    Rev.    P.A.    Rev.    P.A.    Rev.    P.A.\n")
        f_out.write(" p (mb)     PA      PA      NA      NA    CAPE    CAPE    DCAPE STDCAPE    STDCAPE\n")
        f_out.write(" ------    ----    ----    ----    ----    ----    ----   -----   -------  -------\n")
        for i in range(actual_nk):
            f_out.write(f" {pl[i]:6.1f}{par[i]:8.1f}{pap[i]:8.1f}{nar[i]:8.1f}{nap[i]:8.1f}"
                        f"{caper[i]:8.1f}{capep[i]:8.1f}{dcape[i]:8.1f}{0.0:8.1f}{0.0:8.1f}\n")

    # Arquivos adicionais para contornos/perfis (ex: tcon.m e tcon.py)
    with open('p.out', 'w') as f_p:
        for pi in p: f_p.write(f"{pi:.2f}\n")

    with open('porig.out', 'w') as f_po:
        for pli in pl: f_po.write(f"{pli:.2f}\n")

    # Matrizes de Anomalia Térmica (Linhas: nível elevado j; Colunas: nível de origem i)
    with open('tdifrev.out', 'w') as f_tr:
        for j in range(n):
            f_tr.write(" ".join(f"{tvrdif[i][j]:8.3f}" for i in range(actual_nk)) + "\n")

    with open('tdifpseudo.out', 'w') as f_tp:
        for j in range(n):
            f_tp.write(" ".join(f"{tvpdif[i][j]:8.3f}" for i in range(actual_nk)) + "\n")

    # modsound.txt para alimentação direta do skewt.m e skewt.py
    with open('modsound.txt', 'w') as f_mod:
        for k in range(n_raw):
            t_c = ttem[k] - 273.15
            rh_k = min(1.0, max(0.0, evtem[k] / estem[k])) if estem[k] > 0 else 0.0
            f_mod.write(f"{ptem[k]:8.2f} {t_c:8.2f} {rh_k:8.4f}\n")

    print("\n" + "="*70)
    print(" SUCESSO: Processamento Termodinâmico Concluído (Emanuel 1994)")
    print("="*70)
    print(" Arquivos gerados:")
    print("   -> cape.out (Tabela com CAPE Reversível e Pseudoadiabático)")
    print("   -> p.out, porig.out")
    print("   -> tdifrev.out, tdifpseudo.out (Matrizes para tcon.py e tcon.m)")
    print("   -> modsound.txt (Para skewt.py e skewt.m)")
    print("="*70)
    print(f" Nível de Superfície: {pl[0]:.1f} mb")
    print(f"   PA Pseudoadiabática (Tv) : {pap[0]:.1f} J/kg")
    print(f"   PA Reversível (T_rho)     : {par[0]:.1f} J/kg")
    print(f"   NA (Inibição CIN)         : {nap[0]:.1f} J/kg")
    print(f"   DCAPE (Rajada Descendente): {dcape[0]:.1f} J/kg")
    reducao = ((pap[0] - par[0]) / pap[0] * 100) if pap[0] > 0 else 0
    print(f"   Redução por Water Loading : {reducao:.1f}%")
    print("="*70)

if __name__ == '__main__':
    run_wyoming()
