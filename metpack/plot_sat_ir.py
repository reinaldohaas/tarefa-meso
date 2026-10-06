"""
Gera a figura científica oficial da imagem de satélite infravermelho (IR 11 µm)
para o dia 24/12/1995 utilizando dados reais do NOAA CDR ISCCP-H (GOES-8 / Meteosat).
Utiliza escala padrão de 256 níveis de cinza da meteorologia de satélites operacionais
(evitando saturação em preto absoluto nas áreas de superfície).
"""
import os
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def create_standard_256_ir_colormap():
    """
    Paleta padrão de 256 cores (níveis de cinza) para satélite infravermelho operacional:
    - 256 níveis discretos de quantização (0 a 255).
    - Topos convectivos frios (< -60°C a -80°C): branco puro brilhante (níveis 240 a 255).
    - Nuvens médias/altas (-40°C a -20°C): tons de cinza claro a médio (níveis 160 a 239).
    - Nuvens baixas / transição (-20°C a 0°C): tons de cinza médio (níveis 110 a 159).
    - Superfície continental e oceânica quente (> 0°C a +35°C): cinza escuro suave visível
      (níveis 55 a 109, intensidade ~0.22 a 0.42), evitando áreas totalmente pretas (0.0)
      para permitir visualização nítida de continentes, estados e linhas de costa.
    """
    n_colors = 256
    # Variação linear de 1.0 (branco no frio) até 0.22 (cinza visível no quente)
    # garantindo que o continente e o oceano permaneçam nítidos e não em preto puro
    gray_levels = np.linspace(1.0, 0.22, n_colors)
    colors = np.column_stack([gray_levels, gray_levels, gray_levels])
    return mcolors.ListedColormap(colors, name='standard_ir_256')

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
        
        # Onde for céu claro ou máscara, preenche com temperatura de superfície (~24C)
        data_C = np.array(tc) - 273.15
        mask = getattr(tc, 'mask', np.zeros_like(data_C, dtype=bool))
        
        data_C[mask] = 24.0
        data_C[cld < 5] = 24.0
        return data_C

    tc12_C = extract_field(ds12)
    tc18_C = extract_field(ds18)

    fig = plt.figure(figsize=(16, 8.4), facecolor='#0f172a')
    proj = ccrs.PlateCarree()

    cmap = create_standard_256_ir_colormap()
    vmin, vmax = -80.0, 32.0
    levels = np.linspace(vmin, vmax, 256)
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    times = [
        ('Painel A: 12:00 UTC (09:00 HL) — Síncrono com a Radiossondagem SBPA', tc12_C, 1),
        ('Painel B: 18:00 UTC (15:00 HL) — Período Vespertino de Atividade Convectiva', tc18_C, 2)
    ]

    for title_text, data, subplot_idx in times:
        ax = fig.add_subplot(1, 2, subplot_idx, projection=proj)
        ax.set_extent([-65, -44, -39.5, -22], crs=proj)

        # Plot com escala padrão 256 cores (níveis de cinza operacionais)
        cf = ax.contourf(sub_lons, sub_lats, data, levels=levels,
                         cmap=cmap, norm=norm, extend='both', transform=proj)

        # Contornos de isotermas de topos frios (-40°C, -50°C, -60°C)
        cs = ax.contour(sub_lons, sub_lats, data, levels=[-60, -50, -40],
                        colors=['#ef4444', '#f59e0b', '#38bdf8'],
                        linewidths=[1.8, 1.4, 1.1], transform=proj)
        ax.clabel(cs, inline=True, fontsize=8, fmt='%d°C', colors=['#ef4444', '#f59e0b', '#38bdf8'])

        # Limites geográficos com alta visibilidade
        ax.add_feature(cfeature.COASTLINE, edgecolor='#38bdf8', linewidth=1.2, zorder=5)
        ax.add_feature(cfeature.BORDERS, edgecolor='#f8fafc', linewidth=1.1, linestyle='-', zorder=5)
        ax.add_feature(cfeature.STATES, edgecolor='#e2e8f0', linewidth=0.75, linestyle=':', zorder=5)

        # Destaque de Santa Catarina (Defesa Civil de SC)
        ax.plot(-48.55, -27.60, marker='o', color='#38bdf8', markersize=7.5, transform=proj,
                markeredgecolor='#ffffff', markeredgewidth=1.2, zorder=10)
        ax.text(-48.2, -27.4, 'Florianópolis (SC)\nDefesa Civil SC', color='#bae6fd', fontsize=8.5, fontweight='bold',
                transform=proj, bbox=dict(boxstyle='round,pad=0.25', facecolor='#0f172a', alpha=0.9, edgecolor='#38bdf8', lw=1.2),
                zorder=11)

        # Marcação de Porto Alegre (SBPA)
        ax.plot(-51.18, -29.99, marker='^', color='#facc15', markersize=9, transform=proj,
                markeredgecolor='#000000', markeredgewidth=1.2, zorder=10)
        ax.text(-50.9, -29.7, 'SBPA (Porto Alegre)\nRadiossondagem 12Z', color='#fef08a', fontsize=8.5, fontweight='bold',
                transform=proj, bbox=dict(boxstyle='round,pad=0.25', facecolor='#0f172a', alpha=0.9, edgecolor='#facc15', lw=1.2),
                zorder=11)

        # Gridlines
        gl = ax.gridlines(crs=proj, draw_labels=True, linewidth=0.5, color='#64748b', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 9, 'color': '#cbd5e1'}
        gl.ylabel_style = {'size': 9, 'color': '#cbd5e1'}

        min_val = np.nanmin(data)
        ax.set_title(f"{title_text}\nTemperatura Mínima Observada no Domínio: {min_val:.1f}°C",
                     color='#f8fafc', fontsize=11, fontweight='bold', pad=10)

    # Barra de cores compartilhada com 256 níveis de cinza
    cbar_ax = fig.add_axes([0.18, 0.08, 0.64, 0.026])
    ticks = np.arange(-80, 31, 10)
    cbar = fig.colorbar(cf, cax=cbar_ax, orientation='horizontal', ticks=ticks)
    cbar.set_label('Temperatura de Brilho / Topo de Nuvens IR (°C) — Escala Padrão Operacional 256 Níveis de Cinza (Branco = Topo Frio | Cinza = Superfície)',
                   color='#f8fafc', fontsize=9.5, fontweight='bold')
    cbar.ax.tick_params(labelsize=9, colors='#f8fafc')

    fig.suptitle('Satélite GOES-8 / NOAA ISCCP-H — Imagem de Infravermelho em Escala Padrão 256 Níveis de Cinza (24/12/1995)\n'
                 'Monitoramento da Cobertura de Nuvens no Sul do Brasil (12:00 UTC vs 18:00 UTC) — Apoio à Defesa Civil de SC',
                 color='#38bdf8', fontsize=13.5, fontweight='bold', y=0.97)

    plt.subplots_adjust(top=0.85, bottom=0.16, left=0.05, right=0.95, wspace=0.14)
    
    out_fig = 'metpack/fig_sat_ir_19951224.png'
    plt.savefig(out_fig, dpi=250, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"-> Salvo com sucesso com escala padrão 256 cores: {out_fig}")

if __name__ == '__main__':
    plot_satellite_ir()
