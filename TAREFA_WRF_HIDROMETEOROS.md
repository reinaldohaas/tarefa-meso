# Seminário Final (Parte 2): simulação WRF de evento severo

**Disciplina:** FSC7116 Meteorologia de Mesoescala (UFSC)
**Docente:** Prof. Dr. Reinaldo Haas
**Entrega no Moodle (WRF 2, TCD):** até sábado, 5 de dezembro de 2026, 00:00

Convecção explícita (3 km ou menos), microfísica (granizo, graupel e água super-resfriada), visualização de cada hidrometeoro em 3D, página no GitHub e apresentação de 20 minutos.

## 1. Postura científica: o modelo não precisa acertar

A simulação não precisa prever corretamente o evento escolhido. Erros de fase (antecipação ou atraso), de posição e de intensidade fazem parte do aprendizado em modelagem de mesoescala.

Você será avaliado principalmente por:
- investigar com rigor por que a simulação divergiu das observações (radar, satélite, superfície);
- dizer se a quantidade e a distribuição de granizo, graupel e água super-resfriada são coerentes com a dinâmica simulada;
- explicar à banca as limitações físicas e numéricas da configuração que você escolheu.

A pergunta de fundo é a mesma da Parte 1 (sondagens): os hidrometeoros modulam o evento severo? Na matriz de Emanuel, reter a água condensada (modo reversível) reduz a flutuabilidade em relação ao cálculo pseudoadiabático. Aqui você vai ver onde essa água e esse gelo estão dentro da nuvem simulada.

## 2. Requisitos mínimos

| Item | Mínimo exigido |
| :--- | :--- |
| Modelo | WRF-ARW 4.x (pode ser o WRF-Chem, rodando só a meteorologia) |
| Aninhamento | 3 domínios (`max_dom = 3`), razão 3 entre eles |
| Resolução | 3 km ou menos no domínio interno. Exemplos: 27/9/3 km ou 9/3/1 km |
| Cumulus | desligado (`cu_physics = 0`) no domínio de 3 km ou menos |
| Duração | o evento inteiro, com pelo menos 6 h de aquecimento antes da convecção |
| Saída do domínio interno | a cada 10 ou 15 min durante o evento |
| Microfísica | com gelo, neve e graupel, e de preferência granizo separado (item 5) |
| Refletividade | `do_radar_ref = 1`, para ter `REFL_10CM` |
| Visualização | ParaView, IDV ou VAPOR, com uma imagem 3D por hidrometeoro |
| GitHub | repositório público com namelists, relatório, figuras e página (item 9) |

## 3. Ambientes de modelagem

**Regra para todos:** você digita e roda cada comando no terminal. Para cada rodada experimental, crie uma pasta própria com cópias (ou links) dos executáveis e uma cópia da `namelist.input`, sem sobrescrever a rodada anterior.

- **Opção A: cluster ou servidor da UFSC.** Ideal para os 3 domínios com o interno de 1 a 3 km, com MPI em vários processadores. Permite microfísica de 2 momentos sem restrição de memória.
- **Opção B: computador pessoal (Linux nativo ou WSL2 no Windows).** Domínios menores, com o interno centrado só na área da tempestade, para caber na memória e no tempo disponível. A resolução mínima continua 3 km.
- **Opção C: com um assistente de IA como tutor.** O assistente explica, revisa e faz perguntas; você roda tudo no terminal e escolhe a configuração. Use o prompt do item 12.

## 4. Etapas

1. **O caso.** Retome o evento da Parte 1: data e hora (UTC), local, o que foi observado (granizo, rajada, chuva, tornado) e as fontes (Defesa Civil, imprensa, radar, satélite).
2. **Dados de entrada.** ERA5 (Copernicus CDS, níveis de pressão e superfície) ou GFS/FNL (NCAR RDA, ds083.2 ou ds084.1), a cada 3 ou 6 h.
3. **Domínios (WPS).** Domínio interno centrado no evento, com folga de pelo menos 50 km até a borda. O GIS4WRF (plugin do QGIS) ajuda a desenhar e conferir.
4. **Física (`namelist.input`).** Você escolhe e justifica a combinação de microfísica, camada limite, radiação e passo de tempo (CFL). Não copie configuração sem entender cada opção.
5. **Rodada.** `real.exe` e `wrf.exe`. Guarde o `rsl.error.0000` e confira se termina com `SUCCESS COMPLETE WRF`.
6. **Diagnóstico da microfísica** (itens 5 e 6).
7. **Comparação com a observação** (item 7).
8. **Página no GitHub** (item 9) e **apresentação** (item 10).

