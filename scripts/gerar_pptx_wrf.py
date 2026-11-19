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
         "Esquema Milbrandt-Yau 2 momentos, Grell-Freitas em d01 e convecção explícita em d02/d03",
         "03 a 06 min",
         "Combinação Física da Rodada r1_milbrandt_yau_2km",
         [
             "Microfísica Milbrandt-Yau 2 momentos (mp_physics = 9): prevê massa e número de 6 classes, separando Graupel (QGRAUP, 400 kg/m³) e Granizo de alta densidade (QHAIL, 900 kg/m³).",
             "Cumulus (cu_physics = 3, 0, 0): Grell-Freitas no d01 (18 km) e DESLIGADO em d02 (6 km) e d03 (2 km) para convecção explícita sem estabilização prematura da tarde.",
             "Refletividade e Granizo: do_radar_ref = 1 (REFL_10CM) e hailcast_opt = 0, 0, 1 (diagnóstico HAILCAST no d03).",
             "Camada limite e superfície: YSU PBL (bl_pbl_physics = 1), Monin-Obukhov (sf_sfclay = 1) e Noah LSM (sf_surface = 2).",
             "Radiação e Passo de Tempo: RRTMG LW/SW (ra = 4, icloud = 1) e passo adaptativo (target_cfl = 1.2, dt ~ 16 s no d03).",
         ],
         os.path.join(fig_dir, '3d_QHAIL.png'),
         "Isosuperfície 3D do Granizo (QHAIL >= 0,1 g/kg) prevista pelo esquema Milbrandt-Yau"),

        ("Slide 5: Microfísica em 3D no ParaView: Supercélula Noturna",
         "Altura geométrica real z = (PH + PHB)/9,81, exagero vertical de 4x, cores e limiares fixos",
         "06 a 10 min",
         "Pico da tempestade severa noturna às 22:45 UTC (19:45 Local)",
         [
             "Horário de pico alinhado ao evento real noturno: 22:45 UTC (19:45 Local) sobre a Grande Florianópolis.",
             "Água super-resfriada (SLW = QCLOUD + QRAIN com T < 0 °C, verde): abundante até 7,24 g/kg a 6,83 km (-12,3 °C).",
             "Graupel (QGRAUP, laranja): coluna maciça de 8,30 g/kg a 10,78 km (-39,6 °C) na zona de crescimento rápido.",
             "Granizo severo (QHAIL, vermelho): núcleo denso de 5,21 g/kg a 4,27 km (+1,7 °C), com refletividade de 77,4 dBZ.",
             "Animação 3D com rotação 360° contínua e técnica de despir/vestir as camadas disponível em apresentacao_parte2.html.",
         ],
         os.path.join(fig_dir, '3d_todos.png'),
         "Hidrometeoros em 3D às 22:45 UTC: cores fixas sobre o relevo de Santa Catarina"),

        ("Slide 6: Corte Vertical pela Célula Noturna e Tabela de Máximos",
         "Corrente ascendente W (31 m/s), SLW (7,2 g/kg), Graupel (8,3 g/kg) e Granizo (5,2 g/kg)",
         "06 a 10 min",
         "Corte oeste-leste em -27,58°, -48,50° (22:45 UTC), sobre Florianópolis",
         [
             "Isotermas: 0 °C a 4,71 km; -20 °C a 7,8 km; -40 °C (nucleação homogênea) a 10,8 km.",
             "A água super-resfriada (7,24 g/kg, verde) atua como combustível líquido na corrente ascendente.",
             "Corrente ascendente W vigorosa de 31,0 m/s (com pico de 34,2 m/s às 23:15 UTC), suspendendo grandes pedras de granizo.",
             "O graupel (8,30 g/kg) alimenta o crescimento rápido do granizo severo (5,21 g/kg), que precipita em direção ao solo.",
         ],
         os.path.join(fig_dir, 'corte_vertical.png'),
         "Corte vertical oeste-leste pela célula noturna às 22:45 UTC"),

        ("Slide 7: Refletividade Composta (REFL_10CM) e Série Temporal",
         "Ciclo da supercélula noturna no domínio interno de 2 km (21:45 a 23:15 UTC)",
         "10 a 14 min",
         "Evolução da convecção explícita noturna em d03",
         [
             "Início explosivo às 21:45 UTC na borda oeste do domínio d03, avançando a leste.",
             "Intensificação rápida: 22:15 UTC com 65 dBZ e W = 24 m/s; 22:30 UTC com 70 dBZ e W = 26 m/s.",
             "Pico absoluto às 22:45 UTC: 77,4 dBZ, 5,21 g/kg de granizo e 8,30 g/kg de graupel sobre a Ilha.",
             "Núcleo severo persistente: mantém >70 dBZ até 23:15 UTC (W = 34,2 m/s) antes de dissipar sobre o oceano.",
         ],
         os.path.join(fig_dir, 'refletividade.png'),
         "Refletividade máxima na coluna às 22:45 UTC e série temporal da supercélula em d03"),

        ("Slide 8: Comparação com a Observação: Concordância Noturna",
         "Simulação WRF validada contra radar Morro da Igreja (DECEA) e relatos de solo",
         "10 a 14 min",
         "Excelente concordância temporal e espacial",
         [
             "Horário: a supercélula simulada cruzou Biguaçu e Florianópolis entre 22:15 e 23:00 UTC, em perfeita sincronia com os relatos (22:00–23:00 UTC).",
             "Radar Morro da Igreja: registrou núcleos >60 dBZ entre 22:16 e 22:36 UTC no estreito norte e na Ilha, coincidindo com o pico simulado de 70–77 dBZ.",
             "Satélite GOES-19: confirmou convecção vigorosa e topos frios (-62,9 °C) no mesmo período noturno.",
         ],
         os.path.join(fig_dir, 'comparacao_obs.png'),
         "Painel às 22:30–22:45 UTC: radar/relatos observados (esquerda) e REFL_10CM simulada (direita)"),

        ("Slide 9: Sensibilidade e Física Convectiva: Lições da Parametrização",
         "Por que Kain-Fritsch falhou à tarde e como Grell-Freitas capturou a noite",
         "14 a 17 min",
         "Compreensão física dos processos de mesoescala",
         [
             "1. Esquema Kain-Fritsch em grade de 6 km consumiu prematuramente a CAPE às 13–17h UTC, gerando convecção diurna falsa e noites estáveis.",
             "2. Com Grell-Freitas em d01 e convecção explícita em d02 e d03 (cu_physics = 3, 0, 0), a instabilidade foi preservada ao longo da tarde.",
             "3. A forçante sinótica e o cisalhamento vertical dispararam a supercélula no momento e local corretos (noite de 29/08/2026).",
             "4. A ascendente intensa (31–34 m/s) sustentou o granizo gigante (5,21 g/kg), explicando os danos severos observados em Biguaçu e no Norte da Ilha.",
         ],
         os.path.join(fig_dir, '3d_QHAIL.png'),
         "Núcleo de granizo severo (5,21 g/kg) simulado na supercélula noturna"),

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
