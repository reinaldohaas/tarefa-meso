# Rodada r1_milbrandt_yau_2km

- **Caso:** Evento severo de granizo no Norte da Ilha de Santa Catarina (Florianópolis e Biguaçu, SC) em 29/08/2026, com relatos de superfície entre 22:00 e 23:00 UTC (19:00–20:00 BRT), topos frios no GOES-19 de $-62,9\text{ }^\circ\text{C}$ às 22:20 UTC e núcleo severo no radar do Morro da Igreja entre 22:16 e 22:36 UTC.
- **Ambiente:** Computador pessoal Windows (`C:\gis4wrf\projects\granizo`); WRF-ARW V4.2.2 (`WRF-4.2-mpi`); processadores: 6 núcleos físicos via Microsoft MPI (`mpiexec -n 6`).
- **Dados de entrada:** Reanálise ERA5 (Copernicus CDS, 37 níveis de pressão e superfície), a cada 1 h (`interval_seconds = 3600`), de `2026-08-29_12:00:00` a `2026-08-30_00:00:00` UTC (10 h de *spin-up* antes do evento severo).
- **Domínios:** Aninhamento triplo bidirecional (`feedback = 1`), razão 1:3, projeção Lambert Conformal. O d01 é centrado em $-28,49^\circ\text{S}, -49,69^\circ\text{W}$ e o d02 também é deslocado para sudoeste, para que a Ilha fique a 2/3 da largura para leste e para norte (regra dos 2/3) e a área a montante, de onde vem a convecção, fique dentro da grade; o d03 é centrado na Ilha:
  - `d01`: $\Delta x = 18\text{ km}$, $38 \times 38$ pontos ($666 \times 666\text{ km}$)
  - `d02`: $\Delta x = 6\text{ km}$, $49 \times 49$ pontos ($288 \times 288\text{ km}$)
  - `d03`: $\Delta x = 2\text{ km}$, $61 \times 61$ pontos ($120 \times 120\text{ km}$, centrado na Ilha)
  - Níveis verticais: `e_vert = 45` níveis $\eta$, topo em `p_top_requested = 5000` Pa ($50\text{ hPa}$).
- **Física e justificativa (uma linha cada):**
  - **Microfísica (`mp_physics = 9`, Milbrandt-Yau 2 momentos nos 3 domínios):** Esquema de dois momentos com 6 classes de hidrometeoros que resolve explicitamente e em categorias separadas o graupel (`QGRAUP`, `QNGRAUPEL`, menor densidade) e o granizo (`QHAIL`, `QNHAIL`, alta densidade), além de diagnóstico `hailcast_opt = 0, 0, 1` e refletividade Rayleigh/Mie `do_radar_ref = 1` (`REFL_10CM`).
  - **Cumulus (`cu_physics = 1, 1, 0`):** Kain-Fritsch nos domínios externos (`d01` de 18 km e `d02` de 6 km) e **desligado (`cu_physics = 0`) no domínio interno `d03` (2 km)** para permitir convecção explícita na escala de resolução de tempestades.
  - **Camada limite planetária (`bl_pbl_physics = 1`, YSU):** Esquema não-local (Yonsei University) com entranhamento explícito no topo da CLP, adequado para mistura pré-convectiva diurna.
  - **Camada superficial e solo (`sf_sfclay_physics = 1`, `sf_surface_physics = 2`):** Similaridade de Monin-Obukhov (MM5) acoplada ao modelo de superfície terrestre Noah LSM de 4 camadas.
  - **Radiação (`ra_lw_physics = 4`, `ra_sw_physics = 4`, `radt = 15` min):** Esquema RRTMG de ondas longas e curtas com interação óptica com as frações de nuvem e gelo (`icloud = 1`).
  - **Passo de tempo:** Passo adaptativo (`use_adaptive_time_step = .true.`) com `target_cfl = 1.2, 1.2, 1.2` e `step_to_output_time = .true.`, garantindo estabilidade numérica sem violação de CFL e saídas exatas a cada 15 min em `d03`.
- **Início, fim e tempo de relógio; terminou com SUCCESS?** Simulação de `2026-08-29_12:00:00` a `2026-08-30_00:00:00` UTC (~13 minutos de tempo de relógio em 6 núcleos); terminou com `sim (SUCCESS COMPLETE WRF)`.
- **Problemas e como resolveu:**
  1. O recorte regional do arquivo GRIB do ERA5 disponível localmente ($21,75^\circ\text{S}$ a $33,00^\circ\text{S}$; $54,50^\circ\text{W}$ a $43,00^\circ\text{W}$) causou erro de valores ausentes (`Missing values encountered in interpolated fields`) no `metgrid.exe` quando `d01` ultrapassava $1200\text{ km}$ de lado; resolvido dimensionando `d01` para $38 \times 38$ pontos com $\Delta x = 18\text{ km}$ ($666\text{ km}$ de lado), inteiramente contido na grade do ERA5.
  2. Com `e_vert = 40` e `dzstretch_s = 1.1`, o `real.exe` acusou `not enough eta levels to reach p_top`; resolvido elevando para `e_vert = 45` níveis verticais.
- **Resultado em uma frase:** No horário analisado (`2026-08-29_12:45:05 UTC`, o de mais graupel e granizo a até 25 km de Jurerê, com a célula sobre a Ilha), o modelo mostrou convecção profunda explícita no domínio de 2 km com coexistência de água super-resfriada (`SLW` máx de `3.77 g/kg`), graupel (`QGRAUP` máx de `4.925 g/kg` a `7.55 km` / `-18.9 °C`) e granizo separado (`QHAIL` máx de `0.501 g/kg` a `4.73 km` / `-1.2 °C`), cerca de 9,5 h antes do granizo observado; na janela observada (22:30 UTC) o eco simulado mais forte ficou a `69.7 km` de Jurerê.
- **Diferença para a rodada anterior e por quê:** Primeira rodada oficial do projeto `granizo` com o esquema Milbrandt-Yau de 2 momentos (`mp_physics = 9`), escolhida especificamente para separar as categorias de graupel (`QGRAUP`) e granizo (`QHAIL`) conforme recomendado na Seção 5.3 do enunciado.

---

## Tabela de Máximos dos Hidrometeoros no Domínio Interno (`d03`, `2026-08-29_12:45:05 UTC`)

| Variável | Hidrometeoro | Máximo (g/kg) | Altura Real $z$ (km MSL) | Temperatura ($^\circ\text{C}$) | Pressão (hPa) | Limiar 3D (g/kg) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `QCLOUD` | Nuvem | 3.761 | 5.68 | -5.7 | 509.6 | 0.1 |
| `QRAIN` | Chuva | 0.422 | 3.43 | 6.0 | 674.9 | 0.5 |
| `QICE` | Cristais de Gelo | 0.564 | 9.89 | -36.6 | 287.7 | 0.05 |
| `QSNOW` | Neve | 0.319 | 9.89 | -36.5 | 287.8 | 0.1 |
| `QGRAUP` | Graupel | 4.925 | 7.55 | -18.9 | 398.4 | 0.5 |
| `QHAIL` | Granizo | 0.501 | 4.73 | -1.2 | 575.0 | 0.1 |
| `SLW` | Água Super-resfriada ($T < 0\text{ }^\circ\text{C}$) | 3.77 | 5.68 | -5.7 | 509.6 | 0.2 |
