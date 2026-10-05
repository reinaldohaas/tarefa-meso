"""
generate_pptx.py - Geração automatizada da apresentação de slides (PPTX)
Seminário de Meteorologia de Mesoescala (FSC7116 - CFM / UFSC)
Professor: Dr. Reinaldo Haas
Roteiro Cronometrado: 20 Minutos | 10 Slides Estritamente Alinhados à Banca
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# ==============================================================================
# CONFIGURAÇÕES GERAIS DE DESIGN & PALETA DE CORES (MODERNA / CIENTÍFICA)
# ==============================================================================
C_BG = RGBColor(11, 19, 43)          # Dark Executive Navy (#0B132B)
C_CARD_BG = RGBColor(19, 30, 58)     # Deep Slate Card (#131E3A)
C_CARD_BORDER = RGBColor(46, 64, 102)# Subtle Card Border
C_WHITE = RGBColor(248, 250, 252)    # Crisp Off-White Text (#F8FAFC)
C_MUTED = RGBColor(148, 163, 184)    # Secondary Muted Text (#94A3B8)
C_CYAN = RGBColor(56, 189, 248)      # Accent Cyan / Highlights (#38BDF8)
C_AMBER = RGBColor(251, 191, 36)     # Accent Gold / Warnings (#FBBF24)
C_EMERALD = RGBColor(52, 211, 153)   # Accent Green / Stability (#34D399)
C_ROSE = RGBColor(248, 113, 113)     # Accent Red / Instability (#F87171)
C_PURPLE = RGBColor(167, 139, 250)   # Accent Violet (#A78BFA)

def set_slide_background(slide):
    """Cria um fundo escuro elegante em tela cheia."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = C_BG
    bg_shape.line.fill.background() # Sem borda
    return bg_shape

def create_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BORDER):
    """Cria um container em formato de card moderno."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
    else:
        card.line.fill.background()
    return card

def add_header(slide, title_text, subtitle_text, time_badge_text, slide_num):
    """Adiciona cabeçalho padrão com metadados do curso e cronômetro."""
    # Barra de Metadados Superior
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.28), Inches(7.5), Inches(0.4))
    tf_top = header_box.text_frame
    tf_top.word_wrap = True
    tf_top.margin_left = tf_top.margin_top = tf_top.margin_right = tf_top.margin_bottom = 0
    p_meta = tf_top.paragraphs[0]
    p_meta.text = "UFSC  •  FSC7116 METEOROLOGIA DE MESOESCALA  •  PROF. REINALDO HAAS"
    p_meta.font.size = Pt(9.5)
    p_meta.font.bold = True
    p_meta.font.color.rgb = C_CYAN

    # Badge de Tempo e Slide (Canto Superior Direito)
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.8), Inches(0.25), Inches(2.75), Inches(0.42))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(30, 41, 59)
    badge.line.color.rgb = C_AMBER
    badge.line.width = Pt(1.0)
    tf_badge = badge.text_frame
    tf_badge.margin_left = tf_badge.margin_top = tf_badge.margin_right = tf_badge.margin_bottom = 0
    p_b = tf_badge.paragraphs[0]
    p_b.text = f"⏱️  {time_badge_text}  |  Slide {slide_num}/10"
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(9.5)
    p_b.font.bold = True
    p_b.font.color.rgb = C_AMBER

    # Título Principal
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.8), Inches(0.6))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = C_WHITE

    # Subtítulo Explicativo
    s_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.22), Inches(11.8), Inches(0.35))
    tf_s = s_box.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
    p_s = tf_s.paragraphs[0]
    p_s.text = subtitle_text
    p_s.font.size = Pt(11.5)
    p_s.font.color.rgb = C_MUTED

def set_speaker_notes(slide, notes_text):
    """Define as notas do orador para a apresentação cronometrada."""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text

# ==============================================================================
# CONSTRUÇÃO DOS SLIDES
# ==============================================================================

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    print("Iniciando montagem dos 10 slides do Seminário de Mesoescala...")

    # --------------------------------------------------------------------------
    # SLIDE 1: Capa & Contexto do Caso Severo (00 - 03 min, Parte 1)
    # --------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Header de Apresentação
    top_box = s1.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(0.5))
    p1 = top_box.text_frame.paragraphs[0]
    p1.text = "UNIVERSIDADE FEDERAL DE SANTA CATARINA  |  DEPARTAMENTO DE FÍSICA / CFM"
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = C_CYAN

    # Título Gigante
    t1_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.4), Inches(11.3), Inches(1.8))
    tf1 = t1_box.text_frame
    tf1.word_wrap = True
    p_title = tf1.paragraphs[0]
    p_title.text = "Diagnóstico Termodinâmico e Dinâmico\nde Tempestade Severa em Mesoescala"
    p_title.font.size = Pt(32)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE

    p_sub = tf1.add_paragraph()
    p_sub.text = "Estudo do Caso Extremo de Porto Alegre (SBPA - 83971) em 24 de Dezembro de 1995"
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = C_AMBER
    p_sub.space_before = Pt(8)

    # 3 Cards de Destaque
    cards_data = [
        ("📍 Local & Horário", "Porto Alegre (SBPA - 83971)\n12Z (09:00 Horário Local)\nBacia do Prata / Cone Sul", C_CYAN),
        ("⚡ Severidade Convectiva", "MUCAPE: 4.645 J/kg\nSBCAPE: 1.862 J/kg | CIN: -6 J/kg\nJBN em 925 hPa: 44 kt (23 m/s)", C_ROSE),
        ("📚 Fundamentação Teórica", "Teoria de Emanuel (1994)\nCódigo wyoming.f / tcon.py\nMIT OCW 12.811 & MetPy", C_EMERALD)
    ]
    for i, (ctitle, cdesc, ccol) in enumerate(cards_data):
        card = create_card(s1, Inches(1.0 + i * 3.85), Inches(3.4), Inches(3.6), Inches(2.3))
        tb = s1.shapes.add_textbox(Inches(1.15 + i * 3.85), Inches(3.55), Inches(3.3), Inches(2.0))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = ctitle
        pt.font.size = Pt(14)
        pt.font.bold = True
        pt.font.color.rgb = ccol

        pd = tf.add_paragraph()
        pd.text = cdesc
        pd.font.size = Pt(11)
        pd.font.color.rgb = C_WHITE
        pd.space_before = Pt(8)

    # Rodapé com Autor e Orientador
    foot_box = s1.shapes.add_textbox(Inches(1.0), Inches(6.1), Inches(11.3), Inches(0.9))
    tf_f = foot_box.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "Disciplina: FSC7116 - Meteorologia de Mesoescala   •   Orientador: Prof. Dr. Reinaldo Haas"
    p_f.font.size = Pt(11)
    p_f.font.bold = True
    p_f.font.color.rgb = C_MUTED
    p_f2 = tf_f.add_paragraph()
    p_f2.text = "⏱️ Tempo de Apresentação: 20 Minutos  |  Roteiro Estruturado para Arguição da Banca"
    p_f2.font.size = Pt(10)
    p_f2.font.color.rgb = C_AMBER
    p_f2.space_before = Pt(3)

    set_speaker_notes(s1, """ROTEIRO DO ORADOR (00:00 - 01:30):
