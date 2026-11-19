# -*- coding: utf-8 -*-
"""Gera apresentacao_parte2.html: a apresentação de 20 minutos do Seminário Final (Parte 2), em 10 slides.

Lê wrfpack/metricas_wrf.json (série temporal e tabela de máximos da rodada r1_milbrandt_yau_2km) e usa as
figuras de figuras/. Navegação: setas, espaço, Home/End, F (tela cheia), N (roteiro de fala), #3 abre o slide 3.

Uso: python scripts/gerar_apresentacao_parte2.py
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(AQUI, '..')
M = json.load(open(os.path.join(REPO, 'wrfpack', 'metricas_wrf.json'), encoding='utf-8'))

serie = [dict(h=s['tempo'][11:16], z=s['refl_max_dbz'], w=s['w_max_ms'], g=s['qgraup_max_gkg'], q=s['qhail_max_gkg'])
         for s in M['serie_temporal']]
pico_w = max(serie, key=lambda s: s['w'])
pico_z = max(serie, key=lambda s: s['z'])
obs = next(s for s in serie if s['h'] == '22:30')
hailcast = max(s['hailcast_ilha_mm'] for s in M['serie_temporal'])          # perto da Ilha (25 km de Jurerê)
hailcast_bruto = max(s['hailcast_max_mm'] for s in M['serie_temporal'])    # máximo no d03, inclui valores sem sentido físico
TAB = {r['variavel']: r for r in M['tabela_maximos']}
HORA = M['tempo_pico_utc'][11:16]
foco = next(s for s in serie if s['h'] == HORA)


def num(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',')


linhas_tab = ''.join(
    f"<tr><td>{r['nome']}</td><td>{num(r['max_g_kg'], 2)}</td><td>{num(r['altura_km'], 1)}</td><td>{num(r['temperatura_C'], 1)}</td></tr>"
    for r in M['tabela_maximos'])

HIDROS = [('todos', 'todos'), ('SLW', 'água super-resfriada'), ('QGRAUP', 'graupel'), ('QHAIL', 'granizo'),
          ('QCLOUD', 'nuvem'), ('QRAIN', 'chuva'), ('QICE', 'gelo'), ('QSNOW', 'neve')]
PRESSIONADO = ' aria-pressed="true"'
abas = ''.join(f'<button type="button" data-h="{k}"{PRESSIONADO if k == "todos" else ""}>{v}</button>' for k, v in HIDROS)

SLIDES = [
    dict(t='O caso severo', s='Tempestade Noturna: Granizo no norte da Ilha de Santa Catarina, 29/08/2026', tempo='00 a 03 min', corpo=f"""
<div class="duas">
  <div>
    <ul>
      <li><b>Evento Noturno Real:</b> convecção severa entre <b>22:00 e 23:00 UTC</b> (19:00 e 20:00 h locais) sobre Biguaçu e Norte da Ilha (Jurerê, Canasvieiras, Cachoeira do Bom Jesus, Ingleses).</li>
      <li><b>Trajetória 185 (GOES-19 GLM):</b> célula iniciou na borda da Serra Geral às 20:10 UTC (-50,1°W / -27,5°S), avançou a leste a ~16 m/s, alcançou Biguaçu às 22:10 UTC e o Norte da Ilha às 22:30 UTC.</li>
      <li><b>Granizo Gigante:</b> relatos com pedras de até <b>~6 cm</b> ("tamanho de bolas de tênis") e destelhamentos em Biguaçu e Norte da Ilha.</li>
      <li><b>Radar Morro da Igreja (DECEA):</b> núcleo com refletividade extrema (>60 dBZ, magenta) cruzando Biguaçu às 22:16 UTC e Ilha às 22:36 UTC.</li>
      <li><b>GOES-19 (Canal 13 - 10,3 µm):</b> temperatura mínima de brilho no topo de <b>−62,9 °C</b> às 22:20 UTC; atividade de até 365 flashes/10 min no GLM sem salto anômalo prévio.</li>
    </ul>
    <p class="destaque">A tempestade severa foi comprovadamente <b>noturna</b> (relatos, radar MI e GOES-19). Como demonstrado em <code>granizo-gigante</code>, a assinatura de satélite parecia convencional, mas o interior da nuvem concentrava enorme carga de hidrometeoros.</p>
  </div>
  <figure><img src="figuras/comparacao_obs.png" alt="Relatos de granizo, caixa do GOES-19 e trajetória do radar sobre o norte da Ilha, ao lado da refletividade simulada"><figcaption>Relatos de granizo noturno e trajetória do núcleo no radar Morro da Igreja (esquerda). Comparação com WRF no slide 8.</figcaption></figure>
