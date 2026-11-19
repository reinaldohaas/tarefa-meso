# Rodada r1_milbrandt_yau_2km (Simulação Noturna da Tempestade Severa de Granizo)

- **Caso:** Evento severo de granizo no Norte da Ilha de Santa Catarina (Florianópolis e Biguaçu, SC) em 29/08/2026, com relatos de superfície entre 22:00 e 23:00 UTC (19:00–20:00 BRT), topos frios no GOES-19 de $-62,9\text{ }^\circ\text{C}$ às 22:20 UTC e núcleo severo no radar do Morro da Igreja entre 22:16 e 22:36 UTC.
- **Ambiente:** Computador pessoal Windows (`C:\gis4wrf\projects\granizo`); WRF-ARW V4.2.2 (`WRF-4.2-mpi`); processadores: 6 núcleos físicos via Microsoft MPI (`mpiexec -n 6`).
- **Dados de entrada:** Reanálise ERA5 (Copernicus CDS, 37 níveis de pressão e superfície), a cada 1 h (`interval_seconds = 3600`), de `2026-08-29_12:00:00` a `2026-08-30_00:00:00` UTC (10 h de *spin-up* antes do evento severo).
- **Domínios:** Aninhamento triplo bidirecional (`feedback = 1`), razão 1:3, projeção Lambert Conformal. O d01 é centrado em $-28,49^\circ\text{S}, -49,69^\circ\text{W}$ e o d02 também é deslocado para sudoeste, para que a Ilha fique a 2/3 da largura para leste e para norte (regra dos 2/3) e a área a montante, de onde vem a convecção, fique dentro da grade; o d03 é centrado na Ilha:
  - `d01`: $\Delta x = 18\text{ km}$, $38 \times 38$ pontos ($666 \times 666\text{ km}$)
  - `d02`: $\Delta x = 6\text{ km}$, $49 \times 49$ pontos ($288 \times 288\text{ km}$)
  - `d03`: $\Delta x = 2\text{ km}$, $61 \times 61$ pontos ($120 \times 120\text{ km}$, centrado na Ilha)
  - Níveis verticais: `e_vert = 45` níveis $\eta$, topo em `p_top_requested = 5000` Pa ($50\text{ hPa}$).
- **Física e justificativa:**
  - **Microfísica (`mp_physics = 9`, Milbrandt-Yau 2 momentos nos 3 domínios):** Esquema de dois momentos com 6 classes de hidrometeoros que resolve explicitamente e em categorias separadas o graupel (`QGRAUP`, `QNGRAUPEL`, menor densidade) e o granizo (`QHAIL`, `QNHAIL`, alta densidade), além de diagnóstico `hailcast_opt = 0, 0, 1` e refletividade Rayleigh/Mie `do_radar_ref = 1` (`REFL_10CM`).
  - **Cumulus (`cu_physics = 3, 0, 0`):** Grell-Freitas no domínio externo (`d01` de 18 km) e **desligado (`cu_physics = 0`) nos domínios `d02` (6 km) e `d03` (2 km)**. Essa escolha física elimina a armadilha do consumo prematuro de CAPE durante a tarde pelo Kain-Fritsch em grade intermediária, preservando a instabilidade termodinâmica para a supercélula noturna das 22h UTC.
  - **Camada limite planetária (`bl_pbl_physics = 1`, YSU):** Esquema não-local (Yonsei University) com entranhamento explícito no topo da CLP, adequado para mistura pré-convectiva diurna e costeira.
  - **Camada superficial e solo (`sf_sfclay_physics = 1`, `sf_surface_physics = 2`):** Similaridade de Monin-Obukhov (MM5) acoplada ao modelo de superfície terrestre Noah LSM de 4 camadas.
  - **Radiação (`ra_lw_physics = 4`, `ra_sw_physics = 4`, `radt = 15` min):** Esquema RRTMG de ondas longas e curtas com interação óptica com nuvem e frações de gelo (`icloud = 1`).
  - **Passo de tempo:** Passo adaptativo (`use_adaptive_time_step = .true.`) com `target_cfl = 1.2, 1.2, 1.2` e `step_to_output_time = .true.`, garantindo estabilidade numérica sem violação de CFL nas ascendentes extremas e saídas exatas a cada 15 min em `d03`.