Bom dia à banca examinadora, ao Professor Reinaldo Haas e aos colegas presentes.
Hoje apresento o seminário de Meteorologia de Mesoescala referente à análise diagnóstica completa de uma tempestade severa histórica na Bacia do Prata, ocorrida em 24 de dezembro de 1995 às 12Z sobre a estação de Porto Alegre (SBPA).

Este trabalho está fundamentado na termodinâmica de parcelas formulada por Kerry Emanuel em seu clássico livro 'Atmospheric Convection' (1994) e no código wyoming.f do MIT OCW 12.811, combinado com o ecossistema moderno em Python utilizando o MetPy.

Nosso objetivo neste seminário de 20 minutos é responder: quais foram os gatilhos termodinâmicos e dinâmicos que transformaram uma atmosfera pós-frontal estável em um ambiente de convecção profunda explosiva com CAPE superior a 4.600 J/kg e cisalhamento vertical capaz de gerar supercélulas de alta precipitação e rajadas destrutivas.""")

    # --------------------------------------------------------------------------
    # SLIDE 2: Sinótica e Caso de Estudo - 500 hPa e 850 hPa (00 - 03 min, Parte 2)
    # --------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Forçamento Sinótico & Suporte Dinâmico de Mesoescala",
               "Acoplamento Vertical entre o Cavado em 500 hPa e o Jato em Baixos Níveis (JBN) em 850 hPa",
               "00 - 03 min", 2)

    # Imagem Sinótica à esquerda
    img_syn = 'metpack/fig_synoptic_analysis.png'
    if os.path.exists(img_syn):
        s2.shapes.add_picture(img_syn, Inches(0.8), Inches(1.75), width=Inches(7.2))

    # Card Explicativo à direita
    card_syn = create_card(s2, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_syn = s2.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_syn = tb_syn.text_frame
    tf_syn.word_wrap = True

    pts_syn = [
        ("Nível Médio (500 hPa) - Forçamento QG:", [
            "Cavado de onda curta pronunciado sobre a Argentina/Cordilheira.",
            "Forte difluência de mesoescala a jusante diretamente sobre o RS.",
            "Advecção de Vorticidade Ciclônica Relativa (CVA / PVA) gerando sustentação de larga escala (ω < 0 via Equação Ômega Quase-Geostrófica)."
        ], C_CYAN),
        ("Baixos Níveis (850 hPa) - Alimentação Termodinâmica:", [
            "Jato em Baixos Níveis (JBN) da América do Sul ativo com ventos > 23 m/s (44 kt) transportando calor e umidade tropical da Amazônia e Chaco.",
            "Crista pronunciada de θe (> 350 K) focada sobre o centro-oeste e sul do RS.",
            "Convergência de massa e umidade (∇·(qV) < 0) desestabilizando a camada limite."
        ], C_AMBER),
        ("Acoplamento Vertical:", [
            "Sobreposição de suporte dinâmico aloft e convergência térmica em baixos níveis, preparando o ambiente para convecção profunda explosiva."
        ], C_EMERALD)
    ]
    for block_title, bullets, bcol in pts_syn:
        pb = tf_syn.add_paragraph() if tf_syn.paragraphs[0].text else tf_syn.paragraphs[0]
        pb.text = block_title
        pb.font.size = Pt(11)
        pb.font.bold = True
        pb.font.color.rgb = bcol
        pb.space_before = Pt(6)
        for b in bullets:
            p_bullet = tf_syn.add_paragraph()
            p_bullet.text = f"• {b}"
            p_bullet.font.size = Pt(9.5)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s2, """ROTEIRO DO ORADOR (01:30 - 03:00):
Passando para a configuração sinótica que sustentou este caso no dia 24 de dezembro de 1995 às 12Z.
À esquerda, temos o mapa de reanálise em dois níveis fundamentais: 500 hPa e 850 hPa.
Em 500 hPa, observamos um cavado pronunciado adentrando a partir da Argentina, estabelecendo uma forte difluência de mesoescala sobre o Rio Grande do Sul. Pela teoria Quase-Geostrófica, a advecção de vorticidade ciclônica relativa positiva (CVA ou PVA) força movimentos verticais ascendentes de grande escala (ômega negativo), reduzindo as pressões à superfície e enfraquecendo a estabilidade atmosférica.

