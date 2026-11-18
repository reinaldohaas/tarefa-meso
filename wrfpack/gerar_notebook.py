# -*- coding: utf-8 -*-
"""Gera WRF_VLab_tarefa.ipynb (Seminário Final, Parte 2, no VLab da UFSC).

Uso: uv run --with nbformat python wrfpack/gerar_notebook.py
O notebook usa wrfpack/hidrometeoros.py nas etapas de diagnóstico e visualização.
"""
import os

import nbformat as nbf

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, '..', 'WRF_VLab_tarefa.ipynb')
ENUNCIADO = 'https://github.com/reinaldohaas/tarefa-meso/blob/master/TAREFA_WRF_HIDROMETEOROS.md'

celulas = []


def md(texto):
    celulas.append(nbf.v4.new_markdown_cell(texto.strip('\n')))


def code(texto, tags=()):
    c = nbf.v4.new_code_cell(texto.strip('\n'))
    if tags:
        c.metadata['tags'] = list(tags)
    celulas.append(c)


md(f"""
# Seminário Final (Parte 2): WRF no VLab

**FSC7116 Meteorologia de Mesoescala (UFSC)**, Prof. Dr. Reinaldo Haas. Entrega no Moodle até **5/12/2026**.

Este notebook leva você por todas as etapas da tarefa no VLab: dados do ERA5, domínios e WPS, `namelist.input`, `real.exe` e `wrf.exe`, diagnóstico da água super-resfriada, do graupel e do granizo, corte vertical, refletividade contra o radar, figuras 3D de cada hidrometeoro, página no GitHub, `RELATORIO_RODADA.md` e roteiro da apresentação.

O enunciado completo, com os critérios de avaliação, está em [TAREFA_WRF_HIDROMETEOROS.md]({ENUNCIADO}).

**Como usar**
- No VLab, abra um terminal do JupyterLab e baixe o repositório na sua pasta:
  `git clone https://github.com/reinaldohaas/tarefa-meso.git`
- Abra `tarefa-meso/WRF_VLab_tarefa.ipynb` e rode **uma célula por vez**, lendo antes o que ela faz.
- As células que começam com `%%bash` são os mesmos comandos que você digitaria no terminal. Se preferir, copie e rode no terminal.
- Onde aparece `PREENCHA`, a decisão é sua e deve ser justificada no relatório. O notebook confere os requisitos mínimos, mas não escolhe a física por você.
- O modelo não precisa acertar o evento. O que conta é investigar e explicar por que ele divergiu da observação.

A Parte 1 (sondagens) tem o seu próprio notebook: `Seminario_plot_sounding_revisado.ipynb`, que também roda no VLab.
""")

md("""
## 1. Caminhos e ambiente

Ajuste os caminhos do WRF, do WPS e dos dados geográficos estáticos (`geog`) do VLab. Se não souber onde estão, pergunte ao professor. A pasta `TRABALHO` é onde ficam os seus dados e rodadas; ela precisa de alguns GB livres.
""")
code("""
import os, glob, json, shutil, subprocess, pathlib, datetime as dt

WRF_DIR  = os.environ.get('WRF_DIR',  '/home/jovyan/privado/WRF-Chem/WRF')        # tem main/ ou run/ com real.exe e wrf.exe
WPS_DIR  = os.environ.get('WPS_DIR',  '/home/jovyan/privado/WRF-Chem/WPS')        # tem geogrid.exe, ungrib.exe, metgrid.exe
GEOG_DIR = os.environ.get('GEOG_DIR', '/home/jovyan/privado/gis4wrf/datasets/geog')
TRABALHO = pathlib.Path(os.environ.get('TRABALHO', '~/fsc7116_wrf')).expanduser()
NP = 4                                   # processadores para o MPI (veja o resultado de nproc abaixo)
LANCADOR = 'mpirun -np {np}'             # troque se o WRF do VLab usar outro lançador

REPO = pathlib.Path.cwd()                # pasta do tarefa-meso (onde está este notebook)
for p in ('dados/era5', 'wps', 'rodadas', 'site/figuras', 'site/3d'):
    (TRABALHO / p).mkdir(parents=True, exist_ok=True)

def acha(pasta, nome):
    for sub in ('main', 'run', '', 'geogrid/src', 'ungrib/src', 'metgrid/src'):
        f = pathlib.Path(pasta) / sub / nome
        if f.exists():
            return f
    return None

EXE = {n: acha(WRF_DIR, n) for n in ('real.exe', 'wrf.exe')}
EXE.update({n: acha(WPS_DIR, n) for n in ('geogrid.exe', 'ungrib.exe', 'metgrid.exe')})
for n, f in EXE.items():
    print(f'{n:12s}', f if f else 'NÃO ENCONTRADO')
print('geog:', GEOG_DIR, 'ok' if pathlib.Path(GEOG_DIR).exists() else 'NÃO ENCONTRADO')
print('trabalho:', TRABALHO)
""")
code("""
%%bash -s "{EXE['real.exe']}" "{EXE['wrf.exe']}" "{TRABALHO}"
# Bibliotecas que faltam aos executáveis (nenhuma linha "not found" é o esperado), processadores e espaço livre
for f in "$1" "$2"; do echo "== $f"; ldd "$f" 2>&1 | grep -i "not found" || echo "bibliotecas ok"; done
echo "processadores: $(nproc)"
df -h "$3" | tail -1
""")
code("""
# Bibliotecas de Python usadas na análise (instala só o que faltar, na sua conta)
import importlib, sys
faltam = [p for p in ('numpy', 'xarray', 'netCDF4', 'matplotlib', 'plotly', 'cdsapi')
          if importlib.util.find_spec(p) is None]
if faltam:
    print('instalando:', faltam)
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', '-q'] + faltam, check=True)
sys.path.insert(0, str(REPO / 'wrfpack'))
import numpy as np, matplotlib.pyplot as plt
import hidrometeoros as H
print('ok')
""")

