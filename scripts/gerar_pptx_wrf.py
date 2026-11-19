# -*- coding: utf-8 -*-
r"""
Gera apresentacao/apresentacao_wrf_granizo.pptx (10 slides cronometrados para 20 minutos,
seguindo a Seção 10 de TAREFA_WRF_HIDROMETEOROS.md) para o projeto C:\gis4wrf\projects\granizo
e sincroniza em C:\Users\haas\github\tarefa-meso\apresentacao\apresentacao_wrf_granizo.pptx.
"""
import os
import json
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

BASE = r'C:\gis4wrf\projects\granizo'
REPO = r'C:\Users\haas\github\tarefa-meso'

C_BG = RGBColor(11, 19, 43)
C_CARD = RGBColor(19, 30, 58)
C_BORDER = RGBColor(46, 64, 102)
C_WHITE = RGBColor(248, 250, 252)
C_MUTED = RGBColor(148, 163, 184)
C_CYAN = RGBColor(56, 189, 248)
C_AMBER = RGBColor(251, 191, 36)


def bg(slide):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    s.fill.solid()
    s.fill.fore_color.rgb = C_BG
    s.line.fill.background()


def header(slide, title, subtitle, badge_txt, num):
    hb = slide.shapes.add_textbox(Inches(0.6), Inches(0.25), Inches(8.2), Inches(0.35))
    p = hb.text_frame.paragraphs[0]
    p.text = "UFSC • FSC7116 METEOROLOGIA DE MESOESCALA • SEMINÁRIO FINAL (PARTE 2: WRF)"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.6), Inches(0.22), Inches(3.1), Inches(0.4))
    b.fill.solid()
    b.fill.fore_color.rgb = RGBColor(30, 41, 59)
    b.line.color.rgb = C_AMBER
    pb = b.text_frame.paragraphs[0]
    pb.text = f"⏱ {badge_txt} | Slide {num}/10"
    pb.alignment = PP_ALIGN.CENTER
    pb.font.size = Pt(9.5)
    pb.font.bold = True
    pb.font.color.rgb = C_AMBER

    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.62), Inches(12.1), Inches(0.5))
    pt = tb.text_frame.paragraphs[0]
    pt.text = title
    pt.font.size = Pt(19)
    pt.font.bold = True
    pt.font.color.rgb = C_WHITE

    sb = slide.shapes.add_textbox(Inches(0.6), Inches(1.12), Inches(12.1), Inches(0.35))
    ps = sb.text_frame.paragraphs[0]
    ps.text = subtitle
    ps.font.size = Pt(11)
    ps.font.color.rgb = C_MUTED