Simultaneamente, em 850 hPa, identificamos a atuação clássica do Jato em Baixos Níveis da América do Sul (JBN), canalizado a leste dos Andes. O JBN atinge velocidades superiores a 23 m/s (44 nós) em 925/850 hPa, bombeando uma língua de altíssima temperatura potencial equivalente (θe > 350 K) direto da bacia Amazônica e do Chaco em direção ao RS.
Esse acoplamento vertical — forçamento dinâmico em médios níveis sobreposto a uma advecção térmica e de umidade agressiva em baixos níveis — é o clássico 'carregamento da mola' para os maiores eventos de tempo severo da América do Sul.""")

    # --------------------------------------------------------------------------
    # SLIDE 3: As 3 Sondagens - Comparação dos Skew-T (03 - 07 min, Parte 1)
    # --------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Evolução Temporal: Comparação das 3 Sondagens",
               "Transição Atmosférica em Porto Alegre: Pós-Frontal Estável (12/12) ➔ Neutro/Transição (23/12) ➔ Explosivo Severo (24/12)",
               "03 - 07 min", 3)

    img_3s = 'metpack/fig_3_soundings_skewt.png'
    if os.path.exists(img_3s):
        s3.shapes.add_picture(img_3s, Inches(0.8), Inches(1.75), width=Inches(11.75))

    # Banner comparativo inferior
    c_banner = create_card(s3, Inches(0.8), Inches(5.8), Inches(11.75), Inches(1.2))
    tb_b = s3.shapes.add_textbox(Inches(0.95), Inches(5.85), Inches(11.45), Inches(1.1))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    pb_t = tf_b.paragraphs[0]
    pb_t.text = "Síntese Física da Evolução Sinótica das Sondagens da Universidade de Wyoming:"
    pb_t.font.size = Pt(10.5)
    pb_t.font.bold = True
    pb_t.font.color.rgb = C_AMBER

    pb_desc = tf_b.add_paragraph()
    pb_desc.text = "12/12/1995 (Estável): Subsidência pós-frontal anticiclônica, atmosfera seca em médios níveis (T-Td > 15°C), CAPE = 0 J/kg, ar estável.\n" \
                   "23/12/1995 (Neutro/Transição): Retorno do fluxo de norte, umedecimento da coluna, CAPE moderado (848 J/kg), CIN significativo (-120 J/kg).\n" \
                   "24/12/1995 (Severo): Rompimento de barreira por advecção quente em 925 hPa (T=30°C, Td=25°C), MUCAPE = 4.645 J/kg, CIN = -6.5 J/kg."
    pb_desc.font.size = Pt(9.5)
    pb_desc.font.color.rgb = C_WHITE
    pb_desc.space_before = Pt(2)

    set_speaker_notes(s3, """ROTEIRO DO ORADOR (03:00 - 05:00):
Entrando no bloco obrigatório de comparação das três sondagens atmosféricas de Porto Alegre obtidas na Universidade de Wyoming.
No primeiro painel, dia 12 de dezembro de 1995 às 12Z, temos a condição de estabilidade pós-frontal. Notem a grande separação entre a curva vermelha (temperatura) e a verde (ponto de orvalho) em médios níveis, denotando subsidência anticiclônica e ar extremamente seco. A parcela de superfície não encontra nível de convecção livre (LFC); o CAPE é estritamente zero e a atmosfera é termodinamicamente inerte.

No segundo painel, dia 23 de dezembro, 11 dias depois, a sinótica começa a mudar. O fluxo de norte reintroduz umidade nos primeiros quilômetros. O perfil apresenta CAPE de 848 J/kg, porém ainda associado a uma inibição convectiva (CIN) substancial de -120 J/kg que bloqueia a convecção espontânea (estado marginalmente neutro/transição).

Finalmente, no terceiro painel, dia 24 de dezembro, a situação atinge o limiar explosivo. A curva de orvalho cola na de temperatura nos primeiros 900 hPa. Há uma inversão extremamente quente e úmida em 925 hPa onde a temperatura atinge 30°C com ponto de orvalho de 25°C. O CAPE salta para mais de 1.860 J/kg para a superfície e incríveis 4.645 J/kg para a parcela mais instável (MUCAPE), enquanto a inibição cai para apenas -6.5 J/kg.""")

    # --------------------------------------------------------------------------
    # SLIDE 4: Diagnóstico Termodinâmico: CAPE, CIN e d(theta_e)/dz (03 - 07 min, Parte 2)
    # --------------------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Diagnóstico Termodinâmico: Flutuabilidade & Instabilidade Potencial",
               "Interpretação Física das Integrais de CAPE/CIN, Níveis Críticos (LCL, LFC, EL) e ∂θe/∂z < 0",
               "03 - 07 min", 4)

    img_skew = 'metpack/fig_colab_severe_skewt.png'
    if os.path.exists(img_skew):
        s4.shapes.add_picture(img_skew, Inches(0.8), Inches(1.75), width=Inches(7.2))

    card_th = create_card(s4, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_th = s4.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_th = tb_th.text_frame
    tf_th.word_wrap = True

    sections_th = [
        ("Definição Física do CAPE e CIN:", [
            "CAPE = ∫ [g · (Tv,p - Tv,e) / Tv,e] dz  (entre LFC e EL).",
            "MUCAPE: 4.645 J/kg | SBCAPE: 1.862 J/kg.",
            "W_max teórico = √(2 · CAPE) ≈ 96.4 m/s (corrente ascendente explosiva, limitada por arrasto e entranhamento)."
        ], C_ROSE),
        ("Níveis Convectivos Fundamentais:", [
            "LCL (Condensação por Levantamento): 942 hPa (~600 m). Nuvens com base muito baixa.",
            "LFC (Convecção Livre): Imediato para parcela de 925 hPa; CIN insignificante (-6.5 J/kg).",
            "EL (Equilíbrio Térmico): 165 hPa (~13.8 km), topo de nuvem penetrando a tropopausa."
        ], C_CYAN),
        ("Critério de Instabilidade Potencial / Convectiva:", [
            "∂θe / ∂z < 0 presente desde a superfície até 650 hPa.",
            "Se uma camada com essa propriedade for forçada a subir em bloco até a saturação, torna-se fortemente instável para parcelas individuais."
        ], C_EMERALD)
    ]
    for stitle, sbullets, scol in sections_th:
        pb = tf_th.add_paragraph() if tf_th.paragraphs[0].text else tf_th.paragraphs[0]
        pb.text = stitle
        pb.font.size = Pt(11)
        pb.font.bold = True
        pb.font.color.rgb = scol
        pb.space_before = Pt(6)
        for b in sbullets:
            p_bullet = tf_th.add_paragraph()
            p_bullet.text = f"• {b}"
            p_bullet.font.size = Pt(9.5)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s4, """ROTEIRO DO ORADOR (05:00 - 07:00):