md("""
## 2. O caso

Retome o evento da Parte 1. O início da rodada deve ficar pelo menos 6 h antes da convecção; o fim, depois do evento.
""")
code("""
CASO = dict(
    nome      = 'PREENCHA',              # ex.: 'Granizo em Biguaçu'
    descricao = 'PREENCHA',              # o que foi observado e as fontes (Defesa Civil, radar, satélite)
    inicio    = 'PREENCHA',              # 'AAAA-MM-DD_HH:00:00' (UTC)
    fim       = 'PREENCHA',              # 'AAAA-MM-DD_HH:00:00' (UTC)
    lat       = None,                    # centro do evento, graus (sul negativo)
    lon       = None,                    # graus (oeste negativo)
)
assert 'PREENCHA' not in CASO.values() and None not in CASO.values(), 'preencha todos os campos do CASO'
INI = dt.datetime.strptime(CASO['inicio'], '%Y-%m-%d_%H:%M:%S')
FIM = dt.datetime.strptime(CASO['fim'], '%Y-%m-%d_%H:%M:%S')
print(CASO['nome'], INI, '->', FIM, f'({(FIM - INI).total_seconds() / 3600:.0f} h)')
""")

md("""
## 3. Domínios

Três domínios com razão 3 e o interno com 3 km ou menos (27/9/3 ou 9/3/1 km). O interno deve ficar centrado no evento, com pelo menos 50 km de folga até a borda. Quanto maior a grade, mais tempo e memória: no VLab, comece pequeno.

Regras que a célula confere: `(e_we - 1)` e `(e_sn - 1)` dos domínios filhos divisíveis por 3, e cada filho a pelo menos 5 pontos da borda do pai.
""")
code("""
DOM = dict(
    dx_d01 = None,                       # metros, ex.: 9000 (d02 = dx/3, d03 = dx/9)
    e_we   = [None, None, None],         # pontos oeste-leste de d01, d02, d03
    e_sn   = [None, None, None],         # pontos sul-norte
    i_parent_start = [1, None, None],    # posição do canto sudoeste de cada filho na grade do pai
    j_parent_start = [1, None, None],
    e_vert = 50,                         # níveis verticais (decisão sua: justifique)
)
assert None not in [DOM['dx_d01']] + DOM['e_we'] + DOM['e_sn'] + DOM['i_parent_start'] + DOM['j_parent_start'], 'preencha o DOM'
dx = [DOM['dx_d01'] / 3 ** k for k in range(3)]
assert dx[2] <= 3000, f'o domínio interno tem {dx[2]:.0f} m: precisa de 3 km ou menos'
for k in (1, 2):
    assert (DOM['e_we'][k] - 1) % 3 == 0 and (DOM['e_sn'][k] - 1) % 3 == 0, f'd0{k+1}: e_we-1 e e_sn-1 devem ser múltiplos de 3'
    assert DOM['i_parent_start'][k] >= 5 and DOM['j_parent_start'][k] >= 5, f'd0{k+1} encostado na borda do pai'
    assert DOM['i_parent_start'][k] + (DOM['e_we'][k] - 1) // 3 <= DOM['e_we'][k - 1] - 5, f'd0{k+1} passa da borda leste do pai'
    assert DOM['j_parent_start'][k] + (DOM['e_sn'][k] - 1) // 3 <= DOM['e_sn'][k - 1] - 5, f'd0{k+1} passa da borda norte do pai'
for k in range(3):
    print(f'd0{k+1}: {dx[k]/1000:g} km, {DOM["e_we"][k]} x {DOM["e_sn"][k]} = '
          f'{(DOM["e_we"][k]-1)*dx[k]/1000:.0f} x {(DOM["e_sn"][k]-1)*dx[k]/1000:.0f} km')
""")
code("""
def namelist_wps(prefixo='FILE', fg=('FILE',)):
    lista = lambda v: ', '.join(str(x) for x in v)
    datas = lambda d: ', '.join([f"'{d:%Y-%m-%d_%H:%M:%S}'"] * 3)
    return f\"\"\"&share
 wrf_core = 'ARW', max_dom = 3, nocolons = .true.,
 start_date = {datas(INI)},
 end_date   = {datas(FIM)},
 interval_seconds = {INTERVALO_H * 3600},
/
&geogrid
 parent_id = 1, 1, 2,
 parent_grid_ratio = 1, 3, 3,
 i_parent_start = {lista(DOM['i_parent_start'])},
 j_parent_start = {lista(DOM['j_parent_start'])},
 e_we = {lista(DOM['e_we'])},
 e_sn = {lista(DOM['e_sn'])},
 geog_data_res = 'default', 'default', 'default',
 dx = {DOM['dx_d01']}, dy = {DOM['dx_d01']},
 map_proj = 'lambert',
 ref_lat = {CASO['lat']}, ref_lon = {CASO['lon']},
 truelat1 = {CASO['lat']}, truelat2 = {CASO['lat']}, stand_lon = {CASO['lon']},
 geog_data_path = '{GEOG_DIR}/',
/
&ungrib
 out_format = 'WPS', prefix = '{prefixo}',
/
&metgrid
 fg_name = {', '.join(repr(f) for f in fg)},
/
\"\"\"

INTERVALO_H = 3                          # intervalo dos dados de entrada (h): 1, 3 ou 6
WPS = TRABALHO / 'wps'
(WPS / 'namelist.wps').write_text(namelist_wps())
print((WPS / 'namelist.wps').read_text())
""")
code("""
%%bash -s "{WPS}" "{WPS_DIR}" "{EXE['geogrid.exe']}"
# geogrid: grava os geo_em.d0N.nc com relevo e uso do solo
cd "$1"
ln -sf "$2/geogrid" .                    # tabelas GEOGRID.TBL
"$3" > geogrid.log 2>&1
tail -2 geogrid.log; ls -la geo_em.d0*.nc
""")
code("""
# Figura dos domínios (relevo do d01 e contorno de d02 e d03): vai para a página e para o slide 3
import netCDF4
fig, ax = plt.subplots(figsize=(7, 6))
for k, cor in zip((1, 2, 3), ('k', '#c2410c', '#1971c2')):
    g = netCDF4.Dataset(WPS / f'geo_em.d0{k}.nc')
    la, lo = g['XLAT_M'][0], g['XLONG_M'][0]
    if k == 1:
        m = ax.pcolormesh(lo, la, g['HGT_M'][0], cmap='terrain', shading='auto')
        plt.colorbar(m, label='relevo (m)')
    borda = np.concatenate([np.c_[lo[0], la[0]], np.c_[lo[:, -1], la[:, -1]], np.c_[lo[-1, ::-1], la[-1, ::-1]], np.c_[lo[::-1, 0], la[::-1, 0]]])
    ax.plot(borda[:, 0], borda[:, 1], color=cor, lw=2, label=f'd0{k} ({dx[k-1]/1000:g} km)')
ax.plot(CASO['lon'], CASO['lat'], 'r*', ms=14, label='evento')
ax.set_xlabel('longitude'); ax.set_ylabel('latitude'); ax.legend(loc='lower left'); ax.set_title('Domínios do WRF')
fig.savefig(TRABALHO / 'site/figuras/dominios.png', dpi=130, bbox_inches='tight')
""")