## 5. Microfísica de nuvens em convecção severa

### 5.1 Água super-resfriada (SLW)

É a água líquida em níveis com temperatura abaixo de 0 °C. Pode permanecer líquida, em estado metaestável, até cerca de −38 a −40 °C, limite da nucleação homogênea. É o "combustível" do granizo: as gotículas colidem com partículas de gelo e congelam na superfície delas (acreção ou *riming*).

No `wrfout` não existe uma variável de SLW. Calcule:
- temperatura: T = (`T` + 300) × ((`P` + `PB`) / 100000)^0,2854, em K (`T` do WRF é a perturbação da temperatura potencial);
- SLW = `QCLOUD` + `QRAIN` nos pontos com T < 273,15 K (em g/kg, multiplique por 1000).

### 5.2 Crescimento do granizo por acreção

A taxa clássica de crescimento da massa M de uma pedra de raio R é

dM/dt = π R² · E · V · ρ_SLW

onde V é a velocidade de queda da pedra em relação às gotículas, E é a eficiência de coleta e ρ_SLW é a densidade de água super-resfriada (kg/m³) disponível na corrente ascendente. Pedras grandes precisam de muita SLW e de tempo dentro da ascendente.

### 5.3 O que cada esquema separa

| Esquema | `mp_physics` | Graupel | Granizo |
| :--- | :--- | :--- | :--- |
| WSM6 | 6 | sim (`hail_opt = 1` troca por granizo) | idem |
| Thompson | 8 | sim | não |
| Morrison 2 momentos | 10 | uma categoria de gelo rimado: granizo se `morr_rimed_ice = 1` (padrão), graupel se 0 | idem |
| Milbrandt-Yau 2 momentos | 9 | sim | sim |
| NSSL 2 momentos | 18, com `nssl_hail_on = 1` | sim | sim, com densidade prevista se `nssl_density_on = 2` |

Atenção: em Thompson, WSM6 e Morrison, `QGRAUP` é uma única categoria de gelo denso, que pode representar graupel ou granizo, mas não os dois. Para ver graupel e granizo separados (`QGRAUP` e `QHAIL`), avalie NSSL ou Milbrandt-Yau. Na versão 4.7, o `mp_physics = 17` é um apelido obsoleto que o modelo troca por 18 com as opções `nssl_*`; escreva as opções explicitamente. A escolha é sua e deve ser justificada.

Se quiser o tamanho máximo do granizo na superfície, ligue `hailcast_opt = 1` no domínio interno.

### 5.4 Variáveis obrigatórias do `wrfout`

| Variável | Significado | O que analisar |
| :--- | :--- | :--- |
| `QGRAUP` (e `QHAIL`, se houver) | razão de mistura de graupel e granizo (kg/kg) | núcleo de máxima concentração suspensa na convecção |
| `QCLOUD` | água líquida de nuvem (kg/kg) | quanto se estende acima da isoterma de 0 °C (SLW) |
| `QRAIN` | chuva (kg/kg) | chuva acima de 0 °C (SLW) e carga de precipitação |
| `QICE`, `QSNOW` | cristais de gelo e neve (kg/kg) | glaciação no topo (T < −40 °C) e bigorna |
| `W` | velocidade vertical (m/s) | corrente ascendente que sustenta a SLW e o granizo |
| `REFL_10CM` | refletividade equivalente (dBZ) | ecos acima de 50 a 55 dBZ, comparação com o radar |

## 6. Visualização dos hidrometeoros

### 6.1 Cuidados que costumam estragar a figura

