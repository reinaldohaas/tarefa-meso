# 🎓 Roteiro Completo do Estudante: Laboratório e Defesa Oral de Mesoescala

**Disciplina:** Meteorologia de Mesoescala (FSC7116)  
**Docente:** Prof. Dr. Reinaldo Haas  
**Instituição:** Universidade Federal de Santa Catarina (UFSC)  
**Repositório Base:** [tarefa-meso](https://github.com/reinaldohaas/tarefa-meso)  

---

## 📋 Sumário Executivo
Este documento orienta os estudantes no cumprimento integral da tarefa de meteorologia de mesoescala. O trabalho consiste em diagnosticar **três regimes atmosféricos distintos** (Estável, Neutro e Instável) a partir de **três radiossondagens reais escolhidas pelo próprio aluno ou dupla**, processar as variáveis termodinâmicas e cinemáticas clássicas e avançadas (algoritmo de Kerry Emanuel, 1994), e produzir **duas apresentações complementares**:

1. **Apresentação 1 (Laboratório e Diagnóstico Físico):** Foco em metodologia de extração e controle de qualidade dos dados, reprodução do código no Google Colab / Python local, geração e interpretação detalhada de todos os perfis verticais ($\theta, \theta_e, \theta_s, N, S, r, PW$), diagramas Skew-T, hodógrafos e matrizes 2D de Emanuel.
2. **Apresentação 2 (Defesa Oral de 20 Minutos perante os Previsores da Defesa Civil de SC):** Apresentação formal de síntese diagnóstica e operacional (10 slides em formato 16:9 widescreen sob orientação do Prof. Dr. Reinaldo Haas), rigorosamente cronometrada, com acoplamento dinâmico, suporte de cisalhamento em baixos níveis e balanço termodinâmico.

> **Importante (Integridade dos Dados):** Todos os valores citados devem sair da execução do notebook (ou do MATLAB) com as SUAS três sondagens: saídas das células e o arquivo `metpack/metricas_notebook.json` gerado na sua execução. O `metpack/metricas.json` do repositório contém apenas os valores do exemplo do tutorial. É proibido inventar valores ou copiar os do exemplo.

---

## 1. 🎯 Requisito Fundamental: As Três Radiossondagens
Os casos de Porto Alegre (SBPA 83971) em 12/12, 22/12 e 24/12/1995 são apenas o **exemplo resolvido** do tutorial.
**Cada aluno ou dupla deve trocar as três sondagens**, escolhendo:
- **datas e/ou estações próprias**, diferentes das do exemplo e das dos colegas (combine a escolha com o professor);
- **uma sondagem para cada regime** (estável, neutro e instável), justificando a classificação com os índices calculados;
- presumivelmente, a sondagem **instável** é a mais próxima (no tempo e no espaço) do evento severo escolhido para o trabalho de fim de curso; as sondagens estável e neutra servem de contraste;
- estações disponíveis no arquivo da Universidade de Wyoming (código WMO de 5 dígitos, por exemplo 83971 Porto Alegre, 83899 Florianópolis, 83840 Curitiba), nos horários 00Z ou 12Z, conferindo antes no site que a sondagem existe.

| Regime Atmosférico | Assinatura Termodinâmica Típica | Comportamento Físico Esperado | Exemplo do tutorial (SBPA 83971), não reutilizar |
| :--- | :--- | :--- | :--- |
| **1. Atmosfera ESTÁVEL** | Inversão térmica ou isotermia em baixos níveis; ar seco na média troposfera; estratificação estável com $N > 0$; $\text{SBCAPE} < 50\text{ J/kg}$. | Estratificação térmica e hidrostática estável; ausência de convecção profunda. | `12/12/1995 12Z`<br>($\text{SBCAPE} = 15.7\text{ J/kg}$, $\text{MUCAPE} = 0.9\text{ J/kg}$, $\text{PW} = 35.1\text{ mm}$) |
| **2. Atmosfera NEUTRA** | Camada limite com umidade moderada; fraca flutuabilidade; cisalhamento e convergência fracos. | Transição convectiva; umedecimento progressivo da troposfera. | `22/12/1995 12Z`<br>($\text{SBCAPE} = 836.0\text{ J/kg}$, $\text{MUCAPE} = 836.0\text{ J/kg}$, $\text{SBCIN} = -221.8\text{ J/kg}$, $\text{PW} = 43.9\text{ mm}$, Shear 0–6 km = $2.8\text{ m/s}$) |
| **3. Atmosfera INSTÁVEL** | Camada limite quente e úmida; forte gradiente vertical de $\theta_e$ ($\partial \theta_e / \partial z < 0$); elevado CAPE; vento intenso em baixos níveis e suporte cinemático. | Potencial para convecção profunda e tempestades severas. | `24/12/1995 12Z`<br>Sondagem Completa (Oficial): $\text{MUCAPE} = 7810.0\text{ J/kg}$, $\text{SBCAPE} = 1861.9\text{ J/kg}$<br>Teste de Sensibilidade: $\text{MUCAPE} = 1860.1\text{ J/kg}$ (sem os níveis próximos a 925 hPa)<br>Vento 925 hPa: $43.9\text{ kt}$ ($22.6\text{ m/s}$) de $060^\circ$<br>Shear 0–6 km: $12.6\text{ m/s}$ ($24.5\text{ kt}$)<br>SRH 0–3 km (LM): $-123.3\text{ m}^2/\text{s}^2$ |

---

## 2. 🌐 Obtenção e Tratamento dos Dados da Universidade de Wyoming

### 2.1. Estrutura da URL de Consulta e Servidor WSGI
As sondagens completas com a tabela vertical de variáveis e o bloco oficial de índices termodinâmicos ("Station information and sounding indices") são extraídas do servidor WSGI da Universidade de Wyoming:
- **Tabela Vertical da Sondagem (`TEXT:LIST`):**
  ```text
  https://weather.uwyo.edu/wsgi/sounding?datetime=YYYY-MM-DD%20HH:00:00&id=ESTACAO&type=TEXT:LIST
  ```
- **Índices Oficiais de Diagnóstico (`INDICES`):**
  ```text
  https://weather.uwyo.edu/wsgi/sounding?datetime=YYYY-MM-DD%20HH:00:00&id=ESTACAO&type=INDICES&src=FM35
  ```
Exemplo para Porto Alegre (SBPA / Estação 83971) em 24/12/1995 12Z:
```text
https://weather.uwyo.edu/wsgi/sounding?datetime=1995-12-24%2012:00:00&id=83971&type=TEXT:LIST
```

### 2.2. Entrada do Fortran `wyoming.f` e Formatação Rígida
O código clássico `metpack/wyoming.f` de Kerry Emanuel (1994) requer um formato de entrada estrito:
1. **Cabeçalho:** Exatamente 10 linhas iniciais de cabeçalho (que o programa descarta com `READ(11, *)` em loop até a linha 10).
2. **Formato das Colunas:** As linhas de dados subsequentes são lidas sob o formato estrito:
   ```fortran
   READ(11, 10, END=20) P, T, TD
   10 FORMAT(1X, F6.1, 9X, F5.1, 2X, F5.1)
   ```
   onde:
   - `1X, F6.1`: Pressão ($P$, em hPa) ocupando as primeiras 7 colunas;
   - `9X, F5.1`: Pula 9 colunas e lê a Temperatura ($T$, em °C);
   - `2X, F5.1`: Pula 2 colunas e lê a Temperatura do Ponto de Orvalho ($T_d$, em °C).
Um erro clássico ocorre ao passar o HTML bruto ou saídas do `html2text`, que quebram o alinhamento de colunas, causando erro de execução no Fortran (`Bad integer/real for item in list input`). O script `metpack/prepare_soundings.py` gera exatamente o arquivo no formato que o `wyoming.f` espera.

### 2.3. Porte Python Nativo (`metpack/wyoming.py`)
Para executar os algoritmos de Emanuel (1994) em Python puro no Google Colab ou terminal, utilize o script `metpack/wyoming.py`:
- Suporta o corte térmico de segurança `corte=None|-4.0` documentado para reproduzir o original `TRDBAR/TPDBAR = MAX(valor, -4.0)`;
- Calcula as matrizes de anomalia térmica de densidade ($T_\rho$, `tdifrev.out`) e flutuabilidade pseudoadiabática ($T_v$, `tdifpseudo.out`);
- A comparação coluna a coluna (`cape.out`) e célula a célula com o `wyoming.f` compilado em gfortran atesta concordância quase perfeita (diferença máxima de CAPE $\le 0.6\text{ J/kg}$ e de matriz $\le 0.0020\text{ K}$).
```bash
python metpack/wyoming.py
```

---

## 3. ⚙️ Execução Prática do Ambiente Computacional

### 3.1. Opção A: Execução no Google Colab
1. Abra o notebook oficial da disciplina: [Seminario_plot_sounding_revisado.ipynb](https://colab.research.google.com/github/reinaldohaas/tarefa-meso/blob/master/Seminario_plot_sounding_revisado.ipynb).
2. Execute as células sequencialmente para instalar o `metpy` e `siphon` e compilar o modelo de Kerry Emanuel (`wyoming.f`).
3. Na célula `CASOS`, troque estação e data pelas suas três sondagens:
   ```python
   CASOS = [
       dict(regime='ESTÁVEL',  station='XXXXX', date=datetime(AAAA, MM, DD, HH), src='FM35'),
       dict(regime='NEUTRA',   station='XXXXX', date=datetime(AAAA, MM, DD, HH), src='FM35'),
       dict(regime='INSTÁVEL', station='XXXXX', date=datetime(AAAA, MM, DD, HH), src='FM35'),
   ]
   ```
   As cópias de reserva em `metpack/` existem só para o exemplo; para as suas datas o notebook precisa de internet (Siphon/Wyoming). Confira no site do Wyoming o valor de `src` disponível para a sua data.
4. Execute as rotinas de cálculo para gerar as tabelas comparativas (MetPy vs. Wyoming), diagramas Skew-T, perfis até 200 hPa e matrizes de flutuabilidade de Emanuel.

### 3.2. Opção B: Execução Local com `uv` (Recomendada)
O gerenciador de ambientes [uv](https://github.com/astral-sh/uv) permite rodar os scripts sem conflitos de dependências:
```powershell
# 0. Executar o notebook com as suas sondagens (grava figuras e metpack/metricas_notebook.json; precisa do gfortran)
uv run --with metpy --with siphon --with requests --with matplotlib --with nbconvert --with ipykernel jupyter nbconvert --to notebook --execute --inplace Seminario_plot_sounding_revisado.ipynb

# 1. Montar metpack/metricas.json com os valores do notebook
uv run --with metpy --with pandas --with numpy python metpack/calc_metricas.py

# 2. Figuras complementares (painel triplo, Cap. 2, hodógrafo com Bunkers LM/RM)
uv run --with metpy --with cartopy --with matplotlib --with numpy python generate_figures.py

# 3. Gerar a apresentação em PowerPoint (10 slides)
uv run --with python-pptx python generate_pptx.py

# 4. Compilar o tutorial web (index.html)
uv run python build_index_html.py
```

### 3.3. Opção C: MATLAB Online (programas originais de Kerry Emanuel)
Os programas em MATLAB de Kerry Emanuel ([texmex.mit.edu/pub/emanuel/soundings](https://texmex.mit.edu/pub/emanuel/soundings/): `getsounding.m`, `skewt.m`, `tcon.m`, `wyoming.f` e `instructions.pdf`) foram adaptados em `metpack/` para a interface atual do Wyoming:

| Original (Emanuel) | Adaptado em `metpack/` | O que muda |
| :--- | :--- | :--- |
| `getsounding.m` | `getsounding_wyoming.m` | Usa o endereço atual (`wsgi`), lê as colunas pela posição do cabeçalho, converte o vento SPED (m/s) para nós e grava o `sounding.txt` no formato lido pelo `wyoming.f`. Sem internet, usa a cópia local `sounding_AAAAMMDD_HHZ.txt`. |
| `tcon.m` | `tcon_emanuel.m` | Compila o `wyoming.f` (gfortran), roda e desenha as matrizes reversível e pseudoadiabática lado a lado, na mesma escala, sem o piso artificial de −4 K. |
| `skewt.m` | `skewt.m` (sem mudança) | `skewt(p, T, UR/100)`. |
| — | `tarefa_sondagens.m` | Script principal: roda as três sondagens de `CASOS`. |

Passos no [MATLAB Online](https://matlab.mathworks.com) (é preciso uma conta MathWorks):
1. Envie a pasta `metpack/` do repositório para o MATLAB Drive (Upload) e abra `metpack/tarefa_sondagens.m`.
2. Em `CASOS`, troque estação e data pelas suas três sondagens (o exemplo é Porto Alegre, dezembro de 1995):
   ```matlab
   CASOS = {
       'ESTÁVEL',    XXXXX,    [AAAA MM DD HH];
       'NEUTRA',     XXXXX,    [AAAA MM DD HH];
       'INSTÁVEL',   XXXXX,    [AAAA MM DD HH];
   };
   ```
3. Clique em **Run**. Para cada caso saem o Skew-T de Emanuel e as matrizes de flutuabilidade; no Command Window aparecem a fonte dos dados e as CAPE reversível e pseudoadiabática (superfície e máxima).
4. Se o MATLAB Online não tiver compilador Fortran (`gfortran`), o `tcon_emanuel.m` avisa. Nesse caso, rode o notebook (Opção A) com as mesmas sondagens e copie para a pasta `emanuel_AAAAMMDD_HH` de cada caso os arquivos `p.out`, `porig.out`, `tdifrev.out`, `tdifpseudo.out` e `cape.out`; ao rodar de novo, o MATLAB usa esses arquivos.

Os valores de CAPE de Emanuel obtidos pelo MATLAB devem ser iguais aos do notebook para as mesmas sondagens (é o mesmo `wyoming.f` com a mesma entrada); confira e comente qualquer diferença.

---

## 4. 🔬 Estrutura da Apresentação 1: Laboratório e Diagnóstico Físico
*Objetivo:* Apresentar a memória de cálculo completa, a integridade dos dados e a análise detalhada de todos os perfis verticais e variáveis do Colab.

### Seções Obrigatórias da Apresentação 1:
1. **Identificação e Contextualização das Estações Escolhidas:**
   - Coordenadas geográficas, elevação da estação, horários sinóticos (00Z ou 12Z).
2. **Metodologia de Download, Limpeza e Controle de Qualidade (QC):**
   - Detalhar como os dados foram extraídos e normalizados.
   - Apresentar a verificação de inconsistências físicas (gradientes superadiabáticos $\Gamma > 9.8\text{ K/km}$, saltos abruptos de $\theta_e$).
3. **Diagramas Termodinâmicos Skew-T / Log-P (para as 3 Sondagens):**
   - Curvas de temperatura do ar ($T$), ponto de orvalho ($T_d$) e trajetória da parcela.
   - Identificação dos níveis característicos: LCL, LFC e EL.
4. **Perfis Verticais Completos de Estabilidade (até 200 hPa):**
   - **Temperaturas Potenciais:** $\theta$ (seca), $\theta_e$ (equivalente) e $\theta_s$ (saturação). Identificar camadas com $\partial \theta_e / \partial z < 0$ (instabilidade convectiva).
   - **Frequência de Brunt-Väisälä ($N$):** Identificar inversões térmicas e camadas de alta estabilidade estática ($N^2 > 0$).
   - **Estabilidade Estática ($S$):** Perfis de estabilidade estática e cisalhamento vertical.
5. **Perfis de Umidade e Conteúdo de Água:**
   - Razão de mistura ($r$, $\text{g/kg}$) ao longo da troposfera.
   - Água Precipitável Total ($PW$, $\text{mm}$) obtida por integração vertical.
   - Potencial de Correntes Descendentes ($DCAPE$, $\text{J/kg}$) a partir dos dados de Kerry Emanuel.
6. **Matrizes 2D de Kerry Emanuel (1994):**
   - Comparação entre o modo **Reversível** (com retenção de água líquida $r_l$) e o modo **Pseudoadiabático** (com precipitação instantânea de todo o condensado).
   - Análise da diferença de temperatura de densidade ($\Delta T_\rho$) e seu impacto no CAPE efetivo.

---

## 5. ⏱️ Estrutura da Apresentação 2: Defesa Oral de 20 Minutos perante os Previsores da Defesa Civil de SC

> As datas e os valores citados nesta seção são do exemplo do tutorial (SBPA, dezembro de 1995). Na sua apresentação, use as suas três sondagens e os valores da sua execução.

*Objetivo:* Defesa formal de 20 minutos (10 slides em proporção 16:9), focada na síntese física, forçamento de mesoescala e conclusões diagnósticas sob orientação acadêmica do Prof. Dr. Reinaldo Haas.

### Tabela de Cronometragem Slide a Slide:
| Slide | Minutagem | Título do Slide | Foco Conceitual & Script do Orador | Figura Associada |
| :---: | :---: | :--- | :--- | :--- |
| **01** | `00:00 - 01:30` | **Título & Objetivos da Investigação** | Contextualizar a investigação dos três regimes atmosféricos; enunciar a relevância da previsão operacional de tempestades para a Defesa Civil de SC e a aplicação das teorias de Kerry Emanuel (1994). | Slide de capa institucional |
| **02** | `01:30 - 03:30` | **Forçamento Sinótico & Suporte de Mesoescala** | Analisar o contexto em 500 hPa e baixos níveis a partir de evidências observadas na sondagem.<br>*[carta sinótica: a fazer com reanálise real (ERA5 / NCEP)]*. | Marcador de reanálise real |
| **03** | `03:30 - 05:30` | **Tríplice Diagnóstico: Estável vs. Neutra vs. Instável** | Comparar os três perfis Skew-T lado a lado (`fig_3_soundings_complete_analysis.png`). Contrastar a estratificação estável do caso de 12/12 com a instabilidade moderada de 22/12 e a severa de 24/12. | `fig_3_soundings_complete_analysis.png` |
| **04** | `05:30 - 07:30` | **Balanço Energético: CAPE vs. CIN e Teste de Sensibilidade** | Comparar os valores de CAPE e CIN para as 3 sondagens. No caso de 24/12, apresentar o impacto da camada em 925 hPa: versão Completa Oficial ($\text{MUCAPE} = 7810.0\text{ J/kg}$) versus teste de sensibilidade ($\text{MUCAPE} = 1860.1\text{ J/kg}$, $\text{SBCAPE} = 1860.1\text{ J/kg}$) sem os níveis de 925 hPa. | `fig_sounding_3_instavel.png` |
| **05** | `07:30 - 10:00` | **Termodinâmica Avançada de Emanuel: Matrizes 2D e $T_\rho$** | Explicar o código de Kerry Emanuel (1994). Demonstrar como a retenção de hidrometeoros no modo reversível reduz a flutuabilidade real frente ao cálculo pseudoadiabático tradicional (24/12 na superfície: $402.0\text{ J/kg}$ reversível vs $1479.7\text{ J/kg}$ pseudoadiabático). | `fig_3_soundings_emanuel_matrices.png` |
| **06** | `10:00 - 12:30` | **Perfis Verticais de Estabilidade ($\theta_e, N, S, r$ até 200 hPa)** | Analisar os perfis com topo padronizado em 200 hPa e legendas superiores. Destacar a camada de estabilidade em 925 hPa, a estrutura vertical de $\theta_e$ e a disponibilidade de vapor. | `fig_3_soundings_profiles_comparison.png` |
| **07** | `12:30 - 14:30` | **Diagnóstico de Umidade, Água Precipitável e DCAPE** | Avaliar o conteúdo de água precipitável ($PW$: 12/12 = $35.1\text{ mm}$, 22/12 = $43.9\text{ mm}$, 24/12 Oficial = $55.4\text{ mm}$, Sensibilidade = $50.8\text{ mm}$) e os valores de DCAPE comparando métodos: Emanuel (1994, descida de parcela: máx $195.5\text{ J/kg}$ em 905 hPa para 22/12; máx $60.7\text{ J/kg}$ em 905 hPa para 24/12) versus MetPy (coluna a partir do mín $\theta_e$: $1338.5\text{ J/kg}$ para 22/12 e $1096.8\text{ J/kg}$ para 24/12). | Perfis de umidade e métricas do JSON |
| **08** | `14:30 - 17:00` | **Cinemática: Hodógrafo, JBN e Helicidade no Hemisfério Sul** | Apresentar o hodógrafo (`fig_kinematics_hodograph.png`). Destacar que no Hemisfério Sul o vetor relevante é o Bunkers Left-Mover (LM = $11.4\text{ kt}$ de $048^\circ$), com helicidade ciclônica negativa ($\text{SRH } 0-3\text{ km} = -123.3\text{ m}^2/\text{s}^2$). Vento em 925 hPa de $43.9\text{ kt}$ ($22.6\text{ m/s}$) de $060^\circ$ e cisalhamento bulk 0–6 km de $12.6\text{ m/s}$ ($24.5\text{ kt}$). | `fig_kinematics_hodograph.png` |
| **09** | `17:00 - 19:00` | **Limitações de Dados em Mesoescala: Resolução Espacial de Satélite** | Explicar por que a grade ISCCP de 1° (~110 km) é inadequada para monitoramento de topos convectivos de mesoescala (média espacial que dilui extremos térmicos). Discutir a necessidade de dados em alta resolução espacial (< 4 km) para estudos operacionais da Defesa Civil de SC. | Análise conceitual de resolução espacial |
| **10** | `19:00 - 20:00` | **Conclusões Finais & Abertura para Discussão Técnica** | Recapitular as conclusões termodinâmicas e cinemáticas, pontuar o teste de sensibilidade e abrir formalmente para a arguição técnica dos previsores da Defesa Civil de SC. | Slide final de encerramento |

---

## 6. 🧠 Perguntas Típicas dos Previsores da Defesa Civil de SC e Como Responder

> As datas e os valores citados nesta seção são do exemplo do tutorial (SBPA, dezembro de 1995). Na sua apresentação, use as suas três sondagens e os valores da sua execução.

### Pergunta 1: *"Por que o CAPE no modo reversível de Kerry Emanuel é significativamente menor que no modo pseudoadiabático tradicional?"*
> **Resposta do Aluno:**  
> "No processo pseudoadiabático clássico, assume-se que toda a água condensada precipita instantaneamente ($r_l = 0$), permitindo que a parcela atinja sua flutuabilidade máxima puramente em função da temperatura virtual ($T_v$). No entanto, Kerry Emanuel (1994, Cap. 4 e 6) modela a termodinâmica reversível com a conservação da entropia úmida total, onde os hidrometeoros condensados permanecem suspensos na parcela ascendente. A presença dessa água líquida adiciona uma carga gravitacional de arrasto (termo $-r_l$ na aceleração vertical de flutuabilidade), reduzindo a temperatura de densidade da parcela ($T_\rho = T_v (1 - r_l)$). Consequentemente, a aceleração líquida diminui. No nosso caso de 24/12 na superfície, o CAPE reversível de Kerry Emanuel é de $402.0\text{ J/kg}$ contra $1479.7\text{ J/kg}$ no modo pseudoadiabático."

---

### Pergunta 2: *"Qual é o significado físico da camada quente e úmida em 925 hPa na sondagem de 24/12/1995 para a parcela mais instável?"*
> **Resposta do Aluno:**  
> "Na sondagem observada completa de 24/12/1995 12Z, o nível de 925 hPa registra $T = 30.0\text{ }^\circ\text{C}$ e $T_d = 25.0\text{ }^\circ\text{C}$ ($\theta_e = 377.8\text{ K}$). O diagnóstico de gradientes verticais revela que as camadas imediatamente superiores apresentam gradientes superadiabáticos: 925→910.5 hPa ($\Gamma = 17.65\text{ K/km}$) e 910.5→850 hPa ($\Gamma = 17.88\text{ K/km}$), com decréscimo de $\theta$ com a altura ($d\theta/dz = -8.1\text{ e } -8.4\text{ K/km}$) e forte descontinuidade de $\theta_e$. Essa camada excepcionalmente quente e úmida fornece à parcela mais instável (MUCAPE) uma energia de $7810.0\text{ J/kg}$ no MetPy e $7781.5\text{ J/kg}$ no algoritmo de Emanuel (1994). Por outro lado, ao realizarmos um teste de sensibilidade sem esses níveis específicos, o MUCAPE resulta em $1860.1\text{ J/kg}$, enquanto o SBCAPE permanece estável em $1860.1\text{ J/kg}$. Em vez de descartar os dados sumariamente ou forçar uma narrativa, apresentamos ambos os resultados lado a lado, demonstrando a sensibilidade do diagnóstico convectivo à amostragem vertical e à parcela de teste."

---

### Pergunta 3: *"Por que no Hemisfério Sul a helicidade relevante é negativa e associada ao Left-Mover de Bunkers?"*
> **Resposta do Aluno:**  
> "Em tempestades convectivas e supercélulas, a rotação do mesociclone não se origina diretamente da força de Coriolis (cujo número de Rossby para a escala do mesociclone de ~5 km é $Ro \sim 10$ a $100$), mas sim do **tombamento (*tilting*) da vorticidade horizontal associada ao cisalhamento ambiental vertical** pela corrente ascendente convectiva:
> $$\vec{\omega}_h = \hat{k} \times \frac{\partial \vec{V}}{\partial z}$$
> No Hemisfério Sul, o cisalhamento com hodógrafo curvado no sentido anti-horário gera gradientes dinâmicos de pressão que favorecem a célula que se desvia para a esquerda do vento médio (Bunkers Left-Mover, LM). Pela formulação matemática da helicidade relativa à tempestade:
> $$\text{SRH} = \int_0^h (\vec{V} - \vec{c}) \cdot \left(\hat{k} \times \frac{\partial \vec{V}}{\partial z}\right) dz$$
> onde $\vec{c}$ é o vetor de deslocamento da tempestade, a rotação ciclônica no Hemisfério Sul resulta estritamente em valores **negativos**. Na sondagem observada de 24/12, o vetor Bunkers Left-Mover é de $11.4\text{ kt}$ de $048^\circ$, gerando $\text{SRH } 0-3\text{ km} = -123.3\text{ m}^2/\text{s}^2$ com cisalhamento bulk 0–6 km de $12.6\text{ m/s}$ ($24.5\text{ kt}$)."

---

## 7. 📦 Recursos Prontos Disponíveis no Repositório
- **Métricas do exemplo do tutorial:** `metpack/metricas.json` e `metpack/metricas_notebook.json` (valores das sondagens de Porto Alegre, dezembro de 1995; os seus valores saem da sua execução).
- **Notebook Oficial da Disciplina:** [Seminario_plot_sounding_revisado.ipynb](https://colab.research.google.com/github/reinaldohaas/tarefa-meso/blob/master/Seminario_plot_sounding_revisado.ipynb) (processamento via Siphon/MetPy, conferência com Wyoming e modelagem de parcelas de Emanuel).
- **Apresentação PPTX Formatada:** `apresentacao_meso.pptx` (10 slides 16:9 widescreen gerados por script, com notas de orador completas para os previsores da Defesa Civil de SC).
- **Dashboard Web:** `index.html` (aba de comparação tríplice com tabelas e perfis até 200 hPa, e aba de roteiro pedagógico).
- **Scripts de Processamento:**
  - `metpack/calc_metricas.py`: Consolidação de métricas diagnósticas, índices de Wyoming e teste de sensibilidade.
  - `metpack/wyoming.py`: Algoritmo de Emanuel em Python puro (suporta `corte=None|-4.0`).
  - `metpack/wyoming.f`: Código clássico de Kerry Emanuel em Fortran.
  - `metpack/tcon.py`: Geração das matrizes 2D de diferença térmica de Emanuel.
  - `metpack/tarefa_sondagens.m`, `metpack/getsounding_wyoming.m`, `metpack/tcon_emanuel.m`, `metpack/skewt.m`: versão MATLAB (MATLAB Online) dos programas de Kerry Emanuel.
  - `generate_figures.py`: Geração dos perfis até 200 hPa, Skew-T e hodógrafos.
  - `generate_pptx.py`: Geração da apresentação em PowerPoint.
  - `build_index_html.py`: Compilador do `index.html`.
