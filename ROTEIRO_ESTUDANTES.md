# 🎓 Roteiro Completo do Estudante: Laboratório e Defesa Oral de Mesoescala

**Disciplina:** Meteorologia de Mesoescala  
**Docente:** Prof. Dr. Reinaldo Haas  
**Instituição:** Universidade Federal de Santa Catarina (UFSC)  
**Repositório Base:** [tarefa-meso](https://github.com/haasreinaldo/tarefa-meso)  

---

## 📋 Sumário Executivo
Este documento orienta os estudantes no cumprimento integral da tarefa de mesoescala. O trabalho consiste em diagnosticar **três regimes atmosféricos distintos** (Estável, Neutro e Instável) a partir de dados reais de radiossondagem, processar as variáveis termodinâmicas e cinemáticas clássicas e avançadas (algoritmo de Kerry Emanuel, 1994), e produzir **duas apresentações complementares**:

1. **Apresentação 1 (Laboratório e Diagnóstico Físico):** Foco em metodologia de extração de dados, reprodução do código no Google Colab / Python local, geração e interpretação detalhada de todos os perfis verticais ($\theta, \theta_e, \theta_s, N, S, r, PW$), diagramas Skew-T, hodógrafos e matrizes 2D de Emanuel.
2. **Apresentação 2 (Defesa Oral de 20 Minutos perante a Banca):** Apresentação formal de síntese científica (10 slides em formato 16:9 widescreen), rigorosamente cronometrada, com cartas de reanálise sinótica em Cartopy com limites geopolíticos reais, acoplamento de mesoescala, suporte de cisalhamento do JBN e classificação do modo convectivo.

---

## 1. 🎯 Requisito Fundamental: As Três Radiossondagens
Cada aluno ou dupla deve selecionar e analisar **três radiossondagens obrigatoriamente distintas** (em datas e/ou localidades diferentes):

| Regime Atmosférico | Assinatura Termodinâmica Típica | Comportamento Físico Esperado | Exemplo de Referência (SBPA) |
| :--- | :--- | :--- | :--- |
| **1. Atmosfera ESTÁVEL** | Inversão térmica acentuada na baixa troposfera; ar seco em altitude; $\partial \theta_e / \partial z > 0$; $\text{CAPE} = 0\text{ J/kg}$. | Subsidência anticiclônica ou pós-frontal; ausência de convecção profunda; estratificação laminar estável ($N > 0$). | `12/12/1995 12Z` (Pós-frontal polar) |
| **2. Atmosfera NEUTRA / TRANSIÇÃO** | Camada limite úmida e bem misturada; fraca inibição convectiva ($\text{CIN} \sim 0$); $\text{CAPE}$ baixo a moderado ($200 \text{ a } 800\text{ J/kg}$). | Equilíbrio convectivo ou nebulosidade estratocumuliforme; ausência de forçamento dinâmico vigoroso; cisalhamento vertical fraco. | `23/12/1995 12Z` (Pré-evento / Transição) |
| **3. Atmosfera INSTÁVEL (Severa)** | Camada limite quente e muito úmida; forte inversão de subsidência (*capping lid*) em baixos níveis (ex: 925–850 hPa); decréscimo abrupto de $\theta_e$ ($\partial \theta_e / \partial z \ll 0$); $\text{MUCAPE} > 2500 - 4500\text{ J/kg}$; $\text{CIN} \sim -50 \text{ a } -150\text{ J/kg}$. | Convecção profunda explosiva quando o gatilho sinótico/mesoescala rompe a tampa; tempestades severas, supercélulas e rajadas descendentes. | `24/12/1995 12Z` (Supercélula HP / Véspera de Natal) |

---

## 2. 🌐 Obtenção e Tratamento dos Dados da Universidade de Wyoming

### 2.1. Estrutura da URL de Consulta
As sondagens são extraídas do arquivo da Universidade de Wyoming via requisição HTTP:
```text
http://weather.uwyo.edu/cgi-bin/sounding?region=samer&TYPE=TEXT%3ALIST&YEAR=YYYY&MONTH=MM&FROM=DDHH&TO=DDHH&STNM=ESTACAO
```
Exemplo para Porto Alegre (SBPA / Estação 87576) em 24/12/1995 12Z:
```text
http://weather.uwyo.edu/cgi-bin/sounding?region=samer&TYPE=TEXT%3ALIST&YEAR=1995&MONTH=12&FROM=2412&TO=2412&STNM=87576
```

### 2.2. Armadilha Clássica e Erro no Fortran
Um erro recorrente observado no Google Colab ocorre quando o aluno tenta converter o HTML bruto para texto usando `html2text` e submeter diretamente ao programa Fortran `wyoming.f`:
```bash
! cat sounding.htm | html2text -o sounding.txt
```
**Causa da Falha:** O utilitário `html2text` preserva cabeçalhos, rodapés, tags não tratadas e formatações de tabela que desalinham as colunas. O leitor `wyoming.f` utiliza leitura formatada em ponto fixo (`READ(11, *)` ou formato rígido). Ao encontrar um caractere alfabético onde esperava um inteiro ou real, o compilador aborta com o erro:
```text
At line 93 of file wyoming.f (unit = 11, file = 'sounding.txt')
Fortran runtime error: Bad integer for item 3 in list input
```

### 2.3. Solução Recomendada: Script Python Nativo (`wyoming.py`)
Para evitar erros de compilação Fortran e dependências externas, utilize o script nativo em Python (`wyoming.py`), que realiza o download da página, extrai os blocos delimitados por `<PRE>...</PRE>` e limpa os dados automaticamente:
```bash
# Execução direta via uv ou python
python metpack/wyoming.py
```
O script gera arquivos tabulados consistentes (`sounding.txt` ou com prefixos de data `YYYYMMDD_modsound.txt`), prontos para processamento.

---

## 3. ⚙️ Execução Prática do Ambiente Computacional

### 3.1. Opção A: Execução no Google Colab
1. Abra o notebook de referência da disciplina: [Google Colab de Mesoescala](https://colab.research.google.com/drive/1JumiIUyt3lyDhfuA0EtSB3hAlkS3lSUA?usp=sharing).
2. Execute as células sequencialmente para instalar o `MetPy` e bibliotecas auxiliares (`cartopy`, `matplotlib`, `numpy`).
3. Substitua os parâmetros de data (`YEAR`, `MONTH`, `FROM`, `TO`, `STNM`) para cada uma das suas 3 sondagens selecionadas.
4. Execute as rotinas de cálculo para extrair os índices e perfis de cada uma das 3 atmosferas.

### 3.2. Opção B: Execução Local com `uv` (Recomendada)
O gerenciador de ambientes [uv](https://github.com/astral-sh/uv) permite rodar os scripts sem conflitos de dependências:
```powershell
# 1. Clonar o repositório
git clone https://github.com/haasreinaldo/tarefa-meso.git
cd tarefa-meso

# 2. Gerar as matrizes 2D de Emanuel (tcon.py)
uv run --with matplotlib --with numpy metpack/tcon.py

# 3. Gerar todas as figuras científicas e comparações
uv run --with metpy --with cartopy --with matplotlib --with numpy generate_figures.py

# 4. Gerar a apresentação em PowerPoint
uv run --with python-pptx generate_pptx.py

# 5. Compilar o dashboard web interativo
uv run build_index_html.py
```

---

## 4. 🔬 Estrutura da Apresentação 1: Laboratório e Diagnóstico Físico
*Objetivo:* Apresentar a memória de cálculo completa, a integridade dos dados e a análise detalhada de todos os perfis verticais e variáveis do Colab.

### Seções Obrigatórias da Apresentação 1:
1. **Identificação e Contextualização das Estações Escolhidas:**
   - Coordenadas geográficas, elevação da estação, horários sinóticos (00Z ou 12Z).
2. **Metodologia de Download e Limpeza de Dados:**
   - Detalhar como os dados foram extraídos e normalizados.
3. **Diagramas Termodinâmicos Skew-T / Log-P (para as 3 Sondagens):**
   - Curvas de temperatura do ar ($T$), ponto de orvalho ($T_d$) e trajetória da parcela.
   - Identificação visual dos níveis característicos: NCL (LCL), NLC (LFC) e NE (EL).
4. **Perfis Verticais Completos de Estabilidade:**
   - **Temperaturas Potenciais:** $\theta$ (seca), $\theta_e$ (equivalente) e $\theta_s$ (saturação). Mostrar onde ocorre $\partial \theta_e / \partial z < 0$ (instabilidade potencial/convectiva).
   - **Frequência de Brunt-Väisälä ($N$ e $N^2$):** Identificar inversões térmicas e camadas de alta estabilidade estática que atuam como *capping lid*.
   - **Cisalhamento Vertical ($S = |\partial \vec{V} / \partial z|$):** Camadas com forte cisalhamento cinemático.
5. **Perfis de Umidade e Conteúdo de Água:**
   - Razão de mistura ($r$, $\text{g/kg}$) ao longo da troposfera.
   - Água Precipitável Total ($PW$, $\text{mm}$).
   - Potencial de Correntes Descendentes ($DCAPE$, $\text{J/kg}$) e risco de *microbursts*.
6. **Matrizes 2D de Kerry Emanuel (1994):**
   - Comparação entre o modo **Reversível** (com retenção de água líquida $r_l$) e o modo **Pseudoadiabático** (com precipitação instantânea de todo o condensado).
   - Análise da diferença de temperatura de densidade ($\Delta T_\rho$) e impacto no CAPE efetivo.

---

## 5. ⏱️ Estrutura da Apresentação 2: Defesa Oral de 20 Minutos perante a Banca
*Objetivo:* Defesa formal de 20 minutos (10 slides em proporção 16:9), focada na síntese física, forçamento de mesoescala e conclusões científicas.

### Tabela de Cronometragem Slide a Slide:
| Slide | Minutagem | Título do Slide | Foco Conceitual & Script do Orador | Figura Associada |
| :---: | :---: | :--- | :--- | :--- |
| **01** | `00:00 - 01:30` | **Título & Objetivos da Investigação** | Contextualizar a investigação dos três regimes atmosféricos; enunciar a relevância da previsão de tempestades severas e a aplicação das teorias de Kerry Emanuel. | Slide de capa institucional |
| **02** | `01:30 - 03:30` | **Forçamento Sinótico & Suporte de Mesoescala** | Analisar o suporte dinâmico em 500 hPa (cavado baroclínico e advecção de vorticidade ciclônica) e 850 hPa (Jato em Baixos Níveis transportando calor e umidade da Amazônia). Destacar as fronteiras reais no mapa Cartopy. | `fig_synoptic_analysis.png` |
| **03** | `03:30 - 05:30` | **Tríplice Diagnóstico: Estável vs. Neutra vs. Instável** | Comparar os três perfis Skew-T lado a lado. Contrastar a subsidência seca do caso estável com a saturação quase neutra e a tremenda área de instabilidade do caso severo. | `fig_3_soundings_complete_analysis.png` |
| **04** | `05:30 - 07:30` | **Balanço Energético: CAPE vs. CIN nos Três Regimes** | Demonstrar que a convecção não depende apenas de CAPE elevado, mas do equilíbrio com a inibição convectiva ($\text{CIN}$). Mostrar como o $\text{CIN}$ conteve a energia até o momento do disparo explosivo. | Tabela comparativa e perfis |
| **05** | `07:30 - 10:00` | **Termodinâmica Avançada de Emanuel: Matrizes 2D e $T_\rho$** | Explicar o código de Kerry Emanuel (1994). Demonstrar que a inclusão do carregamento de hidrometeoros no modo reversível reduz a flutuabilidade real em relação ao cálculo pseudoadiabático tradicional. | `fig_3_soundings_emanuel_matrices.png` |
| **06** | `10:00 - 12:30` | **Perfis Verticais de Estabilidade ($\theta, \theta_e, \theta_s, N, S$)** | Analisar o pico de Brunt-Väisälä ($N$) em 925 hPa no caso severo (a tampa protetora), o decréscimo drástico de $\theta_e$ com a altitude e o forte cisalhamento cinemático nos primeiros 3 km. | `fig_3_soundings_profiles_comparison.png` |
| **07** | `12:30 - 14:30` | **Diagnóstico de Umidade, Água Precipitável e DCAPE** | Avaliar a razão de mistura ($r = 16.4\text{ g/kg}$), o conteúdo de água precipitável ($PW = 50.8\text{ mm}$) e o $DCAPE = 1149\text{ J/kg}$, alertando para o altíssimo potencial de rajadas destrutivas (*downbursts*). | Perfis de umidade e métricas |
| **08** | `14:30 - 17:00` | **Cinemática: Hodógrafo, JBN e Helicidade (SRH)** | Apresentar o hodógrafo em espiral; caracterizar o núcleo do JBN em 925 hPa ($44\text{ nós} \approx 23.2\text{ m/s}$), o cisalhamento vertical 0-6 km ($28.7\text{ m/s}$) e a helicidade $0-3\text{ km} = 245\text{ m}^2/\text{s}^2$, provando o suporte à supercélula rotatória. | `fig_kinematics_hodograph.png` |
| **09** | `17:00 - 19:00` | **Monitoramento por Satélite: Imagem Infravermelho (IR 11 µm)** | Apresentar a comprovação observacional via GOES-8 / NOAA ISCCP-H CDR em 24/12/1995. Painel A (12Z síncrono com a sondagem SBPA) com topos a -59°C (170 hPa) e Painel B (18Z auge da convecção) com topos penetrantes a -63.5°C (160 hPa) associados à histórica Enchente de Natal. | `fig_sat_ir_19951224.png` |
| **10** | `19:00 - 20:00` | **Conclusões Finais & Abertura para a Banca** | Recapitular as conclusões principais, agradecer à atenção da banca e colocar-se formalmente à disposição para a sessão de arguição. | Slide final de encerramento |

---

## 6. 🧠 Perguntas Típicas da Banca e Como Responder

### Pergunta 1: *"Por que o CAPE no modo reversível de Kerry Emanuel é significativamente menor que no modo pseudoadiabático tradicional?"*
> **Resposta do Aluno:**  
> "No processo pseudoadiabático clássico, assume-se que toda a água condensada precipita instantaneamente ($r_l = 0$), permitindo que a parcela atinja sua flutuabilidade máxima puramente em função da temperatura virtual ($T_v$). No entanto, Kerry Emanuel (1994, Cap. 4 e 6) modela a termodinâmica reversível com a conservação estrita da entropia úmida total, onde os hidrometeoros condensados permanecem suspensos na parcela ascendente. A presença dessa água líquida adiciona uma carga gravitacional de arrasto (termo $-r_l$ na aceleração vertical de flutuabilidade), reduzindo a temperatura de densidade da parcela ($T_\rho = T_v (1 - r_l)$). Consequentemente, a aceleração líquida para cima diminui, resultando em um CAPE reversível significativamente menor (ex: 2821 J/kg reversível vs. 4646 J/kg pseudoadiabático no nosso caso severo)."

---

### Pergunta 2: *"Qual foi o papel do pico da frequência de Brunt-Väisälä ($N$) em 925 hPa no caso severo?"*
> **Resposta do Aluno:**  
> "O pico de Brunt-Väisälä ($N \approx 0.025\text{ s}^{-1}$) em 925 hPa marca uma camada de altíssima estabilidade estática local, associada à inversão térmica da camada limite (*capping lid*). Esse estrato impediu a liberação prematura de convecção desorganizada durante a manhã, permitindo que a advecção de calor e umidade promovida pelo Jato em Baixos Níveis (JBN) acumulasse energia termodinâmica gigantesca abaixo da tampa. Quando o forçamento dinâmico de grande escala e o aquecimento superficial finalmente romperam essa tampa, a liberação de energia foi violenta e explosiva."

---

### Pergunta 3: *"Por que um cisalhamento 0-6 km de 28.7 m/s e um SRH 0-3 km de 245 m²/s² indicam tempestade supercelular em vez de multicélulas comuns?"*
> **Resposta do Aluno:**  
> "Valores de cisalhamento bulk profundo (0-6 km) acima de $20\text{ m/s}$ são a condição fundamental para inclinar a corrente ascendente, separando-a fisicamente da corrente descendente resfriada pela chuva e impedindo que o *downdraft* destrua a própria tempestade. Adicionalmente, a helicidade relativa à tempestade (SRH 0-3 km) de $245\text{ m}^2/\text{s}^2$, combinada com a curvatura no sentido horário visível no hodógrafo entre a superfície e 3 km, gera forte vorticidade horizontal na baixa troposfera. À medida que o *updraft* ingere essa vorticidade horizontal, ela é basculada (*tilting*) para o eixo vertical, gerando um mesociclone em rotação persistente, característico inequívoco de supercélulas."

---

## 7. 📦 Recursos Prontos Disponíveis no Repositório
- **Apresentação PPTX Formatada:** [`apresentacao_meso.pptx`](apresentacao_meso.pptx) (10 slides 16:9 widescreen com figuras científicas de alta resolução e notas de orador completas embutidas).
- **Dashboard Web Interativo:** [`index.html`](index.html) (visualização comparativa das 3 sondagens, Skew-T interativo, perfis verticais, matrizes de Emanuel e hodógrafo).
- **Scripts de Processamento:**
  - `metpack/wyoming.py`: Download e raspagem limpa de dados de sondagem.
  - `metpack/tcon.py`: Geração dos gráficos de contorno de diferenças térmicas de Emanuel.
  - `metpack/plot_sat_ir.py`: Geração da figura de satélite infravermelho realçado (IR 11 µm) a partir dos dados do NOAA ISCCP-H / GOES-8.
  - `generate_figures.py`: Geração das figuras comparativas, mapas Cartopy e hodógrafos.
  - `generate_pptx.py`: Script gerador do arquivo PowerPoint oficial.