- **Altura.** O eixo vertical do `wrfout` é o índice do nível eta, não a altura. A altura vem do geopotencial: z = (`PH` + `PHB`) / 9,81, com média entre dois níveis vizinhos para cair no centro da célula. Sem isso, a nuvem sai achatada ou deformada sobre o relevo.
- **Projeção.** Use `XLAT` e `XLONG` do arquivo, ou converta para km com a projeção do domínio (`TRUELAT1`, `TRUELAT2` e `STAND_LON` nos atributos globais).
- **Unidade.** As razões de mistura estão em kg/kg. Multiplique por 1000 para g/kg antes de escolher os limiares.
- **Exagero vertical.** A tempestade tem ~15 km de altura e o domínio centenas de km de lado. Use um exagero de 5 a 20 vezes e informe o valor na legenda.
- **Limiares.** Ponto de partida (ajuste e informe): nuvem 0,1 g/kg, chuva 0,5, gelo 0,05, neve 0,1, graupel 0,5, granizo 0,1, SLW 0,2 g/kg.
- **Cores fixas por hidrometeoro em todas as figuras.** Por exemplo: nuvem cinza claro, chuva azul, gelo ciano, neve lilás, graupel laranja, granizo vermelho, SLW verde.

### 6.2 Ferramentas

**VAPOR (NCAR).** Lê o `wrfout` direto (tipo "WRF-ARW") e já usa a altura certa. Um renderizador de isosuperfície ou de volume por variável; ligue e desligue cada um para as imagens separadas.

**IDV (Unidata).** Abre o `wrfout` pelo netCDF-Java. Exibição "Isosurface" em cada razão de mistura; escala vertical em "Projection". Confira se a coordenada vertical está em altura.

**ParaView.** Converta antes com Python (xarray e numpy, ou wrf-python ou xwrf): grade estruturada com x e y em km, z = (`PH` + `PHB`) / 9,81 e um campo por hidrometeoro em g/kg, gravada em `.vts` (pyvista ou vtk). No ParaView, um filtro "Contour" por variável, o terreno (`HGT`) como superfície e "Transform" para o exagero vertical.

### 6.3 Figuras obrigatórias

1. **Uma imagem 3D para cada hidrometeoro** no horário de maior intensidade, todas do mesmo ponto de vista, e uma com todos juntos (inclua a SLW).
2. **Corte vertical pela célula mais vigorosa**, com a isoterma de 0 °C, a de −20 °C (opcional, a de −40 °C), os contornos de SLW, o núcleo de `QGRAUP` (e `QHAIL`) e os contornos de `W`.
3. **Refletividade máxima na coluna** (`REFL_10CM`, composta) no momento de máxima intensidade, destacando valores acima de 50 dBZ.
4. **Tabela** com o máximo de cada hidrometeoro (g/kg), a altura e a temperatura em que ocorre.

## 7. Comparação com a observação

Painel lado a lado, no mesmo horário: radar real (ou GOES: topo frio, raios do GLM) contra a refletividade simulada. Diga quanto o modelo errou em lugar (km) e em hora. Se o modelo antecipou ou atrasou, compare também o horário simulado de maior intensidade com o observado.

## 8. Como discutir as deficiências do modelo

Conduza a discussão com honestidade e rigor:

- **Erro de posição ou de hora.** Possíveis causas físicas: incerteza nas condições de contorno (GFS/ERA5), quebra antecipada ou atrasada da inversão (*capping inversion*), piscina fria (*cold pool*) mal representada, cumulus do domínio externo consumindo a instabilidade antes da hora.
- **Granizo em excesso, em falta, ou derretido antes de chegar ao chão.** Hipóteses do esquema sobre densidade do graupel e do granizo, distribuição de tamanhos, número de momentos e taxa de fusão na camada quente abaixo de 0 °C. Compare a altura da isoterma de 0 °C simulada com a da sondagem da Parte 1.
- **SLW.** Havia água super-resfriada suficiente na ascendente? Ela foi consumida pelo gelo cedo demais (glaciação rápida) ou chegou alta?
- **Benefício da convecção explícita.** O que a grade de 3 km ou menos resolveu (ascendentes concentradas e intensas) que o cumulus do domínio externo não resolveria?