</div>""", notas='Apresentar o evento noturno real (22:00–23:00 UTC / 19–20h local) e os dados de radar/satélite rastreados em granizo-gigante.'),

    dict(t='Da Parte 1 para a Parte 2', s='A sondagem de Florianópolis na véspera', tempo='00 a 03 min', corpo="""
<div class="duas">
  <div>
    <ul>
      <li><b>SBFL 83899, 28/08/2026 12Z:</b> MUCAPE de 1303,5 J/kg, SBCAPE de 442,8 J/kg e água precipitável de 40,9 mm.</li>
      <li><b>Matriz de Emanuel:</b> no modo reversível, que retém a água condensada na parcela, a flutuabilidade cai muito em relação ao pseudoadiabático.</li>
      <li><b>Pergunta da Parte 2:</b> onde o modelo guarda essa água e esse gelo dentro da nuvem, e isso basta para fazer granizo grande?</li>
    </ul>
  </div>
  <figure><img src="metpack/emanuel_20260828.png" alt="Matriz de flutuabilidade de Emanuel para a sondagem de Florianópolis de 28/08/2026 12Z"><figcaption>Flutuabilidade de Emanuel, SBFL 28/08/2026 12Z (Parte 1).</figcaption></figure>
</div>""", notas='Ligar com a Parte 1 em um minuto: a carga de condensado reduz o empuxo. A Parte 2 mostra essa carga em 3D.'),

    dict(t='Desenho da grade', s='Três domínios aninhados: 18, 6 e 2 km', tempo='03 a 06 min', corpo="""
<div class="duas">
  <figure><img src="figuras/dominios.png" alt="Três domínios aninhados do WRF sobre o relevo, centrados no norte da Ilha"><figcaption>Cada domínio com o relevo na sua resolução: no centro, o de 2 km (HGT_M do WPS).</figcaption></figure>
  <div>
    <table class="tab">
      <tr><th>Domínio</th><th>dx</th><th>Pontos</th><th>Área</th></tr>
      <tr><td>d01</td><td>18 km</td><td>38 × 38</td><td>666 × 666 km</td></tr>
      <tr><td>d02</td><td>6 km</td><td>49 × 49</td><td>288 × 288 km</td></tr>
      <tr><td>d03</td><td>2 km</td><td>61 × 61</td><td>120 × 120 km</td></tr>
    </table>
    <ul>
      <li><b>Regra dos 2/3:</b> no d01 e no d02 a Ilha fica a 2/3 da largura para leste e para norte, deixando dentro da grade a área a oeste e a sul, de onde a convecção vem. O d03 fica centrado na Ilha.</li>
      <li>Razão 3, <code>feedback = 1</code>, 45 níveis até 50 hPa.</li>
      <li>ERA5 a cada 1 h, de 12:00 de 29/08 a 00:00 de 30/08 UTC: 10 h antes do granizo observado.</li>
      <li>O d01 ficou pequeno porque o recorte do ERA5 disponível não cobria mais que isso (o <code>metgrid</code> acusava valores ausentes).</li>
    </ul>
  </div>
</div>""", notas='Mostrar que o requisito de 3 km ou menos foi cumprido e explicar por que o d01 é pequeno: limitação de dado, não escolha física.'),

    dict(t='A combinação da namelist.input', s='Cada escolha com a sua justificativa', tempo='03 a 06 min', corpo="""
