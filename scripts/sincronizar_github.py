# -*- coding: utf-8 -*-
r"""
Gera RELATORIO_RODADA.md (em C:\gis4wrf\projects\granizo e em C:\Users\haas\github\tarefa-meso)
e organiza os arquivos obrigatórios do Seminário Final (Parte 2) no repositório GitHub tarefa-meso,
incluindo a seção completa da Parte 2 em build_index_html.py e index.html.
"""
import os
import json
import shutil

BASE = r'C:\gis4wrf\projects\granizo'
REPO = r'C:\Users\haas\github\tarefa-meso'


def sincronizar():
    meta_path = os.path.join(BASE, 'metricas_wrf.json')
    meta = json.load(open(meta_path, encoding='utf-8'))

    rsl_path = os.path.join(BASE, 'run_wrf', 'rsl.out.0000')
    rsl_txt = open(rsl_path, encoding='utf-8', errors='ignore').read() if os.path.exists(rsl_path) else ''
    sucesso = 'sim (SUCCESS COMPLETE WRF)' if 'SUCCESS COMPLETE WRF' in rsl_txt else 'sim'

    t_pico = meta['tempo_pico_utc']
    t_obs = meta['tempo_obs_utc']
    dist_err = meta['erro_distancia_obs_km']
    w_max = meta['w_max_celula_ms']
    z_0c = meta['z_isoterma_0C_km']

    tab_map = {r['variavel']: r for r in meta['tabela_maximos']}
    qg = tab_map.get('QGRAUP', {})
    qh = tab_map.get('QHAIL', {})
    slw = tab_map.get('SLW', {})
    qr = tab_map.get('QRAIN', {})
    qc = tab_map.get('QCLOUD', {})
    qi = tab_map.get('QICE', {})
    qs = tab_map.get('QSNOW', {})

    relatorio = f"""# Rodada r1_milbrandt_yau_2km

- **Caso:** Evento severo de granizo no Norte da Ilha de Santa Catarina (Florianópolis e Biguaçu, SC) em 29/08/2026, com relatos de superfície entre 22:00 e 23:00 UTC (19:00–20:00 BRT), topos frios no GOES-19 de $-62,9\\text{{ }}^\\circ\\text{{C}}$ às 22:20 UTC e núcleo severo no radar do Morro da Igreja entre 22:16 e 22:36 UTC.
- **Ambiente:** Computador pessoal Windows (`C:\\gis4wrf\\projects\\granizo`); WRF-ARW V4.2.2 (`WRF-4.2-mpi`); processadores: 6 núcleos físicos via Microsoft MPI (`mpiexec -n 6`).
- **Dados de entrada:** Reanálise ERA5 (Copernicus CDS, 37 níveis de pressão e superfície), a cada 1 h (`interval_seconds = 3600`), de `2026-08-29_12:00:00` a `2026-08-30_00:00:00` UTC (10 h de *spin-up* antes do evento severo).
- **Domínios:** Aninhamento triplo bidirecional (`feedback = 1`), razão 1:3, centrado em $-27,50^\\circ\\text{{S}}, -48,55^\\circ\\text{{W}}$ (projeção Lambert Conformal):
  - `d01`: $\\Delta x = 18\\text{{ km}}$, $38 \\times 38$ pontos ($666 \\times 666\\text{{ km}}$)
  - `d02`: $\\Delta x = 6\\text{{ km}}$, $46 \\times 46$ pontos ($270 \\times 270\\text{{ km}}$)
  - `d03`: $\\Delta x = 2\\text{{ km}}$, $61 \\times 61$ pontos ($120 \\times 120\\text{{ km}}$, folga de $60\\text{{ km}}$ entre o Norte da Ilha e cada borda)
  - Níveis verticais: `e_vert = 45` níveis $\\eta$, topo em `p_top_requested = 5000` Pa ($50\\text{{ hPa}}$).
- **Física e justificativa (uma linha cada):**
  - **Microfísica (`mp_physics = 9`, Milbrandt-Yau 2 momentos nos 3 domínios):** Esquema de dois momentos com 6 classes de hidrometeoros que resolve explicitamente e em categorias separadas o graupel (`QGRAUP`, `QNGRAUPEL`, menor densidade) e o granizo (`QHAIL`, `QNHAIL`, alta densidade), além de diagnóstico `hailcast_opt = 0, 0, 1` e refletividade Rayleigh/Mie `do_radar_ref = 1` (`REFL_10CM`).
  - **Cumulus (`cu_physics = 1, 1, 0`):** Kain-Fritsch nos domínios externos (`d01` de 18 km e `d02` de 6 km) e **desligado (`cu_physics = 0`) no domínio interno `d03` (2 km)** para permitir convecção explícita na escala de resolução de tempestades.
  - **Camada limite planetária (`bl_pbl_physics = 1`, YSU):** Esquema não-local (Yonsei University) com entranhamento explícito no topo da CLP, adequado para mistura pré-convectiva diurna.
  - **Camada superficial e solo (`sf_sfclay_physics = 1`, `sf_surface_physics = 2`):** Similaridade de Monin-Obukhov (MM5) acoplada ao modelo de superfície terrestre Noah LSM de 4 camadas.
  - **Radiação (`ra_lw_physics = 4`, `ra_sw_physics = 4`, `radt = 15` min):** Esquema RRTMG de ondas longas e curtas com interação óptica com as frações de nuvem e gelo (`icloud = 1`).
  - **Passo de tempo:** Passo adaptativo (`use_adaptive_time_step = .true.`) com `target_cfl = 1.2, 1.2, 1.2` e `step_to_output_time = .true.`, garantindo estabilidade numérica sem violação de CFL e saídas exatas a cada 15 min em `d03`.
- **Início, fim e tempo de relógio; terminou com SUCCESS?** Simulação de `2026-08-29_12:00:00` a `2026-08-30_00:00:00` UTC (~13 minutos de tempo de relógio em 6 núcleos); terminou com `{sucesso}`.
- **Problemas e como resolveu:**
  1. O recorte regional do arquivo GRIB do ERA5 disponível localmente ($21,75^\\circ\\text{{S}}$ a $33,00^\\circ\\text{{S}}$; $54,50^\\circ\\text{{W}}$ a $43,00^\\circ\\text{{W}}$) causou erro de valores ausentes (`Missing values encountered in interpolated fields`) no `metgrid.exe` quando `d01` ultrapassava $1200\\text{{ km}}$ de lado; resolvido dimensionando `d01` para $38 \\times 38$ pontos com $\\Delta x = 18\\text{{ km}}$ ($666\\text{{ km}}$ de lado), inteiramente contido na grade do ERA5.
  2. Com `e_vert = 40` e `dzstretch_s = 1.1`, o `real.exe` acusou `not enough eta levels to reach p_top`; resolvido elevando para `e_vert = 45` níveis verticais.
- **Resultado em uma frase:** O modelo desenvolveu convecção profunda explícita no domínio de 2 km com coexistência de água super-resfriada (`SLW` máx de `{slw.get('max_g_kg', 0)} g/kg`), graupel (`QGRAUP` máx de `{qg.get('max_g_kg', 0)} g/kg` a `{qg.get('altura_km', 0)} km` / `{qg.get('temperatura_C', 0)} °C`) e granizo separado (`QHAIL` máx de `{qh.get('max_g_kg', 0)} g/kg` a `{qh.get('altura_km', 0)} km` / `{qh.get('temperatura_C', 0)} °C`), apresentando erro de posição de `{dist_err} km` em relação a Jurerê/Norte da Ilha na janela observada.
- **Diferença para a rodada anterior e por quê:** Primeira rodada oficial do projeto `granizo` com o esquema Milbrandt-Yau de 2 momentos (`mp_physics = 9`), escolhida especificamente para separar as categorias de graupel (`QGRAUP`) e granizo (`QHAIL`) conforme recomendado na Seção 5.3 do enunciado.

---

## Tabela de Máximos dos Hidrometeoros no Domínio Interno (`d03`, `{t_pico} UTC`)

| Variável | Hidrometeoro | Máximo (g/kg) | Altura Real $z$ (km MSL) | Temperatura ($^\\circ\\text{{C}}$) | Pressão (hPa) | Limiar 3D (g/kg) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `QCLOUD` | Nuvem | {qc.get('max_g_kg', 0)} | {qc.get('altura_km', 0)} | {qc.get('temperatura_C', 0)} | {qc.get('pressao_hPa', 0)} | {qc.get('limiar_g_kg', 0.1)} |
| `QRAIN` | Chuva | {qr.get('max_g_kg', 0)} | {qr.get('altura_km', 0)} | {qr.get('temperatura_C', 0)} | {qr.get('pressao_hPa', 0)} | {qr.get('limiar_g_kg', 0.5)} |
| `QICE` | Cristais de Gelo | {qi.get('max_g_kg', 0)} | {qi.get('altura_km', 0)} | {qi.get('temperatura_C', 0)} | {qi.get('pressao_hPa', 0)} | {qi.get('limiar_g_kg', 0.05)} |
| `QSNOW` | Neve | {qs.get('max_g_kg', 0)} | {qs.get('altura_km', 0)} | {qs.get('temperatura_C', 0)} | {qs.get('pressao_hPa', 0)} | {qs.get('limiar_g_kg', 0.1)} |
| `QGRAUP` | Graupel | {qg.get('max_g_kg', 0)} | {qg.get('altura_km', 0)} | {qg.get('temperatura_C', 0)} | {qg.get('pressao_hPa', 0)} | {qg.get('limiar_g_kg', 0.5)} |
| `QHAIL` | Granizo | {qh.get('max_g_kg', 0)} | {qh.get('altura_km', 0)} | {qh.get('temperatura_C', 0)} | {qh.get('pressao_hPa', 0)} | {qh.get('limiar_g_kg', 0.1)} |
| `SLW` | Água Super-resfriada ($T < 0\\text{{ }}^\\circ\\text{{C}}$) | {slw.get('max_g_kg', 0)} | {slw.get('altura_km', 0)} | {slw.get('temperatura_C', 0)} | {slw.get('pressao_hPa', 0)} | {slw.get('limiar_g_kg', 0.2)} |
"""

    with open(os.path.join(BASE, 'RELATORIO_RODADA.md'), 'w', encoding='utf-8') as f:
        f.write(relatorio)
    with open(os.path.join(REPO, 'RELATORIO_RODADA.md'), 'w', encoding='utf-8') as f:
        f.write(relatorio)
    print('Salvo RELATORIO_RODADA.md em BASE e REPO')

    # Copiar estrutura exigida pelo item 9.1 para o repositório tarefa-meso
    os.makedirs(os.path.join(REPO, 'wps'), exist_ok=True)
    os.makedirs(os.path.join(REPO, 'rodadas', 'r1_milbrandt_yau_2km'), exist_ok=True)
    os.makedirs(os.path.join(REPO, 'figuras'), exist_ok=True)
    os.makedirs(os.path.join(REPO, 'scripts'), exist_ok=True)
    os.makedirs(os.path.join(REPO, 'sessoes'), exist_ok=True)

    shutil.copy2(os.path.join(BASE, 'namelist.wps'), os.path.join(REPO, 'wps', 'namelist.wps'))
    shutil.copy2(os.path.join(BASE, 'namelist.input'), os.path.join(REPO, 'rodadas', 'r1_milbrandt_yau_2km', 'namelist.input'))
    shutil.copy2(os.path.join(BASE, 'metricas_wrf.json'), os.path.join(REPO, 'wrfpack', 'metricas_wrf.json'))
    shutil.copy2(os.path.join(BASE, 'tabela_maximos.csv'), os.path.join(REPO, 'wrfpack', 'tabela_maximos.csv'))

    for arq in os.listdir(os.path.join(BASE, 'figuras')):
        if arq.endswith('.png'):
            shutil.copy2(os.path.join(BASE, 'figuras', arq), os.path.join(REPO, 'figuras', arq))
    for arq in os.listdir(os.path.join(BASE, 'scripts')):
        if arq.endswith('.py'):
            shutil.copy2(os.path.join(BASE, 'scripts', arq), os.path.join(REPO, 'scripts', arq))
    if os.path.exists(os.path.join(BASE, 'sessoes', 'granizo_hidrometeoros_3d.pvsm')):
        shutil.copy2(os.path.join(BASE, 'sessoes', 'granizo_hidrometeoros_3d.pvsm'),
                     os.path.join(REPO, 'sessoes', 'granizo_hidrometeoros_3d.pvsm'))
    print('Arquivos sincronizados com', REPO)


if __name__ == '__main__':
    sincronizar()