Perguntas para orientar a análise:
1. Em que altura e temperatura fica o máximo de cada hidrometeoro? Graupel e granizo ficam acima ou abaixo de 0 °C, e onde derretem?
2. Onde está a SLW em relação à corrente ascendente?
3. Os hidrometeoros explicam o observado: granizo na superfície, rajada (piscina fria, carga de precipitação), chuva intensa?
4. A flutuabilidade reversível de Emanuel, que retém a água condensada, combina com a água e o gelo que o modelo guardou na nuvem?
5. O que o modelo errou, e quanto disso depende da microfísica ou do cumulus no domínio externo?

## 9. Página no GitHub

O repositório público é obrigatório e serve também como página de apresentação dos resultados.

### 9.1 Estrutura sugerida

```text
fsc7116-wrf-<seu-nome>/
├── README.md                  # caso, configuração, link da página e da apresentação
├── RELATORIO_RODADA.md        # relatório de cada rodada (modelo no item 9.3)
├── index.html                 # página com as figuras (GitHub Pages)
├── wps/namelist.wps
├── rodadas/
│   ├── r1_<descricao>/namelist.input
│   └── r2_<descricao>/namelist.input
├── scripts/                   # conversão para o ParaView, cortes, comparação com radar
├── sessoes/                   # .vs3 (VAPOR), .xidv (IDV) ou .pvsm (ParaView)
├── figuras/                   # PNG das figuras do item 6.3 e do item 7
└── apresentacao/              # slides em PDF
```

Não envie `wrfout`, `met_em` nem dados brutos: são grandes demais. Um `.gitignore` com `wrfout_*`, `wrfrst_*`, `met_em*`, `*.grib` e `*.nc` evita o erro.

### 9.2 Página (GitHub Pages)

Ative em Settings → Pages → "Deploy from a branch" → `main`, pasta `/ (root)`. A página fica em `https://<seu-usuario>.github.io/<repositório>/`.

A página deve mostrar:
- o caso e a observação (radar ou satélite);
- a figura dos domínios e a tabela da configuração, com a justificativa de cada escolha;
- as imagens 3D de cada hidrometeoro (lado a lado ou em abas), a imagem combinada e o corte vertical;
- o painel de comparação com a observação;
- a tabela do item 6.3;
- as deficiências e as conclusões, em poucos parágrafos;
- links para as namelists, os scripts e o PDF da apresentação.

Opcional, para quem quiser a nuvem girando no navegador:
- ParaView: File → Export Scene → `.vtkjs`, publicado no repositório e aberto pelo ParaView Glance;
- Python: `plotly.graph_objects.Isosurface` com a grade reduzida (um ponto a cada 2 ou 3), salvo como HTML; mantenha o arquivo abaixo de ~20 MB;
- uma animação em GIF ou MP4 de 1 a 2 h do domínio interno.

### 9.3 Modelo do `RELATORIO_RODADA.md`

```markdown
# Rodada r1_<descricao>

- Caso: <evento, local, data e hora UTC>
- Ambiente: <cluster, PC com WSL2...>; WRF <versão>; processadores: <n>
- Dados de entrada: <ERA5 ou GFS/FNL>, a cada <3 ou 6> h
- Domínios: <dx de cada um>, <pontos>, níveis verticais, topo
- Física e justificativa (uma linha cada): microfísica, cumulus (por domínio),
  camada limite, superfície, radiação, passo de tempo
- Início, fim e tempo de relógio; terminou com SUCCESS? <sim/não>
- Problemas e como resolveu: <CFL, erros do real.exe...>
- Resultado em uma frase: <o que acertou e o que errou>
- Diferença para a rodada anterior e por quê: <...>
```

## 10. Apresentação final (20 minutos)

| Tempo | Slides | Conteúdo |
| :--- | :--- | :--- |
| 00 a 03 min | 1 e 2: o caso severo | retomada do evento da Parte 1, radar ou satélite, relatos de granizo e danos |
| 03 a 06 min | 3 e 4: grade e física | domínios (3 km ou menos no interno) e justificativa da combinação da `namelist.input` |
| 06 a 10 min | 5 e 6: microfísica | imagens 3D de cada hidrometeoro e corte vertical com `QGRAUP`/`QHAIL`, SLW e isoterma de 0 °C |
| 10 a 14 min | 7 e 8: comparação | `REFL_10CM` simulada contra o radar ou o satélite no mesmo horário |
| 14 a 17 min | 9: deficiências | onde o modelo errou (hora, local, granizo) e os mecanismos físicos |
| 17 a 20 min | 10: conclusões | lições de modelagem e o link da página no GitHub, para a arguição |