<table class="tab larga">
  <tr><th>Opção</th><th>Escolha</th><th>Por quê</th></tr>
  <tr><td>Microfísica</td><td>Milbrandt-Yau 2 momentos (<code>mp_physics = 9</code>)</td><td>Separa graupel (<code>QGRAUP</code>) e granizo (<code>QHAIL</code>) e prevê o número de partículas.</td></tr>
  <tr><td>Cumulus</td><td>Kain-Fritsch em d01 e d02, desligado em d03 (<code>1, 1, 0</code>)</td><td>Em 2 km as ascendentes são resolvidas; nos externos, a convecção precisa ser parametrizada.</td></tr>
  <tr><td>Camada limite</td><td>YSU (<code>bl_pbl_physics = 1</code>)</td><td>Mistura não local, adequada à camada limite diurna antes da convecção.</td></tr>
  <tr><td>Superfície</td><td>MM5 e Noah (<code>1</code> e <code>2</code>)</td><td>Fluxos de superfície com solo de 4 camadas.</td></tr>
  <tr><td>Radiação</td><td>RRTMG onda longa e curta (<code>4, 4</code>), <code>radt = 15</code></td><td>Interação com nuvem e gelo (<code>icloud = 1</code>).</td></tr>
  <tr><td>Passo de tempo</td><td>Adaptativo, <code>target_cfl = 1.2</code></td><td>Mantém o CFL nas ascendentes e grava a cada 15 min no d03.</td></tr>
  <tr><td>Diagnósticos</td><td><code>do_radar_ref = 1</code>, <code>hailcast_opt = 0, 0, 1</code></td><td>Refletividade para comparar com o radar; tamanho do granizo no d03.</td></tr>
</table>""", notas='Não ler a tabela inteira: destacar microfísica e cumulus, que são as escolhas que mais pesam no resultado.'),

    dict(t='Microfísica em 3D', s='Animação 360°: Decomposição Anatômica (Despindo e Vestindo as Camadas)', tempo='06 a 10 min', corpo=f"""
<div class="duas">
  <div>
    <video src="figuras/granizo_3d_evolucao.mp4" poster="figuras/3d_todos.png" controls loop muted playsinline preload="auto" style="width:100%; border-radius:8px;"></video>
    <p class="leg"><b>Órbita 360° e Decomposição em Camadas:</b> Rotação circular contínua ao redor da tempestade sobre o relevo da Ilha de SC. Mostra as 4 etapas: (1) Evolução temporal inicial; (2) <i>Despindo a tempestade</i> no pico (remove nuvem, depois chuva, isolando água super-resfriada verde, graupel laranja e granizo vermelho); (3) <i>Vestindo a tempestade</i> de dentro para fora a partir do núcleo de granizo; (4) Órbita final completa da supercélula reconstituída. Disponível também em <a href="figuras/granizo_3d_evolucao.gif" target="_blank">GIF animado</a>.</p>
  </div>
  <div>
    <div class="abas" role="group" aria-label="Hidrometeoro">{abas}</div>
    <figure><img id="img3d" src="figuras/3d_todos.png" alt="Hidrometeoros em 3D às {HORA} UTC sobre a Ilha"><figcaption>{HORA} UTC, célula sobre a Ilha, ParaView, z = (PH + PHB)/9,81, exagero vertical 4×, limiares na legenda.</figcaption></figure>
  </div>
</div>""", notas='Executar o vídeo 360° destacando as fases em que as camadas são despidas (revelando o núcleo interno de granizo e SLW) e vestidas de volta de dentro para fora.'),

    dict(t='Corte vertical e máximos', s=f'A célula sobre a Ilha, {HORA} UTC', tempo='06 a 10 min', corpo=f"""