md("""
## 4. Dados do ERA5

Você precisa de uma conta gratuita no [Copernicus CDS](https://cds.climate.copernicus.eu) e de aceitar a licença do ERA5 no site. A chave fica no arquivo `~/.cdsapirc` da sua conta no VLab, que **você** cria no terminal, com o conteúdo indicado em *How to API* no site do CDS. Nunca escreva a chave dentro do notebook nem a envie ao GitHub.
""")
code("""
import cdsapi
assert pathlib.Path('~/.cdsapirc').expanduser().exists(), 'crie o ~/.cdsapirc no terminal (veja o texto acima)'
g = netCDF4.Dataset(WPS / 'geo_em.d01.nc')
la, lo = g['XLAT_M'][0], g['XLONG_M'][0]
AREA = [float(np.ceil(la.max())) + 1, float(np.floor(lo.min())) - 1, float(np.floor(la.min())) - 1, float(np.ceil(lo.max())) + 1]  # N, O, S, L
dias = sorted({(INI + dt.timedelta(hours=h)).strftime('%Y-%m-%d') for h in range(0, int((FIM - INI).total_seconds() // 3600) + 1)})
horas = [f'{h:02d}:00' for h in range(0, 24, INTERVALO_H)]
comum = dict(product_type=['reanalysis'], date=dias, time=horas, area=AREA, data_format='grib', download_format='unarchived')
c = cdsapi.Client()
print('área', AREA, 'dias', dias)
c.retrieve('reanalysis-era5-pressure-levels', dict(comum,
    variable=['geopotential', 'temperature', 'relative_humidity', 'specific_humidity', 'u_component_of_wind', 'v_component_of_wind'],
    pressure_level=['1000', '975', '950', '925', '900', '875', '850', '825', '800', '775', '750', '700', '650', '600', '550', '500',
                    '450', '400', '350', '300', '250', '225', '200', '175', '150', '125', '100', '70', '50', '30', '20', '10']),
    str(TRABALHO / 'dados/era5/era5_niveis.grib'))
c.retrieve('reanalysis-era5-single-levels', dict(comum,
    variable=['10m_u_component_of_wind', '10m_v_component_of_wind', '2m_temperature', '2m_dewpoint_temperature',
              'surface_pressure', 'mean_sea_level_pressure', 'skin_temperature', 'sea_surface_temperature',
              'soil_temperature_level_1', 'soil_temperature_level_2', 'soil_temperature_level_3', 'soil_temperature_level_4',
              'volumetric_soil_water_layer_1', 'volumetric_soil_water_layer_2', 'volumetric_soil_water_layer_3',
              'volumetric_soil_water_layer_4', 'land_sea_mask', 'sea_ice_cover', 'snow_depth', 'geopotential']),
    str(TRABALHO / 'dados/era5/era5_superficie.grib'))
""")