Aprofundando a interpretação física da sondagem severa do dia 24 de dezembro.
No gráfico Skew-T gerado pelo MetPy à esquerda, a área sombreada em vermelho representa o CAPE — a integral da aceleração de flutuabilidade entre o Nível de Convecção Livre (LFC) e o Nível de Equilíbrio (EL).
Pela fórmula clássica do balanço de energia cinética, a velocidade vertical máxima teórica é a raiz de duas vezes o CAPE. Para o MUCAPE de 4.645 J/kg, isso resulta em um W_max de 96 m/s! Embora na natureza processos de arrasto de gotas, atrito e entranhamento de ar seco reduzam esse valor pela metade (~45 a 50 m/s), trata-se ainda de uma corrente ascendente violenta com energia suficiente para sustentar pedras de granizo gigantes.

Outro aspecto vital cobrado pela banca é a condição de instabilidade potencial ou convectiva, dada matematicamente por ∂θe/∂z < 0. Observamos que θe diminui fortemente com a altitude entre a superfície (349 K), atingindo um pico de 378 K em 925 hPa e caindo para menos de 335 K em 650 hPa. Quando o cavado sinótico ergue essa camada em bloco, o topo atinge a saturação mais tarde que a base úmida, gerando uma taxa de lapso vertical supersaturada extremamente instável.""")

    # --------------------------------------------------------------------------
    # SLIDE 5: Emanuel (1994) & Temp. Densidade (07 - 10 min)
    # --------------------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Teoria de Emanuel (1994) & Temperatura de Densidade (Tρ)",
               "Resultados do wyoming.f / tcon.py - Water Loading (-rl) e Comparação com MIT OCW 12.811",
               "07 - 10 min", 5)

    img_emanuel = 'metpack/tcon_comparacao_emanuel.png'
    if os.path.exists(img_emanuel):
        s5.shapes.add_picture(img_emanuel, Inches(0.8), Inches(1.75), width=Inches(7.2))

    card_em = create_card(s5, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_em = s5.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_em = tb_em.text_frame
    tf_em.word_wrap = True

    sections_em = [
        ("Fundamentação Teórica - Kerry Emanuel (1994):", [
            "Referência: Kerry Emanuel (1994), 'Atmospheric Convection', Oxford Univ. Press (Cap. 2 e 6).",
            "Disciplina de pós-graduação do MIT: MIT OCW 12.811.",
            "Código de referência da comunidade: wyoming.f / tcon.m reimplementado em Python (wyoming.py / tcon.py)."
        ], C_CYAN),
        ("Temperatura de Densidade (Tρ):", [
            "Tρ = T · (1 + rv/ε) / (1 + rv + rl) ≈ Tv · (1 - rl)",
            "Incorpora o peso da água líquida condensada suspensa na parcela (efeito de Water Loading, -rl)."
        ], C_AMBER),
        ("Reversível vs Pseudoadiabático:", [
            "Reversível (Tρ,rev): Todo o condensado é mantido suspenso. O peso da água reduz o empuxo. CAPE_rev = 3.832 J/kg (origem 925 hPa).",
            "Pseudoadiabático (Tv,pse): Condensado precipita instantaneamente (rl = 0). Empuxo máximo. CAPE_pse = 4.172 J/kg.",
            "Diferença por Water Loading: ΔCAPE = 340 J/kg (~8.2% de atenuação da flutuabilidade)."
        ], C_EMERALD)
    ]
    for stitle, sbullets, scol in sections_em:
        pb = tf_em.add_paragraph() if tf_em.paragraphs[0].text else tf_em.paragraphs[0]
        pb.text = stitle
        pb.font.size = Pt(11)
        pb.font.bold = True
        pb.font.color.rgb = scol
        pb.space_before = Pt(6)
        for b in sbullets:
            p_bullet = tf_em.add_paragraph()
            p_bullet.text = f"• {b}"
            p_bullet.font.size = Pt(9.5)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s5, """ROTEIRO DO ORADOR (07:00 - 10:00):
Este slide é de primordial importância para a banca, pois conecta nosso estudo diretamente com o arcabouço teórico de Kerry Emanuel (1994), 'Atmospheric Convection', e o material do curso MIT OCW 12.811.
À esquerda, temos os gráficos 2D gerados pelo tcon.py a partir das saídas do código wyoming.py/wyoming.f.
Emanuel demonstrou que na convecção real a temperatura virtual (Tv) não é suficiente para representar a densidade exata da parcela após a condensação, porque as gotas de água líquida condensada permanecem suspensas na corrente ascendente, exercendo um peso adicional para baixo.