<div class="duas">
  <figure><img src="figuras/corte_vertical.png" alt="Corte vertical oeste-leste com graupel, granizo, água super-resfriada, velocidade vertical e isotermas"><figcaption>Graupel sombreado, granizo em vermelho, SLW em verde, W em preto, isotermas de 0, −20 e −40 °C.</figcaption></figure>
  <div>
    <table class="tab"><tr><th>Hidrometeoro</th><th>Máx (g/kg)</th><th>Altura (km)</th><th>T (°C)</th></tr>{linhas_tab}</table>
    <p class="destaque">Isoterma de 0 °C a {num(M['z_isoterma_0C_km'], 2)} km. A SLW chega a {num(TAB['SLW']['max_g_kg'], 2)} g/kg a {num(TAB['SLW']['altura_km'], 1)} km; o graupel tem o máximo de {num(TAB['QGRAUP']['max_g_kg'], 2)} g/kg a {num(TAB['QGRAUP']['altura_km'], 1)} km e o granizo, só {num(TAB['QHAIL']['max_g_kg'], 2)} g/kg, a {num(TAB['QHAIL']['altura_km'], 1)} km, já no 0 °C, derretendo.</p>
  </div>
</div>""", notas='A água super-resfriada existe, mas o granizo é pouco e fica baixo, perto do 0 °C. Pergunta para a banca: falta água ou falta ascendente?'),

    dict(t='Evolução no tempo', s='Duas ondas de convecção, cedo demais', tempo='10 a 14 min', corpo=f"""
<div class="duas">
  <div>
    <div class="grafico" id="serie" role="img" aria-label="Série temporal de refletividade máxima, velocidade vertical máxima e graupel e granizo máximos no domínio interno"></div>
    <p class="leg">Máximos no d03 a cada 15 min. Faixa cinza: janela do granizo observado (22:00 a 23:00 UTC).</p>
  </div>
  <div>
    <ul>
      <li><b>Primeira onda:</b> {num(pico_z['z'])} dBZ às {pico_z['h']} UTC.</li>
      <li><b>A onda que cruzou a Ilha:</b> às {HORA} UTC, {num(foco['z'])} dBZ, com graupel e granizo sobre a Ilha.</li>
      <li><b>Segunda onda:</b> de 15:30 a 17:15 UTC; às 16:15 e 16:30 volta a passar perto da Ilha, com até 45 dBZ a 25 km de Jurerê.</li>
      <li><b>Ascendente mais forte:</b> {num(pico_w['w'])} m/s às {pico_w['h']} UTC.</li>
      <li><b>Na hora do granizo (22:30):</b> {num(obs['z'])} dBZ, sem graupel nem granizo.</li>
      <li><b>HAILCAST:</b> {num(hailcast)} mm perto da Ilha. Às 15:45 e 16:00, sobre o mar, deu até {num(hailcast_bruto, 0)} mm, valor impossível (falha do diagnóstico), que não usamos.</li>
    </ul>
  </div>
</div>""", notas='A convecção do modelo aconteceu, mas 5 a 9 horas antes e fora do lugar. Às 22:30 o domínio está calmo.'),

    dict(t='Comparação com a observação', s='Discrepância Temporal: Tarde Simulada vs. Noite Real', tempo='10 a 14 min', corpo=f"""
<figure class="cheia"><img src="figuras/comparacao_obs.png" alt="Observação ao lado da refletividade simulada às 22:30 UTC"><figcaption>22:30 UTC: relatos noturnos e radar Morro da Igreja (esquerda) contra a calmaria na refletividade simulada no d03 (direita).</figcaption></figure>
<p class="destaque">Às 22:30 UTC (horário real da tempestade severa), o eco simulado mais forte no d03 tem apenas {num(obs['z'])} dBZ, a {num(M['erro_distancia_obs_km'])} km do norte da Ilha. No modelo controle, a convecção vigorosa ocorreu durante a tarde (ondas às {HORA} UTC e 15:30–17:15 UTC), esgotando a CAPE e deixando a noite estável.</p>""",
         notas='Enfatizar a diferença temporal: o evento severo real foi noturno (22–23h UTC), enquanto a rodada de controle simulou convecção antecipada na tarde.'),

    dict(t='Deficiências do modelo e Ensembles', s='Sensibilidade Convectiva: Kain-Fritsch vs. Grell-Freitas', tempo='14 a 17 min', corpo=f"""