md("""
## 5. WPS: ungrib e metgrid

O `ungrib` roda duas vezes (níveis de pressão e superfície, com prefixos diferentes) e o `metgrid` junta os dois. Confira no fim o número de `met_em` por domínio e o `num_metgrid_levels`, que vai para o `namelist.input`.
""")
code("""
(WPS / 'namelist.wps').write_text(namelist_wps('PL'))
""")
code("""
%%bash -s "{WPS}" "{WPS_DIR}" "{EXE['ungrib.exe']}" "{TRABALHO}/dados/era5"
cd "$1"
ln -sf "$2/ungrib/Variable_Tables/Vtable.ECMWF" Vtable
"$2/link_grib.csh" "$4/era5_niveis.grib"
"$3" > ungrib_pl.log 2>&1; tail -1 ungrib_pl.log
""")
code("""
(WPS / 'namelist.wps').write_text(namelist_wps('SFC'))
""")
code("""
%%bash -s "{WPS}" "{WPS_DIR}" "{EXE['ungrib.exe']}" "{TRABALHO}/dados/era5"
cd "$1"
"$2/link_grib.csh" "$4/era5_superficie.grib"
"$3" > ungrib_sfc.log 2>&1; tail -1 ungrib_sfc.log
ls PL:* SFC:* | head -4
""")
code("""
(WPS / 'namelist.wps').write_text(namelist_wps('FILE', ('PL', 'SFC')))
""")
code("""
%%bash -s "{WPS}" "{WPS_DIR}" "{EXE['metgrid.exe']}"
cd "$1"
ln -sf "$2/metgrid" .                    # tabela METGRID.TBL
"$3" > metgrid.log 2>&1; tail -1 metgrid.log
for d in 1 2 3; do echo "d0$d: $(ls met_em.d0$d.* 2>/dev/null | wc -l) met_em"; done
""")
code("""
m = sorted(glob.glob(str(WPS / 'met_em.d01.*')))
NIVEIS_MET = netCDF4.Dataset(m[0]).dimensions['num_metgrid_levels'].size
NIVEIS_SOLO = netCDF4.Dataset(m[0]).dimensions['num_st_layers'].size if 'num_st_layers' in netCDF4.Dataset(m[0]).dimensions else 4
print('num_metgrid_levels =', NIVEIS_MET, '| num_metgrid_soil_levels =', NIVEIS_SOLO, '|', len(m), 'horários')
""")

