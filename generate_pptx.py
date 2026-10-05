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
    # SLIDE 1: Capa & Tutorial Didático para os Alunos (00 - 03 min, Parte 1)
    # --------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Header de Apresentação
    top_box = s1.shapes.add_textbox(Inches(1.0), Inches(0.55), Inches(11.3), Inches(0.45))
    p1 = top_box.text_frame.paragraphs[0]
    p1.text = "UFSC  |  DEPARTAMENTO DE FÍSICA / CFM  |  FSC7116 METEOROLOGIA DE MESOESCALA"
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = C_CYAN

    # Banner de Tutorial Didático (Obrigatório para os Alunos)
    tut_card = create_card(s1, Inches(1.0), Inches(1.05), Inches(11.33), Inches(1.05), bg_color=RGBColor(24, 38, 70), border_color=C_AMBER)
    tb_tut = s1.shapes.add_textbox(Inches(1.2), Inches(1.12), Inches(10.9), Inches(0.9))
    tf_tut = tb_tut.text_frame
    tf_tut.word_wrap = True
    p_tut1 = tf_tut.paragraphs[0]
    p_tut1.text = "📖 TUTORIAL & DIRETRIZ DIDÁTICA OBRIGATÓRIA PARA OS ALUNOS (PROF. REINALDO HAAS):"
    p_tut1.font.size = Pt(11)
    p_tut1.font.bold = True
    p_tut1.font.color.rgb = C_AMBER

    p_tut2 = tf_tut.add_paragraph()
    p_tut2.text = "Cada aluno ou grupo DEVE selecionar OBRIGATORIAMENTE TRÊS RADIOSSONDAGENS REAIS DISTINTAS contemplando os 3 estados atmosféricos:\n" \
                  "1) Atmosfera ESTÁVEL   |   2) Atmosfera NEUTRA (ou Transição)   |   3) Atmosfera INSTÁVEL (Convecção Severa)\n" \
                  "As sondagens podem diferir em DATAS na mesma localidade OU em LUGARES DIFERENTES (ex: SBPA, SBFL, SBCT, Argentina, etc.)."
    p_tut2.font.size = Pt(9.5)
    p_tut2.font.color.rgb = C_WHITE
    p_tut2.space_before = Pt(3)

    # Título Principal do Seminário
    t1_box = s1.shapes.add_textbox(Inches(1.0), Inches(2.25), Inches(11.3), Inches(1.4))
    tf1 = t1_box.text_frame
    tf1.word_wrap = True
    p_title = tf1.paragraphs[0]
    p_title.text = "Diagnóstico Termodinâmico e Dinâmico\nde Tempestade Severa em Mesoescala"
    p_title.font.size = Pt(28)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE

    p_sub = tf1.add_paragraph()
    p_sub.text = "Aplicação Metodológica: Estudo Comparativo das 3 Sondagens de Porto Alegre (SBPA - 83971)"
    p_sub.font.size = Pt(15)
    p_sub.font.color.rgb = C_CYAN
    p_sub.space_before = Pt(4)

    # 3 Cards de Destaque
    cards_data = [
        ("📍 3 Casos Selecionados", "1. Estável: 12/12/1995 12Z\n2. Neutra: 23/12/1995 12Z\n3. Instável: 24/12/1995 12Z\nLocal: SBPA (Porto Alegre)", C_CYAN),
        ("⚡ 3 Análises Completas", "• Flutuabilidade e CAPE/CIN\n• Emanuel Tρ e Water Loading\n• Freq. Brunt-Väisälä N² e Lid\n• JBN e Helicidade (SRH)", C_ROSE),
        ("📚 Arcabouço Teórico", "• Kerry Emanuel (1994)\n• MIT OCW 12.811\n• wyoming.f / tcon.py\n• MetPy & Cartopy", C_EMERALD)
    ]
    for i, (ctitle, cdesc, ccol) in enumerate(cards_data):
        card = create_card(s1, Inches(1.0 + i * 3.85), Inches(3.75), Inches(3.6), Inches(2.2))
        tb = s1.shapes.add_textbox(Inches(1.15 + i * 3.85), Inches(3.9), Inches(3.3), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = ctitle
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = ccol

        pd = tf.add_paragraph()
        pd.text = cdesc
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = C_WHITE
        pd.space_before = Pt(6)

    # Rodapé com Autor e Orientador
    foot_box = s1.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.85))
    tf_f = foot_box.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "Orientador: Prof. Dr. Reinaldo Haas   •   Disciplina: FSC7116 - Meteorologia de Mesoescala (UFSC)"
    p_f.font.size = Pt(11)
    p_f.font.bold = True
    p_f.font.color.rgb = C_MUTED
    p_f2 = tf_f.add_paragraph()
    p_f2.text = "⏱️ Tempo de Apresentação: 20 Minutos  |  Roteiro com 3 Sondagens e 3 Análises Completas para a Banca"
    p_f2.font.size = Pt(10)
    p_f2.font.color.rgb = C_AMBER
    p_f2.space_before = Pt(3)

    set_speaker_notes(s1, """ROTEIRO DO ORADOR & TUTORIAL DIDÁTICO (00:00 - 01:30):
Bom dia à banca examinadora, ao Professor Reinaldo Haas e aos colegas presentes.
Hoje apresento o seminário de Meteorologia de Mesoescala, concebido como um tutorial metodológico para a análise e diagnóstico de convecção profunda.

Conforme a diretriz da disciplina FSC7116, cada aluno deve selecionar obrigatoriamente três radiossondagens atmosféricas reais representando três estados fundamentais: uma atmosfera Estável, uma atmosfera Neutra (ou de transição) e uma atmosfera Instável (tempo severo).
Essas sondagens podem ser escolhidas em datas diferentes na mesma estação — como fizemos aqui para Porto Alegre (SBPA - 83971) em dezembro de 1995 — ou em estações e regiões geográficas diferentes (por exemplo, comparando simultaneamente SBPA, SBFL e SBCT).

Nossa apresentação contempla três sondagens e três análises físicas aprofundadas, fundamentadas no clássico 'Atmospheric Convection' de Kerry Emanuel (1994), nas rotinas wyoming.f do MIT OCW 12.811 e na biblioteca científica MetPy.""")

    # --------------------------------------------------------------------------
    # SLIDE 2: Sinótica e Caso de Estudo - 500 hPa e 850 hPa com Divisão Continental
    # --------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Forçamento Sinótico & Suporte Dinâmico de Mesoescala",
               "Acoplamento Vertical sobre a América do Sul (500 e 850 hPa) com Divisão de Continentes, Países e Estados (Cartopy)",
               "00 - 03 min", 2)

    # Imagem Sinótica com Cartopy à esquerda
    img_syn = 'metpack/fig_synoptic_analysis.png'
    if os.path.exists(img_syn):
        s2.shapes.add_picture(img_syn, Inches(0.8), Inches(1.75), width=Inches(7.2))

    # Card Explicativo à direita
    card_syn = create_card(s2, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_syn = s2.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_syn = tb_syn.text_frame
    tf_syn.word_wrap = True

    pts_syn = [
        ("Cartografia e Divisão Continental (Cartopy):", [
            "Mapa georreferenciado da América do Sul exibindo fronteiras de Brasil, Argentina, Uruguai e Paraguai, além dos estados (RS, SC, PR).",
            "Permite localizar espacialmente o contraste orográfico dos Andes e a Bacia do Prata."
        ], C_AMBER),
        ("Nível Médio (500 hPa) - Forçamento Dinâmico:", [
            "Cavado de onda curta pronunciado sobre a Argentina / Andes.",
            "Difluência acentuada a jusante diretamente sobre o RS.",
            "Advecção de Vorticidade Ciclônica Relativa (CVA / PVA) gerando sustentação de grande escala (ω < 0 via Eq. Ômega QG)."
        ], C_CYAN),
        ("Baixos Níveis (850 hPa) - Alimentação pelo JBN:", [
            "Jato em Baixos Níveis (JBN) canalizado a leste dos Andes com ventos > 23 m/s (44 kt) transportando calor e umidade da Amazônia/Chaco.",
            "Crista pronunciada de θe (> 355 K) convergindo no RS.",
            "Desestabilização diferencial da camada limite atmosférica."
        ], C_EMERALD)
    ]
    for block_title, bullets, bcol in pts_syn:
        pb = tf_syn.add_paragraph() if tf_syn.paragraphs[0].text else tf_syn.paragraphs[0]
        pb.text = block_title
        pb.font.size = Pt(10.5)
        pb.font.bold = True
        pb.font.color.rgb = bcol
        pb.space_before = Pt(6)
        for b in bullets:
            p_bullet = tf_syn.add_paragraph()
            p_bullet.text = f"• {b}"
            p_bullet.font.size = Pt(9.0)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s2, """ROTEIRO DO ORADOR (01:30 - 03:00):
Passando para a configuração sinótica que sustentou este caso no dia 24 de dezembro de 1995 às 12Z.
À esquerda, temos os mapas sinóticos gerados com a biblioteca Cartopy, incorporando a cartografia real da América do Sul com as divisões de continentes, fronteiras de países (Brasil, Argentina, Uruguai, Paraguai) e divisões estaduais (RS, SC, PR).
Essa divisão geográfica é essencial para visualizar como os Andes canalizam os escoamentos na baixa e média troposfera.

Em 500 hPa, observamos um cavado de onda curta bem estruturado sobre a Argentina, estabelecendo uma forte difluência de mesoescala sobre o Rio Grande do Sul. Pela teoria Quase-Geostrófica, a advecção de vorticidade ciclônica relativa positiva (CVA ou PVA) força movimentos verticais ascendentes de grande escala (ômega negativo), reduzindo as pressões e enfraquecendo a estabilidade.

Simultaneamente, em 850 hPa, identificamos a atuação clássica do Jato em Baixos Níveis da América do Sul (JBN), fluindo ao longo da borda leste dos Andes. O JBN atinge velocidades superiores a 23 m/s (44 nós) em 925/850 hPa, bombeando uma língua de altíssima temperatura potencial equivalente (θe > 355 K) direto da bacia Amazônica e do Chaco para o RS.
Esse acoplamento vertical — suporte dinâmico em altitude e advecção quente/úmida em baixos níveis — prepara o ambiente para a convecção explosiva.""")

    # --------------------------------------------------------------------------
    # SLIDE 3: As 3 Sondagens e as 3 Análises - Parte I: Estável vs Neutra
    # --------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "As Três Sondagens & Três Análises: Estável (12/12) vs Neutra (23/12)",
               "Diagnóstico Físico Individual dos Dois Primeiros Regimes: Pós-Frontal Estável e Transição Neutra",
               "03 - 07 min", 3)

    img_3s = 'metpack/fig_3_soundings_complete_analysis.png'
    if os.path.exists(img_3s):
        s3.shapes.add_picture(img_3s, Inches(0.8), Inches(1.75), width=Inches(7.2))

    card_s3 = create_card(s3, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_s3 = s3.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_s3 = tb_s3.text_frame
    tf_s3.word_wrap = True

    sections_s3 = [
        ("ANÁLISE 1: Atmosfera Estável (12/12/1995 12Z)", [
            "Sinótica: Domínio pós-frontal de alta pressão migratória e forte subsidência.",
            "Termodinâmica: Ar muito seco em médios níveis (T - Td > 15°C); inversão de subsidência; SBCAPE = 15.7 J/kg; MUCAPE = 0 J/kg; sem LFC/EL.",
            "Emanuel Tρ: Sem água líquida condensada (rl = 0); CAPE reversível e pseudoadiabático nulos.",
            "Brunt-Väisälä: N² > 0 em toda a coluna (estabilidade estática profunda)."
        ], C_CYAN),
        ("ANÁLISE 2: Atmosfera Neutra / Transição (23/12/1995 12Z)", [
            "Sinótica: Deslocamento da alta para o Atlântico; retorno do fluxo tropical de norte.",
            "Termodinâmica: Umedecimento progressivo da CLP (T0=25.8°C, Td0=24.4°C, r_max=19.4 g/kg); SBCAPE = 2762 J/kg; PW = 57.0 mm.",
            "Inibição / Gatilho: Apesar do CAPE moderado, ausência de suporte dinâmico em 500 hPa; cisalhamento fraco (Bulk Shear 0-6km = 10.2 m/s).",
            "Modo Convectivo: Regime quase-neutro, cúmulos desorganizados ou convecção isolada sem severidade."
        ], C_AMBER)
    ]
    for stitle, sbullets, scol in sections_s3:
        pb = tf_s3.add_paragraph() if tf_s3.paragraphs[0].text else tf_s3.paragraphs[0]
        pb.text = stitle
        pb.font.size = Pt(10.5)
        pb.font.bold = True
        pb.font.color.rgb = scol
        pb.space_before = Pt(6)
        for b in sbullets:
            p_bullet = tf_s3.add_paragraph()
            p_bullet.text = f"• {b}"
            p_bullet.font.size = Pt(9.0)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s3, """ROTEIRO DO ORADOR (03:00 - 05:00):
Entrando no bloco das Três Sondagens e Três Análises Físicas, conforme solicitado para a apresentação.
No painel à esquerda, exibimos lado a lado as radiossondagens de Porto Alegre com Skew-T, hodógrafo e métricas diagnósticas.

ANÁLISE 1 (Atmosfera Estável - 12/12/1995 12Z):
Este caso representa a atmosfera sob regime pós-frontal dominada por uma massa de ar frio e crista anticiclônica migratória. Notem a enorme separação entre a temperatura e o ponto de orvalho em médios níveis. O ar descendente (subsidência) aquece adiabaticamente e seca a coluna, impedindo a formação de nuvens convectivas.
O MUCAPE é estritamente zero; a frequência de Brunt-Väisälä N² é positiva em toda a troposfera, caracterizando estabilidade estática profunda. Não há suporte termodinâmico para nenhuma convecção.

ANÁLISE 2 (Atmosfera Neutra / Transição - 23/12/1995 12Z):
Onze dias depois, a sinótica muda: o anticiclone migra para o mar e ventos de quadrante norte começam a injetar umidade na camada limite. A razão de mistura sobe para 19.4 g/kg e o SBCAPE atinge 2.762 J/kg com PW de 57 mm.
No entanto, este ambiente é marginalmente neutro/transicional: não há forçamento dinâmico em 500 hPa e o cisalhamento vertical 0-6 km é fraco (apenas 10.2 m/s, com SRH de 81 m²/s²). O hodógrafo é quase linear e curto. Portanto, embora exista energia potencial, falta organização dinâmica, impedindo tempestades severas.""")

    # --------------------------------------------------------------------------
    # SLIDE 4: As 3 Sondagens e as 3 Análises - Parte II: Instável & Matriz Comparativa
    # --------------------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "As Três Sondagens & Três Análises: Instável Severa (24/12) & Matriz Comparativa",
               "Diagnóstico Físico do Caso Severo e Tabela Comparativa Tríplice dos Três Estados Atmosféricos",
               "03 - 07 min", 4)

    img_skew = 'metpack/fig_colab_severe_skewt.png'
    if os.path.exists(img_skew):
        s4.shapes.add_picture(img_skew, Inches(0.8), Inches(1.75), width=Inches(7.2))

    card_th = create_card(s4, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_th = s4.shapes.add_textbox(Inches(8.4), Inches(1.85), Inches(3.95), Inches(4.9))
    tf_th = tb_th.text_frame
    tf_th.word_wrap = True

    sections_th = [
        ("ANÁLISE 3: Atmosfera Instável / Explosiva (24/12)", [
            "Inversão quente/úmida em 925 hPa (JBN): T = 30°C, Td = 25°C, r = 22.02 g/kg.",
            "MUCAPE: 4.645 J/kg | SBCAPE: 1.862 J/kg | CIN: -6.5 J/kg.",
            "LCL a 600 m (942 hPa), LFC imediato e EL a 165 hPa (~13.8 km).",
            "Instabilidade Convectiva: ∂θe / ∂z < 0 profundo até 650 hPa."
        ], C_ROSE),
        ("MATRIZ COMPARATIVA TRÍPLICE (3 SONDAGENS):", [
            "• Estável (12/12): MUCAPE = 0 J/kg | CIN = 0 | Shear = 13.7 m/s | r = 11.6 g/kg",
            "• Neutra (23/12): MUCAPE = 2762 J/kg | CIN = 0 | Shear = 10.2 m/s | r = 19.4 g/kg",
            "• Instável (24/12): MUCAPE = 4645 J/kg | CIN = -6.5 | Shear = 28.7 m/s | r = 22.0 g/kg",
            "Conclusão: O caso 24/12 combina flutuabilidade extrema com cisalhamento supercelular e JBN."
        ], C_CYAN),
        ("Diretriz Metodológica para os Alunos:", [
            "Ao realizarem o trabalho, os alunos devem montar uma matriz comparativa análoga destacando a evolução física dos três estados."
        ], C_AMBER)
    ]
    for stitle, sbullets, scol in sections_th:
        pb = tf_th.add_paragraph() if tf_th.paragraphs[0].text else tf_th.paragraphs[0]
        pb.text = stitle
        pb.font.size = Pt(10.5)
        pb.font.bold = True
        pb.font.color.rgb = scol
        pb.space_before = Pt(5)
        for b in sbullets:
            p_bullet = tf_th.add_paragraph()
            p_bullet.text = f"• {b}"
            p_bullet.font.size = Pt(8.8)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s4, """ROTEIRO DO ORADOR (05:00 - 07:00):
Avançando para a ANÁLISE 3 (Atmosfera Instável Severa - 24/12/1995 12Z) e o confronto dos três casos na Matriz Comparativa.
No gráfico Skew-T à esquerda, gerado rigorosamente com o código do Google Colab do Prof. Reinaldo Haas, vemos o perfil termodinâmico explosivo de Porto Alegre.
A parcela de 925 hPa apresenta temperatura de 30°C com ponto de orvalho de 25°C e razão de mistura de 22 g/kg!
O MUCAPE atinge 4.645 J/kg com inibição de convecção insignificante (-6.5 J/kg). O LCL é extremamente baixo (600 metros) e o LFC ocorre imediatamente. Pela condição de instabilidade potencial, temos dθe/dz fortemente negativo até 650 hPa.

Na Matriz Comparativa Tríplice que estruturamos para os alunos:
- No dia 12 (Estável): MUCAPE é 0 J/kg, ar seco, subsidência.
- No dia 23 (Neutro): MUCAPE é 2.762 J/kg, mas o cisalhamento vertical é fraco (10.2 m/s) e não há forçamento em 500 hPa.
- No dia 24 (Instável Severo): MUCAPE salta para 4.645 J/kg, acompanhado de cisalhamento profundo de 28.7 m/s e SRH de 245 m²/s².
Essa comparação tríplice ilustra com clareza a física da convecção severa: não basta ter apenas CAPE moderado; é a convergência do JBN, o rompimento da tampa de inversão e o cisalhamento rotatório que determinam o evento severo.""")

    # --------------------------------------------------------------------------
    # SLIDE 5: Emanuel (1994) & Temp. Densidade nas 3 Sondagens (07 - 10 min)
    # --------------------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Teoria de Emanuel (1994) & Matrizes 2D das Três Sondagens",
               "Comparação Tríplice no wyoming.py / tcon.py - Water Loading (-rl) e Flutuabilidade (MIT OCW 12.811)",
               "07 - 10 min", 5)

    img_emanuel = 'metpack/fig_3_soundings_emanuel_matrices.png'
    if not os.path.exists(img_emanuel):
        img_emanuel = 'metpack/tcon_comparacao_emanuel.png'
    if os.path.exists(img_emanuel):
        s5.shapes.add_picture(img_emanuel, Inches(0.8), Inches(1.75), width=Inches(7.2))

    card_em = create_card(s5, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_em = s5.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_em = tb_em.text_frame
    tf_em.word_wrap = True

    sections_em = [
        ("Fundamentação Teórica - Kerry Emanuel (1994):", [
            "Referência: Kerry Emanuel (1994), 'Atmospheric Convection', Oxford Univ. Press (Cap. 4 e 6).",
            "Disciplina clássica do MIT: MIT OCW 12.811.",
            "Código de referência: wyoming.f / wyoming.py e matrizes tdifrev / tdifpseudo."
        ], C_CYAN),
        ("Temperatura de Densidade (Tρ) & Arrasto:", [
            "Tρ = T · (1 + rv/ε) / (1 + rv + rl) ≈ Tv · (1 - rl)",
            "Incorpora o peso da água líquida condensada suspensa na parcela (-rl)."
        ], C_AMBER),
        ("Diagnóstico dos 3 Regimes nas Matrizes 2D:", [
            "12/12 (Estável): Azul em toda a malha. Flutuabilidade negativa, sem suporte a convecção (PA ≈ 23 J/kg).",
            "23/12 (Neutra): Camada de empuxo positiva moderada rasa (PA = 2.536 J/kg pseudo vs 1.266 J/kg rev).",
            "24/12 (Instável Severa): Núcleo maciço de empuxo extremo (ΔT > +10 K) de 950 a 400 hPa. No JBN (925 hPa), PA atinge 7.781 J/kg com redução de 1.534 J/kg (-19.7%) por water loading!"
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
            p_bullet.font.size = Pt(9.3)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s5, """ROTEIRO DO ORADOR (07:00 - 10:00):
Este slide é de primordial importância para a banca, pois conecta nosso estudo diretamente com o arcabouço teórico de Kerry Emanuel (1994), 'Atmospheric Convection', e o material do curso MIT OCW 12.811.
À esquerda, temos os gráficos 2D gerados pelo tcon.py / wyoming.py para as TRÊS radiossondagens simultaneamente.
A linha superior mostra a ascensão Reversível (temperatura de densidade Tρ com retenção de condensado), enquanto a linha inferior mostra a ascensão Pseudoadiabática (temperatura virtual Tv com precipitação instantânea).

Notem o contraste perfeito entre os três regimes:
1. No caso Estável (12/12), a matriz inteira é dominada por cores azuis (anomalia negativa). Qualquer parcela deslocada é mais fria e mais densa que o ambiente, retornando ao equilíbrio.
2. No caso Neutro (23/12), surge uma camada rasa de flutuabilidade positiva moderada perto da superfície, com o CAPE caindo pela metade no modo reversível (de 2536 para 1266 J/kg).
3. No caso Instável Severo (24/12), vemos um núcleo violento de cores quentes (vermelho escuro) estendendo-se de 950 até 400 hPa, com anomalia térmica superior a +10 K!
Para a parcela de 925 hPa (JBN), o PA pseudoadiabático atinge 7.781 J/kg, mas o reversível cai para 6.247 J/kg. A diferença de 1.534 J/kg (-19.7%) é o freio exercido pelo peso dos hidrometeoros retidos (water loading), essencial para não superestimar a corrente ascendente.""")

    # --------------------------------------------------------------------------
    # SLIDE 6: Variáveis do Colab / Cap. 2: Comparação das 3 Sondagens (10 - 14 min, Parte 1)
    # --------------------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Perfis Verticais do Colab: Comparação das Três Sondagens",
               "Confronto de θe, Frequência de Brunt-Väisälä (N), Estabilidade Estática (S) e Umidade (r)",
               "10 - 14 min", 6)

    img_p2 = 'metpack/fig_3_soundings_profiles_comparison.png'
    if not os.path.exists(img_p2):
        img_p2 = 'metpack/fig_cap2_profiles.png'
    if os.path.exists(img_p2):
        s6.shapes.add_picture(img_p2, Inches(0.8), Inches(1.75), width=Inches(7.2))

    card_c2 = create_card(s6, Inches(8.2), Inches(1.75), Inches(4.35), Inches(5.15))
    tb_c2 = s6.shapes.add_textbox(Inches(8.4), Inches(1.9), Inches(3.95), Inches(4.85))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True

    sections_c2 = [
        ("Temperatura Potencial Equivalente (θe):", [
            "12/12 (Estável): θe_sfc = 324.2 K, perfil quase uniforme, sem instabilidade.",
            "23/12 (Neutra): θe_sfc = 354.8 K, umedecimento da coluna, mas gradiente vertical fraco.",
            "24/12 (Severa): Injeção colossal de θe = 377.8 K pelo JBN em 925 hPa com forte gradiente ∂θe/∂z < 0 (instabilidade potencial severa)."
        ], C_CYAN),
        ("Frequência de Brunt-Väisälä (N) & Capping Lid:", [
            "N² = (g / θv) · (∂θv / ∂z) quantifica a rigidez de oscilação das ondas de gravidade.",
            "12/12 & 23/12: Sem inversão expressiva em baixos níveis.",
            "24/12: Pico agudo de N em 925 hPa (~0.028 s⁻¹) formando o Capping Lid (tampa de panela de pressão que conteve a convecção até o disparo explosivo)."
        ], C_PURPLE),
        ("Estabilidade Estática (S) & Razão de Mistura (r):", [
            "12/12: r_max = 11.6 g/kg | PW = 35.1 mm (ar pós-frontal seco).",
            "23/12: r_max = 19.4 g/kg | PW = 57.0 mm (advecção tropical).",
            "24/12: r_max = 22.0 g/kg em 925 hPa | PW = 55.3 mm (núcleo extremo de vapor alimentado pelo JBN)."
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
            p_bullet.font.size = Pt(9.2)
            p_bullet.font.color.rgb = C_WHITE
            p_bullet.space_before = Pt(2)

    set_speaker_notes(s6, """ROTEIRO DO ORADOR (10:00 - 12:00):
Neste slide, confrontamos os perfis verticais calculados no Google Colab via MetPy para as TRÊS radiossondagens simultaneamente, revelando a assinatura termodinâmica de cada regime.
No Painel 1, observem o perfil de temperatura potencial equivalente (θe):
- A curva azul (12/12) reflete a massa de ar pós-frontal estável, com θe de apenas 324 K.
- A curva amarela (23/12) mostra o ar tropical retornando, com θe em 354 K.
- A curva vermelha (24/12) é impressionante: o JBN injeta um pulso de θe de 377.8 K em 925 hPa, criando um fortíssimo decaimento com a altitude (∂θe/∂z < 0). Isso define formalmente a Instabilidade Convectiva Potencial extrema.

No Painel 2, temos a Frequência de Brunt-Väisälä (N).
Vejam como no caso severo de 24/12 surge um pico acentuado de N exatamente em 925 hPa. Esse pico marca a famosa inversão térmica conhecida como 'Capping Lid' (a tampa da camada limite).
Como explicado por Kerry Emanuel no Capítulo 2, o Capping Lid é indispensável para surtos de supercélulas: ele impede que a energia seja liberada prematuramente pela manhã, permitindo que a camada limite acumule vapor e calor até explodir violentamente à tarde.

Nos Painéis 3 e 4, a estabilidade estática S e a razão de mistura r confirmam o quadro: no dia 24/12, a razão de mistura atingiu 22.0 g/kg no nível do Jato, um valor excepcional para latitudes subtropicais.""")

    # --------------------------------------------------------------------------
    # SLIDE 7: Razão de Mistura (r), PW e DCAPE (10 - 14 min, Parte 2)
    # --------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Umidade Troposférica & Potencial de Downbursts",
               "Razão de Mistura r(z), Água Precipitável (PW) e Downdraft CAPE (DCAPE) via Resfriamento Evaporativo",
               "10 - 14 min", 7)

    img_diag = 'metpack/fig_profiles_19951224.png'
    if not os.path.exists(img_diag):
        img_diag = 'metpack/fig_cap2_profiles.png'
    if not os.path.exists(img_diag):
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
    # SLIDE 9: Monitoramento por Satélite: Imagem Infravermelho (IR 11 µm) (17 - 19 min)
    # --------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Monitoramento por Satélite: Imagem Infravermelho (IR 11 µm)",
               "Satélite GOES-8 / NOAA ISCCP-H (24/12/1995): Evolução da Convecção Profunda e Enchente de Natal",
               "17 - 19 min", 9)

    img_sat = 'metpack/fig_sat_ir_19951224.png'
    if os.path.exists(img_sat):
        s9.shapes.add_picture(img_sat, Inches(0.6), Inches(1.7), width=Inches(8.4))

    card_s9 = create_card(s9, Inches(9.2), Inches(1.7), Inches(3.5), Inches(5.2))
    tb_s9 = s9.shapes.add_textbox(Inches(9.35), Inches(1.85), Inches(3.2), Inches(4.9))
    tf_s9 = tb_s9.text_frame
    tf_s9.word_wrap = True

    sections_s9 = [
        ("Satélite & Base de Dados:", [
            "Sensor: Imager GOES-8 (Canal 4 - IR 11 µm).",
            "Fonte: NOAA ISCCP-H CDR (Gridded 10 km).",
            "Cobertura: América do Sul e Bacia do Prata."
        ], C_CYAN),
        ("Painel A (12:00 UTC / 09:00 HL):", [
            "Horário síncrono da radiossondagem de SBPA.",
            "Camada de ar úmido sob forte Capping Lid.",
            "Convecção ativa sobre a fronteira oeste com topos a -59°C (170 hPa)."
        ], C_AMBER),
        ("Painel B (18:00 UTC / 15:00 HL):", [
            "Auge vespertino da convecção severa.",
            "Rompimento explosivo da inversão e avanço do Complexo Convectivo de Mesoescala (CCM).",
            "Topos penetrantes a -63.5°C (160 hPa) descarregando chuvas torrenciais (Enchente de Natal)."
        ], C_ROSE)
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
Apresentamos agora a comprovação observacional por satélite meteorológico para o dia 24 de dezembro de 1995.
Utilizamos os dados do sensor de infravermelho de 11 micrômetros do satélite GOES-8, processados a partir do Climate Data Record ISCCP-H da NOAA, cobrindo o Sul do Brasil e a Bacia do Prata.

No Painel A, correspondente às 12:00 UTC (9 da manhã no horário local), exatamente no momento do lançamento da nossa radiossondagem em Porto Alegre, observamos a nebulosidade associada à frente fria e ao canal de umidade do JBN. Os topos convectivos mais frios já atingiam cerca de -59°C sobre o oeste e sul do Rio Grande do Sul, enquanto a região metropolitana de Porto Alegre ainda acumulava calor sob a tampa de inversão térmica.

No Painel B, às 18:00 UTC (3 da tarde, horário local), testemunhamos o ápice da atividade convectiva explosiva. Com o aquecimento superficial e a advecção forçada, o capping lid foi superado, e a energia disponível de mais de 4.600 J/kg de CAPE foi liberada violentamente.
A imagem infravermelha realçada revela topos penetrantes ultrapassando -63°C no nível de 160 hPa, estruturando um intenso Complexo Convectivo de Mesoescala.
Foi essa configuração de tempestades severas supercelulares de alta precipitação que desencadeou a histórica Enchente de Natal de 1995 no Sul do Brasil, provocando acumulados pluviométricos extremos em Santa Catarina e no leste gaúcho.""")

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
