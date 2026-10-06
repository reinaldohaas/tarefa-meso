# Pacote `metpack`: Diagnóstico Termodinâmico e Cinemático de Mesoescala
**Disciplina:** Meteorologia de Mesoescala (FSC7116 - UFSC)  
**Autor:** Reinaldo Haas  
**Fundamentação Teórica:** Kerry Emanuel (1994, *Atmospheric Convection*, Oxford University Press) e MIT OpenCourseWare (12.811 - *Atmospheric Convection*).

---

## 0. Diretriz Didática para os Alunos (FSC7116 - UFSC)

### ⚠️ Requisito Obrigatório para Apresentação aos Previsores da Defesa Civil de SC (Orientação: Prof. Dr. Reinaldo Haas):
Cada aluno ou grupo de trabalho **DEVE ESCOLHER OBRIGATORIAMENTE TRÊS RADIOSSONDAGENS ATMOSFÉRICAS REAIS DISTINTAS**, contemplando os três estados fundamentais da troposfera:

1. **Atmosfera ESTÁVEL:** Perfil dominado por estratificação térmica estável, ar seco em altitude, CAPE baixo/nulo, estabilidade estática profunda ($N^2 > 0$) e ausência de convecção profunda. *(Exemplo: 12/12/1995)*.
2. **Atmosfera NEUTRA:** Perfil com umidade e equilíbrio convectivo, exibindo flutuabilidade moderada. *(Exemplo: 22/12/1995)*.
3. **Atmosfera INSTÁVEL:** Perfil com acúmulo de energia convectiva, vento intenso em baixos níveis, cisalhamento vertical profundo e helicidade relativa à tempestade ciclônica (SRH negativa no Hemisfério Sul com o vetor Bunkers Left-Mover). *(Exemplo: 24/12/1995)*.

> **Flexibilidade de Escolha:** As 3 sondagens podem ser da **mesma estação em datas diferentes** (como no nosso caso modelo de Porto Alegre - SBPA em dez/1995) **OU de estações e regiões geográficas diferentes** na América do Sul via Universidade de Wyoming.

---

## 1. Visão Geral e Mapeamento MATLAB/Fortran $\iff$ Python

Este pacote reúne rotinas para aquisição, processamento numérico, cálculo de flutuabilidade convectiva e visualização de radiossondagens da atmosfera. 

Todas as rotinas clássicas foram rigorosamente transpostas para **Python 3** moderno, garantindo compatibilidade numérica exata com os originais em MATLAB e Fortran:

| Rotina Original | Equivalente em Python | Função Principal |
| :--- | :--- | :--- |
| **`getsounding.m`** | **`getsounding.py`** | Baixa a radiossondagem da Universidade de Wyoming (endpoint moderno WSGI ou local) e gera `sounding.txt`, `header.txt` e `modsound.txt`. |
| **`wyoming.f`** | **`wyoming.py`** | Executa a ascensão de parcelas de Kerry Emanuel a cada 5 hPa, calculando CAPE Reversível ($T_\rho$), CAPE Pseudoadiabático ($T_v$), CIN e DCAPE. Gera `cape.out`, `tdifrev.out`, `tdifpseudo.out`, `p.out` e `porig.out`. |
| **`skewt.m`** | **`skewt.py`** | Gera o diagrama termodinâmico Skew-T / Log-P com adiabáticas secas ($\theta$), saturadas ($\theta_e$), isohígras ($q_s$) e perfil observado oblíquo. |
| **`tcon.m`** | **`tcon.py`** | Orquestra a execução de `wyoming.py`, plota o Skew-T e gera os mapas de contorno 2D `pcolor`/`contour` de anomalia de temperatura de densidade ($p_{\text{orig}} \times p_{\text{elevada}}$). |

---

## 2. Fundamentos Físico-Matemáticos de Kerry Emanuel (1994)

### 2.1. Temperatura Virtual ($T_v$) vs. Temperatura de Densidade ($T_\rho$)
Na aproximação pseudoadiabática clássica, assume-se que toda a água condensada precipita instantaneamente ($r_l = 0$):
$$T_v = T \left( \frac{1 + \frac{r_v}{\epsilon}}{1 + r_v} \right) \approx T(1 + 0.608\, r_v)$$

No entanto, Kerry Emanuel (1994, Seções 4.3 e 6.3) demonstra que na ascensão real a nuvem retém condensado. A **Temperatura de Densidade ($T_\rho$)** contabiliza o peso gravitacional da água líquida (*water loading*):
$$T_\rho = T \left( \frac{1 + \frac{r_v}{\epsilon}}{1 + r_t} \right) \approx T(1 + 0.608\, r_v - r_l - r_i)$$
onde $r_t$ é a razão de mistura de água total conservada ($r_t = r_{\text{origem}}$) e $r_l = r_t - r_{vs}(T, p)$.

