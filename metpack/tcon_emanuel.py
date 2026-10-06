"""
tcon_emanuel.py - versão Python de tcon_emanuel.m

Executa o programa de Kerry Emanuel (wyoming.f) para a sondagem em PASTA (que contém o
sounding.txt gravado por getsounding_wyoming) e desenha as matrizes de flutuabilidade
(diferença de temperatura de densidade parcela - ambiente) para a ascensão reversível e a
pseudoadiabática, lado a lado e na mesma escala de cores.

Adaptado de tcon.m (K. Emanuel, https://texmex.mit.edu/pub/emanuel/soundings/):
  - compila o wyoming.f com gfortran (uma vez por execução);
  - corte=False (padrão) remove o piso artificial de -4 K do wyoming.f original;
  - sem gfortran, usa os arquivos p.out, porig.out, tdifrev.out, tdifpseudo.out e cape.out
    que já estiverem na pasta (por exemplo, gerados pelo notebook).

Uso:
    from tcon_emanuel import tcon_emanuel
    E = tcon_emanuel('emanuel_19951224_12', 'INSTÁVEL 24/12/1995 12Z')
"""
import os
import re
import shutil
import subprocess

import numpy as np
import matplotlib.pyplot as plt

SAIDAS = ['p.out', 'porig.out', 'tdifrev.out', 'tdifpseudo.out', 'cape.out']


def prepara_wyoming(corte=False):
    """Compila o wyoming.f. Devolve o caminho do executável, ou None se não houver gfortran."""
    pasta_m = os.path.dirname(os.path.abspath(__file__))
    exe = os.path.join(pasta_m, 'wyoming_emanuel.exe' if os.name == 'nt' else 'wyoming_emanuel')
    codigo = open(os.path.join(pasta_m, 'wyoming.f'), encoding='latin1').read()
    if not corte:
        for l in ('TRDBAR(I,J)=MAX(TRDBAR(I,J),-4.0)', 'TPDBAR(I,J)=MAX(TPDBAR(I,J),-4.0)'):
            codigo = codigo.replace(l, 'CONTINUE')
    usado = os.path.join(pasta_m, 'wyoming_usado.f')
    open(usado, 'w', encoding='latin1').write(codigo)
    gf = shutil.which('gfortran')
    if gf and subprocess.run([gf, '-O2', '-o', exe, usado], capture_output=True).returncode == 0:
        return exe
    print('Aviso: não foi possível compilar o wyoming.f (gfortran ausente?). '
          'Serão usados os arquivos .out já existentes na pasta da sondagem.')
    return None


def le_cape_out(arq):
    """Linhas numéricas de cape.out: origem, PA_rev, PA_pse, NA_rev, NA_pse, CAPE_rev, CAPE_pse, DCAPE."""
    linhas = [l.split() for l in open(arq, encoding='latin1') if re.match(r'^\s*-?\d+\.\d', l)]
    return np.array([[float(x) for x in l[:8]] for l in linhas if len(l) >= 8])


def tcon_emanuel(pasta, titulo=None, corte=False, mostrar=False):
    titulo = titulo or pasta
    exe = prepara_wyoming(corte)
    if exe:
        r = subprocess.run([exe], cwd=pasta, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f'wyoming.f falhou na pasta {pasta}:\n{r.stdout}\n{r.stderr}')
    for s in SAIDAS:
        if not os.path.exists(os.path.join(pasta, s)):
            raise FileNotFoundError(f'{s} não encontrado em {pasta}. Sem compilador Fortran, copie para essa pasta '
                                    'p.out, porig.out, tdifrev.out, tdifpseudo.out e cape.out gerados pelo notebook.')
    E = dict(p=np.loadtxt(os.path.join(pasta, 'p.out')),
             porig=np.loadtxt(os.path.join(pasta, 'porig.out')),
             rev=np.loadtxt(os.path.join(pasta, 'tdifrev.out')),
             pse=np.loadtxt(os.path.join(pasta, 'tdifpseudo.out')),
             cape=le_cape_out(os.path.join(pasta, 'cape.out')))
    X, Y = np.meshgrid(E['porig'], E['p'])
    E['X'], E['Y'] = X, Y

    # escala simétrica comum: pelo menos +-6 K, em passos pares, pela maior flutuabilidade positiva
    vis = (Y < X) & (Y >= 100)
    amp = max(6.0, 2 * np.ceil(max(np.nanmax(E['rev'][vis]), np.nanmax(E['pse'][vis])) / 2))

    fig, axs = plt.subplots(1, 2, figsize=(15, 7.5), sharey=True)
    for ax, campo, nome, col in zip(axs, (E['rev'], E['pse']), ('reversível', 'pseudoadiabática'), (5, 6)):
        Z = np.where(Y < X, campo, np.nan)        # só níveis acima do nível de origem
        cf = ax.contourf(X, Y, Z, levels=np.arange(-amp, amp + 0.25, 0.5), cmap='RdBu_r', extend='both')
        cs = ax.contour(X, Y, Z, levels=[v for v in np.arange(-amp, amp + 0.1, 2) if v != 0], colors='k', linewidths=0.7)
        ax.clabel(cs, fmt='%d', fontsize=8)
        ax.contour(X, Y, Z, levels=[0], colors='k', linewidths=2)
        ax.set_xlim(X.max(), X.min())
        ax.set_ylim(Y.max(), 100)
        ax.set_xlabel('Pressão de origem da parcela (hPa)')
        k = int(np.argmax(E['cape'][:, col]))
        ax.set_title(f'Ascensão {nome}\n(CAPE máx: {E["cape"][k, col]:.0f} J/kg, origem {E["cape"][k, 0]:.0f} hPa)')
    axs[0].set_ylabel('Pressão para a qual a parcela é elevada (hPa)')
    fig.colorbar(cf, ax=axs, orientation='horizontal', fraction=0.05, pad=0.12,
                 ticks=np.arange(-amp, amp + 1, 2 if amp <= 10 else 4),
                 label='Diferença de temperatura de densidade parcela − ambiente (K)')
    fig.suptitle(f'Matrizes de flutuabilidade de Emanuel — {titulo}', fontweight='bold')
    fig.savefig(os.path.join(pasta, 'matrizes_emanuel.png'), dpi=150, bbox_inches='tight')
    if mostrar:
        plt.show()
    plt.close(fig)
    return E
