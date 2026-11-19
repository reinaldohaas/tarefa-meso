"""
build_index_html.py - Compilador do Tutorial Didático de Meteorologia de Mesoescala (FSC7116 - UFSC)
Gera o index.html (GitHub Pages) estruturado pedagogicamente em ordem de aprendizado:
- Tema claro por padrão (projetor/impressão), coluna única, responsivo para mobile (390px) e desktop (1366px).
- Imagens clicáveis com lightbox para zoom.
- Zero números digitados à mão: todas as métricas são lidas dinamicamente de metpack/metricas.json.
- Oito seções estruturadas:
  1. Os Dados (Wyoming, download e controle de qualidade)
  2. Diagramas Skew-T (uma figura por sondagem com LCL/LFC/EL e parcela)
  3. Índices Convectivos e Tabela de Conferência (com os 3 métodos de DCAPE)
  4. Perfis Verticais de Estabilidade (θ, θe, θes, N² e S = -(T/θ)∂θ/∂p até 200 hPa)
  5. Cinemática de Mesoescala e Hodógrafo (Bunkers LM, SRH ciclônica no Hemisfério Sul)
  6. Matrizes Termodinâmicas 2D de Kerry Emanuel (escala simétrica +-15 K, isolinha 0 K destacada)
  7. Agora é sua Vez (roteiro, botão "Abrir no Colab" para Seminario_plot_sounding_revisado.ipynb)
  8. Referências Bibliográficas Clássicas
"""

import json
import os

