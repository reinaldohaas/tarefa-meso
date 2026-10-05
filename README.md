# 🌪️ Tarefa de Meteorologia de Mesoescala: Diagnóstico Tríplice & Análise Termodinâmica Avançada

**Docente:** Prof. Dr. Reinaldo Haas  
**Instituição:** Universidade Federal de Santa Catarina (UFSC)  
**Projeto:** Diagnóstico Físico e Termodinâmico de Mesoescala (Kerry Emanuel, 1994)  

---

## 📌 Visão Geral do Projeto
Este repositório contém a infraestrutura computacional completa para análise de radiossondagens, perfis termodinâmicos verticais, matrizes bidimensionais de anomalia de temperatura de densidade ($T_\rho$, Emanuel 1994), dinâmica de cisalhamento/hodógrafo e forçamento sinótico de mesoescala.

O projeto diagnostica **três regimes atmosféricos distintos**:
1. **Atmosfera ESTÁVEL (Pós-frontal / Anticiclônica):** 12/12/1995 12Z (SBPA) — $\text{CAPE} = 0\text{ J/kg}$, forte estratificação com $N > 0$.
2. **Atmosfera NEUTRA / TRANSIÇÃO:** 23/12/1995 12Z (SBPA) — Umidade em baixos níveis, fraca inibição, $\text{CAPE} = 566\text{ J/kg}$.
3. **Atmosfera INSTÁVEL (Convecção Severa / Supercélula HP):** 24/12/1995 12Z (SBPA) — $\text{MUCAPE} = 4646\text{ J/kg}$, *capping lid* em 925 hPa, JBN com 44 nós ($23.2\text{ m/s}$), cisalhamento 0-6 km de $28.7\text{ m/s}$ e $\text{SRH } 0-3\text{ km} = 245\text{ m}^2/\text{s}^2$.

---

## 🚀 Recursos Principais
- 📊 **[Dashboard Web Interativo (GitHub Pages)](index.html):** Painel interativo com Skew-T, hodógrafo polar dinâmico, perfis de $\theta/\theta_e/\theta_s/N/S/r$, matrizes 2D de Emanuel e comparação tríplice das 3 sondagens lado a lado.
- 🎓 **[Roteiro Completo do Estudante](ROTEIRO_ESTUDANTES.md):** Guia detalhado passo a passo cobrindo como escolher as 3 sondagens, como extrair dados de Wyoming (evitando erros de Fortran/html2text), execução no Google Colab / Python local e estrutura cronometrada para **ambas as apresentações**.
- 📥 **[Apresentação Oficial PPTX (apresentacao_meso.pptx)](apresentacao_meso.pptx):** 10 slides em 16:9 widescreen sincronizados com o tempo de 20 minutos de defesa perante a banca examinadora, incluindo figuras científicas em alta resolução e **notas de orador com script falado** em cada slide.
- 🐍 **Pacote `metpack/`:**
  - `wyoming.py`: Download e raspagem limpa de sondagens com cálculo de Emanuel (1994).
  - `tcon.py`: Geração dos gráficos de contorno de diferenças térmicas de densidade ($T_\rho$).
  - `generate_figures.py`: Geração das cartas de reanálise sinótica com fronteiras em Cartopy, comparações de perfis e hodógrafos.

---

## 🛠️ Como Executar com `uv`

```powershell
# 1. Executar as matrizes de Emanuel para as 3 sondagens
uv run --with matplotlib --with numpy metpack/tcon.py

# 2. Gerar todas as figuras científicas e cartas sinóticas
uv run --with metpy --with cartopy --with matplotlib --with numpy generate_figures.py

# 3. Gerar a apresentação em PowerPoint (10 slides / 20 min)
uv run --with python-pptx generate_pptx.py

# 4. Atualizar o dashboard web (index.html)
uv run build_index_html.py
```

---

## 👥 Autoria e Licença
Desenvolvido para fins didáticos e científicos para o curso de Meteorologia da UFSC.