Por isso, ele introduziu formalmente a Temperatura de Densidade (Tρ), que adiciona o termo -rl no denominador: Tρ ≈ Tv * (1 - rl).
Nos mapas de anomalia de temperatura de densidade:
O painel esquerdo mostra a ascensão Reversível, onde a água condensada é retida. Para a parcela mais instável em 925 hPa, o CAPE reversível resulta em 3.832 J/kg.
Já o painel direito mostra o modelo Pseudoadiabático, onde supõe-se que toda chuva precipita imediatamente, resultando em 4.172 J/kg.
A diferença de 340 J/kg (cerca de 8.2%) representa a perda de energia cinética sofrida pela tempestade puramente pelo arrasto da carga de água (water loading). Em tempestades tropicais e subtropicais com alto conteúdo de água, ignorar o water loading leva a erros severos de superestimação da aceleração ascendente.""")

    # --------------------------------------------------------------------------
    # SLIDE 6: Variáveis do Cap. 2: θv e Brunt-Väisälä (N^2) (10 - 14 min, Parte 1)
    # --------------------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Variáveis do Capítulo 2: Perfis Térmicos & Frequência de Brunt-Väisälä",
               "Estabilidade Estática, Ondas de Gravidade na Troposfera e o Efeito Capping Lid (Inversão Tampa)",
               "10 - 14 min", 6)

    img_p2 = 'metpack/fig_cap2_profiles.png'
    if os.path.exists(img_p2):
        s6.shapes.add_picture(img_p2, Inches(0.8), Inches(1.75), width=Inches(7.2))

    card_c2 = create_card(s6, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_c2 = s6.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True

    sections_c2 = [
        ("Temperatura Potencial Virtual (θv):", [
            "θv = θ · (1 + 0.608 q - ql)",
            "Incorpora a densidade dos gases úmidos, sendo a variável canônica para o empuxo térmico na atmosfera seca e sub-saturada."
        ], C_CYAN),
        ("Frequência de Brunt-Väisälä (N²):", [
            "N² = (g / θv) · (∂θv / ∂z)",
            "N² > 0: Frequência de oscilação estável de ondas de gravidade (período τ = 2π / N).",
            "N² < 0: Instabilidade hidrostática pura.",
            "Camada média (800-400 hPa): N² moderado (~1.2 × 10⁻⁴ s⁻²), permitindo propagação vertical de energia."
        ], C_PURPLE),
        ("O 'Capping Lid' em 925-900 hPa:", [
            "Pico expressivo de N² (~4.5 × 10⁻⁴ s⁻²) logo acima do topo da CLP.",
            "Função física de 'tampa de panela de pressão': impede que o ar úmido e quente escape prematuramente em convecções rasas.",
            "Permite acumular 4.600 J/kg de energia até o forçamento sinótico romper a inversão de forma explosiva."
        ], C_AMBER)
    ]
    for stitle, sbullets, scol in sections_c2:
        pb = tf_c2.add_paragraph() if tf_c2.paragraphs[0].text else tf_c2.paragraphs[0]
        pb.text = stitle
        pb.font.size = Pt(11)
        pb.font.bold = True
        pb.font.color.rgb = scol
        pb.space_before = Pt(6)
        for b in sbullets:
            p_bullet = tf_c2.add_paragraph()
            p_bullet.text = f"• {b}"
            p_bullet.font.size = Pt(9.5)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s6, """ROTEIRO DO ORADOR (10:00 - 12:00):
No Capítulo 2 de Kerry Emanuel, a estabilidade atmosférica é formalmente descrita através do perfil vertical de temperatura potencial virtual (θv) e da Frequência de Brunt-Väisälä (N² = g/θv * dθv/dz).
Nos painéis 1 e 2 à esquerda, vemos essa estrutura para o caso de Porto Alegre.
A frequência N² quantifica a rigidez com que uma parcela de ar deslocada verticalmente oscila em torno da sua posição de equilíbrio como uma onda de gravidade interna.

Prestem especial atenção ao comportamento de N² nos primeiros 1.000 metros:
Observamos um pico acentuado de N² atingindo 4.5 × 10⁻⁴ s⁻² exatamente na camada entre 925 e 900 hPa. Esse pico marca a famosa inversão térmica conhecida na meteorologia de mesoescala como 'Capping Lid' (a tampa da camada limite).
A presença do Capping Lid é um ingrediente paradoxal, mas obrigatório, para os maiores surtos de tempestades severas. Se não houvesse essa tampa estável, pequenas cúmulos se formariam desde as primeiras horas da manhã, consumindo gradualmente a umidade e aliviando a energia.
O Capping Lid funciona como a tampa de uma panela de pressão: ele aprisiona todo o calor e umidade transportados pelo JBN na camada limite até que, no início da tarde, o aquecimento solar e a difluência de 500 hPa rompem a tampa, liberando toda a energia acumulada de uma só vez.""")

    # --------------------------------------------------------------------------
    # SLIDE 7: Razão de Mistura (r), PW e DCAPE (10 - 14 min, Parte 2)
    # --------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Umidade Troposférica & Potencial de Downbursts",
               "Razão de Mistura r(z), Água Precipitável (PW) e Downdraft CAPE (DCAPE) via Resfriamento Evaporativo",
               "10 - 14 min", 7)

    img_diag = 'metpack/diagnostico_mesoescala.png'
    if os.path.exists(img_diag):
        s7.shapes.add_picture(img_diag, Inches(0.8), Inches(1.75), width=Inches(7.2))

    card_pw = create_card(s7, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_pw = s7.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_pw = tb_pw.text_frame
    tf_pw.word_wrap = True

    sections_pw = [
        ("Razão de Mistura Extrema (r):", [
            "Superfície: r = 18.0 g/kg.",
            "Pico do JBN (925 hPa): r = 22.02 g/kg (valor excepcional para o Sul do Brasil, característico de massas equatoriais).",
            "Decaimento abrupto acima de 700 hPa, criando contraste com ar seco em médios níveis."
        ], C_CYAN),
        ("Água Precipitável Total (PW):", [
            "PW = (1/g) ∫ q dp = 52.4 mm.",
            "Percentil > 95% para Porto Alegre no mês de dezembro.",
            "Indica alto potencial de precipitação torrencial horária (> 60 mm/h) e inundações repentinas."
        ], C_EMERALD),
        ("Downdraft CAPE (DCAPE = 1.149 J/kg):", [
            "Medida do empuxo negativo gerado pelo resfriamento evaporativo da chuva em ar não saturado a 650 hPa.",
            "Velocidade teórica da descendente: W_down = √(2 · DCAPE) ≈ 47.9 m/s (~172 km/h).",
            "Ambiente altamente propício a Microbursts úmidos e frentes de rajada violentas ao atingir o solo."
        ], C_ROSE)
    ]
    for stitle, sbullets, scol in sections_pw:
        pb = tf_pw.add_paragraph() if tf_pw.paragraphs[0].text else tf_pw.paragraphs[0]
        pb.text = stitle
        pb.font.size = Pt(11)
        pb.font.bold = True
        pb.font.color.rgb = scol
        pb.space_before = Pt(6)
        for b in sbullets:
            p_bullet = tf_pw.add_paragraph()
            p_bullet.text = f"• {b}"
            p_bullet.font.size = Pt(9.5)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s7, """ROTEIRO DO ORADOR (12:00 - 14:00):