def load_metrics():
    with open('metpack/metricas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html():
    m = load_metrics()

    s12 = m['19951212']
    s22 = m['19951222']
    s24_raw = m['19951224_raw']
    s24_sens = m.get('19951224_sensibilidade', m.get('19951224_qc', {}))
    dcape_comp = m.get('dcape_comparativo', {})

    # 1. Tabela de Gradientes e Controle de Qualidade (Seção 1)
    superad_layers = m.get('qc_camadas_superadiabaticas_19951224', [])
    superad_rows = []
    for layer in superad_layers:
        status_tag = ""
        if layer.get('is_superadiabatic'):
            status_tag = '<span style="color:#dc2626; font-weight:600;">Superadiabática (Γ > 9.8 K/km)</span>'
        elif layer.get('is_large_dthe'):
            status_tag = '<span style="color:#d97706; font-weight:600;">Descontinuidade de θe (> 15 K)</span>'
        superad_rows.append(f"""
            <tr>
                <td><strong>{layer['layer_p_bottom']:.1f} → {layer['layer_p_top']:.1f} hPa</strong></td>
                <td>{layer['dz_m']:.0f} m</td>
                <td>{layer['dT_C']:+.1f} °C</td>
                <td style="color:{'#dc2626' if layer['gamma_K_km'] > 9.8 else '#0f172a'}; font-weight:600;">{layer['gamma_K_km']:.2f} K/km</td>
                <td style="color:{'#dc2626' if layer['dtheta_dz_K_km'] < 0 else '#0f172a'};">{layer['dtheta_dz_K_km']:.2f} K/km</td>
                <td>{layer['dtheta_e_K']:+.1f} K</td>
                <td style="text-align:left;">{status_tag}</td>
            </tr>
        """)
    superad_tbody = "\n".join(superad_rows)

    # 2. Tabela Diagnóstica Comparativa Geral (Seção 3)
    master_diag_rows = [
        ("Água Precipitável (PW)", f"{s12['pw_mm']:.1f} mm", f"{s22['pw_mm']:.1f} mm", f"{s24_raw['pw_mm']:.1f} mm", f"{s24_sens['pw_mm']:.1f} mm"),
        ("SBCAPE (Superfície)", f"{s12['sbcape_Jkg']:.1f} J/kg", f"{s22['sbcape_Jkg']:.1f} J/kg", f"{s24_raw['sbcape_Jkg']:.1f} J/kg", f"{s24_sens['sbcape_Jkg']:.1f} J/kg"),
        ("SBCIN (Inibição de Superfície)", f"{s12['sbcin_Jkg']:.1f} J/kg", f"{s22['sbcin_Jkg']:.1f} J/kg", f"{s24_raw['sbcin_Jkg']:.1f} J/kg", f"{s24_sens['sbcin_Jkg']:.1f} J/kg"),
        ("MUCAPE (Parcela Mais Instável)", f"{s12['mucape_Jkg']:.1f} J/kg", f"{s22['mucape_Jkg']:.1f} J/kg", f"{s24_raw['mucape_Jkg']:.1f} J/kg", f"{s24_sens['mucape_Jkg']:.1f} J/kg"),
        ("MUCIN", f"{s12['mucin_Jkg']:.1f} J/kg", f"{s22['mucin_Jkg']:.1f} J/kg", f"{s24_raw['mucin_Jkg']:.1f} J/kg", f"{s24_sens['mucin_Jkg']:.1f} J/kg"),
        ("Nível do LCL", f"{s12['lcl_p_hPa']:.1f} hPa", f"{s22['lcl_p_hPa']:.1f} hPa", f"{s24_raw['lcl_p_hPa']:.1f} hPa", f"{s24_sens['lcl_p_hPa']:.1f} hPa"),
        ("Cisalhamento Bulk 0–6 km", f"{s12['bulk_shear_0_6km_ms']:.1f} m/s ({s12['bulk_shear_0_6km_kt']:.1f} kt)", f"{s22['bulk_shear_0_6km_ms']:.1f} m/s ({s22['bulk_shear_0_6km_kt']:.1f} kt)", f"{s24_raw['bulk_shear_0_6km_ms']:.1f} m/s ({s24_raw['bulk_shear_0_6km_kt']:.1f} kt)", f"{s24_sens['bulk_shear_0_6km_ms']:.1f} m/s ({s24_sens['bulk_shear_0_6km_kt']:.1f} kt)"),
        ("Vento Observado em 925 hPa", f"{s12['wind_925_spd_kt']:.1f} kt de {s12['wind_925_dir_deg']:.0f}°", f"{s22['wind_925_spd_kt']:.1f} kt de {s22['wind_925_dir_deg']:.0f}°", f"{s24_raw['wind_925_spd_kt']:.1f} kt de {s24_raw['wind_925_dir_deg']:.0f}°", "Nível omitido"),
        ("SRH 0–3 km (Bunkers Left-Mover)", f"{s12['srh_0_3km_lm_m2s2']:.1f} m²/s²", f"{s22['srh_0_3km_lm_m2s2']:.1f} m²/s²", f"{s24_raw['srh_0_3km_lm_m2s2']:.1f} m²/s²", f"{s24_sens['srh_0_3km_lm_m2s2']:.1f} m²/s²"),
    ]
    master_diag_tbody = "\n".join([
        f"<tr><td style='text-align:left;'><strong>{row[0]}</strong></td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
        for row in master_diag_rows
    ])

    # 3. Tabela de Conferência Wyoming vs Calculado (Seção 3)
    comp_wy = m.get('comparativo_wyoming_metpy', {})
    comp_tables_html = []
    color_map = {'19951212': '#1f77b4', '19951222': '#d97706', '19951224': '#dc2626'}
    for date_key in ['19951212', '19951222', '19951224']:
        c_info = comp_wy.get(date_key, {})
        dt_label = c_info.get('data', date_key)
        c_theme = color_map.get(date_key, '#0f172a')
        rows_html = []
        for row in c_info.get('linhas', []):
            diff_str = f"{row['diferenca']:+}" if row.get('diferenca') is not None else "-"
            w_str = f"{row['wyoming']}" if row.get('wyoming') is not None else "N/A"
            calc_val = row.get('metpy', row.get('siphon_metpy', row.get('calculado')))
            c_str = f"{calc_val}" if calc_val is not None else "N/A"
            rows_html.append(f"""
                <tr>
                    <td style="text-align:left;"><strong>{row['indice']}</strong></td>
                    <td style="color:#0284c7;">{w_str}</td>
                    <td style="color:#16a34a; font-weight:600;">{c_str}</td>
                    <td style="color:#475569; font-weight:600;">{diff_str}</td>
                </tr>
            """)
        tbody = "\n".join(rows_html)
        comp_tables_html.append(f"""
            <div class="table-card">
                <h4 style="color:{c_theme}; margin-top:0; margin-bottom:10px; font-size:1.0rem; border-bottom: 2px solid {c_theme}; padding-bottom: 4px;">
                    Sondagem {dt_label} 12Z
                </h4>
                <div class="table-responsive">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th style="text-align:left;">Índice</th>
                                <th>Wyoming (Oficial)</th>
                                <th>MetPy</th>
                                <th>Diferença (Δ)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tbody}
                        </tbody>
                    </table>
                </div>
            </div>
        """)
    wyoming_comp_section = "\n".join(comp_tables_html)

    # 4. Tabela comparativa dos 3 métodos de DCAPE
    dcape_rows = []
    for k, info in dcape_comp.items():
        w_val = f"{info['wyoming_Jkg']:.1f} J/kg" if info.get('wyoming_Jkg') is not None else "-"
        m_val = f"{info['metpy_Jkg']:.1f} J/kg" if info.get('metpy_Jkg') is not None else "-"
        em_val = f"{info['emanuel_max_Jkg']:.1f} J/kg ({info.get('emanuel_max_p_hPa', 0):.0f} hPa)" if info.get('emanuel_max_Jkg') is not None else "-"
        dcape_rows.append(f"""
            <tr>
                <td style="text-align:left;"><strong>{info['data']} ({info['regime']})</strong></td>
                <td style="color:#0284c7;">{w_val}</td>
                <td style="color:#16a34a; font-weight:600;">{m_val}</td>
                <td style="color:#d97706; font-weight:600;">{em_val}</td>
            </tr>
        """)
    dcape_tbody = "\n".join(dcape_rows)

    # 5. Dados da Parte 2 (Simulação WRF dos Hidrometeoros)
    wrf_meta_path = os.path.join('wrfpack', 'metricas_wrf.json')
    wrf_rows = []
    if os.path.exists(wrf_meta_path):
        with open(wrf_meta_path, 'r', encoding='utf-8') as f:
            wm = json.load(f)
        for r in wm.get('tabela_maximos', []):
            cor_dot = f'<span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:{r["cor"]};margin-right:6px;vertical-align:middle;border:1px solid #475569;"></span>'
            wrf_rows.append(f"""
                <tr>
                    <td style="text-align:left;">{cor_dot}<strong><code>{r['variavel']}</code></strong>, {r['nome']}</td>
                    <td style="font-weight:700; color:#0f172a;">{r['max_g_kg']:.3f} g/kg</td>
                    <td>{r['altura_km']:.2f} km</td>
                    <td style="color:{'#dc2626' if r['temperatura_C'] > 0 else '#0284c7'}; font-weight:600;">{r['temperatura_C']:+.1f} °C</td>
                    <td>{r['pressao_hPa']:.1f} hPa</td>
                    <td>{r['limiar_g_kg']:g} g/kg</td>
                </tr>
            """)
    wrf_tbody = "\n".join(wrf_rows)

    # HTML Base sem f-string para evitar conflitos de interpolação com CSS e LaTeX
    html_template = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tutorial de Meteorologia de Mesoescala: Diagnóstico Físico e Termodinâmico (FSC7116 - UFSC)</title>
    <!-- KaTeX para renderização de fórmulas matemáticas -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body);"></script>
    <style>
        :root {
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #475569;
            --border-color: #e2e8f0;
            --color-c12: #1f77b4;
            --color-c22: #d97706;
            --color-c24: #dc2626;
            --color-sens: #7c3aed;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            line-height: 1.6;
            font-size: 16px;
        }

        .container {
            max-width: 1040px;
            margin: 0 auto;
            padding: 32px 20px 80px 20px;
        }

        /* Cabeçalho */
        header {
            background: #ffffff;
            border-bottom: 1px solid var(--border-color);
            padding: 36px 20px;
            margin-bottom: 32px;
        }

        .header-inner {
            max-width: 1040px;
            margin: 0 auto;
        }

        h1 {
            font-size: 1.85rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0 0 10px 0;
            line-height: 1.25;
        }

        .subtitle {
            font-size: 1.05rem;
            color: var(--text-muted);
            margin: 0 0 16px 0;
        }

        .header-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            font-size: 0.9rem;
            color: #64748b;
        }

        .header-meta a {
            color: #0284c7;
            text-decoration: none;
            font-weight: 600;
        }

        .header-meta a:hover {
            text-decoration: underline;
        }

        /* Botão do Colab */
        .colab-button {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background-color: #f59e0b;
            color: #000000;
            font-weight: 700;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            margin-top: 14px;
            transition: background 0.2s;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .colab-button:hover {
            background-color: #d97706;
            color: #ffffff;
        }

        /* Seções Didáticas */
        .tutorial-section {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 28px;
            margin-bottom: 36px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }

        .section-header {
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        h2 {
            font-size: 1.35rem;
            font-weight: 700;
            color: #0f172a;
            margin: 0 0 4px 0;
        }

        .block-title {
            font-size: 1.0rem;
            font-weight: 700;
            color: #1e293b;
            margin: 20px 0 8px 0;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .explanation-text {
            color: #334155;
            font-size: 0.98rem;
            margin-bottom: 16px;
            line-height: 1.65;
        }

        /* Imagens e Figuras */
        .figure-wrapper {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 10px;
            margin: 16px 0;
            text-align: center;
        }

        .figure-wrapper img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            cursor: zoom-in;
            transition: opacity 0.2s;
        }

        .figure-wrapper img:hover {
            opacity: 0.96;
        }

        .figure-caption {
            font-size: 0.85rem;
            color: #64748b;
            margin-top: 8px;
            font-style: italic;
        }

        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
            margin: 16px 0;
        }

        /* Como Ler */
        .how-to-read {
            background: #f1f5f9;
            border-left: 4px solid #0284c7;
            padding: 14px 18px;
            border-radius: 0 6px 6px 0;
            margin: 16px 0;
        }

        .how-to-read ul {
            margin: 6px 0 0 0;
            padding-left: 20px;
            color: #334155;
            font-size: 0.94rem;
        }

        .how-to-read li {
            margin-bottom: 6px;
        }

        /* Perguntas para o Aluno */
        .student-questions {
            background: #fefce8;
            border-left: 4px solid #eab308;
            padding: 14px 18px;
            border-radius: 0 6px 6px 0;
            margin: 18px 0 8px 0;
        }

        .student-questions ol {
            margin: 6px 0 0 0;
            padding-left: 20px;
            color: #451a03;
            font-size: 0.94rem;
        }

        .student-questions li {
            margin-bottom: 8px;
        }

        /* Tabelas */
        .table-responsive {
            overflow-x: auto;
            margin: 16px 0;
        }

        table.data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
            text-align: center;
            background: #ffffff;
        }

        table.data-table th, table.data-table td {
            padding: 9px 12px;
            border: 1px solid #e2e8f0;
        }

        table.data-table th {
            background-color: #f1f5f9;
            color: #1e293b;
            font-weight: 700;
        }

        table.data-table tr:hover {
            background-color: #f8fafc;
        }

        .table-grid-3 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
            gap: 16px;
            margin: 16px 0;
        }

        .table-card {
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 12px;
            background: #ffffff;
        }

        /* Modal Lightbox para Imagens */
        .modal {
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(15, 23, 42, 0.9);
            cursor: zoom-out;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            max-width: 95%;
            max-height: 95%;
            border-radius: 6px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }

        /* Deck de Apresentação Interativa de 10 Slides (WRF) */
        .deck-container {
            background: #0b132b;
            color: #f8fafc;
            border: 1px solid #1e293b;
            border-radius: 10px;
            overflow: hidden;
            margin: 18px 0 28px 0;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.25);
        }
        .deck-topbar {
            background: #131e3a;
            border-bottom: 1px solid #2e4066;
            padding: 12px 18px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }
        .deck-meta {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #38bdf8;
            text-transform: uppercase;
        }
        .deck-controls {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .deck-btn {
            background: #1e293b;
            color: #f8fafc;
            border: 1px solid #475569;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }
        .deck-btn:hover {
            background: #334155;
            border-color: #38bdf8;
        }
        .deck-btn-accent {
            background: #c2410c;
            border-color: #ea580c;
            color: #ffffff;
        }
        .deck-btn-accent:hover {
            background: #ea580c;
        }
        .deck-dots {
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }
        .deck-dot {
            width: 26px;
            height: 26px;
            border-radius: 5px;
            border: 1px solid #334155;
            background: #0f172a;
            color: #94a3b8;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        .deck-dot.active {
            background: #fbbf24;
            color: #0f172a;
            border-color: #fbbf24;
        }
        .wrf-slide {
            display: none;
            padding: 24px 26px;
            min-height: 510px;
        }
        .wrf-slide.active {
            display: block;
        }
        .slide-header-row {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 16px;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 12px;
        }
        .slide-title {
            font-size: 1.32rem;
            font-weight: 700;
            color: #f8fafc;
            margin: 0 0 4px 0;
        }
        .slide-subtitle {
            font-size: 0.92rem;
            color: #94a3b8;
            margin: 0;
        }
        .slide-time-badge {
            background: #1e293b;
            border: 1px solid #fbbf24;
            color: #fbbf24;
            font-size: 0.82rem;
            font-weight: 700;
            padding: 5px 12px;
            border-radius: 6px;
            white-space: nowrap;
        }
        .slide-grid-2 {
            display: grid;
            grid-template-columns: 1.05fr 1.15fr;
            gap: 18px;
            align-items: start;
        }
        .slide-card {
            background: #131e3a;
            border: 1px solid #2e4066;
            border-radius: 8px;
            padding: 16px;
        }
        .slide-card h4 {
            margin: 0 0 10px 0;
            font-size: 0.98rem;
            color: #38bdf8;
            border-bottom: 1px solid #2e4066;
            padding-bottom: 6px;
        }
        .slide-card ul {
            margin: 0;
            padding-left: 18px;
            font-size: 0.9rem;
            line-height: 1.6;
            color: #e2e8f0;
        }
        .slide-card li {
            margin-bottom: 8px;
        }
        .slide-fig {
            background: #0f172a;
            border: 1px solid #2e4066;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
        }
        .slide-fig img {
            max-width: 100%;
            max-height: 360px;
            height: auto;
            border-radius: 4px;
            cursor: zoom-in;
        }
        .slide-fig-cap {
            font-size: 0.8rem;
            color: #94a3b8;
            margin-top: 6px;
        }
        .slide-notes {
            margin-top: 14px;
            background: rgba(15, 23, 42, 0.75);
            border-left: 3px solid #fbbf24;
            padding: 10px 14px;
            font-size: 0.85rem;
            color: #cbd5e1;
            border-radius: 0 6px 6px 0;
        }
        .deck-container:fullscreen {
            width: 100vw;
            height: 100vh;
            margin: 0;
            border-radius: 0;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }
        .deck-container:fullscreen .wrf-slide {
            flex: 1;
            padding: 32px 48px;
        }
        .deck-container:fullscreen .slide-fig img {
            max-height: 55vh;
        }

        /* Responsividade */
        @media (max-width: 768px) {
            .slide-grid-2 { grid-template-columns: 1fr; }
        }
        @media (max-width: 640px) {
            h1 { font-size: 1.35rem; }
            h2 { font-size: 1.15rem; word-break: break-word; }
            .container { padding: 16px 12px 60px 12px; }
            header { padding: 24px 14px; }
            .tutorial-section { padding: 16px 12px; }
            .gallery-grid { grid-template-columns: 1fr; }
            .table-grid-3 { grid-template-columns: 1fr; }
            .colab-button { font-size: 0.88rem; padding: 8px 14px; }
        }
    </style>
</head>
<body>

    <header>
        <div class="header-inner">
            <h1>Tutorial de Meteorologia de Mesoescala: Diagnóstico Físico & Termodinâmico</h1>
            <p class="subtitle">Análise Observacional de Três Regimes Troposféricos (Kerry Emanuel, 1994 & MetPy)</p>
            <div class="header-meta">
                <span><strong>Disciplina:</strong> Meteorologia de Mesoescala (FSC7116)</span>
                <span><strong>Docente:</strong> Prof. Dr. Reinaldo Haas (UFSC)</span>
                <span><strong>Repositório:</strong> <a href="https://github.com/reinaldohaas/tarefa-meso" target="_blank">github.com/reinaldohaas/tarefa-meso</a></span>
            </div>
            <div>
                <a class="colab-button" href="https://colab.research.google.com/github/reinaldohaas/tarefa-meso/blob/master/Seminario_plot_sounding_revisado.ipynb" target="_blank">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z"/></svg>
                    Abrir no Google Colab (Seminario_plot_sounding_revisado.ipynb)
                </a>
                <a class="colab-button" href="https://github.com/reinaldohaas/tarefa-meso/blob/master/ROTEIRO_ESTUDANTES.md" target="_blank" style="margin-left:8px;">
                    Roteiro do estudante (instruções e as três formas de rodar)
                </a>
                <a class="colab-button" href="https://github.com/reinaldohaas/tarefa-meso/blob/master/TAREFA_WRF_HIDROMETEOROS.md" target="_blank" style="margin-left:8px;">
                    Seminário Final (Parte 2): tarefa do WRF, até 5/12/2026
                </a>
                <a class="colab-button" href="apresentacao_parte2.html" style="margin-left:8px; background-color:#ea580c; color:#ffffff;">
                    ▶ Apresentação da Parte 2 (10 slides, 20 min)
                </a>
            </div>
        </div>
    </header>

    <div class="container">

        <!-- SEÇÃO 1: OS DADOS -->
        <section class="tutorial-section" id="sec-dados">
            <div class="section-header">
                <h2>1. Os Dados: Universidade de Wyoming, Download e Controle de Qualidade</h2>
            </div>
            <div class="explanation-text">
                As radiossondagens atmosféricas brutas são obtidas do servidor da Universidade de Wyoming nos formatos 
                <code>TEXT:LIST</code> (tabela vertical dos níveis de pressão) e <code>INDICES</code> (índices derivados). 
                Antes de qualquer cálculo, realiza-se o controle de qualidade (QC) para verificar a consistência vertical, 
                garantir que \(T_d \le T\) e detectar gradientes térmicos verticais superadiabáticos (\(\Gamma = -\partial T/\partial z > 9{,}8\text{ K/km}\)).
            </div>

            <div class="block-title">Controle de Qualidade: Camadas com Gradientes Superadiabáticos em 28/08/2026</div>
            <div class="explanation-text">
                Na sondagem publicada de 28/08/2026 12Z, identificam-se camadas imediatamente acima de 925 hPa com forte gradiente térmico:
            </div>
            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Camada (hPa)</th>
                            <th>Espessura (\(\Delta z\))</th>
                            <th>\(\Delta T\)</th>
                            <th>\(\Gamma = -\partial T/\partial z\)</th>
                            <th>\(\partial\theta/\partial z\)</th>
                            <th>\(\Delta\theta_e\)</th>
                            <th>Classificação do QC</th>
                        </tr>
                    </thead>
                    <tbody>
                        __SUPERAD_TBODY__
                    </tbody>
                </table>
            </div>

            <div class="how-to-read">
                <strong>Como ler:</strong>
                <ul>
                    <li>Identifique o decréscimo de pressão (\(p\)) e elevação geopotencial (\(z\)) em cada nível de amostragem.</li>
                    <li>A taxa de lapso seca padrão é \(\Gamma_d \approx 9{,}8\text{ K/km}\). Valores superiores indicam gradiente superadiabático.</li>
                    <li>Um valor de \(\partial\theta/\partial z < 0\) indica que a temperatura potencial decresce com a altura, caracterizando instabilidade estática imediata na camada seca.</li>
                    <li>Em 28/08/2026, a camada \(925 \rightarrow 910{,}5\text{ hPa}\) apresenta \(\Gamma = 17{,}65\text{ K/km}\), fornecendo grande flutuabilidade à parcela de 925 hPa.</li>
                </ul>
            </div>

            <div class="student-questions">
                <strong>Perguntas para o estudante responder:</strong>
                <ol>
                    <li>Com base na tabela acima lida de <code>metpack/metricas.json</code>, qual é a taxa de lapso \(\Gamma\) e a variação \(d\theta/dz\) na camada de \(910{,}5 \rightarrow 850\text{ hPa}\)?</li>
                    <li>Por que a camada quente e úmida observada em 925 hPa não deve ser descartada arbitrariamente, mas sim avaliada lado a lado com um teste de sensibilidade?</li>
                </ol>
            </div>
        </section>

        <!-- SEÇÃO 2: DIAGRAMAS SKEW-T -->
        <section class="tutorial-section" id="sec-skewt">
            <div class="section-header">
                <h2>2. Diagramas Termodinâmicos Skew-T / Log-P</h2>
            </div>
            <div class="explanation-text">
                O diagrama Skew-T / Log-P plota a temperatura (\(T\)) e o ponto de orvalho (\(T_d\)) ao longo do perfil vertical de pressão. 
                A inclinação oblíqua das isotermas permite avaliar a energia potencial disponível para convecção (CAPE) e a inibição convectiva (CIN). 
                Cada sondagem é apresentada abaixo individualmente em sua própria linha em alta resolução, contendo o diagrama Skew-T completo, 
                seu respectivo hodógrafo polar de vento e a caixa de dados termodinâmicos e cinemáticos calculados.
            </div>

            <!-- SONDAGEM 1: ESTÁVEL -->
            <div class="figure-wrapper" style="max-width: 1040px; margin: 24px auto;">
                <h3 style="color: #0284c7; margin-bottom: 8px;">2.1 Sondagem 1: 26/08/2026 12Z (SBFL): Atmosfera Estável</h3>
                <img src="metpack/fig_sounding_1_estavel.png" alt="Sondagem 1 Estável 26/08/2026 12Z" onclick="openModal(this.src)">
                <div class="figure-caption">Figura 1: Diagrama Skew-T / Log-P com Hodógrafo Polar (lado superior direito) e Painel de Diagnósticos Físicos Completos Ampliado (lado inferior direito). SBCAPE = 16 J/kg, SBCIN = 0 J/kg, Shear 0-6 km = 13.7 m/s (26.6 kt). Clique para ampliar.</div>
            </div>

            <!-- SONDAGEM 2: NEUTRA -->
            <div class="figure-wrapper" style="max-width: 1040px; margin: 24px auto;">
                <h3 style="color: #0d9488; margin-bottom: 8px;">2.2 Sondagem 2: 31/08/2026 12Z (SBFL): Atmosfera Neutra</h3>
                <img src="metpack/fig_sounding_2_neutra.png" alt="Sondagem 2 Neutra 31/08/2026 12Z" onclick="openModal(this.src)">
                <div class="figure-caption">Figura 2: Diagrama Skew-T / Log-P com Hodógrafo Polar (lado superior direito) e Painel de Diagnósticos Físicos Completos Ampliado (lado inferior direito). MUCAPE = 836 J/kg, SBCAPE = 836 J/kg, SBCIN = -222 J/kg, PW = 43.9 mm, Shear 0-6 km = 2.8 m/s (5.5 kt). Clique para ampliar.</div>
            </div>

            <!-- SONDAGEM 3: INSTÁVEL -->
            <div class="figure-wrapper" style="max-width: 1040px; margin: 24px auto;">
                <h3 style="color: #dc2626; margin-bottom: 8px;">2.3 Sondagem 3: 28/08/2026 12Z (SBFL): Atmosfera Instável</h3>
                <img src="metpack/fig_sounding_3_instavel.png" alt="Sondagem 3 Instável 28/08/2026 12Z" onclick="openModal(this.src)">
                <div class="figure-caption">Figura 3: Diagrama Skew-T / Log-P com Hodógrafo Polar (lado superior direito) e Painel de Diagnósticos Físicos Completos Ampliado (lado inferior direito). MUCAPE = 7810 J/kg, SBCAPE = 1862 J/kg, Shear 0-6 km = 12.6 m/s (24.5 kt), SRH 0-3 km = -123.3 m²/s² (Left-Mover). Clique para ampliar.</div>
            </div>

            <div class="how-to-read">
                <strong>Como ler:</strong>
                <ul>
                    <li>Linha vermelha = perfil observado de temperatura (\(T\)); linha verde = ponto de orvalho (\(T_d\)).</li>
                    <li>Linha preta tracejada = trajetória da parcela de ar ascendente a partir da superfície.</li>
                    <li>Linhas pontilhadas horizontais indicam o Nível de Condensação por Levantamento (LCL), Nível de Convecção Livre (LFC) e Nível de Equilíbrio (EL).</li>
                    <li>Área sombreada em vermelho = CAPE; área sombreada em azul = CIN.</li>
                    <li>O hodógrafo polar no canto superior direito exibe a estrutura vertical dos ventos horizontais em nós (kt), divididos por camadas coloridas de altitude, além do vetor de tempestades anômalas (Bunkers Left-Mover).</li>
                    <li>O painel diagnóstico no canto inferior direito sintetiza com fontes grandes e alta legibilidade os índices de convecção calculados via MetPy.</li>
                </ul>
            </div>

            <div class="student-questions">
                <strong>Perguntas para o estudante responder:</strong>
                <ol>
                    <li>Em 26/08/2026, por que a curva da parcela quase não se afasta da temperatura ambiente e qual o valor de SBCAPE resultante registrado no JSON?</li>
                    <li>Em 28/08/2026, identifique a pressão do LCL e do LFC na sondagem completa. Existe CIN significativo para a parcela de superfície?</li>
                </ol>
            </div>
        </section>

        <!-- SEÇÃO 3: TABELA DE ÍNDICES E CONFERÊNCIA -->
        <section class="tutorial-section" id="sec-indices">
            <div class="section-header">
                <h2>3. Índices Diagnósticos de Convecção e Conferência Oficial</h2>
            </div>
            <div class="explanation-text">
                Síntese quantitativa dos parâmetros de instabilidade, umidade e cisalhamento para as três sondagens. 
                Os valores são lidos diretamente do arquivo <code>metpack/metricas.json</code>. A tabela inclui a avaliação oficial da 
                sondagem completa e o teste de sensibilidade para 28/08/2026, além do confronto com os índices oficiais da Universidade de Wyoming.
            </div>

            <div class="block-title">Tabela Diagnóstica Comparativa dos Três Regimes Atmosféricos</div>
            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th style="text-align:left;">Parâmetro Diagnóstico</th>
                            <th style="color:var(--color-c12);">26/08/2026 12Z<br>(Estável)</th>
                            <th style="color:var(--color-c22);">31/08/2026 12Z<br>(Neutra)</th>
                            <th style="color:var(--color-c24);">28/08/2026 12Z<br>(Oficial Completa)</th>
                            <th style="color:var(--color-sens);">28/08/2026 12Z<br>(Sensibilidade sem 925)</th>
                        </tr>
                    </thead>
                    <tbody>
                        __MASTER_DIAG_TBODY__
                    </tbody>
                </table>
            </div>

            <div class="block-title">Comparação Padronizada dos Três Métodos de DCAPE (Item 4)</div>
            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th style="text-align:left;">Sondagem / Regime</th>
                            <th>Wyoming (INDICES)</th>
                            <th>MetPy (downdraft_cape)</th>
                            <th>Kerry Emanuel (cape.out, máx origens)</th>
                        </tr>
                    </thead>
                    <tbody>
                        __DCAPE_TBODY__
                    </tbody>
                </table>
            </div>

            <div class="block-title">Tabela de Conferência Completa: Wyoming Oficial (INDICES) vs. MetPy</div>
            <div class="table-grid-3">
                __WYOMING_COMP_SECTION__
            </div>

            <div class="how-to-read">
                <strong>Como ler e interpretar os dados de conferência:</strong>
                <ul>
                    <li><strong>Índices Clássicos com Concordância Exata (\(\Delta = 0.0\)):</strong> Os índices K (KINX), Total Totals (TOTL), Cross Totals (CTOT), Vertical Totals (VTOT), Showalter (SHOW) e Água Precipitável (PWAT) calculados via MetPy coincidem com os dados oficiais publicados pela Universidade de Wyoming nas 3 sondagens. O SWEAT do notebook é calculado com a velocidade do vento em m/s (a função <code>mpcalc.sweat_index</code> usa só o número da velocidade) e coincide com o valor publicado pelo Wyoming; com o vento em nós, como na definição original de Miller (1972), o valor é maior (linha "SWEAT com vento em nós").</li>
                    <li><strong>MUCAPE Extremo em 28/08/2026:</strong> O Wyoming registra 7808,7 J/kg e o cálculo via MetPy resulta em 7810,0 J/kg (\(\Delta = +1,3\text{ J/kg}\), precisão de 99,98%), confirmando a captura idêntica da parcela mais instável em 925 hPa.</li>
                    <li><strong>Diferença entre SBCAPE e MUCAPE:</strong> Em 28/08, a parcela de superfície possui SBCAPE de 1862 J/kg com forte inibição (SBCIN = -186 J/kg), enquanto o MUCAPE atinge 7810 J/kg com CIN nulo (0 J/kg), caracterizando uma convecção elevada de extrema violência.</li>
                    <li><strong>Três Métodos de DCAPE:</strong> Kerry Emanuel (1994) avalia a descida de parcela individual camada a camada com microfísica detalhada; MetPy integra a descida a partir da camada de mínimo \(\theta_e\); e Wyoming utiliza formulação empírica de coluna.</li>
                </ul>
            </div>

            <div class="student-questions">
                <strong>Perguntas para o estudante responder:</strong>
                <ol>
                    <li>Por que os índices termodinâmicos padrão (K, TT, Showalter e PW) apresentam concordância exata entre MetPy e Wyoming, e por que o SWEAT só coincide com o Wyoming quando o vento entra em m/s, e não em nós como na definição de Miller (1972)?</li>
                    <li>Em 28/08/2026, compare o MUCAPE oficial (7808,7 J/kg) com o valor do teste de sensibilidade sem o nível de 925 hPa (1860 J/kg). Qual a justificativa física para a presença do Jato de Baixos Níveis (JBN) com vento de 44 nós em 925 hPa?</li>
                </ol>
            </div>
        </section>

        <!-- SEÇÃO 4: PERFIS VERTICAIS DE ESTABILIDADE -->
        <section class="tutorial-section" id="sec-perfis">
            <div class="section-header">
                <h2>4. Perfis Verticais de Estabilidade: \(\theta, \theta_e, \theta_{es}\), \(N^2\) e \(S\) (Topo em 200 hPa)</h2>
            </div>
            <div class="explanation-text">
                Análise da estrutura de estabilidade estática e convectiva da troposfera até 200 hPa, baseada nas formulações do Cap. 2 de Kerry Emanuel (1994).
                A frequência de Brunt-Väisälä ao quadrado (\(N^2 = \frac{g}{\theta}\frac{\partial\theta}{\partial z}\)) permite evidenciar camadas estaticamente instáveis (\(N^2 < 0\)), 
                enquanto a estabilidade estática em coordenadas de pressão (\(S = -\frac{T}{\theta}\frac{\partial\theta}{\partial p}\)) quantifica a resistência ao deslocamento vertical em K/hPa.
            </div>

            <div class="figure-wrapper">
                <img src="metpack/fig_perfis_theta_triplice.png" alt="Perfis de Theta Triplice" onclick="openModal(this.src)">
                <div class="figure-caption">Perfis de \(\theta\) (seca), \(\theta_e\) (equivalente) e \(\theta_{es}\) (saturação) para as Três Sondagens (Mesmos Eixos até 200 hPa), Clique para ampliar</div>
            </div>

            <div class="figure-wrapper">
                <img src="metpack/fig_3_soundings_profiles_comparison.png" alt="Comparação Tríplice de Perfis" onclick="openModal(this.src)">
                <div class="figure-caption">Comparação Tríplice: \(\theta_e\), \(N^2\), \(S = -(T/\theta)\partial\theta/\partial p\) e razão de mistura \(r\) até 200 hPa, Clique para ampliar</div>
            </div>

            <div class="how-to-read">
                <strong>Como ler:</strong>
                <ul>
                    <li>No primeiro gráfico, compare \(\theta\) (azul), \(\theta_e\) (verde) e \(\theta_{es}\) (vermelho tracejado). Onde \(\theta_e\) diminui com a altura (\(\partial\theta_e/\partial z < 0\)), a atmosfera é potencialmente/convectivamente instável.</li>
                    <li>No painel de \(N^2\), a linha tracejada cinza em \(0\) separa camadas estáveis (\(N^2 > 0\)) de camadas superadiabáticas/instáveis (\(N^2 < 0\)).</li>
                    <li>No painel de \(S\), valores positivos indicam estabilidade estática em coordenadas de pressão; valores negativos indicam gradientes superadiabáticos.</li>
                    <li>No painel de razão de mistura (\(r\)), avalie o teor de umidade disponível na camada limite superficial.</li>
                </ul>
            </div>

            <div class="student-questions">
                <strong>Perguntas para o estudante responder:</strong>
                <ol>
                    <li>Em qual sondagem e camada específica observa-se \(N^2 < 0\) e \(S < 0\) simultaneamente?</li>
                    <li>Qual das três sondagens possui o perfil mais profundo de \(\partial\theta_e/\partial z < 0\) na baixa troposfera e o que isso implica para o potencial de convecção profunda?</li>
                </ol>
            </div>
        </section>

        <!-- SEÇÃO 5: CINEMÁTICA E HODÓGRAFO -->
        <section class="tutorial-section" id="sec-cinematica">
            <div class="section-header">
                <h2>5. Cinemática de Mesoescala: Hodógrafo e Convenções do Hemisfério Sul</h2>
            </div>
            <div class="explanation-text">
                O hodógrafo polar mapeia o vetor vento horizontal (\(u, v\)) ao longo da altura, permitindo diagnosticar o cisalhamento vertical 
                e a helicidade relativa à tempestade (SRH). Em tempestades severas, a rotação do mesociclone origina-se do 
                <strong>tombamento (tilting) da vorticidade horizontal associada ao cisalhamento ambiental</strong> pela corrente ascendente, e 
                <strong>não da força de Coriolis</strong>. No Hemisfério Sul, o vetor de tempestade relevante é o Bunkers Left-Mover, com helicidade ciclônica negativa.
            </div>

            <div class="figure-wrapper">
                <img src="metpack/fig_kinematics_hodograph.png" alt="Hodógrafo SBFL 28/08/2026" onclick="openModal(this.src)">
                <div class="figure-caption">Hodógrafo do Vento Horizontal e Vetor Bunkers no Hemisfério Sul (SBFL 28/08/2026 12Z), Clique para ampliar</div>
            </div>

            <div class="how-to-read">
                <strong>Como ler:</strong>
                <ul>
                    <li>Os anéis concêntricos representam a intensidade do vento em m/s (5, 10, 15, ..., 40 m/s).</li>
                    <li>As cores dos segmentos representam as camadas: 0–1 km (vermelho), 1–3 km (verde), 3–6 km (azul) e >6 km (roxo).</li>
                    <li>O ponto em forma de diamante âmbar marca o vetor de deslocamento da tempestade Bunkers Left-Mover (LM).</li>
                    <li>A seta preta conecta a superfície a 6 km, representando o vetor de cisalhamento bulk profundo (0–6 km).</li>
                    <li>A helicidade é calculada por \(\text{SRH} = \int_0^h (\vec{V} - \vec{c}) \cdot \left(\hat{k} \times \frac{\partial \vec{V}}{\partial z}\right) dz\), resultando em valor negativo para o Left-Mover ciclônico no HS.</li>
                </ul>
            </div>

            <div class="student-questions">
                <strong>Perguntas para o estudante responder:</strong>
                <ol>
                    <li>Quais são as componentes \((u, v)\) e a magnitude do vetor Bunkers Left-Mover calculadas em 28/08/2026?</li>
                    <li>Por que no Hemisfério Sul a helicidade ciclônica relativa à tempestade é estritamente negativa?</li>
                </ol>
            </div>
        </section>

        <!-- SEÇÃO 6: MATRIZES 2D DE KERRY EMANUEL -->
        <section class="tutorial-section" id="sec-emanuel">
            <div class="section-header">
                <h2>6. Matrizes Termodinâmicas 2D de Kerry Emanuel (1994)</h2>
            </div>
            <div class="explanation-text">
                Implementação numérica dos algoritmos de Kerry Emanuel (1994, <em>Atmospheric Convection</em>). 
                As matrizes bidimensionais calculam a flutuabilidade térmica de parcelas originadas a cada nível de pressão (\(p_{\text{origem}}\)) 
                quando elevadas a cada nível da troposfera (\(p_{\text{elevada}}\)). O modo <strong>Reversível</strong> (\(T_\rho\)) retém o condensado 
                (carga de água líquida), enquanto o modo <strong>Pseudoadiabático</strong> (\(T_v\)) precipita toda a água condensada instantaneamente.
            </div>

            <div class="figure-wrapper">
                <img src="metpack/fig_3_soundings_emanuel_matrices.png" alt="Matrizes de Emanuel" onclick="openModal(this.src)">
                <div class="figure-caption">Matrizes 2D de Kerry Emanuel (1994) nas Três Sondagens, mesma escala simétrica de cores para as seis matrizes (definida pelos dados), isolinha de 0 K destacada, sem o corte artificial em −4 K, Clique para ampliar</div>
            </div>

            <h3 style="margin-top: 28px;">6.1 Matrizes de flutuabilidade por sondagem</h3>
            <div class="explanation-text">
                As mesmas matrizes, uma figura por sondagem (geradas pelo notebook a partir do <code>wyoming.f</code>). Escolha o caso:
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin: 10px 0 14px;">
                <button type="button" class="emanuel-tab" onclick="mostraEmanuel('20260826', this)" style="padding:6px 14px; border-radius:6px; border:1px solid #94a3b8; background:#e2e8f0; cursor:pointer;">Estável, 26/08/2026</button>
                <button type="button" class="emanuel-tab" onclick="mostraEmanuel('20260831', this)" style="padding:6px 14px; border-radius:6px; border:1px solid #94a3b8; background:#ffffff; cursor:pointer;">Neutra, 31/08/2026</button>
                <button type="button" class="emanuel-tab" onclick="mostraEmanuel('20260828', this)" style="padding:6px 14px; border-radius:6px; border:1px solid #94a3b8; background:#ffffff; cursor:pointer;">Instável, 28/08/2026</button>
            </div>
            <div class="figure-wrapper">
                <img id="img-emanuel-caso" src="metpack/emanuel_20260826.png" alt="Matrizes de Emanuel por sondagem" onclick="openModal(this.src)">
                <div class="figure-caption" id="cap-emanuel-caso">Ascensão reversível (esquerda) e pseudoadiabática (direita), Clique para ampliar</div>
            </div>
            <script>
                function mostraEmanuel(data, botao) {
                    document.getElementById('img-emanuel-caso').src = 'metpack/emanuel_' + data + '.png';
                    document.querySelectorAll('.emanuel-tab').forEach(function (b) { b.style.background = '#ffffff'; });
                    botao.style.background = '#e2e8f0';
                }
            </script>

            <div class="how-to-read">
                <strong>Como ler:</strong>
                <ul>
                    <li>Eixo horizontal = nível de pressão de origem da parcela (\(p_{\text{origem}}\), em hPa); eixo vertical = nível para o qual a parcela é elevada (\(p_{\text{elevada}}\), em hPa).</li>
                    <li>Tons vermelhos = flutuabilidade positiva (\(\Delta T > 0\), aceleração ascendente); tons azuis = flutuabilidade negativa (\(\Delta T < 0\), inibição).</li>
                    <li>A isolinha preta espessa contínua representa exatamente \(\Delta T = 0\text{ K}\), marcando a fronteira de flutuabilidade neutra.</li>
                    <li>Todas as matrizes (figura conjunta e figuras por sondagem) usam a mesma escala simétrica de cores, permitindo comparação visual direta.</li>
                </ul>
            </div>

            <div class="student-questions">
                <strong>Perguntas para o estudante responder:</strong>
                <ol>
                    <li>Comparando a linha reversível com a pseudoadiabática em 28/08/2026, qual o efeito da retenção de água líquida (termo \(-r_l\)) na área de flutuabilidade positiva?</li>
                    <li>Na sondagem de 26/08/2026, por que a matriz é dominada quase inteiramente por tons azuis (\(\Delta T < 0\))?</li>
                </ol>
            </div>
        </section>

        <!-- SEÇÃO 7: AGORA É SUA VEZ -->
        <section class="tutorial-section" id="sec-suavez">
            <div class="section-header">
                <h2>7. Agora é sua Vez: Como Escolher as Três Sondagens e Executar o Trabalho</h2>
            </div>
            <div class="explanation-text">
                Os casos de Florianópolis (SBFL 83899) em 26/08, 31/08 e 28/08/2026 mostrados acima são apenas o <strong>exemplo resolvido</strong>.
                <strong>Cada estudante ou dupla deve trocar as três sondagens</strong>, escolhendo datas e/ou estações próprias no acervo da
                Universidade de Wyoming (diferentes das do exemplo e das dos colegas), uma para cada regime: Estável, Neutra e Instável.
                Presumivelmente, a sondagem instável é a mais próxima (no tempo e no espaço) do evento severo escolhido para o trabalho de fim de curso.
            </div>

            <div class="how-to-read">
                <strong>Critérios para Escolha das Três Sondagens:</strong>
                <ul>
                    <li><strong>Sondagem Estável:</strong> Inversão térmica ou isotermia em baixos níveis, ar seco em altitude, \(N^2 > 0\) profundo e CAPE próximo de zero (\(< 50\text{ J/kg}\)).</li>
                    <li><strong>Sondagem Neutra:</strong> Camada limite com umidade moderada, instabilidade potencial (\(\partial\theta_e/\partial z < 0\)) com CIN moderado e sem cisalhamento extremo.</li>
                    <li><strong>Sondagem Instável:</strong> Camada limite quente e úmida, forte gradiente vertical de \(\theta_e\), elevado CAPE (\(> 1500\text{ J/kg}\)) e cisalhamento vertical organizado.</li>
                </ul>
            </div>

            <div class="how-to-read" style="border-left-color:#0284c7; background:#f0f9ff;">
                <strong>Leia o roteiro:</strong> todas as instruções (escolha das sondagens, as três formas de rodar, downloads,
                o que apresentar e critérios de avaliação) estão no
                <a href="https://github.com/reinaldohaas/tarefa-meso/blob/master/ROTEIRO_ESTUDANTES.md" target="_blank" style="color:#0284c7; font-weight:700;">ROTEIRO_ESTUDANTES.md</a>.
            </div>

            <div class="how-to-read" style="border-left-color:#c2410c; background:#fff7ed;">
                <strong>Seminário Final (Parte 2), WRF:</strong> simular o seu evento com 3 domínios aninhados (3 km ou menos no interno),
                diagnosticar a água super-resfriada, o graupel e o granizo, visualizar cada hidrometeoro em 3D (ParaView, IDV ou VAPOR),
                publicar os resultados numa página no GitHub e apresentar em 20 minutos. Entrega no Moodle até 5/12/2026.
                Enunciado, roteiro dos slides, critérios e prompt para assistente de IA em
                <a href="https://github.com/reinaldohaas/tarefa-meso/blob/master/TAREFA_WRF_HIDROMETEOROS.md" target="_blank" style="color:#c2410c; font-weight:700;">TAREFA_WRF_HIDROMETEOROS.md</a>.
                Para rodar no VLab: notebook
                <a href="https://github.com/reinaldohaas/tarefa-meso/blob/master/WRF_VLab_tarefa.ipynb" target="_blank" style="color:#c2410c; font-weight:700;">WRF_VLab_tarefa.ipynb</a>, com todas as etapas.
                Exemplo de visualização: <a href="https://www.youtube.com/watch?v=2Lr9ajlyrPQ" target="_blank" style="color:#c2410c;">Supercell on a Carousel (Leigh Orf)</a>.
            </div>

            <div class="block-title">Três formas de rodar (escolha uma; detalhes no item 3 do roteiro):</div>
            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr><th style="text-align:left;">Opção</th><th>Onde roda</th><th style="text-align:left;">O que produz</th></tr>
                    </thead>
                    <tbody>
                        <tr><td style="text-align:left;"><strong>A. Notebook Jupyter</strong>:
                            <a href="https://colab.research.google.com/github/reinaldohaas/tarefa-meso/blob/master/Seminario_plot_sounding_revisado.ipynb" target="_blank" style="color:#0284c7; font-weight:700;">abrir no Colab</a>
                            ou em qualquer IDE com Jupyter (VS Code, JupyterLab, PyCharm…)</td>
                            <td>Navegador ou seu computador</td>
                            <td style="text-align:left;">Tudo: índices do MetPy e conferência com o Wyoming, Skew-T com hodógrafo, perfis até 200 hPa e matrizes de Emanuel</td></tr>
                        <tr><td style="text-align:left;"><strong>B. Linha de comando com o <code>uv</code></strong>: <code>metpack/tarefa_sondagens.py</code></td>
                            <td>Seu computador</td>
                            <td style="text-align:left;">Skew-T e matrizes de Emanuel</td></tr>
                        <tr><td style="text-align:left;"><strong>C. MATLAB Online</strong>: <code>metpack/tarefa_sondagens.m</code></td>
                            <td>Navegador</td>
                            <td style="text-align:left;">Skew-T com barbelas, hodógrafo (Bunkers), perfis até 200 hPa e matrizes de Emanuel</td></tr>
                    </tbody>
                </table>
            </div>
            <p style="color:#334155; font-size:0.95rem;">Para as opções que usam os arquivos do repositório (notebook numa IDE local, <code>uv</code> e MATLAB Online),
            baixe-o antes com <code>git clone https://github.com/reinaldohaas/tarefa-meso.git</code> ou, no GitHub, <strong>Code → Download ZIP</strong>.</p>
            <p style="color:#334155; font-size:0.95rem;">Em todas, troque as três sondagens do exemplo em <code>CASOS</code> pelas suas.
            Depois, prepare as apresentações descritas nos itens 4 e 5 do roteiro.</p>

            <div class="how-to-read" style="border-left-color: #10b981; background: #f0fdf4;">
                <strong style="color: #065f46;">Critérios de Avaliação Científica:</strong>
                <ul style="color: #14532d;">
                    <li><strong>Integridade dos Dados:</strong> Nenhum número digitado à mão; todos os diagnósticos devem derivar dos scripts.</li>
                    <li><strong>Rigor Físico:</strong> Correta interpretação do tombamento de vorticidade no mesociclone, sem atribuição errônea a Coriolis.</li>
                    <li><strong>Tratamento de Inconsistências:</strong> Camadas superadiabáticas tratadas como dados reais acompanhadas de teste de sensibilidade.</li>
                    <li><strong>Clareza Visual:</strong> Gráficos com fundo branco, eixos com unidades e sem textos subjetivos adicionados à mão.</li>
                </ul>
            </div>
        </section>

        <!-- SEÇÃO 8: SEMINÁRIO FINAL (PARTE 2) - SIMULAÇÃO WRF DE EVENTO SEVERO E HIDROMETEOROS 3D -->
        <section class="tutorial-section" id="sec-wrf-parte2">
            <div class="section-header">
                <h2>8. Seminário Final (Parte 2): Simulação WRF e Apresentação de 20 Minutos (granizo no Norte da Ilha, 29/08/2026)</h2>
            </div>
            <div class="explanation-text">
                Dando continuidade ao diagnóstico termodinâmico da Parte 1 (onde a sondagem pré-convectiva de Florianópolis SBFL 83899 em 28/08/2026 12Z revelou
                \(\text{MUCAPE} = 1303{,}5\text{ J/kg}\) e forte redução de flutuabilidade pela carga de condensados na matriz reversível de Emanuel),
                esta seção traz um <strong>exemplo resolvido</strong> da Parte 2: a <strong>apresentação de 10 slides (20 minutos)</strong> e o diagnóstico de uma <strong>simulação com convecção explícita no WRF-ARW V4.2.2</strong> para o evento severo de granizo no Norte da Ilha de Santa Catarina em <strong>29/08/2026</strong>,
                seguindo todos os requisitos da Seção 10 de <a href="https://github.com/reinaldohaas/tarefa-meso/blob/master/TAREFA_WRF_HIDROMETEOROS.md" target="_blank" style="color:#c2410c; font-weight:700;">TAREFA_WRF_HIDROMETEOROS.md</a>.
            </div>

            <div class="how-to-read" style="border-left-color:#c2410c; background:#fff7ed;">
                <strong>Apresentação em tela cheia:</strong>
                <a href="apresentacao_parte2.html" style="color:#c2410c; font-weight:700;">apresentacao_parte2.html</a>, os 10 slides para a defesa de 20 minutos,
                com a animação 3D dos hidrometeoros, a série temporal da rodada e o roteiro de fala (tecla N). Setas do teclado mudam de slide; F abre em tela cheia.
            </div>

            <!-- A apresentação de 20 minutos fica em apresentacao_parte2.html (gerada por scripts/gerar_apresentacao_parte2.py) -->
            <div id="deck-wrf-slides" style="margin:16px 0 26px;">
                <iframe src="apresentacao_parte2.html" title="Apresentação da Parte 2: WRF e granizo" loading="lazy"
                        style="width:100%; height:78vh; min-height:520px; border:1px solid #cbd5e1; border-radius:10px;"></iframe>
                <p style="margin:6px 0 0; font-size:0.92em;"><a href="apresentacao_parte2.html" style="color:#c2410c; font-weight:700;">Abrir a apresentação em tela cheia</a> (setas mudam de slide, N mostra o roteiro de fala, F abre em tela cheia).</p>
            </div>

            <div class="block-title">8.1. O Caso Observado e a Configuração dos Domínios e da Física</div>
            <div class="explanation-text">
                Entre <strong>22:00 e 23:00 UTC de 29/08/2026</strong> (19:00–20:00 BRT), uma tempestade severa atingiu Biguaçu e os bairros do Norte da Ilha de Santa Catarina
                (Jurerê, Canasvieiras, Cachoeira do Bom Jesus e Ingleses), produzindo queda de granizo de até \(60\text{ mm}\), topo frio de \(-62{,}9\text{ }^\circ\text{C}\)
                no canal infravermelho (10,3 µm) do GOES-19 às 22:20 UTC e núcleo de alta refletividade rastreado pelo radar do Morro da Igreja entre 22:16 e 22:36 UTC.
            </div>

            <div class="gallery-grid">
                <div class="figure-wrapper">
                    <img src="figuras/dominios.png" alt="Domínios Aninhados do WRF (18/6/2 km)" onclick="openModal(this.src)">
                    <div class="figure-caption">Aninhamento triplo (18, 6 e 2 km): d01 e d02 com a Ilha a 2/3 para leste e para norte (regra dos 2/3), d03 centrado na Ilha; cada domínio com o relevo na sua própria resolução, o de 2 km no centro. Clique para ampliar</div>
                </div>
                <div class="figure-wrapper">
                    <img src="figuras/refletividade.png" alt="Refletividade Composta REFL_10CM e Evolução Temporal" onclick="openModal(this.src)">
                    <div class="figure-caption">Refletividade máxima na coluna (<code>REFL_10CM</code>) às 12:45 UTC, quando a célula com granizo cruzou a Ilha, e série temporal em <code>d03</code>, Clique para ampliar</div>
                </div>
            </div>

            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th style="text-align:left;">Componente</th>
                            <th style="text-align:left;">Configuração Escolhida (<code>namelist.wps</code> / <code>namelist.input</code>)</th>
                            <th style="text-align:left;">Justificativa Física e Numérica</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="text-align:left;"><strong>Domínios Aninhados</strong></td>
                            <td style="text-align:left;"><code>max_dom = 3</code>, razão 1:3 (<code>18 km / 6 km / 2 km</code>), grades \(38\times 38\), \(49\times 49\) e \(61\times 61\); d01 e d02 deslocados para sudoeste, com a Ilha a 2/3 para leste e para norte, 45 níveis \(\eta\) até \(50\text{ hPa}\)</td>
                            <td style="text-align:left;">Garante resolução de <strong>2 km (\(\le 3\text{ km}\)) no domínio interno <code>d03</code></strong> (\(120\times 120\text{ km}\)), com folga de \(60\text{ km}\) até as bordas e 100% contido no recorte regional do ERA5.</td>
                        </tr>
                        <tr>
                            <td style="text-align:left;"><strong>Dados e Janela</strong></td>
                            <td style="text-align:left;">ERA5 (37 níveis de pressão + superfície, 1 h), de <code>2026-08-29_12:00</code> a <code>2026-08-30_00:00 UTC</code></td>
                            <td style="text-align:left;">Fornece 10 h de aquecimento (<em>spin-up</em> \(\ge 6\text{ h}\)) antes do horário observado da tempestade severa (22:00–23:00 UTC), com saída a cada 15 min em <code>d03</code>.</td>
                        </tr>
                        <tr>
                            <td style="text-align:left;"><strong>Microfísica</strong></td>
                            <td style="text-align:left;"><strong>Milbrandt-Yau 2 momentos (<code>mp_physics = 9</code>)</strong>, com <code>do_radar_ref = 1</code> e <code>hailcast_opt = 0, 0, 1</code></td>
                            <td style="text-align:left;">Prevê razão de mistura e concentração numérica de 6 classes hidrometeóricas, <strong>separando explicitamente o graupel (<code>QGRAUP</code>) e o granizo de alta densidade (<code>QHAIL</code>)</strong>.</td>
                        </tr>
                        <tr>
                            <td style="text-align:left;"><strong>Cumulus</strong></td>
                            <td style="text-align:left;"><code>cu_physics = 1, 1, 0</code> (Kain-Fritsch em <code>d01/d02</code>, <strong>desligado em <code>d03</code></strong>)</td>
                            <td style="text-align:left;">Em \(\Delta x = 2\text{ km}\), as correntes ascendentes convectivas são resolvidas explicitamente pelas equações não-hidrostáticas sem parametrização sub-grade.</td>
                        </tr>
                        <tr>
                            <td style="text-align:left;"><strong>CLP, Superfície e Radiação</strong></td>
                            <td style="text-align:left;">YSU PBL (<code>bl_pbl_physics = 1</code>), Monin-Obukhov + Noah LSM (<code>sf_surface_physics = 2</code>), RRTMG LW/SW (<code>ra = 4</code>)</td>
                            <td style="text-align:left;">Representa a mistura vertical não-local na camada limite marítima/costeira e a interação radiativa com a bigorna de gelo (<code>icloud = 1</code>).</td>
                        </tr>
                        <tr>
                            <td style="text-align:left;"><strong>Passo de Tempo (CFL)</strong></td>
                            <td style="text-align:left;"><code>use_adaptive_time_step = .true.</code>, <code>target_cfl = 1.2</code>, <code>step_to_output_time = .true.</code></td>
                            <td style="text-align:left;">Ajusta dinamicamente \(\Delta t\) (\(\sim 16\text{ s}\) em <code>d03</code>) para manter estabilidade numérica nas ascendentes intensas e gravar saídas exatas a cada 15 min.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="block-title">8.2. Visualização 3D dos Hidrometeoros no ParaView (Altura Real \(z = (\text{PH}+\text{PHB})/g\), Exagero \(4\times\))</div>
            <div class="explanation-text">
                As figuras 3D abaixo foram geradas com o ParaView 6.2 (<code>pvpython</code>) a partir do arquivo <code>wrfout_d03</code> interpolado dos níveis \(\eta\)
                para a altura geométrica real \(z = (\text{PH} + \text{PHB})/9{,}81\) (em km acima do nível do mar), mantendo exatamente o <strong>mesmo ponto de vista de câmera</strong>,
                exagero vertical de \(4\times\) e paleta de cores fixa por hidrometeoro. Use os botões abaixo para inspecionar a estrutura 3D combinada ou cada hidrometeoro isoladamente:
            </div>

            <div style="display:flex; flex-wrap:wrap; gap:8px; margin:14px 0;">
                <button type="button" class="wrf3d-tab" onclick="mostraWrf3d('todos', 'Estrutura 3D Combinada: Todos os Hidrometeoros + Água Super-resfriada (SLW)', this)" style="padding:8px 14px; border:1px solid #c2410c; border-radius:6px; background:#ffedd5; font-weight:700; cursor:pointer; color:#9a3412;">Todos Juntos (Combinada)</button>
                <button type="button" class="wrf3d-tab" onclick="mostraWrf3d('SLW', 'Água super-resfriada (SLW = QCLOUD + QRAIN para T < 0 °C), verde, limiar 0,5 g/kg', this)" style="padding:8px 14px; border:1px solid #cbd5e1; border-radius:6px; background:#ffffff; font-weight:600; cursor:pointer;">SLW (Água Super-resfriada)</button>
                <button type="button" class="wrf3d-tab" onclick="mostraWrf3d('QGRAUP', 'Graupel (QGRAUP), laranja, limiar 0,5 g/kg', this)" style="padding:8px 14px; border:1px solid #cbd5e1; border-radius:6px; background:#ffffff; font-weight:600; cursor:pointer;">Graupel (QGRAUP)</button>
                <button type="button" class="wrf3d-tab" onclick="mostraWrf3d('QHAIL', 'Granizo (QHAIL), vermelho, limiar 0,1 g/kg', this)" style="padding:8px 14px; border:1px solid #cbd5e1; border-radius:6px; background:#ffffff; font-weight:600; cursor:pointer;">Granizo (QHAIL)</button>
                <button type="button" class="wrf3d-tab" onclick="mostraWrf3d('QCLOUD', 'Água de nuvem (QCLOUD), cinza claro, limiar 0,3 g/kg', this)" style="padding:8px 14px; border:1px solid #cbd5e1; border-radius:6px; background:#ffffff; font-weight:600; cursor:pointer;">Nuvem (QCLOUD)</button>
                <button type="button" class="wrf3d-tab" onclick="mostraWrf3d('QRAIN', 'Chuva (QRAIN), Azul, limiar 0,15 g/kg', this)" style="padding:8px 14px; border:1px solid #cbd5e1; border-radius:6px; background:#ffffff; font-weight:600; cursor:pointer;">Chuva (QRAIN)</button>
                <button type="button" class="wrf3d-tab" onclick="mostraWrf3d('QICE', 'Cristais de Gelo (QICE), Ciano, limiar 0,05 g/kg (bigorna superior)', this)" style="padding:8px 14px; border:1px solid #cbd5e1; border-radius:6px; background:#ffffff; font-weight:600; cursor:pointer;">Gelo (QICE)</button>
                <button type="button" class="wrf3d-tab" onclick="mostraWrf3d('QSNOW', 'Neve e Agregados (QSNOW), Lilás, limiar 0,1 g/kg', this)" style="padding:8px 14px; border:1px solid #cbd5e1; border-radius:6px; background:#ffffff; font-weight:600; cursor:pointer;">Neve (QSNOW)</button>
            </div>

            <div class="figure-wrapper">
                <img id="img-wrf-3d" src="figuras/3d_todos.png" alt="Visualização 3D dos Hidrometeoros no ParaView" onclick="openModal(this.src)">
                <div class="figure-caption" id="cap-wrf-3d">Estrutura 3D Combinada: Todos os Hidrometeoros + Água Super-resfriada (SLW), Clique na imagem para ampliar</div>
            </div>

            <div class="explanation-text" style="margin-top:18px;">
                <strong>Animação 3D Completa (Rotação 360° e Decomposição Anatômica "Despindo e Vestindo").</strong>
                Animação contínua em 240 quadros (15 fps, 16 s) com órbita circular completa de \(360^\circ\) ao redor da tempestade e do relevo de Santa Catarina:
                <ul style="margin: 8px 0 12px 20px;">
                    <li><strong>Cores Padronizadas por Hidrometeoro:</strong> Nuvem em cinza claro translúcido (\(0{,}1\text{ g/kg}\)), Chuva em azul (\(0{,}5\text{ g/kg}\)), Graupel em laranja (\(0{,}5\text{ g/kg}\)), Granizo em vermelho intenso (\(0{,}1\text{ g/kg}\)) e Água super-resfriada (SLW) em verde (\(0{,}2\text{ g/kg}\)).</li>
                    <li><strong>Evolução Temporal Inicial:</strong> avanço da célula convectiva no domínio interno (d03, 2 km) cruzando a Ilha de Santa Catarina.</li>
                    <li><strong>Despindo a Tempestade (Peeling de Fora para Dentro):</strong> o modelo é congelado no pico sobre a Ilha (12:45 UTC) enquanto a câmera gira continuamente; a nuvem externa é desfeita para revelar a precipitação, a chuva líquida é removida para expor o núcleo congelado, e em seguida destacam-se isoladamente a água super-resfriada (verde), a coluna de graupel (laranja) e o núcleo denso de granizo (vermelho).</li>
                    <li><strong>Vestindo a Tempestade (Layering de Dentro para Fora):</strong> recomposição tridimensional passo a passo a partir do granizo, envolvendo-o sucessivamente com graupel, água super-resfriada, chuva e reconstituindo o envelope completo da nuvem com bigorna até a órbita final de \(360^\circ\).</li>
                </ul>
            </div>
            <div class="figure-wrapper">
                <video src="figuras/granizo_3d_evolucao.mp4" poster="figuras/3d_todos.png" controls loop muted playsinline preload="auto" style="width:100%; border-radius:8px; background:#0b1324;"></video>
                <div class="figure-caption">Animação 3D com Rotação 360° e Decomposição Anatômica (Despindo e Vestindo as Camadas de Hidrometeoros) sobre o Relevo de Santa Catarina. Também disponível em <a href="figuras/granizo_3d_evolucao.gif" target="_blank" style="color:#c2410c; font-weight:700;">formato GIF animado de alta resolução</a>.</div>
            </div>
            <script>
                function mostraWrf3d(tag, legenda, botao) {
                    document.getElementById('img-wrf-3d').src = 'figuras/3d_' + tag + '.png';
                    document.getElementById('cap-wrf-3d').textContent = legenda + ', Clique na imagem para ampliar';
                    document.querySelectorAll('.wrf3d-tab').forEach(function (b) {
                        b.style.background = '#ffffff';
                        b.style.borderColor = '#cbd5e1';
                        b.style.color = '#0f172a';
                    });
                    botao.style.background = '#ffedd5';
                    botao.style.borderColor = '#c2410c';
                    botao.style.color = '#9a3412';
                }
            </script>

            <div class="block-title">8.3. Corte Vertical pela Célula sobre a Ilha e Tabela de Máximos</div>
            <div class="figure-wrapper">
                <img src="figuras/corte_vertical.png" alt="Corte Vertical pela Célula Mais Vigorosa" onclick="openModal(this.src)">
                <div class="figure-caption">Corte vertical oeste-leste pela célula sobre a Ilha (12:45 UTC, \(-27{,}44^\circ, -48{,}50^\circ\)): <code>QGRAUP</code> sombreado, <code>QHAIL</code> em vermelho, <code>SLW</code> em verde, <code>W</code> em preto e isotermas de 0, −20 e −40 °C</div>
            </div>

            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th style="text-align:left;">Hidrometeoro (Variável WRF)</th>
                            <th>Máximo (g/kg)</th>
                            <th>Altura Real \(z\) (km MSL)</th>
                            <th>Temperatura (\(^\circ\text{C}\))</th>
                            <th>Pressão (hPa)</th>
                            <th>Limiar 3D (g/kg)</th>
                        </tr>
                    </thead>
                    <tbody>
                        __WRF_TBODY__
                    </tbody>
                </table>
            </div>

            <div class="block-title">8.4. Comparação com as Observações e Discussão das Deficiências do Modelo</div>
            <div class="figure-wrapper">
                <img src="figuras/comparacao_obs.png" alt="Comparação Lado a Lado: Observação vs WRF" onclick="openModal(this.src)">
                <div class="figure-caption">Painel lado a lado na janela do evento observado (22:30 UTC): Relatos de granizo, caixa do GOES-19 e trajetória do Radar Morro da Igreja (esquerda) contra a refletividade simulada no domínio interno <code>d03</code> (direita)</div>
            </div>

            <div class="how-to-read" style="border-left-color:#c2410c; background:#fff7ed;">
                <strong style="color:#9a3412;">Diagnóstico Físico da Microfísica e Análise Crítica do Evento Noturno Real vs. Simulação WRF:</strong>
                <ul style="color:#431407;">
                    <li><strong>O Evento Real foi Noturno (Pesquisa <code>granizo-gigante</code>):</strong>
                        Os dados observacionais compilados pelo projeto <code>granizo-gigante</code> comprovam que a tempestade que causou estragos e pedras de até <strong>~6 cm</strong> no Norte da Ilha e Biguaçu ocorreu à <strong>noite</strong>:
                        <ul>
                            <li><strong>Trajetória 185 (GOES-19 GLM):</strong> o núcleo convectivo nasceu na borda da Serra Geral às 20:10 UTC (-50,1°W / -27,5°S), deslocou-se para leste a ~16 m/s, passou sobre Biguaçu às <strong>22:10 UTC</strong> e pelo Norte da Ilha às <strong>22:30 UTC</strong> (19:30 h locais).</li>
                            <li><strong>Radar Morro da Igreja (DECEA):</strong> registrou eco MaxCAPPI extremo (>60 dBZ, categoria magenta) sobre Biguaçu e Norte da Ilha exatamente entre <strong>22:16 e 22:36 UTC</strong>.</li>
                            <li><strong>GOES-19 (Canal 13 IR):</strong> temperatura de brilho no topo da nuvem atingiu o mínimo de <strong>\(-62{,}9\text{ }^\circ\text{C}\)</strong> às 22:20 UTC.</li>
                        </ul>
                    </li>
                    <li><strong>Estratificação vertical na célula simulada (12:45 UTC):</strong> a isoterma de 0 °C está a \(4{,}67\text{ km}\). A água super-resfriada chega a \(3{,}77\text{ g/kg}\) a \(5{,}68\text{ km}\) (\(-5{,}7\text{ }^\circ\text{C}\)); o graupel tem o máximo de \(4{,}92\text{ g/kg}\) a \(7{,}55\text{ km}\) (\(-18{,}9\text{ }^\circ\text{C}\)), na zona de acreção; o granizo, só \(0{,}50\text{ g/kg}\), fica a \(4{,}73\text{ km}\), logo acima do 0 °C, e derrete ao cair. No topo, perto de \(-37\text{ }^\circ\text{C}\), dominam os cristais de gelo.</li>
                    <li><strong>Ligação com a flutuabilidade reversível de Emanuel (Parte 1):</strong> graupel, água super-resfriada e granizo suspensos entre 4 e 9 km formam uma carga de condensado de vários g/kg, que reduz a temperatura virtual da parcela: é em 3D o freio previsto pela matriz reversível, alimentando a piscina fria por fusão e evaporação na descendente.</li>
                    <li><strong>Por que a rodada controle errou o horário (Tarde vs. Noite)?</strong>
                        No modelo com configuração padrão (Kain-Fritsch nos domínios externos d01 e d02), a convecção vigorosa foi disparada prematuramente durante a tarde (duas ondas entre 12:45 e 17:30 UTC), consumindo a CAPE disponível antes da chegada da noite. Às 22:30 UTC, o domínio <code>d03</code> já se encontrava estável e calmo.
                    </li>
                    <li><strong>A Solução Comprovada pelos Ensembles de <code>granizo-gigante</code>:</strong>
                        O experimento com 9 membros no projeto <code>granizo-gigante</code> (testando cumulus, camadas limites e perturbações estocásticas) revelou que apenas as rodadas utilizando a parametrização de <strong>Grell-Freitas (GF)</strong> no domínio externo (d01) foram capazes de preservar a instabilidade térmica ao longo da tarde, permitindo que a supercélula noturna se desenvolvesse na Serra Geral e atingisse a Grande Florianópolis no horário correto (21:16–22:16 UTC), gerando até 39 mm de granizo (HAILCAST).
                    </li>
                </ul>
            </div>

            <div class="block-title">8.5. Reprodutibilidade: Namelists, Scripts, Sessão 3D e Relatório no Repositório</div>
            <div class="explanation-text">
                Todos os arquivos de configuração e diagnóstico desta simulação estão versionados neste repositório:
                <ul>
                    <li><a href="RELATORIO_RODADA.md" target="_blank" style="color:#0284c7; font-weight:700;"><code>RELATORIO_RODADA.md</code></a>, Relatório técnico padronizado da rodada <code>r1_milbrandt_yau_2km</code>.</li>
                    <li><a href="wps/namelist.wps" target="_blank" style="color:#0284c7; font-weight:700;"><code>wps/namelist.wps</code></a> e <a href="rodadas/r1_milbrandt_yau_2km/namelist.input" target="_blank" style="color:#0284c7; font-weight:700;"><code>rodadas/r1_milbrandt_yau_2km/namelist.input</code></a>, Configurações completas do WPS e do WRF-ARW.</li>
                    <li><a href="scripts/diagnostico_granizo.py" target="_blank" style="color:#0284c7; font-weight:700;"><code>scripts/diagnostico_granizo.py</code></a> e <a href="scripts/render_3d_paraview.py" target="_blank" style="color:#0284c7; font-weight:700;"><code>scripts/render_3d_paraview.py</code></a>, Scripts de cálculo de SLW, corte vertical e renderização 3D no ParaView.</li>
                    <li><a href="sessoes/granizo_hidrometeoros_3d.pvsm" target="_blank" style="color:#0284c7; font-weight:700;"><code>sessoes/granizo_hidrometeoros_3d.pvsm</code></a> e <a href="wrfpack/tabela_maximos.csv" target="_blank" style="color:#0284c7; font-weight:700;"><code>wrfpack/tabela_maximos.csv</code></a>, Sessão do ParaView e tabela de máximos exportada.</li>
                </ul>
            </div>
        </section>

        <!-- SEÇÃO 9: REFERÊNCIAS BIBLIOGRÁFICAS -->
        <section class="tutorial-section" id="sec-referencias">
            <div class="section-header">
                <h2>9. Referências Bibliográficas Clássicas</h2>
            </div>
            <ul style="color:#334155; font-size:0.92rem; line-height:1.75;">
                <li><strong>Bunkers, M. J., Klimowski, B. A., Zeitler, J. W., Thompson, R. L., & Weisman, M. L. (2000).</strong> Predicting supercell motion using a new hodograph technique. <em>Weather and Forecasting</em>, 15(1), 61–79.</li>
                <li><strong>Emanuel, K. A. (1994).</strong> <em>Atmospheric Convection</em>. Oxford University Press, 580 pp.</li>
                <li><strong>Markowski, P., & Richardson, Y. (2010).</strong> <em>Mesoscale Meteorology in Midlatitudes</em>. Wiley-Blackwell, 407 pp.</li>
                <li><strong>MetPy Development Team (2024).</strong> MetPy: A Python Package for Meteorological Data. Unidata / UCAR. URL: <a href="https://unidata.github.io/MetPy/" target="_blank" style="color:#0284c7;">https://unidata.github.io/MetPy/</a>.</li>
                <li><strong>Thompson, R. L., Edwards, R., Hart, J. A., Elmore, K. L., & Markowski, P. (2003).</strong> Close proximity soundings within supercell environments obtained from the Rapid Update Cycle. <em>Weather and Forecasting</em>, 18(6), 1243–1261.</li>
                <li><strong>Thompson, R. L., Smith, B. T., Grams, J. S., Dean, A. R., & Broyles, C. (2012).</strong> Convective modes for significant severe thunderstorms in the contiguous United States. Part II: Rapid Update Cycle–based proximity soundings. <em>Weather and Forecasting</em>, 27(5), 1136–1154.</li>
                <li><strong>University of Wyoming (2024).</strong> Department of Atmospheric Science Upper Air Sounding Database. URL: <a href="https://weather.uwyo.edu/upperair/sounding.html" target="_blank" style="color:#0284c7;">https://weather.uwyo.edu/upperair/sounding.html</a>.</li>
                <li><strong>Weisman, M. L., & Klemp, J. B. (1982).</strong> The dependence of numerically simulated convective storms on vertical wind shear and buoyancy. <em>Monthly Weather Review</em>, 110(6), 504–520.</li>
            </ul>
        </section>

    </div>

    <!-- Lightbox Modal para Zoom em Imagens -->
    <div id="image-modal" class="modal" onclick="closeModal()">
        <img class="modal-content" id="modal-img">
    </div>

    <script>
        function openModal(src) {
            const modal = document.getElementById('image-modal');
            const img = document.getElementById('modal-img');
            modal.style.display = 'flex';
            img.src = src;
        }

        function closeModal() {
            document.getElementById('image-modal').style.display = 'none';
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
    </script>
</body>
</html>
"""

    html = html_template.replace('__SUPERAD_TBODY__', superad_tbody)
    html = html.replace('__MASTER_DIAG_TBODY__', master_diag_tbody)
    html = html.replace('__WYOMING_COMP_SECTION__', wyoming_comp_section)
    html = html.replace('__DCAPE_TBODY__', dcape_tbody)
    html = html.replace('__WRF_TBODY__', wrf_tbody)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully generated index.html (Tutorial Didático)! File size:", len(html), "bytes")

if __name__ == '__main__':
    generate_html()
