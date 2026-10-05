"""
=============================================================================
skewt.py - Equivalente em Python de skewt.m (tskew.m)
Diagrama Termodinâmico Skew-T / Log-P com adiabáticas secas, úmidas e isohígras
Disciplina: Meteorologia de Mesoescala (FSC7116 - UFSC)
=============================================================================

Uso:
    from skewt import skewt
    skewt(pz, tz, rhz, title="Porto Alegre 24/12/1995")
"""

import math
import numpy as np
import matplotlib.pyplot as plt

def skewt(pz, tz, rhz, title=None, savepath=None, show=False):
    """
    Equivalente exato da função MATLAB skewt.m:
    success = skewt(pz, tz, rhz)
    
    Parâmetros:
        pz: Vetor de pressão (hPa / mb)
        tz: Vetor de temperatura (°C)
        rhz: Vetor de umidade relativa (0 a 1)
        title: Título do gráfico (opcional)
        savepath: Caminho para salvar a figura (ex: 'skewt.png')
        show: Se True, abre a janela interativa do matplotlib
    """
    pz = np.asarray(pz, dtype=float)
    tz = np.asarray(tz, dtype=float)
    rhz = np.asarray(rhz, dtype=float)

    # 1. Ponto de Orvalho (equações exatas de Tetens usadas em skewt.m)
    ez = 6.112 * np.exp(17.67 * tz / (243.5 + tz))
    # Evita divisão por zero se pz <= ez
    denom = np.maximum(pz - ez, 1e-4)
    qz = rhz * 0.622 * ez / denom
    qz = np.maximum(qz, 1e-8)
    
    chi = np.log(pz * qz / (6.112 * (0.622 + qz)))
    tdz = 243.5 * chi / (17.67 - chi)

    # 2. Grade de Fundo (Idêntica ao skewt.m)
    p = np.arange(1050.0, 75.0, -25.0)  # 1050 down to 100 mb
    t0 = np.arange(-48.0, 52.0, 2.0)    # -48 to 50 C

    ps = len(p)
    ts = len(t0)

    tem = np.zeros((ps, ts))
    thet = np.zeros((ps, ts))
    q = np.zeros((ps, ts))
    thetaea = np.zeros((ps, ts))

    for j in range(ps):
        pj = p[j]
        for i in range(ts):
            # Transformação Skew-T: tem = t0 + 30 * ln(0.001 * p)
            tem_val = t0[i] + 30.0 * np.log(0.001 * pj)
            tem[j, i] = tem_val
            
            # Adiabática Seca (Theta)
            thet_val = (273.15 + tem_val) * ((1000.0 / pj) ** 0.287)
            thet[j, i] = thet_val
            
            # Razão de mistura de saturação (q em g/kg)
            es_val = 6.112 * np.exp(17.67 * tem_val / (243.5 + tem_val))
            denom_s = max(pj - es_val, 1e-4)
            q_val = 622.0 * es_val / denom_s
            q[j, i] = max(0.0, q_val)
            
            # Pseudoadiabática (Theta-e)
            thetaea[j, i] = thet_val * np.exp(2.5 * q_val / (tem_val + 273.15))

    qs = np.sqrt(q)

    # 3. Construção da Figura
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='#0f172a')
    ax.set_facecolor('#1e293b')

    # Isotermas (Linhas cinzas inclinadas)
    ax.contour(t0, p, tem, levels=16, colors='#475569', linewidths=0.7, linestyles='--')

    # Adiabáticas Secas (Theta - Azul)
    ax.contour(t0, p, thet, levels=24, colors='#38bdf8', linewidths=0.8, alpha=0.5)

    # Linhas de Razão de Mistura (Isohígras qs - Verde)
    ax.contour(t0, p, qs, levels=20, colors='#4ade80', linewidths=0.7, alpha=0.4, linestyles=':')

    # Adiabáticas Saturadas (Theta-e - Laranja/Vermelho)
    ax.contour(t0, p, thetaea, levels=24, colors='#f87171', linewidths=0.8, alpha=0.5)

    # 4. Traçado dos Dados Observados no Sistema Oblíquo
    # tzm = tz - 30 * ln(0.001 * pz)
    tzm = tz - 30.0 * np.log(0.001 * pz)
    tdzm = tdz - 30.0 * np.log(0.001 * pz)

    ax.plot(tzm, pz, color='#ef4444', linewidth=2.5, label='Temperatura (T)')
    ax.plot(tdzm, pz, color='#10b981', linewidth=2.5, linestyle='--', label='Ponto de Orvalho (Td)')

    # 5. Configuração dos Eixos (Log e Invertido)
    ax.set_yscale('log')
    ax.set_ylim(1050, 100)
    ax.set_xlim(-40, 45)
    ax.set_yticks([1000, 900, 850, 700, 500, 400, 300, 200, 100])
    ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())

    ax.grid(True, which='both', color='#334155', linestyle='-', linewidth=0.5)
    ax.tick_params(colors='#cbd5e1', labelsize=10)
    ax.set_xlabel('Temperatura (°C)', color='#f8fafc', fontweight='bold', fontsize=11)
    ax.set_ylabel('Pressão (mb / hPa)', color='#f8fafc', fontweight='bold', fontsize=11)

    if title:
        ax.set_title(title, color='#38bdf8', fontweight='bold', fontsize=13, pad=12)
    else:
        ax.set_title('Diagrama Skew-T / Log-P (Algoritmo skewt.m)', color='#38bdf8', fontweight='bold', fontsize=13, pad=12)

    ax.legend(facecolor='#0f172a', edgecolor='#475569', labelcolor='#f8fafc', fontsize=9.5, loc='lower left')

    plt.tight_layout()

    if savepath:
        plt.savefig(savepath, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
        print(f"-> Skew-T salvo em: {savepath}")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return 'yes'

if __name__ == '__main__':
    # Teste carregando modsound.txt existente
    import os
    if os.path.exists('modsound.txt'):
        print("Lendo 'modsound.txt'...")
        arr = np.loadtxt('modsound.txt')
        pr = arr[:, 0]
        tc = arr[:, 1]
        rh = arr[:, 2]
        skewt(pr, tc, rh, title="Sondagem de Teste (modsound.txt)", savepath="skewt_standalone.png")
    else:
        print("Aviso: 'modsound.txt' não encontrado. Execute getsounding.py primeiro.")
