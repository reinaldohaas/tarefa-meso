"""
=============================================================================
tcon.py - Equivalente em Python de tcon.m
Gera os gráficos de contorno 2D de Kerry Emanuel (MIT OCW 12.811 / Emanuel 1994):
1. Skew-T da sondagem (chamando skewt.py)
2. pcolor / contour de tdifrev (Anomalia Térmica de Densidade Reversível em K)
3. pcolor / contour de tdifpseudo (Anomalia Térmica Pseudoadiabática em K)
Disciplina: Meteorologia de Mesoescala (FSC7116 - UFSC)
=============================================================================

Uso via terminal:
    uv run --with matplotlib tcon.py
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from skewt import skewt
from wyoming import run_wyoming

def run_tcon(sounding_file=None, show=False):
    # Garante que a execução ocorra no diretório metpack/ para caminhos relativos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir and os.path.isdir(base_dir):
        os.chdir(base_dir)

    # Resolução de argumentos da linha de comando
    if sounding_file is None and len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg in ('19951212', '19951223', '19951224'):
            sounding_file = f"sounding_{arg}_12Z.txt"
        elif os.path.exists(arg):
            sounding_file = arg

    snd = sounding_file if sounding_file else 'sounding.txt'

    # 1. Garante que as saídas do wyoming estão geradas e atualizadas
    if not (os.path.exists('p.out') and os.path.exists('porig.out') and os.path.exists('tdifrev.out')):
        print(f"-> tcon: Arquivos de saída não encontrados. Executando wyoming.py [{snd}]...")
        run_wyoming(snd)

    # 2. Leitura do cabeçalho (header.txt)
    tit = "SBPA - 24/12/1995 12Z"
    if os.path.exists('header.txt'):
        try:
            with open('header.txt', 'r', encoding='utf-8') as f:
                parts = f.read().split()
                if len(parts) >= 5:
                    st_id, hr, mo, dy, yr = parts[0], parts[1], parts[2], parts[3], parts[4]
                    tit = f"Estação {st_id} - {int(dy):02d}/{int(mo):02d}/{int(yr):04d} 12Z"
        except Exception:
            pass

    print(f"-> Processando tcon para: {tit}")

    # 3. FIGURA 1: Skew-T da Sondagem (Linhas 13-20 do tcon.m)
    if os.path.exists('modsound.txt'):
        mod = np.loadtxt('modsound.txt')
        pr = mod[:, 0]
        tc = mod[:, 1]
        rh = np.clip(mod[:, 2], 0.0, 1.0)
        skewt(pr, tc, rh, title=f"Skew-T: {tit}", savepath="tcon_1_skewt.png", show=show)
    else:
        print("Aviso: 'modsound.txt' não encontrado para o Skew-T.")

    # 4. Leitura das matrizes calculadas por wyoming (p.out, porig.out, tdifrev.out, tdifpseudo.out)
    p = np.loadtxt('p.out')               # Níveis de pressão para onde a parcela é levantada (j)
    porig = np.loadtxt('porig.out')       # Níveis de origem da parcela (i)
    tdifrev = np.loadtxt('tdifrev.out')   # Matriz Reversível (K)
    tdifpseudo = np.loadtxt('tdifpseudo.out') # Matriz Pseudoadiabática (K)

    # Garante alinhamento dimensional exato
    n_rows, n_cols = tdifrev.shape
    p = p[:n_rows]
    porig = porig[:n_cols]

    # 5. FIGURA 2: Contorno de Temperatura de Densidade Reversível (Linhas 22-34 do tcon.m)
    fig2, ax2 = plt.subplots(figsize=(9, 7), facecolor='#0f172a')
    ax2.set_facecolor('#1e293b')

    # Malha 2D (porig no eixo X, p no eixo Y)
    X, Y = np.meshgrid(porig, p)
    
    # pcolor com interpolação suave
    mesh2 = ax2.pcolormesh(X, Y, tdifrev, cmap='RdBu_r', shading='gouraud', vmin=-10, vmax=12)
    cbar2 = plt.colorbar(mesh2, ax=ax2)
    cbar2.set_label('Diferença de Temp. de Densidade Reversível Tρ (K)', color='#f8fafc', fontweight='bold')
    cbar2.ax.tick_params(colors='#cbd5e1')

    # Isolinhas com rótulos (clabel)
    cs2 = ax2.contour(X, Y, tdifrev, levels=np.arange(-8, 14, 2), colors='black', linewidths=1.2)
    ax2.clabel(cs2, inline=True, fontsize=8, fmt='%1.0f')

    # Configuração dos eixos (Ambos invertidos, como no tcon.m)
    ax2.set_xlim(np.max(porig), np.min(porig))
    ax2.set_ylim(np.max(p), np.min(p))
    ax2.set_xlabel('Pressão de Origem da Parcela (mb)', color='#f8fafc', fontweight='bold', fontsize=11)
    ax2.set_ylabel('Pressão para a qual a Parcela é Levantada (mb)', color='#f8fafc', fontweight='bold', fontsize=11)
    ax2.set_title(f"Mean Reversible Density Temperature Difference (K)\n{tit} (Emanuel 1994)", 
                  color='#38bdf8', fontweight='bold', fontsize=12, pad=12)
    ax2.tick_params(colors='#cbd5e1')
    ax2.grid(True, color='#334155', linestyle=':', linewidth=0.6)

    plt.tight_layout()
    plt.savefig("tcon_2_tdifrev.png", dpi=200, facecolor=fig2.get_facecolor(), edgecolor='none')
    print("-> Salvo: 'tcon_2_tdifrev.png' (Contorno Reversível de Emanuel)")
    if show: plt.show()
    plt.close(fig2)

    # 6. FIGURA 3: Contorno Pseudoadiabático (Linhas 37-49 do tcon.m)
    fig3, ax3 = plt.subplots(figsize=(9, 7), facecolor='#0f172a')
    ax3.set_facecolor('#1e293b')

    mesh3 = ax3.pcolormesh(X, Y, tdifpseudo, cmap='RdBu_r', shading='gouraud', vmin=-10, vmax=14)
    cbar3 = plt.colorbar(mesh3, ax=ax3)
    cbar3.set_label('Diferença de Temp. Pseudoadiabática Tv (K)', color='#f8fafc', fontweight='bold')
    cbar3.ax.tick_params(colors='#cbd5e1')

    cs3 = ax3.contour(X, Y, tdifpseudo, levels=np.arange(-8, 16, 2), colors='black', linewidths=1.2)
    ax3.clabel(cs3, inline=True, fontsize=8, fmt='%1.0f')

    ax3.set_xlim(np.max(porig), np.min(porig))
    ax3.set_ylim(np.max(p), np.min(p))
    ax3.set_xlabel('Pressão de Origem da Parcela (mb)', color='#f8fafc', fontweight='bold', fontsize=11)
    ax3.set_ylabel('Pressão para a qual a Parcela é Levantada (mb)', color='#f8fafc', fontweight='bold', fontsize=11)
    ax3.set_title(f"Mean Pseudo-adiabatic Density Temperature Difference (K)\n{tit}", 
                  color='#fbbf24', fontweight='bold', fontsize=12, pad=12)
    ax3.tick_params(colors='#cbd5e1')
    ax3.grid(True, color='#334155', linestyle=':', linewidth=0.6)

    plt.tight_layout()
    plt.savefig("tcon_3_tdifpseudo.png", dpi=200, facecolor=fig3.get_facecolor(), edgecolor='none')
    print("-> Salvo: 'tcon_3_tdifpseudo.png' (Contorno Pseudoadiabático)")
    if show: plt.show()
    plt.close(fig3)

    # 7. FIGURA 4: Painel Comparativo Direto (Reversível vs Pseudoadiabático)
    fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(16, 7), facecolor='#0f172a')
    for ax in (ax4a, ax4b): ax.set_facecolor('#1e293b')

    m1 = ax4a.pcolormesh(X, Y, tdifrev, cmap='RdBu_r', shading='gouraud', vmin=-10, vmax=14)
    c1 = ax4a.contour(X, Y, tdifrev, levels=np.arange(-8, 14, 2), colors='black', linewidths=1)
    ax4a.clabel(c1, inline=True, fontsize=7.5, fmt='%1.0f')
    ax4a.set_xlim(np.max(porig), np.min(porig))
    ax4a.set_ylim(np.max(p), np.min(p))
    ax4a.set_title("Reversível (Tρ com Arrasto de Hidrometeoros)", color='#38bdf8', fontweight='bold', fontsize=11)
    ax4a.set_xlabel('Pressão de Origem (mb)', color='#cbd5e1')
    ax4a.set_ylabel('Pressão Elevada (mb)', color='#cbd5e1')
    ax4a.tick_params(colors='#cbd5e1')

    m2 = ax4b.pcolormesh(X, Y, tdifpseudo, cmap='RdBu_r', shading='gouraud', vmin=-10, vmax=14)
    c2 = ax4b.contour(X, Y, tdifpseudo, levels=np.arange(-8, 14, 2), colors='black', linewidths=1)
    ax4b.clabel(c2, inline=True, fontsize=7.5, fmt='%1.0f')
    ax4b.set_xlim(np.max(porig), np.min(porig))
    ax4b.set_ylim(np.max(p), np.min(p))
    ax4b.set_title("Pseudoadiabático (Tv sem Carga de Água)", color='#fbbf24', fontweight='bold', fontsize=11)
    ax4b.set_xlabel('Pressão de Origem (mb)', color='#cbd5e1')
    ax4b.tick_params(colors='#cbd5e1')

    fig4.suptitle(f"Comparativo de Flutuabilidade de Kerry Emanuel (1994): {tit}", 
                  fontsize=14, fontweight='bold', color='#f8fafc', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig("tcon_comparacao_emanuel.png", dpi=200, facecolor=fig4.get_facecolor(), edgecolor='none')
    print("-> Salvo: 'tcon_comparacao_emanuel.png' (Painel Comparativo)")
    plt.close(fig4)

    print("\n" + "="*70)
    print(" SUCESSO: Todas as figuras equivalentes ao tcon.m foram geradas!")
    print("   1. tcon_1_skewt.png")
    print("   2. tcon_2_tdifrev.png")
    print("   3. tcon_3_tdifpseudo.png")
    print("   4. tcon_comparacao_emanuel.png")
    print("="*70)

if __name__ == '__main__':
    run_tcon(show=False)
