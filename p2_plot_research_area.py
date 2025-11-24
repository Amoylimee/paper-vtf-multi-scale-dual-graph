# -*- coding: utf-8 -*-
"""
Research area schematic map: Zhoushan waters + Shanghai Port area
Basemap: Mapbox Light Style
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.img_tiles import MapboxTiles
from shapely.geometry import Polygon
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

plt.rcParams["font.family"] = "Times New Roman"

# -----------------------
# 1) 输入范围（WGS84 lon/lat）
# -----------------------
# 研究区域（舟山群岛水域）: 左上(121.5056,31.0994) 右下(123.6126,29.5607)
study_lon_min, study_lat_max = 121.5056, 31.0994
study_lon_max, study_lat_min = 123.6126, 29.5607

# 上海港区
sh_lon_min, sh_lon_max = 121.3500, 121.9500
sh_lat_min, sh_lat_max = 30.8500, 31.4500

# 主图显示范围（并集 + 留白）
main_extent = [
    121.30, 123.65,   # lon_min, lon_max
    29.50,  31.50     # lat_min, lat_max
]

# 插图显示范围（更大区域定位）
inset_extent = [
    118.0, 126.5,
    26.0,  34.0
]

# -----------------------
# 2) 构造矩形多边形
# -----------------------
study_poly = Polygon([
    (study_lon_min, study_lat_min),
    (study_lon_min, study_lat_max),
    (study_lon_max, study_lat_max),
    (study_lon_max, study_lat_min)
])

shanghai_poly = Polygon([
    (sh_lon_min, sh_lat_min),
    (sh_lon_min, sh_lat_max),
    (sh_lon_max, sh_lat_max),
    (sh_lon_max, sh_lat_min)
])
zhoushan_poly = study_poly

# -----------------------
# 3) 专业比例尺函数
# -----------------------
def add_scalebar(ax, length_km=50, location=(0.05, 0.05)):
    """
    添加专业的分段式比例尺
    length_km: 比例尺总长度（公里）
    location: 左下角位置 (x, y) 在 axes fraction 坐标系中
    """
    from matplotlib.patches import Rectangle
    import matplotlib.patheffects as path_effects
    
    # 计算经度跨度
    x0, x1, y0, y1 = ax.get_extent(crs=ccrs.PlateCarree())
    mid_lat = (y0 + y1) / 2.0
    km_per_deg_lon = 111.32 * np.cos(np.deg2rad(mid_lat))
    length_deg = length_km / km_per_deg_lon
    
    # 起始位置
    start_lon = x0 + (x1 - x0) * location[0]
    start_lat = y0 + (y1 - y0) * location[1]
    
    # 分段数（黑白相间）
    n_segments = 4
    segment_km = length_km / n_segments
    segment_deg = length_deg / n_segments
    
    # 比例尺高度
    bar_height_deg = (y1 - y0) * 0.008
    
    # 绘制分段矩形（黑白相间）
    for i in range(n_segments):
        seg_start = start_lon + i * segment_deg
        color = 'black' if i % 2 == 0 else 'white'
        edgecolor = 'black'
        
        rect = Rectangle(
            (seg_start, start_lat), segment_deg, bar_height_deg,
            transform=ccrs.PlateCarree(),
            facecolor=color, edgecolor=edgecolor,
            linewidth=1.2, zorder=100
        )
        ax.add_patch(rect)
    
    # 添加刻度标签
    for i in range(n_segments + 1):
        tick_lon = start_lon + i * segment_deg
        tick_label = int(i * segment_km)
        
        # 刻度线
        ax.plot([tick_lon, tick_lon], 
                [start_lat, start_lat - bar_height_deg * 0.3],
                transform=ccrs.PlateCarree(),
                color='black', linewidth=1, zorder=101)
        
        # 数字标签
        if i == 0 or i == n_segments:
            text = ax.text(tick_lon, start_lat - bar_height_deg * 1.2,
                          f'{tick_label}',
                          transform=ccrs.PlateCarree(),
                          ha='center', va='top', fontsize=8.5,
                          zorder=102)
    
    # 添加单位标签
    unit_text = ax.text(start_lon + length_deg / 2, 
                       start_lat + bar_height_deg * 2,
                       'km',
                       transform=ccrs.PlateCarree(),
                       ha='center', va='bottom', 
                       fontsize=9, fontweight='bold',
                       zorder=102)

def add_north_arrow(ax, x=0.95, y=0.12, arrow_length=0.05, width=3):
    """
    添加专业的指北针（透明背景，罗盘风格）
    """
    from matplotlib.patches import Polygon as MPLPolygon, FancyArrowPatch
    import matplotlib.patheffects as path_effects
    
    # 创建罗盘样式的指北针（无背景圆，透明）
    
    # 1. 北向箭头（黑色填充）
    north_arrow = MPLPolygon([
        [x, y + 0.025],  # 顶点
        [x - 0.01, y - 0.002],  # 左下
        [x, y + 0.003],  # 中间点
        [x + 0.01, y - 0.002],  # 右下
    ], transform=ax.transAxes, facecolor='black', 
       edgecolor='black', linewidth=1.2, zorder=100)
    ax.add_patch(north_arrow)
    
    # 2. 南向箭头（白色填充，黑色边框）
    south_arrow = MPLPolygon([
        [x, y - 0.025],  # 底点
        [x - 0.01, y + 0.002],  # 左上
        [x, y - 0.003],  # 中间点
        [x + 0.01, y + 0.002],  # 右上
    ], transform=ax.transAxes, facecolor='white',
       edgecolor='black', linewidth=1.2, zorder=99)
    ax.add_patch(south_arrow)
    
    # 3. 中心小圆点
    from matplotlib.patches import Circle
    center_dot = Circle((x, y), 0.003, transform=ax.transAxes,
                       facecolor='black', edgecolor='black', 
                       linewidth=0.5, zorder=101)
    ax.add_patch(center_dot)
    
    # 4. N 字母（带白色描边以便在任何背景上可见）
    text = ax.text(x, y + 0.038, 'N',
                   transform=ax.transAxes,
                   fontsize=11, fontweight='bold',
                   ha='center', va='center',
                   zorder=102)
    text.set_path_effects([path_effects.Stroke(linewidth=3, foreground='white'),
                          path_effects.Normal()])

# -----------------------
# 4) 画图
# -----------------------
proj = ccrs.PlateCarree()

# 从 .env 文件读取 Mapbox token
# 在 .env 文件中添加: MAPBOX_TOKEN=your_token_here
mapbox_token = os.getenv('MAPBOX_TOKEN')
if not mapbox_token:
    raise ValueError("请在 .env 文件中设置 MAPBOX_TOKEN")

# 使用 Mapbox Light 风格底图（白色简洁风格）
mapbox = MapboxTiles(mapbox_token, 'light-v10')

fig = plt.figure(figsize=(10, 8), dpi=300)
ax = plt.axes(projection=mapbox.crs)

# 底图要素
ax.set_extent(main_extent, crs=proj)
ax.add_image(mapbox, 9)  # zoom level 9，可以根据需要调整 (8-11)

# 研究区矩形
ax.add_geometries(
    [study_poly], crs=proj,
    facecolor='none', edgecolor='crimson',
    linewidth=2.2, linestyle='--', zorder=5
)

# 上海港区矩形
ax.add_geometries(
    [shanghai_poly], crs=proj,
    facecolor='none', edgecolor='navy',
    linewidth=1.8, linestyle='-', zorder=6
)

# 标注文字
ax.text(study_lon_min + 0.05, study_lat_max - 0.08,
        'Study Area near Zhoushan Port \n(Zhejiang, China)',
        transform=proj, fontsize=10, color='crimson',
        ha='left', va='top')

ax.text(sh_lon_min + 0.03, sh_lat_max - 0.05,
        'Study Area near Shanghai Port \n(Shanghai, China)',
        transform=proj, fontsize=10, color='navy',
        ha='left', va='top')

# 经纬网
gl = ax.gridlines(draw_labels=True, linewidth=0.5,
                  color='gray', alpha=0.5, linestyle=':')
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 9}
gl.ylabel_style = {'size': 9}

# 比例尺（专业分段式，位于右下角偏左）
add_scalebar(ax, length_km=50, location=(0.7, 0.07))

# -----------------------
# 5) 插图（区域定位）
# -----------------------
# 放大插图尺寸：从 0.27x0.27 改为 0.30x0.30
inset_ax = fig.add_axes([0.66, 0.66, 0.30, 0.30], projection=mapbox.crs)
# 缩小显示范围以更清晰地显示研究区域
inset_extent_zoomed = [119.5, 125.0, 28.0, 33.0]
inset_ax.set_extent(inset_extent_zoomed, crs=proj)
inset_ax.add_image(mapbox, 7)  # zoom level 7 for inset map

# (a) 主图范围框 - 使用粗实线黑框
main_box = Polygon([
    (main_extent[0], main_extent[2]),
    (main_extent[0], main_extent[3]),
    (main_extent[1], main_extent[3]),
    (main_extent[1], main_extent[2])
])
inset_ax.add_geometries([main_box], crs=proj,
                        facecolor='none', edgecolor='black',
                        linewidth=2.0, linestyle='-', zorder=10)

# (b) 研究区域框 - 使用更细的线和半透明填充以区分
inset_ax.add_geometries([zhoushan_poly], crs=proj,
                        facecolor='crimson', edgecolor='crimson',
                        linewidth=1.5, linestyle='--', 
                        alpha=0.3, zorder=11)
inset_ax.add_geometries([shanghai_poly], crs=proj,
                        facecolor='navy', edgecolor='navy',
                        linewidth=1.5, linestyle='-', 
                        alpha=0.3, zorder=12)

# 插图说明
inset_ax.text(119.7, 32.5, 'Main map extent', transform=proj,
              fontsize=8, color='black', ha='left', va='top',
              bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                       edgecolor='none', alpha=0.8))
inset_ax.text(119.7, 31.8, 'Study areas', transform=proj,
              fontsize=8, color='black', ha='left', va='top',
              bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                       edgecolor='none', alpha=0.8))

# 指北针（添加到插图中，放大尺寸）
def add_north_arrow_large(ax, x=0.88, y=0.15):
    """放大版指北针，适用于小插图"""
    from matplotlib.patches import Polygon as MPLPolygon, Circle
    import matplotlib.patheffects as path_effects
    
    scale = 3  # 放大倍数
    
    # 北向箭头（黑色）
    north_arrow = MPLPolygon([
        [x, y + 0.025*scale],
        [x - 0.01*scale, y - 0.002*scale],
        [x, y + 0.003*scale],
        [x + 0.01*scale, y - 0.002*scale],
    ], transform=ax.transAxes, facecolor='black', 
       edgecolor='black', linewidth=1.5, zorder=100)
    ax.add_patch(north_arrow)
    
    # 南向箭头（白色）
    south_arrow = MPLPolygon([
        [x, y - 0.025*scale],
        [x - 0.01*scale, y + 0.002*scale],
        [x, y - 0.003*scale],
        [x + 0.01*scale, y + 0.002*scale],
    ], transform=ax.transAxes, facecolor='white',
       edgecolor='black', linewidth=1.5, zorder=99)
    ax.add_patch(south_arrow)
    
    # 中心圆点
    center_dot = Circle((x, y), 0.005*scale, transform=ax.transAxes,
                       facecolor='black', edgecolor='black', 
                       linewidth=0.8, zorder=101)
    ax.add_patch(center_dot)
    
    # N 字母
    text = ax.text(x, y + 0.038*scale, 'N',
                   transform=ax.transAxes,
                   fontsize=14, fontweight='bold',
                   ha='center', va='center',
                   zorder=102)
    text.set_path_effects([path_effects.Stroke(linewidth=3.5, foreground='white'),
                          path_effects.Normal()])

add_north_arrow_large(inset_ax, x=0.88, y=0.8)  # 增大 y 值向上移动

plt.show()
# plt.savefig('study_area_map.png', bbox_inches='tight')
