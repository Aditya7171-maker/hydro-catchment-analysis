from urllib.request import urlretrieve
from os.path import basename
from pysheds.grid import Grid
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
fn = "C:\GridIQ\dem.tif"  
grid = Grid.from_raster(fn, nodata=0)
dem = grid.read_raster(fn, nodata=0)

fig = plt.figure(figsize=(8, 4))
ax = plt.axes(projection=ccrs.PlateCarree())
plt.imshow(dem, extent=grid.extent, cmap="terrain", vmin=0, vmax=1500)
plt.colorbar(label="Elevation (m)")
ax.coastlines()
ax.add_feature(cfeature.BORDERS)
ax.gridlines(draw_labels=["bottom", "left"]);
plt.show()

pit_filled_dem = grid.fill_pits(dem)
flooded_dem = grid.fill_depressions(pit_filled_dem)
conditioned_dem = grid.resolve_flats(flooded_dem)

flowdir = grid.flowdir(conditioned_dem)
np.unique(flowdir)
plt.imshow(flowdir, extent=grid.extent, cmap="cividis");
plt.show()

acc = grid.accumulation(flowdir)

x, y = 80.5, 25.0
threshold = np.percentile(acc, 99)
x_snap, y_snap = grid.snap_to_mask(acc > threshold, (x, y))

catch = grid.catchment(x=x_snap, y=y_snap, fdir=flowdir, xytype="coordinate")

grid.clip_to(catch)
clipped_catch = grid.view(catch)
clipped_accumulated_flow = grid.accumulation(flowdir)

fig, ax = plt.subplots()
im = ax.imshow(
    np.where(clipped_catch, clipped_accumulated_flow, np.nan),
    extent=grid.extent,
    cmap="cubehelix",
    norm=LogNorm(1, clipped_accumulated_flow.max()),
    interpolation="bilinear",
)
plt.colorbar(
    im,
    ax=ax,
    label="Upstream Cells",
)
plt.scatter([x_snap], [y_snap], c="r", s=50)
plt.title("Catchment Area")
plt.show()