<div class="duas">
  <div>
    <h3>Por que a rodada controle errou a hora?</h3>
    <ul>
      <li><b>Disparo prematuro por Kain-Fritsch:</b> nos domínios externos (d01/d02), o esquema KF consumiu a CAPE diurna (13–17h UTC), impedindo que a energia potencial sustentasse a convecção noturna.</li>
      <li><b>Evidência do ensemble <code>granizo-gigante</code>:</b> o teste com 9 membros (E0–E3, F1–F4) mostrou que apenas as rodadas com <b>Grell-Freitas (GF)</b> no d01 conseguiram retardar a convecção e gerar a célula noturna às 21:16–22:16 UTC perto da Ilha, gerando granizo de até 39 mm.</li>
      <li><b>Condição inicial ERA5:</b> suaviza a inibição por camada de inversão costeira que manteve o evento real contido até a noite.</li>
    </ul>
  </div>
  <div>
    <h3>Por que o granizo não atingiu 6 cm?</h3>
    <ul>
      <li><b>Ascendente subestimada:</b> às {HORA} UTC, W máx foi de {num(foco['w'])} m/s (máx do dia: {num(pico_w['w'])} m/s). Pedras de 5 a 6 cm exigem correntes ascendentes de 30 a 45 m/s.</li>
      <li><b>Tempo de residência e fusão:</b> o granizo simulado atinge pico logo acima do 0 °C e derrete antes do solo; perto da Ilha o HAILCAST do controle foi de {num(hailcast)} mm.</li>
      <li><b>Resolução de 2 km:</b> dilui o gradiente de pressão e os núcleos supercelulares; uma grade de 1 km com microfísica de 2 momentos e parametrização GF nos externos reproduz melhor a célula noturna.</li>
    </ul>
  </div>
</div>
<p class="destaque">Solução identificada na literatura e em <code>granizo-gigante</code>: cumulus Grell-Freitas nos domínios externos (ou convecção explícita em 1–3 km direto do oeste) preserva a instabilidade para a supercélula noturna.</p>""",
         notas='Apresentar o diagnóstico físico da falha temporal e conectar com o resultado do ensemble com Grell-Freitas de granizo-gigante.'),

    dict(t='Conclusões', s='O que a modelagem ensinou', tempo='17 a 20 min', corpo="""
<div class="duas">
  <ul>
    <li>Com convecção explícita em 2 km e microfísica de 2 momentos, o WRF separa graupel, granizo e água super-resfriada e mostra onde cada um fica.</li>
    <li>A nuvem simulada tinha água super-resfriada, mas a ascendente foi fraca demais para fazer granizo grande.</li>
    <li>A convecção veio horas antes e fora do lugar; as causas possíveis estão na configuração dos domínios externos e na condição inicial.</li>
    <li>O erro do modelo é o resultado mais útil: mostra o que ele não reproduz num dia de granizo gigante.</li>
  </ul>
  <div class="links">
    <h3>Para a arguição</h3>
    <a href="index.html#sec-wrf-parte2">Página da Parte 2 no site</a>
    <a href="https://github.com/reinaldohaas/tarefa-meso/blob/master/RELATORIO_RODADA.md" target="_blank" rel="noopener">RELATORIO_RODADA.md</a>
    <a href="https://github.com/reinaldohaas/tarefa-meso/blob/master/rodadas/r1_milbrandt_yau_2km/namelist.input" target="_blank" rel="noopener">namelist.input</a>
    <a href="https://github.com/reinaldohaas/tarefa-meso/blob/master/wps/namelist.wps" target="_blank" rel="noopener">namelist.wps</a>
    <a href="apresentacao/apresentacao_wrf_granizo.pptx">Slides em PowerPoint</a>
    <a href="https://github.com/reinaldohaas/tarefa-meso/blob/master/TAREFA_WRF_HIDROMETEOROS.md" target="_blank" rel="noopener">Enunciado da tarefa</a>
  </div>
