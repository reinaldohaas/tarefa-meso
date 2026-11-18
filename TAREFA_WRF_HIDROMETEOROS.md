# Tarefa WRF: os hidrometeoros dentro da tempestade

**Disciplina:** FSC7116 Meteorologia de Mesoescala (UFSC)
**Docente:** Prof. Dr. Reinaldo Haas

## 1. Objetivo

Simular com o WRF o evento severo que você escolheu para a disciplina (o mesmo das sondagens, de preferência) e mostrar, em três dimensões, **cada hidrometeoro separadamente**: gotas de nuvem, chuva, gelo, neve, graupel e, se o esquema tiver, granizo.

A pergunta de fundo é a mesma da tarefa das sondagens: os hidrometeoros modulam o evento severo? Na matriz de Emanuel, reter a água condensada (modo reversível) reduz a flutuabilidade em relação ao cálculo pseudoadiabático. Aqui você vai ver onde essa água e esse gelo estão dentro da nuvem simulada, em que altura, em que temperatura e junto de qual corrente ascendente ou descendente.

## 2. Requisitos mínimos

| Item | Mínimo exigido |
| :--- | :--- |
| Modelo | WRF-ARW 4.x (pode ser o WRF-Chem, rodando só a meteorologia) |
| Aninhamento | 3 domínios (`max_dom = 3`), razão 3 entre eles |
| Resolução | 3 km ou menos no domínio interno. Exemplos: 27/9/3 km ou 9/3/1 km |
| Duração | o evento inteiro, com pelo menos 6 h de aquecimento antes da convecção |
| Saída do domínio interno | a cada 10 ou 15 min durante o evento |
| Microfísica | um esquema com pelo menos nuvem, chuva, gelo, neve e graupel (ver item 4) |
| Visualização | ParaView, IDV ou VAPOR, com uma imagem 3D por hidrometeoro |

## 3. Etapas

1. **Escolha do caso e do período.** Data e hora do evento, onde aconteceu e o que foi observado (granizo, rajada, chuva, tornado). Cite a fonte: Defesa Civil, imprensa, radar ou satélite.
2. **Dados de entrada.** ERA5 (Copernicus CDS, níveis de pressão e superfície) ou GFS/FNL (NCAR RDA, ds083.2 ou ds084.1), a cada 3 ou 6 h.
3. **Domínios (WPS).** Desenhe os três domínios com o domínio interno centrado no evento e com folga de pelo menos 50 km até a borda. O GIS4WRF (plugin do QGIS) ajuda a desenhar e a conferir. Mostre uma figura dos domínios com o local do evento.
4. **Física (`namelist.input`).** Justifique cada escolha em uma linha.
   - **Cumulus:** ligado no domínio de 27 km (ou 9 km), desligado no de 3 km ou menos. No de 9 km é zona cinzenta: escolha e justifique.
   - **Microfísica:** veja a tabela abaixo.
5. **Rodada.** `real.exe` e `wrf.exe`. Guarde o `rsl.error.0000` e confira se termina com `SUCCESS COMPLETE WRF`.
6. **Verificação simples.** Compare a simulação com pelo menos uma observação: radar, satélite (topo frio, raios do GLM) ou chuva acumulada (GPM-IMERG ou estações). Diga quanto o modelo errou em lugar e em hora.
7. **Visualização dos hidrometeoros** (item 5).
8. **Discussão** (item 6).

### Microfísica: o que cada esquema separa

| Esquema | `mp_physics` | Graupel | Granizo |
| :--- | :--- | :--- | :--- |
| Thompson | 8 | sim | não |
| Morrison 2 momentos | 10 | uma categoria só de gelo rimado: granizo se `morr_rimed_ice = 1` (padrão), graupel se 0 | idem |
| Milbrandt-Yau 2 momentos | 9 | sim | sim |
| NSSL 2 momentos | 18, com `nssl_hail_on = 1` | sim | sim, com densidade prevista se `nssl_density_on = 2` |

