# 🌪️ Tutorial de Meteorologia de Mesoescala: Diagnóstico Tríplice & Análise Termodinâmica

**Disciplina:** FSC7116 — Meteorologia de Mesoescala  
**Docente:** Prof. Dr. Reinaldo Haas  
**Instituição:** Universidade Federal de Santa Catarina (UFSC)  
**Público-alvo:** Estudantes de graduação/pós-graduação em Meteorologia e previsores da Defesa Civil de Santa Catarina (DCSC).  
**Tutorial Online (GitHub Pages):** [https://reinaldohaas.github.io/tarefa-meso/](https://reinaldohaas.github.io/tarefa-meso/)  

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/reinaldohaas/tarefa-meso/blob/master/Seminario_plot_sounding_revisado.ipynb)

---

## 📌 O que é a Tarefa

Este repositório é um tutorial prático e reprodutível para análise termodinâmica e cinemática de radiossondagens observadas na América do Sul. A tarefa consiste em diagnosticar comparativamente **três regimes atmosféricos observados distintos**:

1. **Atmosfera Estável:** Perfil com inversão ou forte estabilidade térmica, inibição de flutuabilidade positiva e ausência de convecção profunda. *(Exemplo do tutorial: Porto Alegre — SBPA 83971 em 12/12/1995 12Z)*.
2. **Atmosfera de Transição:** Perfil com umedecimento progressivo da troposfera e flutuabilidade moderada. *(Exemplo do tutorial: Porto Alegre — SBPA 83971 em 22/12/1995 12Z)*.
3. **Atmosfera Instável:** Perfil com elevado empuxo térmico, gradiente vertical de $\theta_e$ decrescente com a altura, forte influxo úmido em baixos níveis e suporte cinemático. *(Exemplo do tutorial: Porto Alegre — SBPA 83971 em 24/12/1995 12Z)*.

> **Importante:** Todos os números de diagnóstico (CAPE, CIN, cisalhamento, SRH, PW, DCAPE) são calculados dinamicamente pelos scripts a partir dos dados do Wyoming e centralizados em `metpack/metricas.json`. Para consultar os valores exatos de diagnóstico, tabelas de conferência e matrizes de Emanuel, consulte o [Tutorial Interativo (index.html)](https://reinaldohaas.github.io/tarefa-meso/) ou o arquivo `metpack/metricas.json`.

---

## 📋 Passos para o Estudante

1. **Escolha das Três Sondagens:**  
   Selecione 3 radiossondagens reais no [Banco de Dados da Universidade de Wyoming](https://weather.uwyo.edu/upperair/sounding.html) contemplando os 3 regimes (estável, transição e instável). As sondagens podem ser da mesma estação em datas distintas ou de estações diferentes na América do Sul.
2. **Download dos Dados Completos:**  
   Baixe o formato vertical (`TEXT:LIST`) e os índices oficiais (`INDICES`) para cada data selecionada e armazene na pasta `metpack/`.
3. **Cálculo dos Diagnósticos e Conferência:**  
   Execute os scripts de cálculo termodinâmico (MetPy e rotinas de Kerry Emanuel 1994) para gerar as métricas e comparar com os índices oficiais publicados pelo Wyoming.
4. **Geração das Figuras Didáticas:**  
   Gere os diagramas Skew-T individuais e comparativos, perfis verticais de $\theta_e, N^2, S, r$ até 200 hPa, hodógrafo com convenções do Hemisfério Sul (Bunkers Left-Mover) e matrizes 2D de Emanuel ($T_\rho$ vs $T_v$).
5. **Preparação da Apresentação Final:**  
   Compile a apresentação de 10 slides (20 minutos) no formato estabelecido para defesa técnica perante os previsores da Defesa Civil de Santa Catarina.

---

## 📂 Estrutura de Pastas do Repositório

```text
tarefa-meso/
├── index.html                   # Tutorial didático para web (GitHub Pages)
├── build_index_html.py          # Script gerador do index.html
├── generate_figures.py          # Script que plota todas as figuras científicas
├── generate_pptx.py             # Script gerador da apresentação de 10 slides (PPTX)
├── apresentacao_meso.pptx       # Apresentação oficial para a Defesa Civil de SC
├── ROTEIRO_ESTUDANTES.md        # Roteiro passo a passo com critérios de avaliação
├── Seminario_plot_sounding_revisado.ipynb # Notebook oficial para execução no Google Colab
└── metpack/                     # Módulo de processamento meteorológico
    ├── metricas.json            # Fonte única de verdade de todas as métricas calculadas
    ├── calc_metricas.py         # Script que calcula métricas e grava o metricas.json
    ├── wyoming.py               # Algoritmo de Kerry Emanuel (1994) para parcelas e CAPE
    ├── wyoming.f                # Código-fonte original em Fortran 77 (referência teórica)
    ├── tcon.py                  # Script de renderização das matrizes 2D de Emanuel
    ├── getsounding.py           # Utilitário de download de sondagens do Wyoming
    └── *.png                    # Figuras oficiais geradas pelos scripts
```

---

## 🛠️ Comandos de Execução com `uv`

Para executar todo o pipeline sem necessidade de instalar dependências globais:

```powershell
# 1. Calcular todas as métricas oficiais (atualiza metpack/metricas.json)
uv run --with metpy --with pandas --with numpy python metpack/calc_metricas.py

# 2. Gerar as matrizes 2D de Kerry Emanuel (1994)
uv run --with matplotlib --with numpy python metpack/tcon.py

# 3. Gerar todas as figuras científicas (Skew-T, perfis até 200 hPa, hodógrafo)
uv run --with metpy --with cartopy --with matplotlib --with numpy python generate_figures.py

# 4. Gerar o tutorial web para GitHub Pages
uv run python build_index_html.py

# 5. Gerar a apresentação em PowerPoint (10 slides / 20 min)
uv run --with python-pptx python generate_pptx.py
```

---

## 📚 Referências Bibliográficas

- **Emanuel, K. A. (1994):** *Atmospheric Convection*. Oxford University Press, 580 pp.
- **Bunkers, M. J. et al. (2000):** *Predicting Supercell Motion Using a New Hodograph Technique*. Weather and Forecasting, 15(1), 61–79.
- **Markowski, P. & Richardson, Y. (2010):** *Mesoscale Meteorology in Midlatitudes*. Wiley-Blackwell.
- **Thompson, R. L. et al. (2003, 2012):** *Close proximity soundings within supercell environments*. Weather and Forecasting.
- **Weisman, M. L. & Klemp, J. B. (1982):** *The dependence of numerically simulated convective storms on vertical wind shear and buoyancy*. MWR.
- **University of Wyoming:** *Department of Atmospheric Science Radiosonde Archive*.