md("""
## 6. `namelist.input`: a combinação é sua

Escolha e justifique a microfísica, a camada limite, a camada superficial, o solo, a radiação, o cumulus dos domínios externos e o passo de tempo. Pontos de partida para a microfísica (veja a tabela do item 5.3 do enunciado):

| Esquema | `mp_physics` | Graupel | Granizo |
| :--- | :--- | :--- | :--- |
| WSM6 | 6 | sim | com `hail_opt = 1`, na mesma categoria |
| Thompson | 8 | sim | não |
| Morrison | 10 | uma categoria de gelo rimado (granizo se `morr_rimed_ice = 1`, o padrão) | idem |
| Milbrandt-Yau | 9 | sim | sim |
| NSSL 2 momentos | 18 com `nssl_hail_on = 1` | sim | sim |

Opções extras (como `nssl_hail_on`, `nssl_density_on`, `hailcast_opt`) vão em `EXTRA_FISICA`, uma por linha. Passo de tempo: uma regra prática é até 6 × dx (km) segundos no d01; com `use_adaptive_time_step` o modelo ajusta sozinho.

Cada rodada fica numa pasta própria em `rodadas/`, com cópia dos executáveis e do namelist. Para uma nova rodada, troque `RODADA` e rode de novo a partir daqui.
""")
code("""
RODADA = 'r1_PREENCHA'                   # ex.: r1_nssl_ysu
FIS = dict(
    mp_physics         = None,           # mesmo valor nos 3 domínios
    cu_physics         = [None, None, 0],# d03 SEMPRE 0 (convecção explícita)
    bl_pbl_physics     = None,
    sf_sfclay_physics  = None,
    sf_surface_physics = None,
    ra_lw_physics      = None,
    ra_sw_physics      = None,
    radt               = None,           # minutos; costuma ser ~dx do d01 em km
    time_step          = None,           # segundos, no d01
)
EXTRA_FISICA = \"\"\"
\"\"\"                                     # ex.: nssl_hail_on = 1  (uma opção por linha)
EXTRA_DINAMICA = \"\"\"
\"\"\"
SAIDA_MIN = [60, 30, 10]                 # minutos entre saídas de d01, d02, d03 (d03: 10 ou 15)

assert 'PREENCHA' not in RODADA and None not in FIS.values() and None not in FIS['cu_physics'], 'preencha RODADA e FIS'
assert FIS['cu_physics'][2] == 0, 'o domínio interno precisa de cu_physics = 0'
assert SAIDA_MIN[2] <= 15, 'saída do domínio interno a cada 10 ou 15 min'
if FIS['mp_physics'] == 17:
    print('AVISO: mp_physics = 17 é obsoleto na 4.7; use 18 com nssl_2moment_on, nssl_hail_on, nssl_ccn_on e nssl_density_on')
if FIS['mp_physics'] == 18 and 'nssl_hail_on' not in EXTRA_FISICA:
    print('AVISO: NSSL sem nssl_hail_on = 1 não tem categoria de granizo')
if FIS['time_step'] > 6 * DOM['dx_d01'] / 1000:
    print('AVISO: time_step maior que 6 x dx(km): risco de violar o CFL')
""")
code("""
def tres(v):
    return ', '.join(str(x) for x in (v if isinstance(v, (list, tuple)) else [v] * 3))

NAMELIST = f\"\"\"&time_control
 start_year = {tres(INI.year)}, start_month = {tres(INI.month)}, start_day = {tres(INI.day)}, start_hour = {tres(INI.hour)},
 end_year = {tres(FIM.year)}, end_month = {tres(FIM.month)}, end_day = {tres(FIM.day)}, end_hour = {tres(FIM.hour)},
 interval_seconds = {INTERVALO_H * 3600},
 input_from_file = .true., .true., .true.,
 history_interval = {tres(SAIDA_MIN)},
 frames_per_outfile = 1000, 1000, 1000,
 restart = .false., restart_interval = 100000,
 io_form_history = 2, io_form_restart = 2, io_form_input = 2, io_form_boundary = 2,
 nocolons = .true.,
/
&domains
 time_step = {FIS['time_step']},
 max_dom = 3,
 e_we = {tres(DOM['e_we'])}, e_sn = {tres(DOM['e_sn'])}, e_vert = {tres(DOM['e_vert'])},
 p_top_requested = 5000,
 num_metgrid_levels = {NIVEIS_MET}, num_metgrid_soil_levels = {NIVEIS_SOLO},
 dx = {tres(dx)}, dy = {tres(dx)},
 grid_id = 1, 2, 3, parent_id = 0, 1, 2,
 i_parent_start = {tres(DOM['i_parent_start'])}, j_parent_start = {tres(DOM['j_parent_start'])},
 parent_grid_ratio = 1, 3, 3, parent_time_step_ratio = 1, 3, 3,
 feedback = 1, smooth_option = 0,
/
&physics
 mp_physics = {tres(FIS['mp_physics'])},
 cu_physics = {tres(FIS['cu_physics'])},
 bl_pbl_physics = {tres(FIS['bl_pbl_physics'])},
 sf_sfclay_physics = {tres(FIS['sf_sfclay_physics'])},
 sf_surface_physics = {tres(FIS['sf_surface_physics'])},
 ra_lw_physics = {tres(FIS['ra_lw_physics'])}, ra_sw_physics = {tres(FIS['ra_sw_physics'])}, radt = {tres(FIS['radt'])},
 do_radar_ref = 1,
{EXTRA_FISICA.strip()}
/
&dynamics
 w_damping = 1, diff_opt = 2, 2, 2, km_opt = 4, 4, 4,
 damp_opt = 3, zdamp = 5000., 5000., 5000., dampcoef = 0.2, 0.2, 0.2,
 non_hydrostatic = .true., .true., .true.,
{EXTRA_DINAMICA.strip()}
/
&bdy_control
 spec_bdy_width = 5, specified = .true.,
/
&namelist_quilt
 nio_tasks_per_group = 0, nio_groups = 1,
/
\"\"\"
R = TRABALHO / 'rodadas' / RODADA
R.mkdir(parents=True, exist_ok=True)
(R / 'namelist.input').write_text(NAMELIST)
pasta_run = EXE['wrf.exe'].parent.parent / 'run'
for f in pasta_run.iterdir():           # tabelas e dados do WRF (links), sem namelist nem executáveis
    if not f.name.startswith('namelist') and not f.name.endswith('.exe') and not (R / f.name).exists():
        (R / f.name).symlink_to(f)
for n in ('real.exe', 'wrf.exe'):        # cópia local dos executáveis, como pede o enunciado
    shutil.copy2(EXE[n], R / n)
for f in glob.glob(str(WPS / 'met_em.d0*')):
    if not (R / os.path.basename(f)).exists():
        (R / os.path.basename(f)).symlink_to(f)
print(NAMELIST)
print('rodada em', R)
""")

