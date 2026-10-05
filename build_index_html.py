import json
import os

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laboratório de Meteorologia de Mesoescala (FSC7116 - UFSC)</title>
    <!-- KaTeX para renderização de fórmulas matemáticas -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body);"></script>
    <style>
        :root {
            --bg-primary: #0a0f1d;
            --bg-secondary: #131c31;
            --bg-card: #1e293b;
            --accent-blue: #38bdf8;
            --accent-green: #4ade80;
            --accent-red: #f87171;
            --accent-yellow: #fbbf24;
            --accent-purple: #c084fc;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --border-color: #334155;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.5;
            padding: 16px;
        }

        header {
            background-color: var(--bg-secondary);
            border-bottom: 2px solid var(--accent-blue);
            padding: 18px 24px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }

        .title-container h1 {
            font-size: 1.5rem;
            color: var(--accent-blue);
            font-weight: 700;
        }

        .title-container p {
            font-size: 0.88rem;
            color: var(--text-secondary);
        }

        .case-selector {
            display: flex;
            align-items: center;
            gap: 12px;
            background: var(--bg-card);
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        select {
            background: var(--bg-primary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.92rem;
            outline: none;
            cursor: pointer;
        }

        .nav-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 18px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
            flex-wrap: wrap;
        }

        .tab-btn {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
            padding: 9px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .tab-btn.active, .tab-btn:hover {
            background: var(--accent-blue);
            color: #0a0f1d;
            border-color: var(--accent-blue);
        }

        .grid-dashboard {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 18px;
            margin-bottom: 20px;
        }

        .card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);
        }

        .col-12 { grid-column: span 12; }
        .col-8 { grid-column: span 8; }
        .col-6 { grid-column: span 6; }
        .col-4 { grid-column: span 4; }

        @media (max-width: 1024px) {
            .col-8, .col-6, .col-4 { grid-column: span 12; }
        }

        .card-title {
            font-size: 1.05rem;
            color: var(--accent-blue);
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 12px;
        }

        .metric-box {
            background: var(--bg-card);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid var(--accent-blue);
        }

        .metric-box.danger { border-left-color: var(--accent-red); }
        .metric-box.warning { border-left-color: var(--accent-yellow); }
        .metric-box.success { border-left-color: var(--accent-green); }
        .metric-box.purple { border-left-color: var(--accent-purple); }

        .metric-val {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .metric-lbl {
            font-size: 0.72rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        canvas {
            display: block;
            width: 100%;
            border-radius: 8px;
            background: #080c16;
        }

        .btn-group {
            display: flex;
            gap: 6px;
        }

        .btn-sm {
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 4px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.8rem;
        }

        .btn-sm.active, .btn-sm:hover {
            background: var(--accent-blue);
            color: #0a0f1d;
            font-weight: 600;
        }

        .status-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .badge-stable { background: #0284c7; color: #ffffff; }
        .badge-mod { background: #eab308; color: #000000; }
        .badge-extreme { background: #dc2626; color: #ffffff; }
        .badge-neutral { background: #475569; color: #ffffff; }

        .table-container {
            overflow-x: auto;
            max-height: 480px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            text-align: right;
        }

        th, td {
            padding: 8px 12px;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            background-color: var(--bg-card);
            color: var(--accent-blue);
            position: sticky;
            top: 0;
            z-index: 2;
            font-weight: 600;
        }

        tr:nth-child(even) {
            background-color: rgba(255, 255, 255, 0.02);
        }

        tr:hover {
            background-color: rgba(56, 189, 248, 0.08);
        }

        .theory-box {
            background: var(--bg-card);
            border-left: 4px solid var(--accent-yellow);
            padding: 12px 16px;
            border-radius: 0 8px 8px 0;
            font-size: 0.88rem;
            margin-top: 10px;
            color: #cbd5e1;
        }

        .legend-row {
            display: flex;
            gap: 15px;
            font-size: 0.78rem;
            color: var(--text-secondary);
            margin-top: 8px;
            flex-wrap: wrap;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }

        .timeline-card {
            border-left: 3px solid var(--accent-blue);
            padding-left: 14px;
            margin-bottom: 16px;
            position: relative;
        }

        .timeline-card.alert { border-left-color: var(--accent-yellow); }
        .timeline-card.danger { border-left-color: var(--accent-red); }

        .time-badge {
            display: inline-block;
            background: var(--bg-card);
            color: var(--accent-blue);
            font-size: 0.75rem;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
            margin-bottom: 4px;
        }

        img.responsive-fig {
            width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            transition: transform 0.2s;
        }

        img.responsive-fig:hover {
            transform: scale(1.005);
        }
    </style>
</head>
<body>

    <!-- CABEÇALHO PRINCIPAL -->
    <header>
        <div class="title-container">
            <h1>Laboratório de Meteorologia de Mesoescala (FSC7116 - UFSC)</h1>
            <p>Prof. Dr. Reinaldo Haas • Termodinâmica de Convecção (Emanuel 1994) & Diagnóstico Tríplice de Mesoescala</p>
        </div>
        <div class="case-selector">
            <label for="soundingSelect"><strong>Sondagem SBPA:</strong></label>
            <select id="soundingSelect" onchange="loadCase(this.value)">
                <option value="19951212">12/12/1995 12Z - Pós-frontal / Estável</option>
                <option value="19951223">23/12/1995 12Z - Pré-convectivo Moderado / Neutra</option>
                <option value="19951224" selected>24/12/1995 12Z - Convecção Explosiva / Severa</option>
            </select>
        </div>
    </header>

    <!-- NAVEGAÇÃO DE ABAS: 3 ABAS CIENTÍFICAS E DIRETAS -->
    <div class="nav-tabs" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <button class="tab-btn active" id="tabMainBtn" onclick="switchTab('main')">📊 Painel Interativo de Mesoescala</button>
            <button class="tab-btn" id="tabComparisonBtn" onclick="switchTab('comparison')">⚖️ Comparação Tríplice (3 Sondagens Lado a Lado)</button>
            <button class="tab-btn" id="tabRoadmapBtn" onclick="switchTab('roadmap')">🎓 Roteiro do Estudante (Ambas Apresentações)</button>
        </div>
        <div>
            <a href="apresentacao_meso.pptx" download class="tab-btn" style="background: #2563eb; color: #ffffff; text-decoration: none; font-weight: bold; border: 1px solid #3b82f6; box-shadow: 0 2px 8px rgba(37,99,235,0.3);">
                📥 Baixar Apresentação PPTX (10 Slides / 20 min)
            </a>
        </div>
    </div>

    <!-- ======================================================================= -->
    <!-- ABA 1: PAINEL PRINCIPAL DE DIAGNÓSTICO -->
    <!-- ======================================================================= -->
    <div id="tabMain">
        <!-- MÉTRICAS INTEGRADAS -->
        <div class="grid-dashboard">
            <div class="card col-12">
                <div class="card-title">
                    <span>Parâmetros Ambientais & Índices Termodinâmicos de Severidade</span>
                    <span id="caseBadge" class="status-badge badge-extreme">AVALIAÇÃO SEVERA</span>
                </div>
                <div class="metrics-grid">
                    <div class="metric-box danger">
                        <div class="metric-val" id="mucapeVal">4646 J/kg</div>
                        <div class="metric-lbl">MUCAPE (Pseudo Tv)</div>
                    </div>
                    <div class="metric-box warning">
                        <div class="metric-val" id="capeRevVal">3832 J/kg</div>
                        <div class="metric-lbl">CAPE Reversível (Tρ)</div>
                    </div>
                    <div class="metric-box success">
                        <div class="metric-val" id="mucinVal">-6.5 J/kg</div>
                        <div class="metric-lbl">MUCIN (Inibição)</div>
                    </div>
                    <div class="metric-box danger">
                        <div class="metric-val" id="dcapeVal">1149 J/kg</div>
                        <div class="metric-lbl">DCAPE (Downburst)</div>
                    </div>
                    <div class="metric-box purple">
                        <div class="metric-val" id="shear1kmVal">18.4 m/s</div>
                        <div class="metric-lbl">Cisalhamento 0-1km</div>
                    </div>
                    <div class="metric-box purple">
                        <div class="metric-val" id="shear6kmVal">28.7 m/s</div>
                        <div class="metric-lbl">Cisalhamento 0-6km</div>
                    </div>
                    <div class="metric-box danger">
                        <div class="metric-val" id="srhVal">245 m²/s²</div>
                        <div class="metric-lbl">SRH 0-3km (Helicidade)</div>
                    </div>
                    <div class="metric-box warning">
                        <div class="metric-val" id="pwVal">55.3 mm</div>
                        <div class="metric-lbl">Água Precipitável (PW)</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- GRÁFICOS INTERATIVOS: SKEW-T E HODÓGRAFO -->
        <div class="grid-dashboard">
            <!-- SKEW-T -->
            <div class="card col-8">
                <div class="card-title">
                    <span>Diagrama Termodinâmico Skew-T / Log-P Interativo</span>
                    <div class="btn-group">
                        <button class="btn-sm active" id="btnPseudo" onclick="toggleParcelMode('pseudo')">Pseudoadiabático (Tv)</button>
                        <button class="btn-sm" id="btnRev" onclick="toggleParcelMode('reversible')">Reversível (Tρ Emanuel)</button>
                    </div>
                </div>
                <canvas id="skewtCanvas" width="750" height="520"></canvas>
                <div class="legend-row">
                    <div class="legend-item"><div class="legend-dot" style="background:#ef4444;"></div> Temp. Ambiente (T)</div>
                    <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div> Ponto de Orvalho (Td)</div>
                    <div class="legend-item"><div class="legend-dot" style="background:#fbbf24;"></div> Trajetória Parcela (Tp)</div>
                    <div class="legend-item"><div class="legend-dot" style="background:rgba(74, 222, 128, 0.4);"></div> CAPE (Flutuabilidade +)</div>
                    <div class="legend-item"><div class="legend-dot" style="background:rgba(248, 113, 113, 0.4);"></div> CIN (Inibição -)</div>
                </div>
                <div class="theory-box" id="emanuelTheoryText">
                    <strong>Fundamento de Kerry Emanuel (1994, Cap. 4 & 6; MIT 12.811):</strong>
                    Na ascensão <em>reversível</em>, o código <code>wyoming.py</code> calcula 
                    <code>TLVR = TG * (1. + RG/EPS) / (1. + R(I))</code>. O termo <code>-r_l</code> 
                    (carga de água líquida retida) reduz a flutuabilidade positiva da parcela, evitando superestimação física do CAPE.
                </div>
            </div>

            <!-- HODÓGRAFO E BRUNT-VÄISÄLÄ -->
            <div class="card col-4">
                <div class="card-title">
                    <span>Hodógrafo Polar do Vento & Helicidade</span>
                </div>
                <canvas id="hodoCanvas" width="380" height="300"></canvas>
                <div class="legend-row">
                    <div class="legend-item"><div class="legend-dot" style="background:#ef4444;"></div> 0 - 1 km (JBN)</div>
                    <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div> 1 - 3 km</div>
                    <div class="legend-item"><div class="legend-dot" style="background:#38bdf8;"></div> 3 - 6 km</div>
                    <div class="legend-item"><div class="legend-dot" style="background:#fbbf24;"></div> Vetor Tempestade (c)</div>
                </div>

                <div class="card-title" style="margin-top: 16px;">
                    <span>Perfil de Brunt-Väisälä: N²(z)</span>
                </div>
                <canvas id="bruntCanvas" width="380" height="150"></canvas>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 4px;">
                    Camadas com N² > 3.5×10⁻⁴ s⁻² caracterizam forte estabilidade estática e inversão de capeamento (<em>capping lid</em>).
                </div>
            </div>
        </div>

        <!-- PERFIS VERTICAIS DO COLAB PARA O CASO SELECIONADO -->
        <div class="grid-dashboard">
            <div class="card col-12">
                <div class="card-title">
                    <span id="colabProfilesTitle">Perfis Verticais de Mesoescala do Colab (θ, θe, θs, N, S, r)</span>
                    <span class="status-badge badge-mod" id="colabProfilesBadge">CASO ATUAL</span>
                </div>
                <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 12px;">
                    Perfis completos calculados no Colab via MetPy: (1) Temperatura Potencial Seca (\(\theta\)), Equivalente (\(\theta_e\)) e de Saturação (\(\theta_s\)); (2) Frequência de Brunt-Väisälä (\(N\) em s⁻¹); (3) Estabilidade Estática (\(S\)); (4) Razão de Mistura (\(r\) em g/kg) e Água Precipitável (\(PW\)).
                </p>
                <img id="imgColabProfiles" src="metpack/fig_profiles_19951224.png" alt="Perfis do Colab" class="responsive-fig">
            </div>
        </div>

        <!-- MATRIZES 2D DE KERRY EMANUEL PARA O CASO SELECIONADO -->
        <div class="grid-dashboard">
            <div class="card col-6">
                <div class="card-title">
                    <span id="emanuelRevTitle">Matriz 2D Reversível: Diferença de Temp. de Densidade Tρ (K)</span>
                    <span class="status-badge badge-stable">Emanuel wyoming.f / tcon.py</span>
                </div>
                <p style="font-size: 0.84rem; color: #cbd5e1; margin-bottom: 8px;">
                    Calcula \(\Delta T_\rho = T_\rho - T_{\rho,a}\) retendo todo o condensado (\(r_l = r_t - r_v\)). Penalidade gravitacional de arrasto dos hidrometeoros.
                </p>
                <img id="imgEmanuelRev" src="metpack/tcon_tdifrev_19951224.png" alt="Matriz Reversível" class="responsive-fig">
            </div>

            <div class="card col-6">
                <div class="card-title">
                    <span id="emanuelPseudoTitle">Matriz 2D Pseudoadiabática: Diferença de Temp. Virtual Tv (K)</span>
                    <span class="status-badge badge-mod">Emanuel wyoming.f / tcon.py</span>
                </div>
                <p style="font-size: 0.84rem; color: #cbd5e1; margin-bottom: 8px;">
                    Assume precipitação instantânea de todo o condensado (\(r_l = 0\)). Flutuabilidade máxima atingida na média e alta troposfera.
                </p>
                <img id="imgEmanuelPseudo" src="metpack/tcon_tdifpseudo_19951224.png" alt="Matriz Pseudoadiabática" class="responsive-fig">
            </div>
        </div>

        <!-- TABELA DE DADOS BRUTOS DA SONDAGEM OBSERVADA -->
        <div class="grid-dashboard">
            <div class="card col-12">
                <div class="card-title">
                    <span>Níveis de Pressão e Perfis Observados da Estação SBPA</span>
                    <span style="font-size: 0.8rem; color: var(--text-secondary);">Fonte: Wyoming Upper Air Data (SBPA 83971)</span>
                </div>
                <div class="table-container">
                    <table id="soundingTable">
                        <thead>
                            <tr>
                                <th>PRES (hPa)</th>
                                <th>HGHT (m)</th>
                                <th>TEMP (°C)</th>
                                <th>DWPT (°C)</th>
                                <th>DIR (°)</th>
                                <th>SPED (m/s)</th>
                                <th>θe (K)</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- ======================================================================= -->
    <!-- ABA 2: COMPARAÇÃO TRÍPLICE CIENTÍFICA (3 CASOS LADO A LADO) -->
    <!-- ======================================================================= -->
    <div id="tabComparison" style="display: none;">
        <div class="grid-dashboard">
            <div class="card col-12">
                <div class="card-title">
                    <span>1. Comparação Tríplice dos Diagramas Skew-T e Hodógrafos do Vento</span>
                    <span class="status-badge badge-mod">3 ESTADOS ATMOSFÉRICOS</span>
                </div>
                <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 12px;">
                    Comparação direta entre o regime pós-frontal Estável (12/12/1995), o regime de transição Neutro (23/12/1995) e o regime de convecção severa explosiva com Supercélula HP (24/12/1995).
                </p>
                <img src="metpack/fig_3_soundings_complete_analysis.png" alt="Comparação Tríplice Skew-T" class="responsive-fig">
            </div>

            <div class="card col-12">
                <div class="card-title">
                    <span>2. Comparação dos Perfis Verticais do Colab Lado a Lado (θe, N, S, r)</span>
                    <span class="status-badge badge-extreme">METPY + COLAB</span>
                </div>
                <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 12px;">
                    Confronto das 4 variáveis-chave do Colab entre os 3 regimes: (1) Injeção de \(\theta_e = 377.8\text{ K}\) no JBN; (2) Inversão de Brunt-Väisälä (\(N\)) funcionando como <em>capping lid</em>; (3) Estabilidade estática \(S\); (4) Estoque de vapor d'água com \(r = 22.0\text{ g/kg}\) no caso severo.
                </p>
                <img src="metpack/fig_3_soundings_profiles_comparison.png" alt="Comparação Perfis Verticais" class="responsive-fig">
            </div>

            <div class="card col-12">
                <div class="card-title">
                    <span>3. Comparação das Matrizes de Convecção 2D de Kerry Emanuel (6 Painéis)</span>
                    <span class="status-badge badge-stable">MIT OCW 12.811 / EMANUEL 1994</span>
                </div>
                <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 12px;">
                    Linha 1: Matrizes Reversíveis (\(T_\rho\)) com carga de água retida. Linha 2: Matrizes Pseudoadiabáticas (\(T_v\)). Note como o caso de 12/12 é totalmente frio/estável (azul), o caso de 23/12 possui instabilidade moderada rasa, e o caso de 24/12 apresenta núcleo gigantesco de flutuabilidade positiva (\(\Delta T > +10\text{ K}\)) até 400 mb.
                </p>
                <img src="metpack/fig_3_soundings_emanuel_matrices.png" alt="Comparação Matrizes Emanuel" class="responsive-fig">
            </div>

            <div class="card col-12">
                <div class="card-title">
                    <span>4. Tabela Comparativa Tríplice de Índices Diagnósticos de Severidade</span>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Parâmetro Diagnóstico</th>
                                <th style="color: #38bdf8;">12/12/1995 (Estável)</th>
                                <th style="color: #fbbf24;">23/12/1995 (Neutra)</th>
                                <th style="color: #f87171;">24/12/1995 (Instável Severa)</th>
                                <th>Interpretação Física</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>Temperatura à Superfície (T₀)</td><td>19.4 °C</td><td>25.8 °C</td><td>24.6 °C</td><td>Aquecimento pré-frontal acentuado</td></tr>
                            <tr><td>Ponto de Orvalho à Superfície (Td₀)</td><td>16.3 °C</td><td>24.4 °C</td><td>23.2 °C</td><td>Advecção maciça de umidade tropical</td></tr>
                            <tr><td>Razão de Mistura Máxima (r_max)</td><td>11.6 g/kg (Sfc)</td><td>19.4 g/kg (Sfc)</td><td style="color:#f87171; font-weight:bold;">22.0 g/kg (925 hPa)</td><td>Jato em Baixos Níveis concentrando vapor</td></tr>
                            <tr><td>SBCAPE (Superfície)</td><td>15.7 J/kg</td><td>2761.7 J/kg</td><td>1861.9 J/kg</td><td>Parcela de superfície vs parcela mais instável</td></tr>
                            <tr><td>MUCAPE (Mais Instável)</td><td>0.0 J/kg</td><td>2761.7 J/kg</td><td style="color:#f87171; font-weight:bold;">4645.5 J/kg (7781 J/kg Emanuel)</td><td>Energia potencial extrema para correntes ascendentes</td></tr>
                            <tr><td>Inibição Convectiva (CIN)</td><td>0.0 J/kg</td><td>0.0 J/kg</td><td style="color:#fbbf24;">-6.5 J/kg (-185 J/kg na Sfc)</td><td>Capping lid rompe com aquecimento e convergência</td></tr>
                            <tr><td>Água Precipitável (PW)</td><td>35.1 mm</td><td style="color:#fbbf24;">57.0 mm</td><td style="color:#f87171; font-weight:bold;">55.3 mm</td><td>Chuva torrencial e inundações repentinas</td></tr>
                            <tr><td>Cisalhamento Bulk 0-6 km</td><td>13.7 m/s</td><td>10.2 m/s</td><td style="color:#f87171; font-weight:bold;">28.7 m/s (55.8 kt)</td><td>Limiar severo de supercélulas (> 20 m/s)</td></tr>
                            <tr><td>Helicidade Relativa 0-3 km (SRH)</td><td>58 m²/s²</td><td>135 m²/s²</td><td style="color:#f87171; font-weight:bold;">245 m²/s²</td><td>Rotação de mesociclone na média troposfera</td></tr>
                            <tr><td>Downdraft CAPE (DCAPE)</td><td>0 J/kg</td><td>0 J/kg</td><td style="color:#f87171; font-weight:bold;">1149 J/kg</td><td>Rajadas severas descendentes (downbursts ~ 48 m/s)</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- ======================================================================= -->
    <!-- ABA 3: ROTEIRO PEDAGÓGICO DO ESTUDANTE (AMBAS APRESENTAÇÕES) -->
    <!-- ======================================================================= -->
    <div id="tabRoadmap" style="display: none;">
        <div class="grid-dashboard">
            <!-- BANNER DE DOWNLOAD DA APRESENTAÇÃO -->
            <div class="card col-12" style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 2px solid #3b82f6; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                            <span class="status-badge badge-extreme" style="background: #2563eb;">ARQUIVO PPTX PRONTO</span>
                            <span class="status-badge badge-mod">10 SLIDES EM 16:9 WIDESCREEN</span>
                            <span class="status-badge badge-neutral">CRONÔMETRO: 20 MINUTOS</span>
                        </div>
                        <h2 style="color: #60a5fa; margin-bottom: 6px; font-size: 1.35rem;">Apresentação Completa do Seminário: <code>apresentacao_meso.pptx</code></h2>
                        <p style="color: #cbd5e1; font-size: 0.92rem; margin: 0; max-width: 820px;">
                            Contém todos os 10 slides estritamente sincronizados com o roteiro de 20 minutos da banca (Prof. Reinaldo Haas - UFSC), figuras científicas de alta resolução embutidas e <strong>notas completas do orador com o script falado</strong> em cada slide.
                        </p>
                    </div>
                    <div>
                        <a href="apresentacao_meso.pptx" download style="display: inline-flex; align-items: center; gap: 8px; background: #2563eb; color: #fff; padding: 13px 24px; border-radius: 8px; font-weight: bold; text-decoration: none; box-shadow: 0 4px 15px rgba(37,99,235,0.4); font-size: 1.05rem; border: 1px solid #60a5fa;">
                            📥 Baixar apresentacao_meso.pptx (5.3 MB)
                        </a>
                    </div>
                </div>
            </div>

            <!-- GUIA TUTORIAL DIDÁTICO PARA OS ALUNOS -->
            <div class="card col-12" style="background: rgba(30, 41, 59, 0.7); border: 2px solid #eab308; margin-bottom: 12px;">
                <div class="card-title">
                    <span style="color: #facc15;">📚 Tutorial Metodológico para os Alunos (FSC7116 - UFSC)</span>
                    <span class="status-badge badge-mod" style="background: #a16207; color: #fef08a;">DIRETRIZ OFICIAL</span>
                </div>
                <div style="font-size: 0.95rem; color: #e2e8f0; line-height: 1.6;">
                    <p style="margin-bottom: 10px;">
                        <strong>Objetivo Pedagógico da Disciplina:</strong> Capacitar o estudante a realizar um diagnóstico termodinâmico e dinâmico completo de mesoescala, confrontando perfis verticais reais da atmosfera e compreendendo a física de parcelas de Kerry Emanuel (1994) e a cinemática de cisalhamento.
                    </p>
                    <div style="background: #0f172a; padding: 14px 18px; border-radius: 8px; border-left: 4px solid #facc15; margin-bottom: 12px;">
                        <h4 style="color: #facc15; margin: 0 0 6px 0; font-size: 1rem;">⚠️ REQUISITO OBRIGATÓRIO PARA AVALIAÇÃO DA BANCA (PROF. REINALDO HAAS):</h4>
                        <p style="margin: 0; color: #f8fafc; font-size: 0.92rem;">
                            Cada estudante ou grupo <strong>DEVE OBRIGATORIAMENTE PREPARAR DUAS APRESENTAÇÕES</strong> com base em <strong>TRÊS RADIOSSONDAGENS REAIS DISTINTAS</strong> cobrindo os três regimes troposféricos:
                        </p>
                        <ul style="margin: 8px 0 8px 20px; padding: 0; font-size: 0.9rem; color: #cbd5e1;">
                            <li><strong style="color: #38bdf8;">1. Atmosfera ESTÁVEL:</strong> Perfil pós-frontal anticiclônico com ar seco em altitude, CAPE = 0 J/kg, forte estratificação estável (\(N > 0\)), sem LFC.</li>
                            <li><strong style="color: #facc15;">2. Atmosfera NEUTRA (ou Transição):</strong> Perfil com umidade na camada limite e CAPE moderado, mas cisalhamento vertical fraco e inibição convectiva.</li>
                            <li><strong style="color: #f87171;">3. Atmosfera INSTÁVEL (Convecção Severa):</strong> Perfil com MUCAPE \(> 2500-4500\text{ J/kg}\), capping lid em 925 hPa com posterior rompimento explosivo, JBN com vento \(> 20\text{ m/s}\) e helicidade SRH \(> 200\text{ m}^2/\text{s}^2\).</li>
                        </ul>
                    </div>

                    <h4 style="color: #38bdf8; margin: 14px 0 6px 0;">🎯 As Duas Apresentações Exigidas:</h4>
                    <p><strong>Apresentação 1 (Diagnóstico Científico & Laboratório):</strong> Foco na metodologia, download dos dados brutos de Wyoming, execução do Colab e dos códigos Python (<code>wyoming.py</code>, <code>tcon.py</code>), análise de todos os perfis verticais (\(\theta, \theta_e, \theta_s, N, S, r, PW\)), Skew-T, Hodógrafo e matrizes 2D de Kerry Emanuel.</p>
                    <p style="margin-top: 6px;"><strong>Apresentação 2 (Defesa Oficial perante a Banca - 20 minutos):</strong> Apresentação formal de síntese científica (10 slides), cronometrada slide a slide, com foco na dinâmica de mesoescala, acoplamento sinótico (500 e 850 hPa com mapa Cartopy de fronteiras reais), suporte de cisalhamento do JBN e classificação do modo convectivo supercelular HP.</p>
                </div>
            </div>

            <div class="card col-12">
                <div class="card-title">
                    <span>Roteiro Cronometrado da Apresentação 2 (Defesa Oral de 20 Minutos perante a Banca)</span>
                    <span class="status-badge badge-mod">SLIDE A SLIDE COM SCRIPT FALADO</span>
                </div>

                <!-- BLOCO 1 -->
                <div class="timeline-card">
                    <span class="time-badge">00 - 03 min | Slides 1 & 2</span>
                    <h3 style="color: var(--accent-blue); margin-bottom: 6px;">Sinótica e Contexto do Caso Extremo</h3>
                    <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 8px;">
                        Apresentação do evento severo (24/12/1995 em SBPA) e cartas de reanálise de 500 hPa (cavado baroclínico e difluência a jusante com CVA máxima) e 850 hPa (JBN advectando calor e umidade com \(\theta_e > 360\text{ K}\)). Mapas com divisão geográfica e fronteiras reais geradas via Cartopy.
                    </p>
                    <div>
                        <a href="metpack/fig_synoptic_analysis.png" target="_blank" style="color: #38bdf8; font-size: 0.85rem; font-weight: 600; text-decoration: underline;">🔍 Ver Carta Sinótica de Reanálise (fig_synoptic_analysis.png)</a>
                    </div>
                </div>

                <!-- BLOCO 2 -->
                <div class="timeline-card alert">
                    <span class="time-badge">03 - 07 min | Slides 3 & 4</span>
                    <h3 style="color: var(--accent-yellow); margin-bottom: 6px;">As Três Sondagens e as Três Análises Físicas Completas</h3>
                    <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 8px;">
                        Comparação dos 3 perfis no Skew-T (12/12 estável, 23/12 moderado, 24/12 severo). Formalismo de CAPE e CIN, e análise do gradiente vertical \(\partial \theta_e/\partial z < 0\) demonstrando instabilidade convectiva severa.
                    </p>
                    <div>
                        <a href="metpack/fig_3_soundings_complete_analysis.png" target="_blank" style="color: #facc15; font-size: 0.85rem; font-weight: 600; text-decoration: underline;">🔍 Ver Matriz Comparativa Tríplice Completa (fig_3_soundings_complete_analysis.png)</a>
                    </div>
                </div>

                <!-- BLOCO 3 -->
                <div class="timeline-card danger">
                    <span class="time-badge">07 - 10 min | Slide 5</span>
                    <h3 style="color: var(--accent-red); margin-bottom: 6px;">Temperatura de Densidade (Tρ) e Algoritmo de Kerry Emanuel</h3>
                    <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 8px;">
                        Explicação dos resultados do <code>wyoming.py</code> citando rigorosamente <em>Atmospheric Convection</em> (Emanuel, 1994, Cap. 4 & 6). Demonstrar como o termo de carregamento de hidrometeoros (<code>-r_l</code>) reduz a flutuabilidade real entre as matrizes reversível e pseudoadiabática.
                    </p>
                    <div>
                        <a href="metpack/fig_3_soundings_emanuel_matrices.png" target="_blank" style="color: #38bdf8; font-size: 0.85rem; font-weight: 600; text-decoration: underline;">🔍 Ver Matrizes 2D das Três Sondagens (fig_3_soundings_emanuel_matrices.png)</a>
                    </div>
                </div>

                <!-- BLOCO 4 -->
                <div class="timeline-card">
                    <span class="time-badge">10 - 14 min | Slides 6 & 7</span>
                    <h3 style="color: var(--accent-purple); margin-bottom: 6px;">Variáveis do Capítulo 2: θv, Brunt-Väisälä (N²), Razão de Mistura e PW</h3>
                    <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 8px;">
                        Perfis verticais comparados para as 3 sondagens: temperatura potencial equivalente (\(\theta_e\)), frequência de Brunt-Väisälä (\(N\)), razão de mistura (\(r\)) e DCAPE (1149 J/kg). Mostrar que o pico de \(N\) em 925 hPa agiu como <em>capping lid</em> acumulador de energia no caso severo.
                    </p>
                    <div>
                        <a href="metpack/fig_3_soundings_profiles_comparison.png" target="_blank" style="color: #38bdf8; font-size: 0.85rem; font-weight: 600; text-decoration: underline;">🔍 Ver Comparação de Perfis das 3 Sondagens (fig_3_soundings_profiles_comparison.png)</a>
                    </div>
                </div>

                <!-- BLOCO 5 -->
                <div class="timeline-card danger">
                    <span class="time-badge">14 - 17 min | Slide 8</span>
                    <h3 style="color: var(--accent-blue); margin-bottom: 6px;">Cinemática: Hodógrafo, Jato em Baixos Níveis (JBN) e Helicidade (SRH)</h3>
                    <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 8px;">
                        Análise do hodógrafo curvo, identificação do núcleo do JBN em 925 hPa com vento de 44 nós (23.2 m/s), cisalhamento bulk 0-6 km de 28.7 m/s e SRH 0-3 km de 245 m²/s² suportando convecção supercelular rotatória.
                    </p>
                    <div>
                        <a href="metpack/fig_kinematics_hodograph.png" target="_blank" style="color: #38bdf8; font-size: 0.85rem; font-weight: 600; text-decoration: underline;">🔍 Ver Hodógrafo Polar Detalhado (fig_kinematics_hodograph.png)</a>
                    </div>
                </div>

                <!-- BLOCO 6 -->
                <div class="timeline-card">
                    <span class="time-badge">17 - 20 min | Slides 9 & 10</span>
                    <h3 style="color: var(--accent-green); margin-bottom: 6px;">Conclusão: Síntese dos Gatilhos de Mesoescala & Fechamento para a Banca</h3>
                    <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 8px;">
                        Síntese integrada (Instabilidade Extrema + Rompimento do Capping Lid + Suporte Cinemático do JBN). Classificação como Supercélulas de Alta Precipitação (HP) com rajadas descendentes severas. Abertura formal para a arguição da banca examinadora.
                    </p>
                    <div style="margin-top: 8px;">
                        <a href="metpack/fig_esquema_supercelula_hp.png" target="_blank" style="color: #38bdf8; font-size: 0.85rem; font-weight: 600; text-decoration: underline;">🔍 Ver Esquema Conceitual Supercélula HP (fig_esquema_supercelula_hp.png)</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- SCRIPT DE INTERATIVIDADE E DADOS EMBUTIDOS -->
    <script>
        // Dados resumidos de cada sondagem
        const soundings = {
            "19951212": {
                date: "12/12/1995 12Z",
                status: "ESTÁVEL / PÓS-FRONTAL",
                badgeClass: "badge-stable",
                mucape: 15.7,
                capeRev: 17.7,
                mucin: 0.0,
                dcape: 0.0,
                pw: 35.1,
                rmax: 11.6,
                li: 2.5,
                shear1km: 6.2,
                shear6km: 13.7,
                srh3km: 58.0,
                stormMotion: [15.2, 5.1],
                colabProfilesFig: "metpack/fig_profiles_19951212.png",
                emanuelRevFig: "metpack/tcon_tdifrev_19951212.png",
                emanuelPseudoFig: "metpack/tcon_tdifpseudo_19951212.png",
                levels: [
                    {p: 1014.0, z: 3, t: 19.4, td: 16.3, dir: 180, spd: 4.1, thte: 324.2, thtv: 293.4},
                    {p: 1000.0, z: 119, t: 18.4, td: 15.7, dir: 170, spd: 5.2, thte: 323.6, thtv: 293.5},
                    {p: 979.1, z: 300, t: 16.7, td: 14.6, dir: 165, spd: 6.2, thte: 322.2, thtv: 293.5},
                    {p: 948.0, z: 576, t: 14.2, td: 12.9, dir: 170, spd: 5.7, thte: 320.1, thtv: 293.5},
                    {p: 925.0, z: 784, t: 12.8, td: 11.7, dir: 160, spd: 4.6, thte: 319.3, thtv: 294.0},
                    {p: 885.0, z: 1155, t: 13.2, td: -0.8, dir: 189, spd: 4.6, thte: 308.8, thtv: 297.3},
                    {p: 850.0, z: 1495, t: 13.4, td: 6.4, dir: 215, spd: 4.6, thte: 321.4, thtv: 301.5},
                    {p: 811.0, z: 1889, t: 12.2, td: 4.2, dir: 225, spd: 8.0, thte: 322.4, thtv: 304.1},
                    {p: 755.0, z: 2484, t: 8.0, td: 5.5, dir: 236, spd: 11.3, thte: 327.5, thtv: 306.0},
                    {p: 700.0, z: 3106, t: 5.8, td: -3.2, dir: 245, spd: 10.8, thte: 322.5, thtv: 309.7},
                    {p: 614.0, z: 4168, t: -1.3, td: -1.4, dir: 255, spd: 17.3, thte: 330.4, thtv: 313.6},
                    {p: 500.0, z: 5780, t: -11.5, td: -25.5, dir: 265, spd: 12.4, thte: 322.4, thtv: 319.1},
                    {p: 400.0, z: 7460, t: -20.7, td: -31.7, dir: 250, spd: 28.3, thte: 330.5, thtv: 328.1},
                    {p: 300.0, z: 9540, t: -34.1, td: -50.1, dir: 230, spd: 33.0, thte: 337.7, thtv: 337.2},
                    {p: 250.0, z: 10800, t: -41.7, td: -65.7, dir: 260, spd: 40.2, thte: 344.0, thtv: 343.9},
                    {p: 200.0, z: 12250, t: -53.3, td: -70.3, dir: 305, spd: 14.4, thte: 348.3, thtv: 348.2},
                    {p: 150.0, z: 14070, t: -63.9, td: -76.9, dir: 250, spd: 36.5, thte: 359.8, thtv: 359.8},
                    {p: 100.0, z: 16510, t: -74.3, td: -87.3, dir: 250, spd: 23.2, thte: 383.9, thtv: 383.9}
                ]
            },
            "19951223": {
                date: "23/12/1995 12Z",
                status: "NEUTRA / PRÉ-CONVECTIVA",
                badgeClass: "badge-mod",
                mucape: 2761.7,
                capeRev: 1266.5,
                mucin: 0.0,
                dcape: 0.0,
                pw: 57.0,
                rmax: 19.4,
                li: -6.1,
                shear1km: 11.8,
                shear6km: 10.2,
                srh3km: 135.0,
                stormMotion: [9.5, -4.2],
                colabProfilesFig: "metpack/fig_profiles_19951223.png",
                emanuelRevFig: "metpack/tcon_tdifrev_19951223.png",
                emanuelPseudoFig: "metpack/tcon_tdifpseudo_19951223.png",
                levels: [
                    {p: 1009.0, z: 3, t: 25.8, td: 24.4, dir: 100, spd: 2.1, thte: 354.8, thtv: 301.6},
                    {p: 1000.0, z: 83, t: 25.0, td: 23.8, dir: 135, spd: 1.5, thte: 353.2, thtv: 301.5},
                    {p: 975.3, z: 300, t: 23.2, td: 22.7, dir: 195, spd: 4.1, thte: 351.2, thtv: 301.7},
                    {p: 942.0, z: 600, t: 21.3, td: 20.7, dir: 230, spd: 7.7, thte: 348.0, thtv: 302.5},
                    {p: 925.0, z: 757, t: 20.6, td: 19.5, dir: 230, spd: 10.8, thte: 346.3, thtv: 303.2},
                    {p: 850.0, z: 1497, t: 18.4, td: 12.4, dir: 245, spd: 12.9, thte: 337.8, thtv: 307.4},
                    {p: 810.0, z: 1906, t: 15.4, td: 14.8, dir: 248, spd: 14.3, thte: 346.3, thtv: 308.9},
                    {p: 763.4, z: 2400, t: 12.6, td: 11.3, dir: 250, spd: 16.0, thte: 342.7, thtv: 310.7},
                    {p: 700.0, z: 3122, t: 8.4, td: 6.3, dir: 245, spd: 14.9, thte: 338.6, thtv: 313.4},
                    {p: 614.0, z: 4200, t: 2.2, td: -1.1, dir: 245, spd: 5.7, thte: 335.1, thtv: 317.7},
                    {p: 500.0, z: 5840, t: -7.5, td: -10.2, dir: 265, spd: 9.3, thte: 335.8, thtv: 324.5},
                    {p: 400.0, z: 7540, t: -18.7, td: -23.5, dir: 205, spd: 6.7, thte: 335.8, thtv: 330.9},
                    {p: 300.0, z: 9640, t: -33.9, td: -44.9, dir: 220, spd: 4.6, thte: 338.4, thtv: 337.5},
                    {p: 250.0, z: 10880, t: -42.9, td: -64.9, dir: 240, spd: 5.2, thte: 342.3, thtv: 342.2},
                    {p: 200.0, z: 12350, t: -52.9, td: -74.9, dir: 130, spd: 12.9, thte: 348.9, thtv: 348.8},
                    {p: 150.0, z: 14160, t: -65.1, td: -83.1, dir: 115, spd: 18.5, thte: 357.8, thtv: 357.7},
                    {p: 100.0, z: 16598, t: -72.1, td: -88.1, dir: 85, spd: 4.1, thte: 388.2, thtv: 388.2}
                ]
            },
            "19951224": {
                date: "24/12/1995 12Z",
                status: "CONVECÇÃO SEVERA EXPLOSIVA",
                badgeClass: "badge-extreme",
                mucape: 4645.5,
                capeRev: 3832.0,
                mucin: -6.5,
                dcape: 1149.0,
                pw: 55.3,
                rmax: 22.0,
                li: -5.2,
                shear1km: 18.4,
                shear6km: 28.7,
                srh3km: 245.0,
                stormMotion: [-16.5, -9.2],
                colabProfilesFig: "metpack/fig_profiles_19951224.png",
                emanuelRevFig: "metpack/tcon_tdifrev_19951224.png",
                emanuelPseudoFig: "metpack/tcon_tdifpseudo_19951224.png",
                levels: [
                    {p: 1009.0, z: 3, t: 24.6, td: 23.2, dir: 110, spd: 5.2, thte: 349.2, thtv: 300.2},
                    {p: 1000.0, z: 84, t: 24.8, td: 22.5, dir: 80, spd: 8.8, thte: 348.6, thtv: 301.0},
                    {p: 975.4, z: 300, t: 22.7, td: 21.0, dir: 70, spd: 13.4, thte: 345.3, thtv: 300.8},
                    {p: 942.5, z: 600, t: 26.9, td: 23.3, dir: 65, spd: 19.6, thte: 363.7, thtv: 308.7},
                    {p: 925.0, z: 764, t: 30.0, td: 25.0, dir: 60, spd: 22.6, thte: 377.8, thtv: 314.0},
                    {p: 910.5, z: 900, t: 27.6, td: 22.7, dir: 60, spd: 23.2, thte: 368.2, thtv: 312.5},
                    {p: 850.0, z: 1493, t: 17.0, td: 12.7, dir: 60, spd: 20.1, thte: 336.7, thtv: 305.9},
                    {p: 802.0, z: 1984, t: 13.2, td: 13.2, dir: 52, spd: 13.0, thte: 341.0, thtv: 307.2},
                    {p: 762.8, z: 2400, t: 10.8, td: 10.8, dir: 50, spd: 8.8, thte: 339.5, thtv: 308.8},
                    {p: 700.0, z: 3112, t: 6.8, td: 6.7, dir: 45, spd: 9.3, thte: 337.3, thtv: 311.6},
                    {p: 619.0, z: 4120, t: 1.2, td: 1.1, dir: 40, spd: 11.6, thte: 336.0, thtv: 315.9},
                    {p: 500.0, z: 5820, t: -7.7, td: -16.7, dir: 35, spd: 12.4, thte: 330.8, thtv: 324.0},
                    {p: 400.0, z: 7520, t: -18.1, td: -50.1, dir: 35, spd: 16.5, thte: 331.8, thtv: 331.4},
                    {p: 300.0, z: 9610, t: -33.5, td: -43.5, dir: 10, spd: 7.2, thte: 339.2, thtv: 338.1},
                    {p: 250.0, z: 10850, t: -43.1, td: -56.1, dir: 15, spd: 14.9, thte: 342.2, thtv: 341.9},
                    {p: 200.0, z: 12320, t: -53.9, td: -72.9, dir: 15, spd: 14.9, thte: 347.3, thtv: 347.3},
                    {p: 150.0, z: 14130, t: -65.3, td: -82.3, dir: 15, spd: 14.9, thte: 357.4, thtv: 357.4},
                    {p: 100.0, z: 16580, t: -71.3, td: -87.3, dir: 15, spd: 14.9, thte: 389.7, thtv: 389.7}
                ]
            }
        };

        let currentCase = "19951224";
        let parcelMode = "pseudo";

        function switchTab(tab) {
            document.getElementById('tabMain').style.display = tab === 'main' ? 'block' : 'none';
            document.getElementById('tabComparison').style.display = tab === 'comparison' ? 'block' : 'none';
            document.getElementById('tabRoadmap').style.display = tab === 'roadmap' ? 'block' : 'none';

            document.getElementById('tabMainBtn').classList.toggle('active', tab === 'main');
            document.getElementById('tabComparisonBtn').classList.toggle('active', tab === 'comparison');
            document.getElementById('tabRoadmapBtn').classList.toggle('active', tab === 'roadmap');

            if (tab === 'main') {
                renderSkewT();
                renderHodograph();
                renderBruntVaisala();
            }
        }

        function toggleParcelMode(mode) {
            parcelMode = mode;
            document.getElementById('btnPseudo').classList.toggle('active', mode === 'pseudo');
            document.getElementById('btnRev').classList.toggle('active', mode === 'reversible');
            
            const theory = document.getElementById('emanuelTheoryText');
            if (mode === 'reversible') {
                theory.innerHTML = `<strong>Modo Reversível (Emanuel 1994, Cap. 4 & 6; MIT 12.811):</strong> A parcela conserva a entropia úmida total <code>s = (cpd + rt*cl)*ln(T) - Rd*ln(pd) + Lv*rv/T</code>. O termo <code>TLVR = TG * (1. + RG/EPS) / (1. + R(I))</code> subtrai ativamente o peso dos hidrometeoros retidos. O CAPE efetivo é reduzido para <strong>${soundings[currentCase].capeRev.toFixed(0)} J/kg</strong>.`;
            } else {
                theory.innerHTML = `<strong>Modo Pseudoadiabático (Clássico):</strong> Assume precipitação instantânea de todo o condensado (sem carregamento de água líquida: <code>r_l = 0</code>). A flutuabilidade utiliza apenas a temperatura virtual pura <code>Tv = TG * (1 + 0.608*rv)</code>. O CAPE atinge o valor máximo de <strong>${soundings[currentCase].mucape.toFixed(0)} J/kg</strong>.`;
            }
            renderSkewT();
        }

        function loadCase(key) {
            currentCase = key;
            const data = soundings[key];

            // Atualiza badge e métricas
            document.getElementById('caseBadge').className = `status-badge ${data.badgeClass}`;
            document.getElementById('caseBadge').innerText = data.status;

            document.getElementById('mucapeVal').innerText = `${data.mucape.toFixed(0)} J/kg`;
            document.getElementById('capeRevVal').innerText = `${data.capeRev.toFixed(0)} J/kg`;
            document.getElementById('mucinVal').innerText = `${data.mucin.toFixed(1)} J/kg`;
            document.getElementById('dcapeVal').innerText = `${data.dcape.toFixed(0)} J/kg`;
            document.getElementById('shear1kmVal').innerText = `${data.shear1km.toFixed(1)} m/s`;
            document.getElementById('shear6kmVal').innerText = `${data.shear6km.toFixed(1)} m/s`;
            document.getElementById('srhVal').innerText = `${data.srh3km.toFixed(0)} m²/s²`;
            document.getElementById('pwVal').innerText = `${data.pw.toFixed(1)} mm`;

            // Atualiza imagens de perfis e matrizes de Emanuel
            document.getElementById('imgColabProfiles').src = data.colabProfilesFig;
            document.getElementById('colabProfilesTitle').innerText = `Perfis Verticais de Mesoescala do Colab (θ, θe, θs, N, S, r) - ${data.date}`;
            document.getElementById('colabProfilesBadge').innerText = data.status;

            document.getElementById('imgEmanuelRev').src = data.emanuelRevFig;
            document.getElementById('imgEmanuelPseudo').src = data.emanuelPseudoFig;
            document.getElementById('emanuelRevTitle').innerText = `Matriz 2D Reversível Tρ (K) - ${data.date}`;
            document.getElementById('emanuelPseudoTitle').innerText = `Matriz 2D Pseudoadiabática Tv (K) - ${data.date}`;

            // Tabela básica de níveis observados
            const tbody = document.querySelector('#soundingTable tbody');
            tbody.innerHTML = '';
            data.levels.forEach(lvl => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${lvl.p.toFixed(1)}</td>
                    <td>${lvl.z}</td>
                    <td style="color:#ef4444;">${lvl.t.toFixed(1)}</td>
                    <td style="color:#10b981;">${lvl.td.toFixed(1)}</td>
                    <td>${lvl.dir}°</td>
                    <td>${lvl.spd.toFixed(1)}</td>
                    <td>${lvl.thte.toFixed(1)}</td>
                `;
                tbody.appendChild(tr);
            });

            // Redesenha gráficos canvas
            renderSkewT();
            renderHodograph();
            renderBruntVaisala();
        }

        function renderSkewT() {
            const canvas = document.getElementById('skewtCanvas');
            const ctx = canvas.getContext('2d');
            const w = canvas.width;
            const h = canvas.height;
            const data = soundings[currentCase];

            ctx.clearRect(0, 0, w, h);

            const pMin = 100, pMax = 1050;
            const tMin = -70, tMax = 40;

            function getY(p) {
                return h * (Math.log(p) - Math.log(pMin)) / (Math.log(pMax) - Math.log(pMin));
            }

            function getX(t, p) {
                const y = getY(p);
                const skewOffset = (h - y) * 0.75;
                const tNorm = (t - tMin) / (tMax - tMin);
                return (tNorm * (w - 100)) + 60 + skewOffset * 0.5 - 120;
            }

            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 1;
            ctx.fillStyle = '#64748b';
            ctx.font = '10px monospace';
            const isobaricLevels = [1000, 850, 700, 500, 400, 300, 200, 150, 100];
            isobaricLevels.forEach(p => {
                const y = getY(p);
                ctx.beginPath();
                ctx.moveTo(50, y);
                ctx.lineTo(w - 20, y);
                ctx.stroke();
                ctx.fillText(`${p} hPa`, 10, y + 3);
            });

            for (let t = -80; t <= 40; t += 10) {
                ctx.beginPath();
                ctx.moveTo(getX(t, pMax), getY(pMax));
                ctx.lineTo(getX(t, pMin), getY(pMin));
                ctx.strokeStyle = t === 0 ? '#334155' : '#141d2e';
                ctx.lineWidth = t === 0 ? 1.5 : 1;
                ctx.stroke();
                if (t % 20 === 0) {
                    ctx.fillText(`${t}°C`, getX(t, 1000), getY(1000) + 12);
                }
            }

            // Sombra de CAPE
            if (data.mucape > 50) {
                ctx.fillStyle = 'rgba(74, 222, 128, 0.18)';
                ctx.beginPath();
                const elP = currentCase === '19951224' ? 140 : 250;
                ctx.moveTo(getX(data.levels[0].t, data.levels[0].p), getY(data.levels[0].p));
                for (let p = data.levels[0].p; p >= elP; p -= 20) {
                    const tParcel = data.levels[0].t - (6.0 * (data.levels[0].p - p) / 100.0) + (parcelMode === 'reversible' ? -2.5 : 0.0);
                    ctx.lineTo(getX(tParcel, p), getY(p));
                }
                for (let i = data.levels.length - 1; i >= 0; i--) {
                    if (data.levels[i].p >= elP && data.levels[i].p <= data.levels[0].p) {
                        ctx.lineTo(getX(data.levels[i].t, data.levels[i].p), getY(data.levels[i].p));
                    }
                }
                ctx.closePath();
                ctx.fill();
            }

            // Ponto de Orvalho Td
            ctx.strokeStyle = '#10b981';
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            data.levels.forEach((lvl, i) => {
                const x = getX(lvl.td, lvl.p);
                const y = getY(lvl.p);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();

            // Temperatura T
            ctx.strokeStyle = '#ef4444';
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            data.levels.forEach((lvl, i) => {
                const x = getX(lvl.t, lvl.p);
                const y = getY(lvl.p);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();

            // Trajetória da Parcela
            if (data.mucape > 5) {
                ctx.strokeStyle = parcelMode === 'reversible' ? '#38bdf8' : '#fbbf24';
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 4]);
                ctx.beginPath();
                const sfc = data.levels[0];
                ctx.moveTo(getX(sfc.t, sfc.p), getY(sfc.p));
                const topP = currentCase === '19951224' ? 120 : 200;
                for (let p = sfc.p; p >= topP; p -= 15) {
                    const deltaT = (sfc.p - p) * 0.055;
                    const waterLoad = (parcelMode === 'reversible' && p < 800) ? 2.5 : 0.0;
                    const tp = (sfc.t - deltaT) - waterLoad;
                    ctx.lineTo(getX(tp, p), getY(p));
                }
                ctx.stroke();
                ctx.setLineDash([]);
            }
        }

        function renderHodograph() {
            const canvas = document.getElementById('hodoCanvas');
            const ctx = canvas.getContext('2d');
            const w = canvas.width;
            const h = canvas.height;
            const cx = w / 2;
            const cy = h / 2;
            const scale = 4.8;

            ctx.clearRect(0, 0, w, h);

            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 1;
            ctx.fillStyle = '#64748b';
            ctx.font = '10px monospace';
            [10, 20, 30, 40].forEach(spd => {
                const r = spd * scale;
                ctx.beginPath();
                ctx.arc(cx, cy, r, 0, 2 * Math.PI);
                ctx.stroke();
                ctx.fillText(`${spd} m/s`, cx + r - 25, cy - 4);
            });

            ctx.beginPath();
            ctx.moveTo(15, cy); ctx.lineTo(w - 15, cy);
            ctx.moveTo(cx, 15); ctx.lineTo(cx, h - 15);
            ctx.stroke();

            const data = soundings[currentCase];
            const pts = data.levels.map(l => {
                const rad = (l.dir * Math.PI) / 180;
                const u = -l.spd * Math.sin(rad);
                const v = -l.spd * Math.cos(rad);
                return { x: cx + u * scale, y: cy - v * scale, z: l.z };
            });

            for (let i = 0; i < pts.length - 1; i++) {
                const p1 = pts[i];
                const p2 = pts[i + 1];
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.lineWidth = 3;

                if (p2.z <= 1000) ctx.strokeStyle = '#ef4444';
                else if (p2.z <= 3000) ctx.strokeStyle = '#10b981';
                else if (p2.z <= 6000) ctx.strokeStyle = '#38bdf8';
                else ctx.strokeStyle = '#64748b';
                ctx.stroke();
            }

            const [smU, smV] = data.stormMotion;
            const smX = cx + smU * scale;
            const smY = cy - smV * scale;
            ctx.fillStyle = '#fbbf24';
            ctx.beginPath();
            ctx.arc(smX, smY, 5, 0, 2 * Math.PI);
            ctx.fill();
            ctx.fillText('c', smX + 7, smY + 4);
        }

        function renderBruntVaisala() {
            const canvas = document.getElementById('bruntCanvas');
            const ctx = canvas.getContext('2d');
            const w = canvas.width;
            const h = canvas.height;
            const data = soundings[currentCase];

            ctx.clearRect(0, 0, w, h);

            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(40, 10); ctx.lineTo(40, h - 25);
            ctx.lineTo(w - 15, h - 25);
            ctx.stroke();

            ctx.fillStyle = '#64748b';
            ctx.font = '9px monospace';
            ctx.fillText('0', 40, h - 10);
            ctx.fillText('2×10⁻⁴', 130, h - 10);
            ctx.fillText('4×10⁻⁴ s⁻²', 240, h - 10);

            const g = 9.80665;
            const n2Pts = [];
            for (let i = 0; i < data.levels.length - 1; i++) {
                const l1 = data.levels[i];
                const l2 = data.levels[i + 1];
                const dz = l2.z - l1.z;
                if (dz > 20 && l2.z <= 8000) {
                    const dth = l2.thtv - l1.thtv;
                    const thMid = 0.5 * (l1.thtv + l2.thtv);
                    const n2 = Math.max(-0.5e-4, (g / thMid) * (dth / dz));
                    n2Pts.push({ n2: n2, z: 0.5 * (l1.z + l2.z) });
                }
            }

            ctx.strokeStyle = '#c084fc';
            ctx.lineWidth = 2;
            ctx.beginPath();
            n2Pts.forEach((pt, i) => {
                const x = 40 + (pt.n2 / 5e-4) * (w - 70);
                const y = (h - 25) - (pt.z / 8000) * (h - 40);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();
        }

        window.onload = () => {
            loadCase(currentCase);
        };
    </script>
</body>
</html>
'''

def main():
    final_html = HTML_TEMPLATE
    with open('index.html', 'w', encoding='utf-8') as f_out:
        f_out.write(final_html)

    print(f"Successfully generated index.html without the removed tabs! File size: {len(final_html):,} bytes")

if __name__ == '__main__':
    main()