Para ver graupel e granizo separados, use o NSSL ou o Milbrandt-Yau. Na versão 4.7, o `mp_physics = 17` é um apelido obsoleto: o modelo o troca por 18 com as opções `nssl_*`. Escreva as opções explicitamente. Variáveis no `wrfout`: `QCLOUD`, `QRAIN`, `QICE`, `QSNOW`, `QGRAUP` e, conforme o esquema, `QHAIL` (ou `QH`), além das concentrações em número (`QNRAIN`, `QNGRAUPEL`, `QNHAIL`...).

Ligue também `do_radar_ref = 1` (refletividade simulada, para comparar com o radar) e, se quiser o tamanho do granizo, `hailcast_opt = 1` no domínio interno.

## 4. Cuidados que costumam estragar a figura 3D

- **Altura.** O eixo vertical do `wrfout` é o índice do nível eta, não a altura. A altura de cada ponto vem do geopotencial: z = (PH + PHB) / 9,81, com média entre dois níveis vizinhos para cair no centro da célula. Sem isso, a nuvem aparece achatada ou deformada sobre o relevo.
- **Projeção.** Use `XLAT` e `XLONG` do próprio arquivo, ou converta para quilômetros com a projeção do domínio (`TRUELAT1`, `TRUELAT2`, `STAND_LON` nos atributos globais).
- **Unidade.** As razões de mistura estão em kg/kg. Multiplique por 1000 para g/kg antes de escolher os limiares.
- **Exagero vertical.** A tempestade tem ~15 km de altura e o domínio centenas de km de lado. Um exagero vertical de 5 a 20 vezes deixa a estrutura legível; informe o valor na legenda.
- **Limiar de cada isosuperfície.** Um ponto de partida (ajuste ao seu caso e diga qual usou): nuvem 0,1 g/kg, chuva 0,5 g/kg, gelo 0,05 g/kg, neve 0,1 g/kg, graupel 0,5 g/kg, granizo 0,1 g/kg.
- **Cores.** Uma cor fixa por hidrometeoro em todas as figuras, por exemplo: nuvem branca ou cinza claro, chuva azul, gelo ciano, neve lilás, graupel laranja, granizo vermelho.

## 5. Visualização: escolha uma ferramenta

**VAPOR (NCAR).** Lê o `wrfout` direto (tipo de dado "WRF-ARW") e já usa a altura certa. Crie um renderizador de isosuperfície ou de volume por variável (`QRAIN`, `QGRAUP`...). Ligue e desligue cada um para as imagens separadas e junte todos para a imagem combinada. É o caminho mais curto.

**IDV (Unidata).** Abre o `wrfout` pelo netCDF-Java. Use a exibição "Isosurface" em cada razão de mistura e ajuste a escala vertical em "Projection". Confira a coordenada vertical que o IDV escolheu: se ela não estiver em altura, a figura sai deformada.

**ParaView.** Não lê o `wrfout` do jeito certo sozinho. Converta antes com um script em Python (xarray e numpy, ou wrf-python ou xwrf) que monte uma grade estruturada com x e y em km e z = (PH + PHB) / 9,81. Grave um `.vts` (pyvista ou vtk) com um campo por hidrometeoro em g/kg. No ParaView, use um filtro "Contour" por variável, o terreno (`HGT`) como superfície e "Transform" para o exagero vertical.

Para qualquer uma das três, entregue:
- uma imagem 3D **para cada hidrometeoro** no horário de maior intensidade, todas do mesmo ponto de vista;
- uma imagem com todos juntos;
- um corte vertical (2D) passando pela corrente ascendente mais forte, com as razões de mistura de cada hidrometeoro, o contorno de `W` e as isotermas de 0 °C e −20 °C;
- opcional: uma animação de 1 a 2 h do domínio interno.

## 6. O que discutir

1. Em que altura e em que temperatura fica o máximo de cada hidrometeoro? Graupel e granizo ficam acima ou abaixo da isoterma de 0 °C, e onde derretem?
2. Onde está a água líquida super-resfriada (nuvem e chuva acima do nível de 0 °C) em relação à corrente ascendente?
3. Os hidrometeoros explicam o que foi observado: granizo na superfície, rajada (piscina fria, carga de precipitação), chuva intensa?
4. Ligação com as sondagens: a flutuabilidade reversível de Emanuel, que retém a água condensada, combina com a quantidade de água e gelo que o modelo guardou na nuvem?
5. O que o modelo errou, e quanto isso depende da microfísica ou do esquema de cumulus no domínio externo?