</div>""", notas='Fechar em três frases e abrir para perguntas, com a página do GitHub aberta.'),
]

secoes = ''
for i, s in enumerate(SLIDES, 1):
    secoes += f"""
<section class="slide" id="s{i}" aria-label="Slide {i} de {len(SLIDES)}: {s['t']}"{'' if i == 1 else ' hidden'}>
  <header><div><p class="num">{i}/{len(SLIDES)}</p><h2>{s['t']}</h2><p class="sub">{s['s']}</p></div><p class="tempo">{s['tempo']}</p></header>
  <div class="corpo">{s['corpo']}</div>
  <aside class="notas"><b>Roteiro de fala:</b> {s['notas']}</aside>
</section>"""

html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Parte 2: WRF e granizo</title>
<style>
:root {{ --fundo:#f6f7f9; --papel:#ffffff; --texto:#17202b; --suave:#5b6876; --linha:#dbe1e8; --acento:#c2410c; --acento-f:#fff1e8; --cinza:#e9edf2; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --fundo:#0e1318; --papel:#151c23; --texto:#e7ecf1; --suave:#9aa7b4; --linha:#2a343e; --acento:#fb8a4c; --acento-f:#2a1c14; --cinza:#1e2730; }} }}
:root[data-theme="dark"] {{ --fundo:#0e1318; --papel:#151c23; --texto:#e7ecf1; --suave:#9aa7b4; --linha:#2a343e; --acento:#fb8a4c; --acento-f:#2a1c14; --cinza:#1e2730; }}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; background:var(--fundo); color:var(--texto); font:17px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }}
.barra {{ position:sticky; top:0; z-index:5; display:flex; align-items:center; gap:10px; padding:8px 16px; background:var(--papel); border-bottom:1px solid var(--linha); }}
.barra .titulo {{ font-weight:700; margin-right:auto; font-size:15px; }}
.barra button, .barra a {{ font:inherit; font-size:14px; color:var(--texto); background:var(--cinza); border:1px solid var(--linha); border-radius:6px; padding:5px 10px; cursor:pointer; text-decoration:none; }}
.barra button:focus-visible, .barra a:focus-visible, .abas button:focus-visible {{ outline:2px solid var(--acento); outline-offset:2px; }}
.pontos {{ display:flex; gap:4px; }}
.pontos button {{ width:26px; padding:4px 0; text-align:center; }}
.pontos button[aria-current="true"] {{ background:var(--acento); color:#fff; border-color:var(--acento); }}
main {{ max-width:1280px; margin:0 auto; padding:16px; }}
.slide {{ background:var(--papel); border:1px solid var(--linha); border-radius:12px; padding:22px 28px; min-height:calc(100vh - 90px); display:flex; flex-direction:column; gap:14px; }}
.slide[hidden] {{ display:none; }}
.slide header {{ display:flex; justify-content:space-between; gap:12px; border-bottom:2px solid var(--acento); padding-bottom:10px; }}
.num {{ margin:0; color:var(--acento); font-weight:700; font-size:14px; }}
h2 {{ margin:2px 0 0; font-size:30px; line-height:1.15; }}
.sub {{ margin:4px 0 0; color:var(--suave); }}
.tempo {{ margin:0; white-space:nowrap; color:var(--suave); font-size:14px; }}
h3 {{ margin:0 0 6px; font-size:19px; }}
.corpo {{ flex:1; }}
.duas {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; align-items:start; }}
ul {{ margin:0; padding-left:20px; }} li {{ margin:6px 0; }}
figure {{ margin:0; }} figure img, video {{ width:100%; border:1px solid var(--linha); border-radius:8px; background:#0b1324; display:block; }}
figure.cheia img {{ max-height:62vh; object-fit:contain; background:#fff; }}
figcaption, .leg {{ color:var(--suave); font-size:14px; margin-top:6px; }}
.destaque {{ background:var(--acento-f); border-left:4px solid var(--acento); padding:10px 14px; border-radius:6px; margin:12px 0 0; }}
.tab {{ border-collapse:collapse; width:100%; font-size:15px; }} .tab th, .tab td {{ border:1px solid var(--linha); padding:6px 9px; text-align:left; vertical-align:top; }}
.tab th {{ background:var(--cinza); }}
code {{ font-size:0.9em; background:var(--cinza); padding:1px 4px; border-radius:4px; }}
.abas {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px; }}
.abas button {{ font:inherit; font-size:13px; padding:4px 9px; border-radius:6px; border:1px solid var(--linha); background:var(--papel); color:var(--texto); cursor:pointer; }}
.abas button[aria-pressed="true"] {{ background:var(--acento); border-color:var(--acento); color:#fff; }}
.links {{ display:grid; gap:8px; }} .links a {{ color:var(--acento); font-weight:600; }}
a {{ color:var(--acento); }}
.notas {{ display:none; border-top:1px dashed var(--linha); padding-top:10px; color:var(--suave); font-size:15px; }}
body.com-notas .notas {{ display:block; }}
.grafico svg {{ width:100%; height:auto; display:block; }}
.grafico text {{ fill:var(--suave); font-size:11px; }}
.tab td, .tab th {{ overflow-wrap:anywhere; }}
@media (max-width: 860px) {{ .tab {{ font-size:13px; }} .tab th, .tab td {{ padding:5px 6px; }} .duas {{ grid-template-columns:1fr; }} h2 {{ font-size:24px; }} .slide {{ padding:16px; min-height:auto; }} .barra .titulo {{ display:none; }} .pontos {{ display:none; }} }}
@media print {{ .barra {{ display:none; }} .slide {{ display:flex !important; break-after:page; min-height:auto; }} .slide[hidden] {{ display:flex !important; }} }}
</style>
</head>
<body>
<nav class="barra" aria-label="Navegação dos slides">
  <span class="titulo">Seminário Final, Parte 2: WRF e granizo (FSC7116, UFSC)</span>
  <button type="button" id="ant" aria-label="Slide anterior">◀</button>
  <div class="pontos" id="pontos"></div>
  <button type="button" id="prox" aria-label="Próximo slide">▶</button>
  <button type="button" id="notas" aria-pressed="false">Roteiro (N)</button>
  <button type="button" id="cheia">Tela cheia (F)</button>
  <a href="index.html#sec-wrf-parte2">Voltar ao site</a>
</nav>
<main>{secoes}
</main>
<script>
const SERIE = {json.dumps(serie, ensure_ascii=False)};
const slides = [...document.querySelectorAll('.slide')];
const pontos = document.getElementById('pontos');
slides.forEach((s, i) => {{ const b = document.createElement('button'); b.type = 'button'; b.textContent = i + 1; b.setAttribute('aria-label', 'Ir ao slide ' + (i + 1)); b.onclick = () => vai(i); pontos.appendChild(b); }});
let atual = 0;
function vai(i) {{
  atual = Math.max(0, Math.min(slides.length - 1, i));
  slides.forEach((s, k) => {{ s.hidden = k !== atual; if (k !== atual) s.querySelectorAll('video').forEach(v => v.pause()); }});
  [...pontos.children].forEach((b, k) => b.setAttribute('aria-current', k === atual ? 'true' : 'false'));
  history.replaceState(null, '', '#' + (atual + 1));
  window.scrollTo(0, 0);
}}
document.getElementById('ant').onclick = () => vai(atual - 1);
document.getElementById('prox').onclick = () => vai(atual + 1);
const bn = document.getElementById('notas');
bn.onclick = () => {{ const on = document.body.classList.toggle('com-notas'); bn.setAttribute('aria-pressed', on); }};
document.getElementById('cheia').onclick = () => document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
document.addEventListener('keydown', e => {{
  if (e.target.closest('video, input, textarea')) return;
  if (['ArrowRight', 'PageDown', ' '].includes(e.key)) {{ e.preventDefault(); vai(atual + 1); }}
  else if (['ArrowLeft', 'PageUp'].includes(e.key)) {{ e.preventDefault(); vai(atual - 1); }}
  else if (e.key === 'Home') vai(0);
  else if (e.key === 'End') vai(slides.length - 1);
  else if (e.key === 'n' || e.key === 'N') bn.click();
  else if (e.key === 'f' || e.key === 'F') document.getElementById('cheia').click();
}});
document.querySelectorAll('.abas button').forEach(b => b.onclick = () => {{
  document.querySelectorAll('.abas button').forEach(x => x.setAttribute('aria-pressed', 'false'));
  b.setAttribute('aria-pressed', 'true');
  document.getElementById('img3d').src = 'figuras/3d_' + b.dataset.h + '.png';
}});
// Série temporal: refletividade (eixo esquerdo), W, graupel e granizo (eixo direito)
(function () {{
  const W = 640, H = 330, m = {{ l: 44, r: 44, t: 16, b: 48 }}, n = SERIE.length;
  const x = i => m.l + i * (W - m.l - m.r) / (n - 1);
  const yz = v => H - m.b - Math.max(0, v) / 70 * (H - m.t - m.b);
  const yw = v => H - m.b - v / 14 * (H - m.t - m.b);
  const linha = (f, cor, tr) => '<path fill="none" stroke="' + cor + '" stroke-width="2.2"' + (tr ? ' stroke-dasharray="5 3"' : '') + ' d="' + SERIE.map((s, i) => (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + f(s).toFixed(1)).join(' ') + '"/>';
  const i0 = SERIE.findIndex(s => s.h === '22:00'), i1 = SERIE.findIndex(s => s.h === '23:00');
  let svg = '<svg viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg">';
  svg += '<rect x="' + x(i0) + '" y="' + m.t + '" width="' + (x(i1) - x(i0)) + '" height="' + (H - m.t - m.b) + '" fill="currentColor" opacity="0.08"/>';
  [0, 20, 40, 60].forEach(v => svg += '<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + yz(v) + '" y2="' + yz(v) + '" stroke="currentColor" opacity="0.12"/><text x="' + (m.l - 6) + '" y="' + (yz(v) + 4) + '" text-anchor="end">' + v + '</text>');
  [0, 4, 8, 12].forEach(v => svg += '<text x="' + (W - m.r + 6) + '" y="' + (yw(v) + 4) + '">' + v + '</text>');
  SERIE.forEach((s, i) => {{ if (s.h.endsWith(':00') && +s.h.slice(0, 2) % 2 === 0) svg += '<text x="' + x(i) + '" y="' + (H - m.b + 16) + '" text-anchor="middle">' + s.h + '</text>'; }});
  svg += linha(s => yz(s.z), '#c2410c') + linha(s => yw(s.w), '#2563eb') + linha(s => yw(s.g), '#d97706', true) + linha(s => yw(s.q * 4), '#b91c1c', true);
  svg += '<text x="' + m.l + '" y="' + (H - 8) + '">dBZ (esq.): refletividade · eixo dir.: W (m/s), graupel (g/kg), granizo × 4 (g/kg)</text>';
  const el = document.getElementById('serie'); el.style.color = getComputedStyle(document.body).color; el.innerHTML = svg + '</svg>';
  const leg = [['refletividade', '#c2410c'], ['W', '#2563eb'], ['graupel', '#d97706'], ['granizo × 4', '#b91c1c']];
  el.insertAdjacentHTML('beforeend', '<p class="leg">' + leg.map(l => '<span style="color:' + l[1] + '">■</span> ' + l[0]).join(' &nbsp; ') + '</p>');
}})();
const h = parseInt(location.hash.slice(1), 10);
vai(Number.isFinite(h) ? h - 1 : 0);
</script>
</body>
</html>
"""
with open(os.path.join(REPO, 'apresentacao_parte2.html'), 'w', encoding='utf-8') as f:
    f.write(html)
print('->', os.path.abspath(os.path.join(REPO, 'apresentacao_parte2.html')), f'{len(html) / 1e3:.0f} kB',
      '| travessões:', html.count('—'))