def add_bullets_card(slide, left, top, width, height, heading, bullets):
    c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    c.fill.solid()
    c.fill.fore_color.rgb = C_CARD
    c.line.color.rgb = C_BORDER
    c.line.width = Pt(1.2)

    tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.15), Inches(width - 0.4), Inches(height - 0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = heading
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.space_after = Pt(8)

    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(10.8)
        p.font.color.rgb = C_WHITE
        p.space_after = Pt(6)


def add_image_card(slide, img_path, left, top, width, height, caption=""):
    c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    c.fill.solid()
    c.fill.fore_color.rgb = RGBColor(15, 23, 42)
    c.line.color.rgb = C_BORDER
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(left + 0.12), Inches(top + 0.12), width=Inches(width - 0.24))
    if caption:
        cb = slide.shapes.add_textbox(Inches(left + 0.12), Inches(top + height - 0.42), Inches(width - 0.24), Inches(0.35))
        cb.text_frame.word_wrap = True
        p = cb.text_frame.paragraphs[0]
        p.text = caption
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_MUTED


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    fig_dir = os.path.join(BASE, 'figuras')

    slides_data = [
        ("Slide 1: O Caso Severo: Granizo no Norte da Ilha de SC (29/08/2026)",
         "Relatos de superfície, satélite GOES-19 (Canal 13 e GLM) e radar do Morro da Igreja",
         "00 a 03 min",
         "Cronologia e Evidências Observacionais (22:00–23:00 UTC)",
         [
             "Evento severo em 29/08/2026 entre 22:00 e 23:00 UTC (19:00–20:00 BRT) na Grande Florianópolis.",
             "Relatos de granizo (até 60 mm): Biguaçu (22:00–22:30Z), Jurerê/Canasvieiras (22:00–22:30Z), Cachoeira do Bom Jesus (22:50Z) e Ingleses/Vargem (22:40–23:00Z).",
             "Satélite GOES-19 (10,3 µm): topo mais frio de -62,9 °C às 22:20 UTC sobre o Norte da Ilha, igual ao das outras células e sem topo penetrante; até 320 flashes por 10 min no GLM, sem salto de raios.",
             "Radar Morro da Igreja: núcleo convectivo severo cruzando o estreito norte e a Ilha entre 22:16Z e 22:36Z.",
         ],
         os.path.join(fig_dir, 'comparacao_obs.png'),
         "Localização dos relatos de granizo (1–4), caixa do GOES-19 e trajetória do Radar Morro da Igreja"),

        ("Slide 2: Conexão com a Parte 1: Sondagem Pré-Convectiva e Flutuabilidade",
         "Sondagem de Florianópolis (SBFL 83899) e o efeito da carga de água/gelo condensado",
         "00 a 03 min",
         "Da Termodinâmica 1D (Emanuel) à Nuvem 3D (WRF)",
         [
             "Sondagem precursora (SBFL 83899 em 28/08/2026 12Z): MUCAPE = 1303,5 J/kg, SBCAPE = 442,8 J/kg e PW = 40,9 mm.",
             "Matriz de Emanuel (Parte 1): a retenção da água condensada (modo reversível) reduz a flutuabilidade positiva em relação ao modo pseudoadiabático.",
             "Equação da flutuabilidade: B = g [ (Tv - Tv_amb)/Tv_amb - (r_l + r_i) ].",
             "Pergunta científica da Parte 2: Onde a água super-resfriada (SLW), o graupel (QGRAUP) e o granizo (QHAIL) ficam suspensos em 3D dentro da nuvem simulada?",
         ],
         os.path.join(REPO, 'metpack', 'emanuel_20260828.png'),
         "Matriz de flutuabilidade de Emanuel (28/08/2026 12Z): modo reversível (esq.) vs. pseudoadiabático (dir.)"),

        ("Slide 3: Configuração dos Domínios (WPS: 18 / 6 / 2 km)",
         "Três domínios aninhados com razão 1:3 e convecção explícita no domínio interno",
         "03 a 06 min",
         "Arquitetura da grade",
         [
             "Projeção Lambert Conformal centrada no Norte da Ilha (-27,50°S, -48,55°W), max_dom = 3, feedback = 1.",
             "d01 (18 km): 38×38 pontos (666×666 km), contido 100% no recorte regional do ERA5 (37 níveis, 1 h).",
             "d02 (6 km): 46×46 pontos (270×270 km), transição sobre o leste de SC e oceano adjacente.",
             "d03 (2 km <= 3 km): 61×61 pontos (120×120 km), garantindo 60 km de folga até as bordas.",
             "45 níveis verticais eta até 50 hPa; 10 h de spin-up antes do evento (início 12:00 UTC) e saída a cada 15 min em d03.",
         ],
         os.path.join(fig_dir, 'dominios.png'),
         "Três domínios aninhados (18 / 6 / 2 km) sobre a topografia HGT_M do WPS"),

        ("Slide 4: Física Escolhida e Justificativa (namelist.input)",
         "Esquema Milbrandt-Yau de 2 momentos, desligamento do cumulus em 2 km e controle de CFL",
         "03 a 06 min",
         "Combinação Física da Rodada r1_milbrandt_yau_2km",
         [
             "Microfísica Milbrandt-Yau 2 momentos (mp_physics = 9): separa explicitamente Graupel (QGRAUP, 400 kg/m³) e Granizo (QHAIL, 900 kg/m³) em categorias distintas.",
             "Cumulus (cu_physics = 1, 1, 0): Kain-Fritsch em d01/d02 e DESLIGADO em d03 (2 km) para convecção explícita.",
             "Refletividade e Granizo: do_radar_ref = 1 (REFL_10CM) e hailcast_opt = 0, 0, 1 (modelo 1D HAILCAST em d03).",
             "Camada limite e superfície: YSU PBL (bl_pbl_physics = 1), Monin-Obukhov (sf_sfclay = 1) e Noah LSM (sf_surface = 2).",
             "Radiação e Passo de Tempo: RRTMG LW/SW (ra = 4, icloud = 1) e passo adaptativo (target_cfl = 1.2, dt ~ 16 s em d03).",
         ],
         os.path.join(fig_dir, '3d_QHAIL.png'),
         "Isosuperfície 3D do Granizo separado (QHAIL >= 0,1 g/kg) prevista pelo esquema Milbrandt-Yau"),

        ("Slide 5: Microfísica em 3D no ParaView: Todos os Hidrometeoros e SLW",
         "Reconstrução na altura geométrica real z = (PH + PHB)/9,81 com exagero vertical de 4x",
         "06 a 10 min",
         "Estratificação Tridimensional da Tempestade (17:00 UTC)",
         [
             "Coordenada vertical real z = (PH + PHB)/g (km MSL) e temperatura física T = (T_wrf + 300)*(p/100000)^0,2854.",
             "Água Super-resfriada (SLW = QCLOUD + QRAIN para T < 0 °C, verde): máximo de 2,87 g/kg a 5,69 km (-6,6 °C), combustível da acreção.",
             "Graupel (QGRAUP, laranja): domina a meia-alta troposfera com máximo de 6,12 g/kg a 8,26 km (-23,5 °C).",
             "Granizo (QHAIL, vermelho): concentra-se na base da camada super-resfriada (0,55 g/kg a 4,65 km, -0,7 °C).",
             "Bigorna superior: Cristais de gelo (QICE, ciano, 0,56 g/kg) e Neve (QSNOW, lilás, 0,46 g/kg) em 9,88 km (-36,6 °C).",
         ],
         os.path.join(fig_dir, '3d_todos.png'),
         "Estrutura 3D combinada no ParaView (17:00 UTC): 7 classes hidrometeóricas com cores fixas e limiares"),

        ("Slide 6: Corte Vertical pela Célula Mais Vigorosa e Tabela de Máximos",
         "Acoplamento entre corrente ascendente W, SLW, QGRAUP, QHAIL e isotermas de 0, -20 e -40 °C",
         "06 a 10 min",
         "Diagnóstico do Corte Vertical Oeste–Leste (-27,54°S, -48,02°W)",
         [
             "Isotermas: 0 °C em z = 4,4 km; -20 °C em z = 7,5 km; -40 °C (nucleação homogênea) em z = 10,3 km.",
             "A corrente ascendente W (contornos pretos até 7,4 m/s) sustenta o bolso de SLW (contornos verdes) entre 4,4 e 9,5 km.",
             "Núcleo de QGRAUP (sombreado laranja, 6,12 g/kg) cresce entre -15 e -30 °C acima do núcleo de SLW.",
             "Núcleo de QHAIL (contornos vermelhos, 0,55 g/kg) cai através da isoterma de 0 °C até 2,7 km, onde derrete e origina o máximo de chuva QRAIN (0,43 g/kg a 2,46 km, +13,4 °C).",
         ],
         os.path.join(fig_dir, 'corte_vertical.png'),
         "Corte vertical Oeste–Leste pela célula mais vigorosa às 17:00 UTC"),

        ("Slide 7: Refletividade Composta (REFL_10CM) e Evolução Temporal",
         "Desenvolvimento dos pulsos convectivos no domínio interno de 2 km",
         "10 a 14 min",
         "Evolução da Convecção Explícita em d03 (12:00 a 00:00 UTC)",
         [
             "1º Pulso (12:45–13:30 UTC): disparo rápido pós-inicialização com 43,1 dBZ sobre o Norte da Ilha e 60,3 dBZ no domínio.",
             "2º Pulso Maduro (15:45–17:30 UTC): célula vigorosa a leste da Ilha (-27,54°S, -48,02°W) atinge 52,3 dBZ às 17:00 UTC (eco >= 50 dBZ contornado em preto).",
             "Período Noturno (20:00–23:00 UTC): após a passagem dos pulsos diurnos, a refletividade no domínio cai para 18–33 dBZ.",
         ],
         os.path.join(fig_dir, 'refletividade.png'),
         "Refletividade máxima na coluna REFL_10CM às 17:00 UTC e série temporal em d03"),

        ("Slide 8: Comparação com a Observação: Erros de Lugar e de Hora",
         "Confronto objetivo entre a simulação WRF e os relatos/radar/GOES-19",
         "10 a 14 min",
         "Quantificação dos Desvios Espaciais e Temporais",
         [
             "Erro de Hora (Fase): o pico convectivo maduro do modelo ocorreu às 17:00 UTC, adiantado em 5,5 horas em relação ao evento severo observado (22:20–22:30 UTC).",
             "Erro de Lugar no Pico (17:00 UTC): a célula de 52,3 dBZ posicionou-se no oceano a ~46 km a leste-sudeste do Norte da Ilha.",
             "Erro de Lugar no Horário Real (22:30 UTC): sobre o Norte da Ilha a refletividade simulada foi de 7,4 dBZ, enquanto o eco máximo de d03 (22,8 dBZ) ficou no continente a 67,2 km a noroeste de Jurerê.",
         ],
         os.path.join(fig_dir, 'comparacao_obs.png'),
         "Painel comparativo às 22:30 UTC: Observação (esquerda) vs. REFL_10CM simulada (direita)"),

        ("Slide 9: Discussão das Deficiências do Modelo: Mecanismos Físicos",
         "Por que a tempestade adiantou e por que o granizo derreteu antes do solo?",
         "14 a 17 min",
         "Análise Crítica da Física e da Configuração Numérica",
         [
             "1. Cumulus nos domínios externos (d01/d02): o esquema Kain-Fritsch liberou a instabilidade convectiva cedo demais à tarde, consumindo a CAPE pré-frontal antes da noite.",
             "2. Suavização do CIN no ERA5 (0,25°): a reanálise subestima a inversão de bloqueio (capping inversion) que segurou o disparo real até as 21:30–22:30 UTC.",
             "3. Resolução de 2 km e Fusão na Camada Quente: em dx = 2 km a ascendente (7,4 a 15 m/s) produz pedras menores de granizo em altitude (0,55 g/kg a 4,65 km), que derretem totalmente ao atravessar os 4,4 km de camada quente abaixo de 0 °C.",
         ],
         os.path.join(fig_dir, '3d_QGRAUP.png'),
         "Pluma 3D de Graupel (QGRAUP >= 0,5 g/kg, máx 6,12 g/kg a 8,26 km)"),

        ("Slide 10: Conclusões, Lições de Modelagem e Repositório no GitHub",
         "Síntese das Partes 1 e 2 e links públicos para arguição da banca",
         "17 a 20 min",
         "Conclusões Físicas e Reprodutibilidade",
         [
             "A microfísica Milbrandt-Yau de 2 momentos (mp_physics = 9) separou com clareza física a SLW (2,87 g/kg), o graupel em meia-alta troposfera (6,12 g/kg a -23,5 °C) e o granizo na zona de transição (0,55 g/kg a -0,7 °C).",
             "A carga combinada de condensados (> 8 g/kg entre 4,5 e 9 km) comprova em 3D a redução de flutuabilidade prevista pelo cálculo reversível de Kerry Emanuel na Parte 1.",
             "Melhorias recomendadas: grade interna <= 1 km, desligar cumulus desde o domínio de 6 km e assimilação de radar/satélite.",
             "Página GitHub Pages: https://reinaldohaas.github.io/tarefa-meso/",
             "Repositório com namelists, scripts, .pvsm e relatório: https://github.com/reinaldohaas/tarefa-meso",
         ],
         os.path.join(fig_dir, '3d_SLW.png'),
         "Isosuperfície 3D da Água Super-resfriada (SLW >= 0,2 g/kg, máx 2,87 g/kg)"),
    ]

    for idx, (tit, sub, tempo, card_h, bullets, img, cap) in enumerate(slides_data, 1):
        sl = prs.slides.add_slide(blank)
        bg(sl)
        header(sl, tit, sub, tempo, idx)
        add_bullets_card(sl, 0.6, 1.65, 6.1, 5.35, card_h, bullets)
        add_image_card(sl, img, 6.9, 1.65, 5.8, 5.35, cap)

    os.makedirs(os.path.join(BASE, 'apresentacao'), exist_ok=True)
    os.makedirs(os.path.join(REPO, 'apresentacao'), exist_ok=True)
    out_base = os.path.join(BASE, 'apresentacao', 'apresentacao_wrf_granizo.pptx')
    out_repo = os.path.join(REPO, 'apresentacao', 'apresentacao_wrf_granizo.pptx')
    prs.save(out_base)
    shutil.copy2(out_base, out_repo)
    print('Salvo PPTX:', out_base)
    print('Copiado para:', out_repo)


if __name__ == '__main__':
    main()