Continuando o diagnóstico do Capítulo 2, examinamos o conteúdo de vapor d'água e o risco de correntes descendentes violentas.
A razão de mistura de vapor d'água (r) medida em Porto Alegre atinge impressionantes 22.0 g/kg no nível de 925 hPa! Esse valor é extraordinário para latitudes subtropicais e atesta a eficiência do JBN em bombear umidade pura da Amazônia.
A integral de umidade na coluna fornece uma Água Precipitável (PW) de 52.4 mm, situando-se no percentil 95 superior para o clima do Rio Grande do Sul.

Mas o aspecto mais perigoso desta sondagem está na camada de ar mais seco localizada em médios níveis (~650 hPa).
Quando a chuva intensa cai através dessa camada de ar insaturado, a evaporação parcial das gotas retira calor latente do ar, resfriando bruscamente a parcela. A parcela torna-se muito mais densa que a vizinhança e despenca em direção à superfície acelerada pela gravidade.
O código wyoming.f de Kerry Emanuel calculou o Downdraft CAPE (DCAPE) deste perfil em 1.149 J/kg!
Aplicando a equação da energia cinética descendente, obtemos uma velocidade de queda teórica de 47.9 m/s, correspondendo a ventos de até 172 km/h quando esse bolsão de ar atinge o solo e se espalha radialmente. Esse é o mecanismo físico gerador de microbursts e frentes de rajada destruidoras em tempestades severas.""")

    # --------------------------------------------------------------------------
    # SLIDE 8: Cinemática, Hodógrafo, JBN e Helicidade (14 - 17 min)
    # --------------------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Cinemática & Dinâmica: Hodógrafo, JBN e Helicidade (SRH)",
               "Curvatura do Vento na Baixa Troposfera e Cisalhamento Vertical Suportando Supercélulas de Alta Precipitação",
               "14 - 17 min", 8)

    img_hodo = 'metpack/fig_kinematics_hodograph.png'
    if os.path.exists(img_hodo):
        s8.shapes.add_picture(img_hodo, Inches(0.8), Inches(1.75), width=Inches(7.2))

    card_kin = create_card(s8, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_kin = s8.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_kin = tb_kin.text_frame
    tf_kin.word_wrap = True

    sections_kin = [
        ("Jato em Baixos Níveis (JBN) em 925 hPa:", [
            "Vento de 44 nós (23.2 m/s) de direção 60° (ENE).",
            "Gera curvatura anticiclônica proeminente no hodógrafo nos primeiros 1.500 m.",
            "No Hemisfério Sul, giro do vento no sentido horário com a altura favorece supercélulas de rotação ciclônica."
        ], C_AMBER),
        ("Cisalhamento Vertical Profundo (Bulk Shear 0-6 km):", [
            "Magnitude: 28.7 m/s (55.8 nós).",
            "Limiar clássico de supercélulas é > 20 m/s (Markowski & Richardson, 2010).",
            "Garante a separação física entre a corrente ascendente e as correntes descendentes de precipitação."
        ], C_CYAN),
        ("Helicidade Relativa à Tempestade (SRH):", [
            "SRH 0-1 km: 158 m²/s² | SRH 0-3 km: 245 m²/s².",
            "Valores > 150-200 m²/s² fornecem influxo contínuo de vorticidade streamwise à corrente ascendente.",
            "Bulk Richardson Number: BRN = 34.2 (faixa ideal para supercélulas isoladas e multicélulas severas)."
        ], C_EMERALD)
    ]
    for stitle, sbullets, scol in sections_kin:
        pb = tf_kin.add_paragraph() if tf_kin.paragraphs[0].text else tf_kin.paragraphs[0]
        pb.text = stitle
        pb.font.size = Pt(11)
        pb.font.bold = True
        pb.font.color.rgb = scol
        pb.space_before = Pt(6)
        for b in sbullets:
            p_bullet = tf_kin.add_paragraph()
            p_bullet.text = f"• {b}"
            p_bullet.font.size = Pt(9.5)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s8, """ROTEIRO DO ORADOR (14:00 - 17:00):
Entramos no bloco crucial de cinemática e dinâmica do vento.
O gráfico à esquerda é o Hodógrafo Polar detalhado da sondagem de Porto Alegre.
Cada ponto representa a ponta do vetor vento horizontal em diferentes altitudes, colorido por camadas de 0-1 km (vermelho), 1-3 km (verde), 3-6 km (azul) e alta troposfera (roxo).

Dois aspectos saltam aos olhos:
Primeiro, a presença evidente do Jato em Baixos Níveis (JBN) em 925 hPa, com vento atingindo 44 nós (23.2 m/s). Esse jato gera um semicírculo pronunciado no hodógrafo nos primeiros 1.500 metros.
No Hemisfério Sul, essa curvatura com giro horário do vento com a altura produz vorticidade horizontal puramente paralela ao escoamento relativo (vorticidade streamwise). Quando o ar entra na corrente ascendente, essa vorticidade horizontal é inclinada (tilting) para a vertical, gerando um mesociclone giratório sustentado!

