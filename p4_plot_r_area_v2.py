"""
Figure 1: Regional context map (no study-area rectangles; just show where ports are)
Figure 2: Two side-by-side study-area maps (Zhoushan vs Shanghai), same size.

Author: Amoylimee
Date: 2025-11-24
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import cartopy.crs as ccrs
from cartopy.io.img_tiles import MapboxTiles
from shapely.geometry import Polygon
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import os
import json
from dotenv import load_dotenv

# =========================================================
# 0) ENV / FONT
# =========================================================
load_dotenv()

font_available = any('Times New Roman' in f.name for f in fm.fontManager.ttflist)
if not font_available:
    font_dir = "fonts"
    if os.path.exists(font_dir):
        for font_file in os.listdir(font_dir):
            if font_file.lower().endswith(('.ttf', '.otf')):
                fm.fontManager.addfont(os.path.join(font_dir, font_file))
    font_available = any('Times New Roman' in f.name for f in fm.fontManager.ttflist)

plt.rcParams["font.family"] = "Times New Roman"

# =========================================================
# 1) PATHS / COLOR CONFIG (same as yours)
# =========================================================
GRID_PATH = os.path.join("output", "p2_grid_ais", "ais_grids.geojson")

USE_PERCENTILE_CLIPPING = True
VMIN_PERCENTILE = int(os.getenv('VMIN_PERCENTILE', 0))
VMAX_PERCENTILE = int(os.getenv('VMAX_PERCENTILE', 95))

MANUAL_VMIN = 1
MANUAL_VMAX = 100

# =========================================================
# 2) GEOGRAPHIC CONFIG (same as yours)
# =========================================================
def scale_extent(ext, scale=1.1):
    lon0, lon1, lat0, lat1 = ext
    clon = (lon0 + lon1) / 2
    clat = (lat0 + lat1) / 2
    dx = (lon1 - lon0) * scale / 2
    dy = (lat1 - lat0) * scale / 2
    return [clon - dx, clon + dx, clat - dy, clat + dy]

# Zhoushan waters rectangle
study_lon_min, study_lat_max = 121.5056, 31.0994
study_lon_max, study_lat_min = 123.6126, 29.5607

# Shanghai Port rectangle
sh_lon_min, sh_lon_max = 121.3500, 121.9500
sh_lat_min, sh_lat_max = 30.8500, 31.4500

# subplots extents (light buffer only)
zhoushan_extent = [
    study_lon_min - 0.12, study_lon_max + 0.12,
    study_lat_min - 0.32, study_lat_max + 0.32
]
shanghai_extent = [
    sh_lon_min - 0.12, sh_lon_max + 0.12,
    sh_lat_min - 0.12, sh_lat_max + 0.12
]

# context map extent (old inset / regional context)
context_extent = [117.5, 127.0, 25.5, 34.5]
# main map extent box (same as p3 main figure)
# main_extent = [121.30, 123.65, 29.50, 31.50]
main_extent = scale_extent([121.30, 123.65, 29.50, 31.50], scale=1.15)

# easy-to-tweak panel viewports (edit these to adjust framing)
PANEL_VIEWPORTS = {
    "a": {"extent": context_extent, "zoom": 6, "scalebar_km": 200},
    "b": {"extent": zhoushan_extent, "zoom": 9, "scalebar_km": 50},
    "c": {"extent": shanghai_extent, "zoom": 10, "scalebar_km": 20},
}

# polygons
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

# polygon centers for context markers
zh_center_lon = (study_lon_min + study_lon_max) / 2
zh_center_lat = (study_lat_min + study_lat_max) / 2
sh_center_lon = (sh_lon_min + sh_lon_max) / 2
sh_center_lat = (sh_lat_min + sh_lat_max) / 2

# =========================================================
# 3) FUNCTIONS (keep yours)
# =========================================================
proj = ccrs.PlateCarree()

def add_panel_label(ax, label, y=-0.08, fontsize=14):
    ax.text(
        0.5, y, f"({label})",
        transform=ax.transAxes,
        ha="center", va="top",
        fontsize=fontsize, fontweight="bold",
    )

def add_scalebar(ax, length_km=50, location=(0.05, 0.05)):
    from matplotlib.patches import Rectangle

    x0, x1, y0, y1 = ax.get_extent(crs=proj)
    mid_lat = (y0 + y1) / 2.0
    km_per_deg_lon = 111.32 * np.cos(np.deg2rad(mid_lat))
    length_deg = length_km / km_per_deg_lon

    start_lon = x0 + (x1 - x0) * location[0]
    start_lat = y0 + (y1 - y0) * location[1]

    n_segments = 4
    segment_km = length_km / n_segments
    segment_deg = length_deg / n_segments
    bar_height_deg = (y1 - y0) * 0.008

    for i in range(n_segments):
        seg_start = start_lon + i * segment_deg
        color = "black" if i % 2 == 0 else "white"
        rect = Rectangle(
            (seg_start, start_lat),
            segment_deg,
            bar_height_deg,
            transform=proj,
            facecolor=color,
            edgecolor="black",
            linewidth=1.2,
            zorder=100,
        )
        ax.add_patch(rect)

    for i in range(n_segments + 1):
        tick_lon = start_lon + i * segment_deg
        tick_label = int(i * segment_km)
        ax.plot(
            [tick_lon, tick_lon],
            [start_lat, start_lat - bar_height_deg * 0.3],
            transform=proj,
            color="black",
            linewidth=1,
            zorder=101,
        )
        if i == 0 or i == n_segments:
            ax.text(
                tick_lon,
                start_lat - bar_height_deg * 1.2,
                f"{tick_label}",
                transform=proj,
                ha="center",
                va="top",
                fontsize=8.5,
                zorder=102,
            )

    ax.text(
        start_lon + length_deg / 2,
        start_lat + bar_height_deg * 2,
        "km",
        transform=proj,
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        zorder=102,
    )

def add_north_arrow(ax, x=0.95, y=0.12):
    from matplotlib.patches import Polygon as MPLPolygon, Circle
    import matplotlib.patheffects as path_effects

    north_arrow = MPLPolygon(
        [[x, y + 0.025], [x - 0.01, y - 0.002], [x, y + 0.003], [x + 0.01, y - 0.002]],
        transform=ax.transAxes,
        facecolor="black",
        edgecolor="black",
        linewidth=1.2,
        zorder=100,
    )
    ax.add_patch(north_arrow)

    south_arrow = MPLPolygon(
        [[x, y - 0.025], [x - 0.01, y + 0.002], [x, y - 0.003], [x + 0.01, y + 0.002]],
        transform=ax.transAxes,
        facecolor="white",
        edgecolor="black",
        linewidth=1.2,
        zorder=99,
    )
    ax.add_patch(south_arrow)

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

    text = ax.text(
        x, y + 0.038, "N",
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
    if not os.path.exists(grid_path):
        return [], np.array([])

    with open(grid_path, "r", encoding="utf-8") as f:
        geo = json.load(f)

    patches, values = [], []
    for feat in geo.get("features", []):
        coords = feat.get("geometry", {}).get("coordinates", [])
        if not coords:
            continue
        patches.append(mpatches.Polygon(coords[0], closed=True))
        values.append(feat.get("properties", {}).get("point_count", 0))

    return patches, np.array(values, dtype=float)

# =========================================================
# 4) MAPBOX
# =========================================================
mapbox_token = os.getenv("MAPBOX_TOKEN")
if not mapbox_token:
    raise ValueError("请在 .env 文件中设置 MAPBOX_TOKEN")
mapbox = MapboxTiles(mapbox_token, "light-v10")

# =========================================================
# COMBINED FIGURE: 3 side-by-side panels (explicit fixed boxes)
# Layout: [regional context] | [Zhoushan] | [Shanghai] | [colorbar]
# =========================================================
fig = plt.figure(figsize=(20, 7), dpi=300)

# Manual layout to guarantee identical panel sizes
left_margin = 0.035
right_margin = 0.97
bottom_margin = 0.12
top_margin = 0.98
panel_gap = 0.03
colorbar_gap = 0.02
colorbar_width = 0.015

available_width = right_margin - left_margin - 2 * panel_gap - colorbar_gap - colorbar_width
panel_width = available_width / 3.0
panel_height = top_margin - bottom_margin

panel_positions = [
    [left_margin + i * (panel_width + panel_gap), bottom_margin, panel_width, panel_height]
    for i in range(3)
]
cbar_position = [
    panel_positions[-1][0] + panel_width + colorbar_gap,
    bottom_margin,
    colorbar_width,
    panel_height,
]

ax0 = fig.add_axes(panel_positions[0], projection=mapbox.crs)
ax1 = fig.add_axes(panel_positions[1], projection=mapbox.crs)
ax2 = fig.add_axes(panel_positions[2], projection=mapbox.crs)

# =========================================================
# PANEL (a): REGIONAL CONTEXT MAP
# =========================================================
ax0.set_extent(PANEL_VIEWPORTS["a"]["extent"], crs=proj)
ax0.add_image(mapbox, PANEL_VIEWPORTS["a"]["zoom"])
ax0.set_aspect("auto")  # force map to fill the panel box

# draw main-figure extent box for reference
main_box = Polygon(
    [
        (main_extent[0], main_extent[2]),
        (main_extent[0], main_extent[3]),
        (main_extent[1], main_extent[3]),
        (main_extent[1], main_extent[2]),
    ]
)
ax0.add_geometries(
    [main_box],
    crs=proj,
    facecolor="none",
    edgecolor="black",
    linewidth=2.0,
    linestyle="-",
    zorder=8,
)

# two subtle, same-style markers (avoid size comparison)
ax0.plot(
    [zh_center_lon, sh_center_lon],
    [zh_center_lat, sh_center_lat],
    marker="o",
    markersize=6,
    linestyle="None",
    color="black",
    transform=proj,
    zorder=10,
)

# labels (same font/weight; neutral color)
ax0.text(
    zh_center_lon - 0.80, zh_center_lat - 0.40,
    "Zhoushan Port",
    transform=proj, fontsize=11, color="black",
    ha="left", va="bottom", fontweight="bold", zorder=11
)
ax0.text(
    sh_center_lon + 0.12, sh_center_lat - 0.30,
    "Shanghai Port",
    transform=proj, fontsize=11, color="black",
    ha="left", va="bottom", fontweight="bold", zorder=11
)

# gridlines
gl0 = ax0.gridlines(draw_labels=True, linewidth=0.5, color="gray", alpha=0.5, linestyle=":")
gl0.top_labels = False
gl0.right_labels = False
gl0.left_labels = True
gl0.bottom_labels = True
gl0.xlabel_style = {"size": 9}
gl0.ylabel_style = {"size": 9}

# scalebar + north arrow (bigger bar for regional map)
add_scalebar(ax0, length_km=PANEL_VIEWPORTS["a"]["scalebar_km"], location=(0.7, 0.06))
add_north_arrow(ax0, x=0.95, y=0.92)

# =========================================================
grid_patches, grid_values = load_grid_patches(GRID_PATH)

if len(grid_patches) > 0:
    if USE_PERCENTILE_CLIPPING:
        vmin = np.percentile(grid_values, VMIN_PERCENTILE) if VMIN_PERCENTILE > 0 else grid_values.min()
        vmax = np.percentile(grid_values, VMAX_PERCENTILE)
        print(f"Using percentile clipping: vmin={vmin:.1f} ({VMIN_PERCENTILE}%), vmax={vmax:.1f} ({VMAX_PERCENTILE}%)")
    else:
        vmin, vmax = MANUAL_VMIN, MANUAL_VMAX
        print(f"Using manual range: vmin={vmin}, vmax={vmax}")
else:
    vmin, vmax = None, None

collections = []

side_panels = [
    {"ax": ax1, "poly": zhoushan_poly, "color": "crimson", "label": "Zhoushan", "key": "b"},
    {"ax": ax2, "poly": shanghai_poly, "color": "navy", "label": "Shanghai", "key": "c"},
]

for panel in side_panels:
    ax = panel["ax"]
    poly = panel["poly"]
    color = panel["color"]
    label = panel["label"]
    key = panel["key"]

    ax.set_extent(PANEL_VIEWPORTS[key]["extent"], crs=proj)
    ax.add_image(mapbox, PANEL_VIEWPORTS[key]["zoom"])
    ax.set_aspect("auto")  # force map to fill the panel box

    if len(grid_patches) > 0:
        grid_collection = PatchCollection(
            grid_patches,
            cmap="viridis",
            alpha=0.5,
            linewidths=0.3,
            edgecolor="none",
            zorder=3,
        )
        grid_collection.set_transform(proj)
        grid_collection.set_array(grid_values)
        grid_collection.set_clim(vmin, vmax)
        ax.add_collection(grid_collection)
        collections.append(grid_collection)

    ax.add_geometries(
        [poly],
        crs=proj,
        facecolor="none",
        edgecolor=color,
        linewidth=2.2,
        linestyle="--",
        zorder=5,
    )

    lon_min, lat_min, lon_max, lat_max = poly.bounds
    ax.text(
        lon_min + 0.03, lat_max - 0.05,
        label, transform=proj,
        fontsize=14, color=color,
        ha="left", va="top", fontweight="bold", zorder=6,
    )

    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color="gray", alpha=0.5, linestyle=":")
    gl.top_labels = False
    gl.right_labels = False
    gl.left_labels = True
    gl.bottom_labels = True
    gl.xlabel_style = {"size": 9}
    gl.ylabel_style = {"size": 9}

    add_scalebar(ax, length_km=PANEL_VIEWPORTS[key]["scalebar_km"], location=(0.70, 0.07))
    add_north_arrow(ax, x=0.95, y=0.12)
    
# shared colorbar in dedicated axis for perfect panel alignment
if len(collections) > 0:
    cax = fig.add_axes(cbar_position)
    cbar = plt.colorbar(collections[-1], cax=cax, orientation="vertical", extend="max")
    cbar.set_label("Low \u2190     Traffic Density     \u2192 High", fontsize=14, fontweight="bold")
    cbar.set_ticks([])
    cbar.ax.tick_params(length=0)
    cbar.outline.set_visible(True)
    cbar.solids.set_edgecolor("face")
    cbar.solids.set_linewidth(0)


# panel labels along a shared baseline (figure coords)
panel_axes = [ax0, ax1, ax2]
label_y_fig = bottom_margin - 0.04
for axis, lbl in zip(panel_axes, ["a", "b", "c"]):
    pos = axis.get_position()
    cx = pos.x0 + pos.width / 2
    fig.text(cx, label_y_fig, f"({lbl})", ha="center", va="top", fontsize=18, fontweight="bold")

plt.show()

# 保存（可选）
# fig.savefig(f'./output/p3_plot/combined_three_maps_{VMIN_PERCENTILE}_{VMAX_PERCENTILE}.png', bbox_inches='tight')
# fig.savefig(f'./output/p3_plot/combined_three_maps_{VMIN_PERCENTILE}_{VMAX_PERCENTILE}.pdf', bbox_inches='tight')
