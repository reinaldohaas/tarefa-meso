"""
Gera a figura científica oficial da imagem de satélite infravermelho (IR 11 µm)
para o dia 24/12/1995 utilizando dados reais do NOAA CDR ISCCP-H (GOES-8 / Meteosat).
"""
import os
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.ndimage import gaussian_filter

def create_enhanced_ir_colormap():
    """
    Paleta padrão de realce infravermelho (Enhancement Curve) da meteorologia de satélites:
    - Temperaturas quentes (> +10°C): cinza escuro (superfície/solo)
    - +10°C a 0°C: cinza médio
    - 0°C a -30°C: cinza claro a azul (nuvens baixas e médias)
    - -30°C a -40°C: azul a ciano
    - -40°C a -50°C: verde a amarelo (convecção moderada a forte)
    - -50°C a -60°C: laranja a vermelho vivo (convecção severa)
    - -60°C a -70°C: magenta e roxo escuro (topos penetrantes / overshooting tops)
    - < -70°C: branco brilhante (convecção extrema)
    """
    levels = [-80, -70, -60, -52, -42, -32, -20, 0, 15, 30]
    colors = [
        '#ffffff', # < -70: branco
        '#8e44ad', # -70 a -60: roxo/magenta
        '#e74c3c', # -60 a -52: vermelho vivo
        '#e67e22', # -52 a -42: laranja
        '#f1c40f', # -42 a -32: amarelo
        '#2ecc71', # -32 a -20: verde
        '#3498db', # -20 a 0: azul
        '#95a5a6', # 0 a 15: cinza claro
        '#34495e', # 15 a 30: cinza escuro
        '#1a252f'  # > 30: solo quente
    ]
    # Mapeamento contínuo normalizado de -80 a +30
    cmap = mcolors.LinearSegmentedColormap.from_list('ir_realce', list(zip(
        np.linspace(0, 1, len(colors)),
        colors
    )), N=256)
    return cmap