Segundo, o cisalhamento vertical profundo de 0 a 6 km atinge 28.7 m/s (quase 56 nós).
A literatura clássica (Markowski & Richardson, 2010; Doswell, 2001) estabelece que cisalhamentos 0-6 km superiores a 20 m/s são a condição sine qua non para o desenvolvimento de Supercélulas.
O cisalhamento profundo inclina a coluna convectiva, fazendo com que a chuva e o granizo caiam fora da corrente ascendente, permitindo que a tempestade se auto-sustente por horas sem ser sufocada pela própria precipitação.
Com SRH 0-3 km de 245 m²/s² e Bulk Richardson Number de 34, a cinemática confirma um ambiente clássico para tempestades supercelulares.""")

    # --------------------------------------------------------------------------
    # SLIDE 9: Síntese dos Gatilhos de Mesoescala & Modo Convectivo (17 - 20 min, Parte 1)
    # --------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Síntese dos Gatilhos de Mesoescala & Modo Convectivo",
               "Modelo Conceitual: Supercélula de Alta Precipitação (HP) com Transição para Linha de Instabilidade",
               "17 - 20 min", 9)

    img_hp = 'metpack/fig_esquema_supercelula_hp.png'
    if os.path.exists(img_hp):
        s9.shapes.add_picture(img_hp, Inches(0.8), Inches(1.75), width=Inches(7.2))

    card_s9 = create_card(s9, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_s9 = s9.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_s9 = tb_s9.text_frame
    tf_s9.word_wrap = True

    sections_s9 = [
        ("Matriz de Gatilhos de Mesoescala:", [
            "1. Gatilho Dinâmico: Difluência e CVA em 500 hPa gerando ascensão sinótica.",
            "2. Gatilho Termodinâmico: Rompimento do Capping Lid em 925 hPa por aquecimento diurno e convergência no JBN.",
            "3. Fonte de Umidade: Fluxo de θe > 350 K e r = 22 g/kg suprido ininterruptamente."
        ], C_CYAN),
        ("Classificação do Modo Convectivo:", [
            "Alto CAPE (> 3.800 J/kg) + Alto Cisalhamento 0-6 km (28.7 m/s) = Supercélula.",
            "PW Extremo (52.4 mm) + Alto DCAPE (1.149 J/kg) = Subtipo de Alta Precipitação (HP Supercell).",
            "O mesociclone fica envolto por cortinas pesadas de chuva torrencial e granizo."
        ], C_ROSE),
        ("Evolução para Linha de Instabilidade:", [
            "O alto DCAPE gera piscinas frias (cold pools) densas e frentes de rajada vigorosas.",
            "A rápida coalescência das piscinas frias promove a transição da supercélula para Linha de Instabilidade / CCM em poucas horas."
        ], C_AMBER)
    ]
    for stitle, sbullets, scol in sections_s9:
        pb = tf_s9.add_paragraph() if tf_s9.paragraphs[0].text else tf_s9.paragraphs[0]
        pb.text = stitle
        pb.font.size = Pt(11)
        pb.font.bold = True
        pb.font.color.rgb = scol
        pb.space_before = Pt(6)
        for b in sbullets:
            p_bullet = tf_s9.add_paragraph()
            p_bullet.text = f"• {b}"
            p_bullet.font.size = Pt(9.5)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s9, """ROTEIRO DO ORADOR (17:00 - 18:30):
Integrando todos os diagnósticos termodinâmicos e cinemáticos em um modelo conceitual de mesoescala.
À esquerda, sintetizamos a estrutura física da tempestade prevista para este evento.
A combinação de alto CAPE (acima de 3.800 J/kg no modelo reversível e 4.600 J/kg no MUCAPE) com cisalhamento vertical profundo de 28.7 m/s classifica inequivocamente o sistema como uma tempestade Supercelular.

Entretanto, devido ao conteúdo excepcional de umidade troposférica (PW de 52.4 mm), esta tempestade não se comporta como uma supercélula clássica de planície seca (LP), mas sim como uma Supercélula de Alta Precipitação (HP Supercell).
Em uma supercélula HP, a precipitação pesada e o granizo envolvem completamente o mesociclone, ocultando a rotação de observadores em solo e gerando chuvas torrenciais.

