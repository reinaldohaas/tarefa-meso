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
             "d01 e d02 com a Ilha a 2/3 para leste e para norte: a área a oeste e a sul, de onde vem a convecção, fica dentro da grade.",
             "d02 (6 km): 49×49 pontos (288×288 km).",
             "d03 (2 km <= 3 km): 61×61 pontos (120×120 km), centrado na Ilha.",
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

        ("Slide 5: Microfísica em 3D no ParaView: a célula sobre a Ilha",
         "Altura geométrica real z = (PH + PHB)/9,81, exagero vertical de 4x, cores e limiares fixos",
         "06 a 10 min",
         "A célula que cruzou a Ilha às 12:45 UTC",
         [
             "Horário escolhido pelo granizo perto da Ilha (a até 25 km de Jurerê), não pelo máximo do domínio.",
             "Água super-resfriada (SLW = QCLOUD + QRAIN com T < 0 °C, verde): até 3,77 g/kg a 5,68 km (-5,7 °C).",
             "Graupel (QGRAUP, laranja): 4,92 g/kg a 7,55 km (-18,9 °C), na zona de acreção.",
             "Granizo (QHAIL, vermelho): 0,50 g/kg a 4,73 km, logo acima do 0 °C; gelo (QICE, ciano) no topo, a 9,9 km (-37 °C).",
             "Animação 3D (câmera girando, cada hidrometeoro sozinho) em apresentacao_parte2.html e no site.",
         ],
         os.path.join(fig_dir, '3d_todos.png'),
         "Hidrometeoros em 3D às 12:45 UTC; a linha branca marca a coluna da célula, sobre a Ilha"),

        ("Slide 6: Corte Vertical pela Célula sobre a Ilha e Tabela de Máximos",
         "Corrente ascendente W, SLW, QGRAUP, QHAIL e isotermas de 0, -20 e -40 °C",
         "06 a 10 min",
         "Corte oeste-leste em -27,44°, -48,50° (12:45 UTC), sobre o norte da Ilha",
         [
             "Isotermas: 0 °C a 4,7 km; -20 °C a 7,6 km; -40 °C (nucleação homogênea) a 10,3 km.",
             "A água super-resfriada (verde) envolve o núcleo de graupel entre 4,7 e 9,5 km.",
             "O graupel (laranja, até 4,92 g/kg) tem o máximo a 7,5 km, perto de -20 °C.",
             "O granizo (0,50 g/kg) fica logo acima do 0 °C e derrete ao cair; a chuva tem o máximo a 3,4 km.",
         ],
         os.path.join(fig_dir, 'corte_vertical.png'),
         "Corte vertical oeste-leste pela célula sobre a Ilha às 12:45 UTC"),

        ("Slide 7: Refletividade Composta (REFL_10CM) e Evolução Temporal",
         "Duas ondas de convecção no domínio interno de 2 km, cedo demais",
         "10 a 14 min",
         "Evolução da convecção explícita em d03 (12:00 a 00:00 UTC)",
         [
             "1ª onda (12:45 a 13:30 UTC): cruzou o norte da Ilha com graupel e granizo; até 56 dBZ a 25 km de Jurerê às 13:00.",
             "2ª onda (15:30 a 17:15 UTC): volta a passar perto da Ilha às 16:15 e 16:30, com até 45 dBZ.",
             "Noite (20:00 a 23:00 UTC): refletividade de 18 a 33 dBZ, sem graupel nem granizo.",
         ],
         os.path.join(fig_dir, 'refletividade.png'),
         "Refletividade máxima na coluna às 12:45 UTC e série temporal em d03"),

        ("Slide 8: Comparação com a Observação: Erros de Lugar e de Hora",
         "Simulação contra relatos, radar e GOES-19",
         "10 a 14 min",
         "Quanto o modelo errou",
         [
             "Hora: o granizo simulado sobre a Ilha veio às 12:45 UTC, cerca de 9,5 h antes do observado (22:00 a 23:00 UTC).",
             "Lugar: às 22:30 UTC, o eco simulado mais forte ficava a 69,7 km de Jurerê.",
             "A 2ª onda passou perto da Ilha às 16:15 e 16:30, ainda 6 h antes do observado.",
         ],
         os.path.join(fig_dir, 'comparacao_obs.png'),
         "Painel às 22:30 UTC: observação (esquerda) e REFL_10CM simulada (direita)"),

        ("Slide 9: Deficiências do Modelo: Possíveis Causas",
         "Por que a tempestade veio cedo e por que o granizo ficou pequeno",
         "14 a 17 min",
         "Hipóteses a testar com outras rodadas",
         [
             "1. Cumulus nos domínios externos (18 e 6 km): o Kain-Fritsch pode liberar a instabilidade cedo demais.",
             "2. ERA5 (0,25°): suaviza a inibição e a convergência costeira que seguraram a convecção até a noite.",
             "3. Ascendente fraca: no máximo 16 m/s no dia; pedras de 5 a 6 cm pedem algo como 30 a 40 m/s. Perto da Ilha o HAILCAST ficou em 0 mm.",
             "4. Granizo baixo: 0,50 g/kg a 4,7 km, logo acima do 0 °C, derretendo antes do chão.",
         ],
         os.path.join(fig_dir, '3d_QHAIL.png'),
         "Granizo (QHAIL >= 0,1 g/kg) às 12:45 UTC, sobre a Ilha"),

        ("Slide 10: Conclusões e Repositório no GitHub",
         "O que a modelagem ensinou e onde estão os arquivos",
         "17 a 20 min",
         "Conclusões",
         [
             "Com convecção explícita em 2 km e 2 momentos, o WRF separou graupel, granizo e água super-resfriada e mostrou onde cada um fica.",
             "A célula que cruzou a Ilha tinha água super-resfriada de sobra, mas a ascendente foi fraca para fazer granizo grande.",
             "A convecção veio horas antes do observado; as causas possíveis estão nos domínios externos e na condição inicial.",
             "Próximo teste: sem cumulus nos domínios externos e com o domínio interno em 1 km.",
             "Apresentação e animação: https://reinaldohaas.github.io/tarefa-meso/apresentacao_parte2.html",
         ],
         os.path.join(fig_dir, '3d_SLW.png'),
         "Água super-resfriada (SLW >= 0,5 g/kg) às 12:45 UTC"),
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