- Tempo rigoroso: 20 minutos por estudante, em sala.
- Teste antes os slides nos computadores do Departamento de Física.
- A página do GitHub não substitui os slides, mas pode ser aberta na arguição para mostrar a nuvem em 3D.

## 11. Entrega e avaliação

**No Moodle, antes da sessão:** os slides (PowerPoint ou PDF), o `RELATORIO_RODADA.md` e o link do repositório e da página no GitHub.

**No GitHub (público):** o que está no item 9.1, com `namelist.wps`, `namelist.input` de cada rodada e os arquivos de configuração versionados.

| Critério | Peso |
| :--- | :--- |
| Configuração (3 domínios, 3 km ou menos, cumulus desligado no interno, física justificada) | 20% |
| Microfísica: SLW, graupel e granizo, figuras 3D com altura certa, corte vertical | 30% |
| Comparação com a observação | 15% |
| Discussão das deficiências do modelo | 25% |
| Página no GitHub e reprodutibilidade (namelists, relatório, scripts ou sessão) | 10% |

## 12. Prompt para usar com um assistente de IA

Copie o bloco abaixo, preencha o que está entre colchetes e cole no início da conversa com o assistente (Claude, ChatGPT, Gemini ou outro). Quem roda os comandos, escolhe a configuração e confere os números é você.

```text
Você é meu orientador científico no Seminário Final do WRF (FSC7116 Meteorologia
de Mesoescala, UFSC). Eu sou o autor e condutor de todas as etapas e rodarei
pessoalmente cada comando no meu terminal. O enunciado completo está em
https://github.com/reinaldohaas/tarefa-meso/blob/master/TAREFA_WRF_HIDROMETEOROS.md

Meu caso:
- evento: [tipo de evento, cidade, data e hora em UTC]
- observação disponível: [radar, satélite, relatos, chuva medida]
- ambiente: [cluster da UFSC, PC com Linux/WSL2]; WRF versão [x.y]
- dados de entrada: [ERA5 ou GFS/FNL]
- visualização 3D: [VAPOR, IDV ou ParaView]
- meu repositório no GitHub: [link]

Diretrizes:
1. NÃO execute comandos por conta própria. Eu executo e te mostro a saída.
2. O objetivo é convecção explícita: 3 domínios aninhados (max_dom = 3), razão 3,
   domínio interno com 3 km ou menos e cumulus desligado nele.
3. Não me dê a namelist pronta. Explique as opções e as consequências de cada
   uma (microfísica, camada limite, radiação, passo de tempo e CFL); eu escolho
   e justifico.
4. O foco da análise é a microfísica: água super-resfriada (QCLOUD e QRAIN abaixo
   de 0 °C), graupel e granizo (QGRAUP e, se o esquema tiver, QHAIL).
5. Se o modelo errar o lugar ou a hora da tempestade, isso faz parte do trabalho:
   me ajude a investigar o porquê, sem tentar "consertar" a rodada para acertar.
6. Uma etapa por vez: domínios, WPS, namelist, rodada, diagnóstico, comparação,
   visualização, página no GitHub, apresentação. Espere meu resultado antes de
   seguir.
7. Quando eu colar um erro (rsl.error, ungrib, metgrid), explique a causa provável
   e o que conferir antes de mudar qualquer coisa.
8. Não invente números, nomes de variáveis nem opções. Se não tiver certeza de que
   algo existe na minha versão do WRF, diga e me mostre como conferir no Registry
   ou no wrfout (ncdump -h).
9. Na visualização, lembre que a altura vem de (PH + PHB)/9,81, não do índice do
   nível; uma figura por hidrometeoro, mesmo ponto de vista, cores fixas e limiar
   na legenda.
10. Na página do GitHub e nos slides, revise a clareza e a ordem, mas o texto e as
    conclusões são meus. Na discussão, me faça perguntas em vez de escrever por mim.
```