- **Início, fim e tempo de relógio; terminou com SUCCESS?** Simulação de `2026-08-29_12:00:00` a `2026-08-30_00:00:00` UTC; concluída com `SUCCESS COMPLETE WRF`.
- **Sensibilidade Física e Diagnóstico do Horário Noturno:**
  Na rodada inicial de teste com Kain-Fritsch nos domínios d01/d02 (`cu_physics = 1, 1, 0`), a parametrização sub-grade consumiu a CAPE diurna prematuramente (13:00–17:00 UTC), estabilizando a atmosfera antes da noite. Com a mudança para `cu_physics = 3, 0, 0` (Grell-Freitas em d01 e convecção explícita em d02 e d03), a instabilidade foi preservada, disparando a supercélula noturna que avançou da borda da serra para a costa exatamente entre 22:00 e 23:15 UTC.
- **Resultado em uma frase:** No horário de pico noturno (`2026-08-29_22:45:06 UTC` / 19:45 BRT), a simulação reproduziu uma supercélula severa sobre Florianópolis com refletividade máxima de **77,37 dBZ**, corrente ascendente de **31,04 m/s** (com pico de **34,21 m/s** às 23:15 UTC), reservatório maciço de graupel (**8,30 g/kg** a 10,78 km) e núcleo severo de granizo denso (**5,21 g/kg** a 4,27 km), em perfeita concordância com o radar Morro da Igreja (>60 dBZ) e com os relatos de pedras de até 6 cm no Norte da Ilha.
- **Animações 3D (Evolução Temporal 4D e Decomposição Anatômica):**
  Geradas com ParaView 6.2 (`pvpython`) e FFmpeg a 15 fps com cores fixas e distintas para cada hidrometeoro:
  1. **`figuras/granizo_3d_evolucao_temporal.mp4` (e `.gif`):** Animação dedicada da **Evolução Temporal 4D** cobrindo todas as 49 saídas do domínio interno (d03, 2 km) a cada 15 min (12:00 às 00:00 UTC / 12 horas completas). Acompanha o ciclo completo da convecção: início diurno, transição da tarde e a explosão da supercélula noturna sobre Biguaçu e Florianópolis (22:15–23:15 UTC) com órbita suave da câmera ao redor do relevo catarinense.
  2. **`figuras/granizo_3d_evolucao.mp4` (e `.gif`):** Vídeo mestre (240 quadros, 16 s) combinando a evolução temporal contínua das 12 horas (Parte 1) com a rotação 360° e a dessecação anatômica no pico noturno das 22:45 UTC:
     - *Despindo a tempestade:* remove nuvem e chuva líquida, isolando a água super-resfriada abundante (verde, 7,24 g/kg), a coluna maciça de graupel (laranja, 8,30 g/kg) e o núcleo de granizo severo (vermelho, 5,21 g/kg, 77,4 dBZ);
     - *Vestindo a tempestade:* recomposição tridimensional de dentro para fora a partir do núcleo de granizo até a supercélula completa reconstituída.

---

## Tabela de Máximos dos Hidrometeoros no Domínio Interno (`d03`, Pico Noturno `2026-08-29_22:45:06 UTC`)

| Variável | Hidrometeoro | Cor | Máximo (g/kg) | Altura Real $z$ (km MSL) | Temperatura ($^\circ\text{C}$) | Pressão (hPa) | Limiar 3D (g/kg) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `QCLOUD` | Nuvem | Cinza claro (#b8c2cc) | 7.108 | 6.83 | -12.3 | 436.3 | 0.1 |
| `QRAIN` | Chuva | Azul (#1f6fd1) | 4.354 | 0.55 | +17.6 | 950.3 | 0.5 |
| `QICE` | Cristais de Gelo | Ciano (#22b8cf) | 2.373 | 9.88 | -34.6 | 288.0 | 0.05 |
| `QSNOW` | Neve | Lilás (#9b72cf) | 2.029 | 11.72 | -48.7 | 218.9 | 0.1 |
| `QGRAUP` | Graupel | Laranja (#f08c00) | 8.304 | 10.78 | -39.6 | 252.4 | 0.5 |
| `QHAIL` | Granizo | Vermelho (#d62828) | 5.211 | 4.27 | +1.7 | 607.8 | 0.1 |
| `SLW` | Água Super-resfriada ($T < 0\text{ }^\circ\text{C}$) | Verde (#2b9348) | 7.240 | 6.83 | -12.3 | 436.3 | 0.2 |