md("""
## 7. `real.exe` e `wrf.exe`

O `real.exe` leva minutos. O `wrf.exe` pode levar horas: ele roda em segundo plano, e a célula seguinte mostra o andamento sem travar o notebook. Se o VLab desligar o JupyterLab por inatividade, a rodada continua; volte e rode a célula do andamento.
""")
code("""
cmd = LANCADOR.format(np=NP)
print(subprocess.run(f'cd {R} && {cmd} ./real.exe', shell=True, capture_output=True, text=True).stdout[-500:])
log = sorted(R.glob('rsl.error.0000'))
print(log[0].read_text()[-300:] if log else 'sem rsl.error.0000')
print('wrfinput/wrfbdy:', sorted(p.name for p in R.glob('wrf[ib]*')))
""")
code("""
# Lança o wrf.exe em segundo plano (guarda o rsl do real.exe numa subpasta antes)
(R / 'rsl_real').mkdir(exist_ok=True)
for f in R.glob('rsl.*'):
    f.rename(R / 'rsl_real' / f.name)
subprocess.Popen(f'cd {R} && nohup {LANCADOR.format(np=NP)} ./wrf.exe > wrf.log 2>&1 &', shell=True)
print('wrf.exe lançado em', dt.datetime.now().strftime('%H:%M'))
""")
code("""
# Andamento: rode de novo quando quiser
import re
log = R / 'rsl.error.0000'
txt = log.read_text() if log.exists() else ''
t = re.findall(r'Timing for main: time (\\S+) on domain\\s+1', txt)
if t:
    agora = dt.datetime.strptime(t[-1], '%Y-%m-%d_%H_%M_%S' if '_' in t[-1][11:] else '%Y-%m-%d_%H:%M:%S')
    print(f'modelo em {agora}: {100 * (agora - INI) / (FIM - INI):.0f}%')
print('SUCCESS' if 'SUCCESS COMPLETE WRF' in txt else 'ainda rodando ou parou: veja o fim do log abaixo')
print(txt[-600:])
""")

md("""
## 8. Diagnóstico da microfísica

Abra o `wrfout` do domínio interno, ache o horário de maior refletividade e calcule a água super-resfriada (SLW = QCLOUD + QRAIN onde T < 0 °C). As funções estão em `wrfpack/hidrometeoros.py`: leia o código para saber exatamente o que cada uma faz.
""")
code("""
WRFOUT = sorted(R.glob('wrfout_d03_*'))[0]          # ou o caminho de outro wrfout
ds = H.abrir(WRFOUT)
HORAS = H.horarios(ds)
DX_KM = ds.attrs['DX'] / 1000
print(WRFOUT.name, '|', len(HORAS), 'horários de', HORAS[0], 'a', HORAS[-1], '| dx =', DX_KM, 'km')
print('hidrometeoros neste wrfout:', H.presentes(ds), '| MP_PHYSICS =', ds.attrs.get('MP_PHYSICS'))
""", tags=('analise',))
code("""
# Horário de maior refletividade numa janela (índices dos horários; ajuste para a hora do evento)
JANELA = (0, len(HORAS))
IT, maximos = H.horario_mais_intenso(ds, *JANELA)
print('mais intenso:', HORAS[IT], f'{max(maximos):.1f} dBZ')
C = H.campos(ds, IT)
C['dx_km'] = DX_KM
import pandas as pd
TAB = pd.DataFrame(H.tabela_maximos(C))
TAB.to_csv(TRABALHO / 'site/tabela_maximos.csv', index=False)
TAB
""", tags=('analise',))

md("""
## 9. Corte vertical pela célula mais vigorosa

Graupel e granizo sombreados, SLW em verde, W em preto (tracejado: descendente) e as isotermas de 0, −20 e −40 °C. A coluna é a de maior W; troque `J, I` ou a direção se quiser outro corte.
""")
code("""
J, I = H.ponto_mais_forte(C)
print('coluna:', J, I, f"lat {C['lat'][J, I]:.3f} lon {C['lon'][J, I]:.3f}, W máx {C['W'].max():.1f} m/s")
fig, ax = plt.subplots(figsize=(10, 5.5))
H.corte_vertical(C, J, I, DX_KM, meia_largura_km=40, direcao='oeste-leste', ax=ax)
ax.set_title(f'{CASO["nome"]}: corte vertical, {HORAS[IT]} UTC', fontsize=11)
fig.savefig(TRABALHO / 'site/figuras/corte_vertical.png', dpi=130, bbox_inches='tight')
""", tags=('analise',))

md("""
## 10. Refletividade simulada contra a observação

Ponha numa pasta a imagem do radar (ou do GOES) do mesmo horário e indique o caminho em `OBS_IMG`. Diga, no relatório, quanto o modelo errou em lugar (km) e em hora.
""")
code("""
OBS_IMG = None                           # ex.: TRABALHO / 'obs/radar_2026-08-29_2220.png'
Z = H.refl_composta(ds, IT)
fig, axs = plt.subplots(1, 2 if OBS_IMG else 1, figsize=(13 if OBS_IMG else 7, 5.5), squeeze=False)
m = axs[0, 0].pcolormesh(C['lon'], C['lat'], np.ma.masked_less(Z, 5), cmap='turbo', vmin=0, vmax=70, shading='auto')
axs[0, 0].contour(C['lon'], C['lat'], Z, levels=[50], colors='k', linewidths=1)
axs[0, 0].contour(C['lon'], C['lat'], C['hgt'], levels=[0.001], colors='0.4', linewidths=0.6)   # linha de costa aproximada
axs[0, 0].plot(CASO['lon'], CASO['lat'], 'k*', ms=12)
plt.colorbar(m, ax=axs[0, 0], label='REFL_10CM máxima na coluna (dBZ); contorno: 50 dBZ')
axs[0, 0].set_title(f'WRF {HORAS[IT]} UTC')
if OBS_IMG:
    axs[0, 1].imshow(plt.imread(OBS_IMG)); axs[0, 1].axis('off'); axs[0, 1].set_title('Observação')
fig.savefig(TRABALHO / 'site/figuras/refletividade.png', dpi=130, bbox_inches='tight')
""", tags=('analise',))

