"""Plot research area map.

Create a professional map showing the study areas:
- Zhoushan Port waters (Zhejiang, China)
- Shanghai Port area (Shanghai, China)

Features:
- Mapbox Light basemap
- Professional scale bar and north arrow
- Inset map showing regional context

Author: Amoylimee
Date: 2025-11-24
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.img_tiles import MapboxTiles
from shapely.geometry import Polygon
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from matplotlib.collections import PatchCollection
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import os
import json
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 配置 Times New Roman 字体
# 先检查系统是否有该字体，如果没有则从 fonts/ 文件夹加载
font_available = any('Times New Roman' in f.name for f in fm.fontManager.ttflist)
if not font_available:
    # 系统中找不到，尝试从 fonts/ 文件夹加载
    font_dir = "fonts"
    if os.path.exists(font_dir):
        for font_file in os.listdir(font_dir):
            if font_file.lower().endswith(('.ttf', '.otf')):
                font_path = os.path.join(font_dir, font_file)
                fm.fontManager.addfont(font_path)
                print(f"Loaded font from: {font_path}")
    # 重新检查是否加载成功
    font_available = any('Times New Roman' in f.name for f in fm.fontManager.ttflist)
    if font_available:
        print("Times New Roman font loaded successfully from fonts/ directory")
    else:
        print("Warning: Times New Roman font not found. Using default serif font.")
        
plt.rcParams["font.family"] = "Times New Roman"

# Path to p2 grid output
GRID_PATH = os.path.join("output", "p2_grid_ais", "ais_grids.geojson")

# ====================================================================
# Color Scale Configuration for Grid Density
# ====================================================================
# 调整这些参数来控制颜色映射
# 数据分布：中位数=2，95%分位数=34，99%分位数=252，最大值=28180

# 选项1：使用分位数截断（推荐）
USE_PERCENTILE_CLIPPING = True
VMIN_PERCENTILE = int(os.getenv('VMIN_PERCENTILE', 0))    # 从环境变量读取，默认0
VMAX_PERCENTILE = int(os.getenv('VMAX_PERCENTILE', 95))   # 从环境变量读取，默认95

# 选项2：手动设置范围（如果 USE_PERCENTILE_CLIPPING = False）
MANUAL_VMIN = 1
MANUAL_VMAX = 100

# ====================================================================
# Configuration: Geographic Extents (WGS84 lon/lat)
# ====================================================================

# Study area: Zhoushan waters
# Upper-left: (121.5056, 31.0994), Lower-right: (123.6126, 29.5607)
study_lon_min, study_lat_max = 121.5056, 31.0994
study_lon_max, study_lat_min = 123.6126, 29.5607

# Shanghai Port area
sh_lon_min, sh_lon_max = 121.3500, 121.9500
sh_lat_min, sh_lat_max = 30.8500, 31.4500

# Main map extent (union + buffer)
main_extent = [
    121.30,
    123.65,  # lon_min, lon_max
    29.50,
    31.50,  # lat_min, lat_max
]

# 插图显示范围（更大区域定位）
inset_extent = [118.0, 126.5, 26.0, 34.0]

# -----------------------
# 2) 构造矩形多边形
# -----------------------
study_poly = Polygon(
    [
        (study_lon_min, study_lat_min),
        (study_lon_min, study_lat_max),
        (study_lon_max, study_lat_max),
        (study_lon_max, study_lat_min),
    ]
)

shanghai_poly = Polygon(
    [
        (sh_lon_min, sh_lat_min),
        (sh_lon_min, sh_lat_max),
        (sh_lon_max, sh_lat_max),
        (sh_lon_max, sh_lat_min),
    ]
)
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
        color = "black" if i % 2 == 0 else "white"
        edgecolor = "black"

        rect = Rectangle(
            (seg_start, start_lat),
            segment_deg,
            bar_height_deg,
            transform=ccrs.PlateCarree(),
            facecolor=color,
            edgecolor=edgecolor,
            linewidth=1.2,
            zorder=100,
        )
        ax.add_patch(rect)

    # 添加刻度标签
    for i in range(n_segments + 1):
        tick_lon = start_lon + i * segment_deg
        tick_label = int(i * segment_km)

        # 刻度线
        ax.plot(
            [tick_lon, tick_lon],
            [start_lat, start_lat - bar_height_deg * 0.3],
            transform=ccrs.PlateCarree(),
            color="black",
            linewidth=1,
            zorder=101,
        )

        # 数字标签
        if i == 0 or i == n_segments:
            text = ax.text(
                tick_lon,
                start_lat - bar_height_deg * 1.2,
                f"{tick_label}",
                transform=ccrs.PlateCarree(),
                ha="center",
                va="top",
                fontsize=8.5,
                zorder=102,
            )

    # 添加单位标签
    unit_text = ax.text(
        start_lon + length_deg / 2,
        start_lat + bar_height_deg * 2,
        "km",
        transform=ccrs.PlateCarree(),
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        zorder=102,
    )


def add_north_arrow(ax, x=0.95, y=0.12, arrow_length=0.05, width=3):
    """
    添加专业的指北针（透明背景，罗盘风格）
    """
    from matplotlib.patches import Polygon as MPLPolygon, FancyArrowPatch
    import matplotlib.patheffects as path_effects

    # 创建罗盘样式的指北针（无背景圆，透明）

    # 1. 北向箭头（黑色填充）
    north_arrow = MPLPolygon(
        [
            [x, y + 0.025],  # 顶点
            [x - 0.01, y - 0.002],  # 左下
            [x, y + 0.003],  # 中间点
            [x + 0.01, y - 0.002],  # 右下
        ],
        transform=ax.transAxes,
        facecolor="black",
        edgecolor="black",
        linewidth=1.2,
        zorder=100,
    )
    ax.add_patch(north_arrow)

    # 2. 南向箭头（白色填充，黑色边框）
    south_arrow = MPLPolygon(
        [
            [x, y - 0.025],  # 底点
            [x - 0.01, y + 0.002],  # 左上
            [x, y - 0.003],  # 中间点
            [x + 0.01, y + 0.002],  # 右上
        ],
        transform=ax.transAxes,
        facecolor="white",
        edgecolor="black",
        linewidth=1.2,
        zorder=99,
    )
    ax.add_patch(south_arrow)

    # 3. 中心小圆点
    from matplotlib.patches import Circle

    center_dot = Circle(
        (x, y),
        0.003,
        transform=ax.transAxes,
        facecolor="black",
        edgecolor="black",
        linewidth=0.5,
        zorder=101,
    )
    ax.add_patch(center_dot)

    # 4. N 字母（带白色描边以便在任何背景上可见）
    text = ax.text(
        x,
        y + 0.038,
        "N",
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="center",
        zorder=102,
    )
    text.set_path_effects(
        [path_effects.Stroke(linewidth=3, foreground="white"), path_effects.Normal()]
    )


def load_grid_patches(grid_path):
    """Load grid polygons and compute density from GeoJSON.
    
    Returns patches and density values (points per km²).
    Each grid cell is 1km x 1km = 1 km².
    """
    if not os.path.exists(grid_path):
        return [], np.array([])

    with open(grid_path, "r", encoding="utf-8") as f:
        geo = json.load(f)

    patches, values = [], []
    for feat in geo.get("features", []):
        coords = feat.get("geometry", {}).get("coordinates", [])
        if not coords:
            continue
        # coordinates are [[[lon, lat], ...]]
        patches.append(mpatches.Polygon(coords[0], closed=True))
        point_count = feat.get("properties", {}).get("point_count", 0)
        # Grid resolution is 1000m = 1km, so area = 1 km²
        # Density = point_count / 1 km² = point_count
        values.append(point_count)  # Already density since grid is 1 km²

    return patches, np.array(values, dtype=float)


# -----------------------
# 4) 画图
# -----------------------
proj = ccrs.PlateCarree()

# 从 .env 文件读取 Mapbox token
# 在 .env 文件中添加: MAPBOX_TOKEN=your_token_here
mapbox_token = os.getenv("MAPBOX_TOKEN")
if not mapbox_token:
    raise ValueError("请在 .env 文件中设置 MAPBOX_TOKEN")

# 使用 Mapbox Light 风格底图（白色简洁风格）
mapbox = MapboxTiles(mapbox_token, "light-v10")

fig = plt.figure(figsize=(10, 8), dpi=300)
ax = plt.axes(projection=mapbox.crs)

# 底图要素
ax.set_extent(main_extent, crs=proj)
ax.add_image(mapbox, 9)  # zoom level 9，可以根据需要调整 (8-11)

# 叠加 p2 网格（使用分位数截断处理长尾分布）
grid_patches, grid_values = load_grid_patches(GRID_PATH)
if len(grid_patches) > 0:
    # 根据配置确定颜色范围
    if USE_PERCENTILE_CLIPPING:
        if VMIN_PERCENTILE > 0:
            vmin = np.percentile(grid_values, VMIN_PERCENTILE)
        else:
            vmin = grid_values.min()
        vmax = np.percentile(grid_values, VMAX_PERCENTILE)
        print(f"Using percentile clipping: vmin={vmin:.1f} ({VMIN_PERCENTILE}%), vmax={vmax:.1f} ({VMAX_PERCENTILE}%)")
    else:
        vmin = MANUAL_VMIN
        vmax = MANUAL_VMAX
        print(f"Using manual range: vmin={vmin}, vmax={vmax}")
    
    grid_collection = PatchCollection(
        grid_patches,
        cmap="viridis",
        alpha=0.5,
        linewidths=0.3,
        edgecolor="none",
    )
    grid_collection.set_transform(proj)
    grid_collection.set_array(grid_values)  # 使用原始值
    grid_collection.set_clim(vmin, vmax)
    ax.add_collection(grid_collection)

    # colorbar 嵌入到主图右侧，默认尺寸与位置可按需要微调
    cax = inset_axes(
        ax,
        width="2.8%",
        height="50%",
        loc="lower left",
        bbox_to_anchor=(1.03, 0.12, 1, 1),
        bbox_transform=ax.transAxes,
        borderpad=0,
    )
    cbar = plt.colorbar(grid_collection, cax=cax, orientation="vertical", extend="both")
    cbar.set_label("Traffic Density", fontsize=10, fontweight='bold')
    # 隐藏数字刻度，只显示 Low 和 High 标签
    cbar.set_ticks([vmin, vmax])
    cbar.set_ticklabels(['Low', 'High'], fontsize=9)
    cbar.ax.yaxis.set_tick_params(pad=2)

# 研究区矩形
ax.add_geometries(
    [study_poly],
    crs=proj,
    facecolor="none",
    edgecolor="crimson",
    linewidth=2.2,
    linestyle="--",
    zorder=5,
)

# 上海港区矩形
ax.add_geometries(
    [shanghai_poly],
    crs=proj,
    facecolor="none",
    edgecolor="navy",
    linewidth=1.8,
    linestyle="-",
    zorder=6,
)

# 标注文字
ax.text(
    study_lon_min + 0.03,
    study_lat_max - 0.05,
    "Zhoushan",
    transform=proj,
    fontsize=14,
    color="crimson",
    ha="left",
    va="top",
    fontweight="bold",
)

ax.text(
    sh_lon_min + 0.03,
    sh_lat_max - 0.05,
    "Shanghai",
    transform=proj,
    fontsize=14,
    color="navy",
    ha="left",
    va="top",
    fontweight="bold",
)

# 经纬网
gl = ax.gridlines(
    draw_labels=True, linewidth=0.5, color="gray", alpha=0.5, linestyle=":"
)
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {"size": 9}
gl.ylabel_style = {"size": 9}

# 比例尺（专业分段式，位于右下角偏左）
add_scalebar(ax, length_km=50, location=(0.7, 0.07))

# -----------------------
# 5) 插图（区域定位）
# -----------------------
# 放大插图尺寸：从 0.27x0.27 改为 0.35x0.35
inset_ax = fig.add_axes([0.63, 0.63, 0.35, 0.35], projection=mapbox.crs)
# 缩小显示范围以更清晰地显示研究区域
inset_extent_zoomed = [119.5, 125.0, 28.0, 33.0]
inset_ax.set_extent(inset_extent_zoomed, crs=proj)
inset_ax.add_image(mapbox, 7)  # zoom level 7 for inset map

# (a) 主图范围框 - 使用粗实线黑框
main_box = Polygon(
    [
        (main_extent[0], main_extent[2]),
        (main_extent[0], main_extent[3]),
        (main_extent[1], main_extent[3]),
        (main_extent[1], main_extent[2]),
    ]
)
inset_ax.add_geometries(
    [main_box],
    crs=proj,
    facecolor="none",
    edgecolor="black",
    linewidth=2.0,
    linestyle="-",
    zorder=10,
)

# (b) 研究区域框 - 使用更细的线和半透明填充以区分
inset_ax.add_geometries(
    [zhoushan_poly],
    crs=proj,
    facecolor="crimson",
    edgecolor="crimson",
    linewidth=1.5,
    linestyle="--",
    alpha=0.3,
    zorder=11,
)
inset_ax.add_geometries(
    [shanghai_poly],
    crs=proj,
    facecolor="navy",
    edgecolor="navy",
    linewidth=1.5,
    linestyle="-",
    alpha=0.3,
    zorder=12,
)

# 添加图例
legend_elements = [
    mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='black', 
                       linewidth=2.0, linestyle='-', label='Main map extent'),
    mpatches.Rectangle((0, 0), 1, 1, facecolor='crimson', edgecolor='crimson', 
                       linewidth=1.5, linestyle='--', alpha=0.3, label='Zhoushan area'),
    mpatches.Rectangle((0, 0), 1, 1, facecolor='navy', edgecolor='navy', 
                       linewidth=1.5, linestyle='-', alpha=0.3, label='Shanghai area'),
]
inset_ax.legend(handles=legend_elements, loc='lower left', fontsize=7, 
                framealpha=0.9, edgecolor='gray', fancybox=True)


# 指北针（添加到插图中，放大尺寸）
def add_north_arrow_large(ax, x=0.88, y=0.15):
    """放大版指北针，适用于小插图"""
    from matplotlib.patches import Polygon as MPLPolygon, Circle
    import matplotlib.patheffects as path_effects

    scale = 3  # 放大倍数

    # 北向箭头（黑色）
    north_arrow = MPLPolygon(
        [
            [x, y + 0.025 * scale],
            [x - 0.01 * scale, y - 0.002 * scale],
            [x, y + 0.003 * scale],
            [x + 0.01 * scale, y - 0.002 * scale],
        ],
        transform=ax.transAxes,
        facecolor="black",
        edgecolor="black",
        linewidth=1.5,
        zorder=100,
    )
    ax.add_patch(north_arrow)

    # 南向箭头（白色）
    south_arrow = MPLPolygon(
        [
            [x, y - 0.025 * scale],
            [x - 0.01 * scale, y + 0.002 * scale],
            [x, y - 0.003 * scale],
            [x + 0.01 * scale, y + 0.002 * scale],
        ],
        transform=ax.transAxes,
        facecolor="white",
        edgecolor="black",
        linewidth=1.5,
        zorder=99,
    )
    ax.add_patch(south_arrow)

    # 中心圆点
    center_dot = Circle(
        (x, y),
        0.005 * scale,
        transform=ax.transAxes,
        facecolor="black",
        edgecolor="black",
        linewidth=0.8,
        zorder=101,
    )
    ax.add_patch(center_dot)

    # N 字母
    text = ax.text(
        x,
        y + 0.038 * scale,
        "N",
        transform=ax.transAxes,
        fontsize=14,
        fontweight="bold",
        ha="center",
        va="center",
        zorder=102,
    )
    text.set_path_effects(
        [path_effects.Stroke(linewidth=3.5, foreground="white"), path_effects.Normal()]
    )


add_north_arrow_large(inset_ax, x=0.88, y=0.8)  # 增大 y 值向上移动

# plt.show()
plt.savefig(f'./output/p3_plot/study_area_map_{VMIN_PERCENTILE}_{VMAX_PERCENTILE}.png', bbox_inches='tight')