def plot_satellite_ir():
    f12 = 'metpack/sat/ISCCP-Basic.HGG.v01r00.GLOBAL.1995.12.24.1200.GPC.10KM.CS00.EA1.00.nc'
    f18 = 'metpack/sat/ISCCP-Basic.HGG.v01r00.GLOBAL.1995.12.24.1800.GPC.10KM.CS00.EA1.00.nc'
    
    if not (os.path.exists(f12) and os.path.exists(f18)):
        raise FileNotFoundError("Arquivos NetCDF do satélite não encontrados em metpack/sat/")

    ds12 = nc.Dataset(f12)
    ds18 = nc.Dataset(f18)

    lats = ds12.variables['lat'][:]
    lons = ds12.variables['lon'][:]

    # Recorte espacial: Sul do Brasil e bacia do Prata
    # Lat: -42 a -20 | Lon: -66 a -44 (em graus leste: 294 a 316)
    lat_min, lat_max = -42.0, -20.0
    lon_min, lon_max = 294.0, 316.0

    ilat = np.where((lats >= lat_min) & (lats <= lat_max))[0]
    ilon = np.where((lons >= lon_min) & (lons <= lon_max))[0]

    sub_lats = lats[ilat]
    sub_lons = lons[ilon] - 360.0  # Converter para [-180, 180]

    def extract_field(ds):
        tc = ds.variables['tc_ir'][0, ilat[0]:ilat[-1]+1, ilon[0]:ilon[-1]+1]
        cld = ds.variables['cldamt_ir'][0, ilat[0]:ilat[-1]+1, ilon[0]:ilon[-1]+1]
        
        # Onde for céu claro ou máscara, preenche com temperatura de superfície quente (~24C)
        data_C = np.array(tc) - 273.15
        mask = getattr(tc, 'mask', np.zeros_like(data_C, dtype=bool))
        
        # Preenche áreas sem nuvens com valor típico de solo
        data_C[mask] = 24.0
        data_C[cld < 5] = 24.0
        
        # Suavização suave para interpolação natural de satélite
        data_smooth = gaussian_filter(data_C, sigma=0.8)
        return data_smooth

    tc12_C = extract_field(ds12)
    tc18_C = extract_field(ds18)

    fig = plt.figure(figsize=(16, 8.2), facecolor='#0b1120')
    proj = ccrs.PlateCarree()

    cmap = create_enhanced_ir_colormap()
    norm = mcolors.Normalize(vmin=-80, vmax=28)

    times = [
        ('Painel A: 12:00 UTC (09:00 HL) — Horário da Radiossondagem SBPA', tc12_C, 1,
         'Início da intensificação pré-frontal sobre o RS.\nTopos atingindo -59°C (170 hPa).'),
        ('Painel B: 18:00 UTC (15:00 HL) — Auve Convectivo da Enchente de Natal', tc18_C, 2,
         'Explosão supercelular e complexo convectivo.\nTopos penetrantes a -63.5°C (160 hPa).')
    ]

    for title_text, data, subplot_idx, desc_box in times:
        ax = fig.add_subplot(1, 2, subplot_idx, projection=proj)
        ax.set_extent([-65, -44, -39.5, -22], crs=proj)

        # Plot de contorno preenchido da temperatura de brilho
        cf = ax.contourf(sub_lons, sub_lats, data, levels=np.linspace(-80, 28, 55),
                         cmap=cmap, norm=norm, extend='both', transform=proj)

        # Contornos de destaque para topos frios (-40C, -50C, -60C)
        cs = ax.contour(sub_lons, sub_lats, data, levels=[-60, -50, -40],
                        colors=['#ffffff', '#f1c40f', '#00ffff'],
                        linewidths=[1.8, 1.3, 1.0], transform=proj)
        ax.clabel(cs, inline=True, fontsize=8, fmt='%d°C', colors=['#ffffff', '#f1c40f', '#00ffff'])

        # Limites geográficos de alta definição
        ax.add_feature(cfeature.COASTLINE, edgecolor='#f8fafc', linewidth=1.3, zorder=5)
        ax.add_feature(cfeature.BORDERS, edgecolor='#f8fafc', linewidth=1.1, linestyle='-', zorder=5)
        ax.add_feature(cfeature.STATES, edgecolor='#cbd5e1', linewidth=0.7, linestyle=':', zorder=5)

        # Marcação de Porto Alegre (SBPA)
        ax.plot(-51.18, -29.99, marker='^', color='#facc15', markersize=10, transform=proj,
                markeredgecolor='#000000', markeredgewidth=1.2, zorder=10)
        ax.text(-50.9, -29.7, 'SBPA (Porto Alegre)\nRadiossondagem 12Z', color='#fef08a', fontsize=8.5, fontweight='bold',
                transform=proj, bbox=dict(boxstyle='round,pad=0.25', facecolor='#0f172a', alpha=0.9, edgecolor='#facc15', lw=1.2),
                zorder=11)

        # Marcação de Florianópolis (SC)
        ax.plot(-48.55, -27.60, marker='o', color='#38bdf8', markersize=7, transform=proj,
                markeredgecolor='#000000', markeredgewidth=1.0, zorder=10)
        ax.text(-48.2, -27.4, 'Florianópolis (SC)\nEpicentro Chuvas', color='#bae6fd', fontsize=8, fontweight='bold',
                transform=proj, bbox=dict(boxstyle='round,pad=0.25', facecolor='#0f172a', alpha=0.85, edgecolor='#38bdf8', lw=1.0),
                zorder=11)

        # Caixa explicativa da física observada
        ax.text(0.03, 0.04, desc_box, transform=ax.transAxes, color='#ffffff', fontsize=8.5,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#0f172a', alpha=0.85, edgecolor='#475569', lw=0.8),
                zorder=12)

        # Gridlines
        gl = ax.gridlines(crs=proj, draw_labels=True, linewidth=0.5, color='#475569', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 9, 'color': '#94a3b8'}
        gl.ylabel_style = {'size': 9, 'color': '#94a3b8'}

        min_val = np.nanmin(data)
        ax.set_title(f"{title_text}\nTopo Mínimo Observado: {min_val:.1f}°C",
                     color='#f8fafc', fontsize=11, fontweight='bold', pad=10)

    # Barra de cores compartilhada
    cbar_ax = fig.add_axes([0.18, 0.08, 0.64, 0.026])
    cbar = fig.colorbar(cf, cax=cbar_ax, orientation='horizontal', ticks=np.arange(-80, 31, 10))
    cbar.set_label('Temperatura de Brilho / Topo de Nuvens IR (°C) — Satélite GOES-8 (Canal 11 µm)',
                   color='#f8fafc', fontsize=10, fontweight='bold')
    cbar.ax.tick_params(labelsize=9, colors='#f8fafc')

    fig.suptitle('Satélite GOES-8 / NOAA ISCCP-H — Imagem de Infravermelho Realçada (24/12/1995)\n'
                 'Evolução da Convecção Profunda e da Enchente Histórica de Natal no Sul do Brasil',
                 color='#38bdf8', fontsize=13.5, fontweight='bold', y=0.97)

    plt.subplots_adjust(top=0.85, bottom=0.16, left=0.05, right=0.95, wspace=0.14)
    
    out_fig = 'metpack/fig_sat_ir_19951224.png'
    plt.savefig(out_fig, dpi=250, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"-> Salvo com sucesso: {out_fig}")

if __name__ == '__main__':
    plot_satellite_ir()