md("""
## 11. Hidrometeoros em 3D

Exemplo do tipo de visualização esperado: [Supercell on a Carousel (2005), de Leigh Orf](https://www.youtube.com/watch?v=2Lr9ajlyrPQ), uma supercélula simulada vista em 3D girando em torno da tempestade. A sua não precisa ter esse acabamento, mas cada hidrometeoro deve aparecer separado e na altura certa.

Uma figura interativa por hidrometeoro (o mesmo ponto de vista e as mesmas cores) e uma com todos juntos, gravadas em HTML para a página do GitHub. Abra cada HTML no navegador, gire até a vista que mostra melhor a estrutura e salve a imagem (ícone de câmera) para os slides 5 e 6. Informe na legenda o limiar e o exagero vertical.

`PASSO = 2` usa um ponto a cada dois e deixa o arquivo menor; `LIMIARES` muda o valor de cada isosuperfície (g/kg).
""")
code("""
PASSO, EXAGERO, MEIA = 2, 3.0, 40.0
LIMIARES = {}                            # ex.: {'QGRAUP': 1.0, 'SLW': 0.5}
nomes = [q for q in H.HIDROMETEOROS if q in C]
for q in nomes:
    H.isosuperficies_html(C, J, I, DX_KM, str(TRABALHO / f'site/3d/{q}.html'), nomes=[q], passo=PASSO, exagero=EXAGERO,
                          meia_largura_km=MEIA, limiares=LIMIARES, titulo=f'{H.HIDROMETEOROS[q][0]}, {HORAS[IT]} UTC')
fig3d = H.isosuperficies_html(C, J, I, DX_KM, str(TRABALHO / 'site/3d/todos.html'), nomes=nomes, passo=PASSO,
                              exagero=EXAGERO, meia_largura_km=MEIA, limiares=LIMIARES, titulo=f'todos, {HORAS[IT]} UTC')
print('HTML em', TRABALHO / 'site/3d')
fig3d
""", tags=('analise',))
code("""
# Para o ParaView: grade com a altura real (km), um campo por hidrometeoro. No VAPOR, abra o wrfout direto (Import > WRF-ARW).
tam = H.gravar_vts(C, str(TRABALHO / f'd03_{HORAS[IT][:16].replace(":", "")}.vts'), passo=2)
print(f'{tam / 1e6:.0f} MB')
""", tags=('analise',))

md("""
## 12. Página no GitHub

A célula abaixo monta `site/index.html` com as figuras, as figuras 3D e a tabela. Depois **copie a pasta `site/` para o seu repositório** (`fsc7116-wrf-<seu-nome>`), junto com `namelist.wps`, os `namelist.input` de cada rodada e o `RELATORIO_RODADA.md`, e ative o GitHub Pages (Settings > Pages > branch `main`, pasta `/`).

Edite o texto da página: os parágrafos marcados com `PREENCHA` são seus.
""")
code("""
def pagina():
    linhas_tab = ''.join(f"<tr><td>{r.nome}</td><td>{r.max_g_kg}</td><td>{r.altura_km}</td><td>{r.temperatura_C}</td></tr>"
                         for r in TAB.itertuples())
    abas = ''.join(f'<a href="3d/{q}.html">{H.HIDROMETEOROS[q][0]}</a> · ' for q in nomes) + '<a href="3d/todos.html">todos</a>'
    return f\"\"\"<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{CASO['nome']}: WRF</title>
<style>:root{{--fundo:#fff;--texto:#1d2733;--linha:#d8dee6}}
@media (prefers-color-scheme:dark){{:root{{--fundo:#11161c;--texto:#e6ebf0;--linha:#2c3640}}}}
body{{background:var(--fundo);color:var(--texto);font:16px/1.6 system-ui,sans-serif;max-width:980px;margin:auto;padding:16px}}
img{{max-width:100%;border:1px solid var(--linha);border-radius:6px}} table{{border-collapse:collapse}}
td,th{{border:1px solid var(--linha);padding:4px 10px;text-align:right}} iframe{{width:100%;height:560px;border:1px solid var(--linha)}}</style>
</head><body>
<h1>{CASO['nome']}</h1><p>{CASO['descricao']}</p>
<p>FSC7116 Meteorologia de Mesoescala, UFSC. Simulação WRF de {INI:%d/%m/%Y %H} UTC a {FIM:%d/%m/%Y %H} UTC.</p>
<h2>Domínios e configuração</h2><img src="figuras/dominios.png" alt="Domínios do WRF">
<p>PREENCHA: a combinação da namelist.input e a justificativa de cada escolha.</p>
<h2>Hidrometeoros em 3D ({HORAS[IT]} UTC)</h2><p>{abas}</p><iframe src="3d/todos.html" title="Hidrometeoros em 3D"></iframe>
<h2>Corte vertical</h2><img src="figuras/corte_vertical.png" alt="Corte vertical pela célula mais vigorosa">
<h2>Máximo de cada hidrometeoro</h2><table><tr><th>hidrometeoro</th><th>máx (g/kg)</th><th>altura (km)</th><th>T (°C)</th></tr>{linhas_tab}</table>
<h2>Comparação com a observação</h2><img src="figuras/refletividade.png" alt="Refletividade simulada e observada">
<h2>Deficiências do modelo</h2><p>PREENCHA</p>
<h2>Conclusões</h2><p>PREENCHA</p>
<p>Namelists, scripts e relatório neste repositório. Apresentação: <a href="apresentacao/">PDF</a>.</p>
</body></html>\"\"\"

(TRABALHO / 'site/index.html').write_text(pagina(), encoding='utf-8')
print('página em', TRABALHO / 'site/index.html')
""", tags=('analise',))
md("""
Comandos para o seu repositório (rode no **terminal**; o `git push` pede o seu usuário e um *token* do GitHub, que você digita lá e nunca escreve no notebook):

```bash
cd ~
git clone https://github.com/<seu-usuario>/fsc7116-wrf-<seu-nome>.git
cd fsc7116-wrf-<seu-nome>
cp -r ~/fsc7116_wrf/site/* .
mkdir -p wps rodadas && cp ~/fsc7116_wrf/wps/namelist.wps wps/
for r in ~/fsc7116_wrf/rodadas/*/; do mkdir -p rodadas/$(basename $r); cp $r/namelist.input rodadas/$(basename $r)/; done
cp ~/fsc7116_wrf/RELATORIO_RODADA.md .
printf 'wrfout_*\\nwrfrst_*\\nmet_em*\\n*.grib\\n*.nc\\n*.vts\\n' > .gitignore
git add . && git commit -m "Seminário Final: WRF" && git push
```
""")