Além disso, como o DCAPE é de 1.149 J/kg, a corrente descendente traseira (RFD) e a dianteira (FFD) produzem piscinas frias (cold pools) muito densas e agressivas.
Quando a frente de rajada da piscina fria avança sobre o ar quente e úmido trazido pelo JBN, ela força novas convecções ao longo de sua borda. Esse mecanismo faz com que supercélulas individuais na Bacia do Prata rapidamente se fundam em linhas de instabilidade organizadas e Complexos Convectivos de Mesoescala (CCMs).""")

    # --------------------------------------------------------------------------
    # SLIDE 10: Conclusão & Fechamento para Arguição da Banca (17 - 20 min, Parte 2)
    # --------------------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Conclusão & Fechamento para Arguição da Banca",
               "Resumo Quantitativo dos Parâmetros Diagnósticos, Bibliografia Citada e Abertura para Perguntas",
               "17 - 20 min", 10)

    # Tabela Resumo à esquerda
    card_tb = create_card(s10, Inches(0.8), Inches(1.75), Inches(5.8), Inches(5.15))
    tb_res = s10.shapes.add_textbox(Inches(0.95), Inches(1.9), Inches(5.5), Inches(4.85))
    tf_res = tb_res.text_frame
    tf_res.word_wrap = True

    p_rt = tf_res.paragraphs[0]
    p_rt.text = "Tabela Resumo dos Parâmetros Diagnósticos (SBPA):"
    p_rt.font.size = Pt(11.5)
    p_rt.font.bold = True
    p_rt.font.color.rgb = C_AMBER

    summary_rows = [
        ("SBCAPE / MUCAPE:", "1.862 J/kg  /  4.645 J/kg", C_ROSE),
        ("SBCIN / MUCIN:", "-185 J/kg  /  -6.5 J/kg", C_CYAN),
        ("Emanuel CAPE (Reversível):", "3.832 J/kg (Water Loading: -340 J/kg)", C_EMERALD),
        ("Downdraft CAPE (DCAPE):", "1.149 J/kg  (W_down ≈ 47.9 m/s)", C_ROSE),
        ("Água Precipitável (PW):", "52.4 mm (Percentil > 95%)", C_CYAN),
        ("Razão de Mistura Máx (925 hPa):", "22.02 g/kg (Alimentação pelo JBN)", C_CYAN),
        ("JBN em 925 hPa:", "44 nós (23.2 m/s) de direção 60° (ENE)", C_AMBER),
        ("Bulk Shear 0-6 km:", "28.7 m/s (55.8 kt) [Supercélulas]", C_EMERALD),
        ("Helicidade SRH 0-3 km:", "245 m²/s² (Rotação Ciclônica no HS)", C_EMERALD),
        ("Bulk Richardson Number (BRN):", "34.2 (Ambiente Supercelular)", C_WHITE)
    ]
    for lbl, val, vcol in summary_rows:
        pr = tf_res.add_paragraph()
        pr.space_before = Pt(3)
        pr.text = f"• {lbl} "
        pr.font.size = Pt(9.5)
        pr.font.color.rgb = C_WHITE
        # Add colored value
        run = pr.add_run()
        run.text = val
        run.font.bold = True
        run.font.color.rgb = vcol

    # Card da Direita: Referências e Encerramento
    card_ref = create_card(s10, Inches(6.8), Inches(1.75), Inches(5.75), Inches(5.15))
    tb_ref = s10.shapes.add_textbox(Inches(7.0), Inches(1.9), Inches(5.35), Inches(4.85))
    tf_ref = tb_ref.text_frame
    tf_ref.word_wrap = True

    p_reft = tf_ref.paragraphs[0]
    p_reft.text = "Referências Bibliográficas Obrigatórias:"
    p_reft.font.size = Pt(11.5)
    p_reft.font.bold = True
    p_reft.font.color.rgb = C_CYAN

    refs = [
        "Emanuel, K. A. (1994). Atmospheric Convection. Oxford University Press, 580 pp.",
        "MIT OpenCourseWare (Course 12.811). Atmospheric Convection. Massachusetts Institute of Technology.",
        "Markowski, P., & Richardson, Y. (2010). Mesoscale Meteorology in Midlatitudes. Wiley-Blackwell, 407 pp.",
        "Doswell, C. A. III (2001). Severe Convective Storms. Meteorological Monographs, AMS.",
        "MetPy Development Team (2024). MetPy: A Python Package for Meteorological Data."
    ]
    for r in refs:
        p_r = tf_ref.add_paragraph()
        p_r.text = f"• {r}"
        p_r.font.size = Pt(8.5)
        p_r.font.color.rgb = C_MUTED
        p_r.space_before = Pt(2)

    p_close = tf_ref.add_paragraph()
    p_close.text = "Fechamento & Agradecimentos:"
    p_close.font.size = Pt(11.5)
    p_close.font.bold = True
    p_close.font.color.rgb = C_EMERALD
    p_close.space_before = Pt(10)

    p_closet = tf_ref.add_paragraph()
    p_closet.text = "Agradeço ao Professor Dr. Reinaldo Haas pela orientação e aos membros da banca examinadora pela atenção.\n\n" \
                    "O código-fonte completo (wyoming.py, tcon.py, skewt.py, plot_meso.py e o dashboard interativo) encontra-se disponível no repositório GitHub.\n\n" \
                    "Estou à disposição para as perguntas e considerações da banca."
    p_closet.font.size = Pt(9.5)
    p_closet.font.color.rgb = C_WHITE
    p_closet.space_before = Pt(3)

    set_speaker_notes(s10, """ROTEIRO DO ORADOR (18:30 - 20:00):
Chegamos à conclusão do nosso seminário com a síntese quantitativa que resume com precisão a magnitude do evento.
À esquerda, a tabela consolida os indicadores diagnosticados:
- O ambiente contava com flutuabilidade extrema (MUCAPE de 4.645 J/kg) e inibição virtualmente nula (-6.5 J/kg).
- O modelo reversível de Emanuel (1994) evidenciou que a retenção de condensado (water loading) atenua o CAPE em 340 J/kg, mas ainda sustenta 3.832 J/kg.
- O DCAPE de 1.149 J/kg conferiu potencial para correntes descendentes de até 48 m/s (172 km/h).
- O JBN em 925 hPa com 44 nós forneceu o influxo massivo de umidade (r = 22 g/kg, PW = 52.4 mm) e estabeleceu a curvatura do hodógrafo que garantiu uma Helicidade Relativa de 245 m²/s² e Cisalhamento 0-6 km de 28.7 m/s, favorecendo o desenvolvimento de uma Supercélula de Alta Precipitação (HP) com rajadas destrutivas.

Agradeço sinceramente ao Professor Reinaldo Haas e aos ilustres membros da banca examinadora.
Encerro a apresentação rigorosamente no tempo regulamentar de 20 minutos e coloco-me à inteira disposição para responder às perguntas da arguição. Muito obrigado!""")

    # Salva a apresentação
    out_pptx = "apresentacao_meso.pptx"
    prs.save(out_pptx)
    print(f"Apresentação salva com sucesso em: {os.path.abspath(out_pptx)}")
    print(f"Total de slides criados: {len(prs.slides)}")

if __name__ == '__main__':
    build_presentation()