## 7. Entrega

- `namelist.wps` e `namelist.input` usados, e o `rsl.error.0000` final;
- a figura dos domínios;
- a verificação contra a observação;
- as figuras do item 5 com legendas (variável, limiar, horário, exagero vertical);
- uma tabela com o máximo de cada hidrometeoro (g/kg), a altura e a temperatura em que ocorre;
- o script de conversão ou o arquivo de sessão da ferramenta (`.vs3` do VAPOR, `.xidv` do IDV ou `.pvsm` do ParaView), para que a figura possa ser refeita;
- a discussão do item 6.

## 8. Critérios de avaliação

| Critério | Peso |
| :--- | :--- |
| Configuração correta (3 domínios, ≤ 3 km, física justificada, rodada completa) | 25% |
| Verificação contra a observação | 15% |
| Figuras 3D com altura certa, um hidrometeoro por figura, legendas completas | 30% |
| Discussão física (itens 6.1 a 6.5) | 25% |
| Reprodutibilidade (namelists, script ou sessão) | 5% |

## 9. Prompt para usar com um assistente de IA

Você pode usar um assistente de IA (Claude, ChatGPT, Gemini ou outro) como monitor. Copie o bloco abaixo, preencha o que está entre colchetes e cole no início da conversa. Quem roda os comandos e confere os números é você: o assistente explica e revisa, mas não pode inventar resultados.

```text
Sou estudante da disciplina FSC7116 Meteorologia de Mesoescala (UFSC). Minha tarefa
é simular com o WRF-ARW um evento severo e visualizar em 3D cada hidrometeoro
separadamente. O enunciado completo está em
https://github.com/reinaldohaas/tarefa-meso/blob/master/TAREFA_WRF_HIDROMETEOROS.md

Meu caso:
- evento: [tipo de evento, cidade, data e hora em UTC]
- observação disponível: [radar, satélite, relatos, chuva medida]
- onde vou rodar: [meu computador com Linux/WSL, cluster, VLab]; WRF versão [x.y]
- dados de entrada: [ERA5 ou GFS/FNL]
- ferramenta de visualização: [VAPOR, IDV ou ParaView]

Requisitos que não podem mudar:
- 3 domínios aninhados (max_dom = 3), razão 3, domínio interno com 3 km ou menos;
- cumulus desligado no domínio interno;
- microfísica com nuvem, chuva, gelo, neve e graupel; de preferência NSSL 2 momentos
  (mp_physics = 18, nssl_hail_on = 1, nssl_density_on = 2) ou Milbrandt-Yau (9),
  para ter graupel e granizo separados;
- saída do domínio interno a cada 10 ou 15 min durante o evento;
- altura dos pontos calculada por z = (PH + PHB)/9,81, nunca pelo índice do nível.

Como quero que você me ajude:
1. Uma etapa por vez: domínios, WPS, namelist.input, rodada, verificação,
   visualização, discussão. Espere eu mostrar o resultado antes de seguir.
2. Para cada opção do namelist que você sugerir, diga o que ela faz e por que serve
   ao meu caso.
3. Quando eu colar um erro (rsl.error, ungrib, metgrid), explique a causa provável
   e o que conferir antes de mudar qualquer coisa.
4. Não invente números, nomes de variáveis nem opções: se não tiver certeza de que
   algo existe na minha versão do WRF, diga e me mostre como conferir no Registry
   ou no wrfout (ncdump -h).
5. Na visualização, me ajude a fazer uma figura por hidrometeoro com o mesmo ponto
   de vista, cores fixas e limiares informados na legenda, mais o corte vertical
   pela corrente ascendente com W e as isotermas de 0 °C e -20 °C.
6. Na discussão, me faça perguntas em vez de escrever o texto por mim.
```