md("""
## 13. `RELATORIO_RODADA.md`

A célula preenche o que está no namelist e no log; o resto é seu.
""")
code("""
txt = (R / 'rsl.error.0000').read_text() if (R / 'rsl.error.0000').exists() else ''
rel = f\"\"\"# Rodada {RODADA}

- Caso: {CASO['nome']}; {CASO['descricao']}
- Ambiente: VLab (UFSC); WRF em {WRF_DIR}; processadores: {NP}
- Dados de entrada: ERA5, a cada {INTERVALO_H} h
- Domínios: {', '.join(f'{d/1000:g} km' for d in dx)}; pontos {DOM['e_we']} x {DOM['e_sn']}; {DOM['e_vert']} níveis
- Física: mp_physics = {FIS['mp_physics']}; cu_physics = {FIS['cu_physics']}; bl_pbl_physics = {FIS['bl_pbl_physics']};
  sf_sfclay_physics = {FIS['sf_sfclay_physics']}; sf_surface_physics = {FIS['sf_surface_physics']};
  ra_lw/ra_sw = {FIS['ra_lw_physics']}/{FIS['ra_sw_physics']}; time_step = {FIS['time_step']} s
- Opções extras: {' '.join(EXTRA_FISICA.split()) or 'nenhuma'}
- Terminou com SUCCESS? {'sim' if 'SUCCESS COMPLETE WRF' in txt else 'não'}
- Justificativa de cada escolha: PREENCHA
- Problemas e como resolveu: PREENCHA
- Resultado em uma frase: PREENCHA
- Diferença para a rodada anterior e por quê: PREENCHA
\"\"\"
(TRABALHO / 'RELATORIO_RODADA.md').write_text(rel, encoding='utf-8')
print(rel)
""")

md("""
## 14. Apresentação (20 minutos)

| Tempo | Slides | Conteúdo | Figura deste notebook |
| :--- | :--- | :--- | :--- |
| 00 a 03 min | 1 e 2 | o caso severo da Parte 1, radar ou satélite, relatos | (suas imagens da observação) |
| 03 a 06 min | 3 e 4 | domínios e a combinação da `namelist.input` | `figuras/dominios.png` |
| 06 a 10 min | 5 e 6 | hidrometeoros em 3D e corte vertical | `3d/*.html` (captura) e `figuras/corte_vertical.png` |
| 10 a 14 min | 7 e 8 | `REFL_10CM` contra o radar ou o satélite | `figuras/refletividade.png` |
| 14 a 17 min | 9 | deficiências: onde o modelo errou e por quê | tabela de máximos |
| 17 a 20 min | 10 | conclusões e o link da página no GitHub | |

Envie ao Moodle os slides (PowerPoint ou PDF), o `RELATORIO_RODADA.md` e o link do repositório e da página, antes da sessão. Teste os slides nos computadores do Departamento de Física.
""")

nb = nbf.v4.new_notebook()
nb.cells = celulas
nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
nb.metadata['language_info'] = {'name': 'python'}
nbf.validate(nb)
nbf.write(nb, SAIDA)
print('->', os.path.abspath(SAIDA), len(celulas), 'células')