### 2.2. Flutuabilidade e CAPE
$$B = g \left( \frac{T_{\rho, p} - T_{\rho, e}}{T_{\rho, e}} \right)$$

$$\text{CAPE} = \int_{p_{\text{EL}}}^{p_{\text{LFC}}} R_d (T_{\rho, p} - T_{\rho, e})\, d\ln p$$

Em ambientes tropicais ou subtropicais quentes e úmidos, o termo $-r_l$ (retenção de água líquida) reduz expressivamente a flutuabilidade e o CAPE efetivo em relação ao cálculo pseudoadiabático convencional. Todos os valores comparativos para as 3 sondagens são calculados dinamicamente e consolidados em `metricas.json`.

---

## 3. Instruções de Execução via Terminal (com `uv`)

Como o gerenciador `uv` gerencia o ambiente Python de forma isolada, não é necessário instalar compiladores nem configurar o PATH do Windows.

### Passo 3.1: Obter uma Sondagem (`getsounding.py`)
```powershell
cd C:\Users\haas\github\tarefa-meso\metpack
& "$HOME\.local\bin\uv.exe" run getsounding.py 83971 1995 12 24 12
```

### Passo 3.2: Processar a Termodinâmica de Emanuel (`wyoming.py`)
```powershell
& "$HOME\.local\bin\uv.exe" run wyoming.py
# Inspecione os resultados
Get-Content cape.out -Head 25
```

### Passo 3.3: Gerar os Gráficos 2D do `tcon.py` (Substituto de `tcon.m`)
```powershell
& "$HOME\.local\bin\uv.exe" run --with matplotlib tcon.py
# Visualize as figuras geradas
Start-Process tcon_1_skewt.png
Start-Process tcon_2_tdifrev.png
Start-Process tcon_3_tdifpseudo.png
Start-Process tcon_comparacao_emanuel.png
```

### Passo 3.4: Gerar as Figuras Científicas do Seminário (`generate_figures.py`)
Gera os gráficos de alta resolução baseados nas rotinas do Google Colab do Prof. Reinaldo Haas:
```powershell
cd C:\Users\haas\github\tarefa-meso
& "$HOME\.local\bin\uv.exe" run --with metpy --with pandas --with matplotlib generate_figures.py
```
Figuras geradas em `metpack/` (as marcadas "gerados pelo notebook" vêm do `Seminario_plot_sounding_revisado.ipynb`):
- `fig_sounding_1_estavel.png`, `fig_sounding_2_neutra.png`, `fig_sounding_3_instavel.png`: Skew-T + hodógrafo (com Bunkers LM/RM) + tabela de índices do MetPy, gerados pelo notebook.
- `fig_3_soundings_skewt.png`: Comparação das 3 sondagens (12/12 estável, 22/12 moderado, 24/12 severo).
- `fig_cap2_profiles.png`: Perfis verticais do Cap. 2 de Emanuel ($\theta/\theta_e/\theta_s$, Brunt-Väisälä $N$, estabilidade $S$, razão de mistura $r$) com topo em 200 hPa.
- `fig_kinematics_hodograph.png`: Hodógrafo polar com Bunkers Left-Mover e Right-Mover no Hemisfério Sul, cisalhamento 0–6 km e SRH 0–3 km.

### Passo 3.5: Gerar a Apresentação em PowerPoint (`generate_pptx.py`)
Gera o arquivo `apresentacao_meso.pptx` estritamente sincronizado com o roteiro de 20 minutos (10 slides) para apresentação aos previsores da Defesa Civil de SC:
```powershell
cd C:\Users\haas\github\tarefa-meso
& "$HOME\.local\bin\uv.exe" run --with python-pptx generate_pptx.py
Start-Process apresentacao_meso.pptx
```

---

## 4. Estrutura dos Arquivos de Saída

* **`apresentacao_meso.pptx`**: Apresentação oficial completa em formato PowerPoint (16:9 widescreen, 10 slides, figuras embutidas, roteiro cronometrado e script falado completo nas notas do orador).
* **`cape.out`**: Tabela com as 20 camadas de origem na baixa troposfera, contendo PA reversível, PA pseudoadiabático, NA (CIN), CAPE reversível, CAPE pseudoadiabático e DCAPE.
* **`p.out`**: Vetor com os níveis de pressão verticais interpolados a cada 5 hPa.
* **`porig.out`**: Vetor com os níveis de pressão de origem da parcela.
* **`tdifrev.out`**: Matriz 2D de anomalias térmicas reversíveis ($\Delta T_\rho$ em K) para cada par $(p_{\text{origem}}, p_{\text{elevada}})$.
* **`tdifpseudo.out`**: Matriz 2D de anomalias térmicas pseudoadiabáticas ($\Delta T_v$ em K).
* **`modsound.txt`**: Perfil tratado da sondagem ($P$, $T$, $RH$).

