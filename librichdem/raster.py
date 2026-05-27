"""Conversion between GRASS rasters and RichDEM rdarray objects."""

import numpy as np
import grass.script as gs
from grass.pygrass.raster import RasterRow
from grass.pygrass.raster.buffer import Buffer
import richdem as rd

_NO_DATA = -9999.0


def rdarray_from_grass(name):
    """Read a GRASS raster map into a RichDEM rdarray."""
    region = gs.region()
    geotransform = np.array([
        region["w"], region["ewres"], 0,
        region["n"], 0, -region["nsres"],
    ])

    r = RasterRow(name)
    r.open()
    data = np.array([np.array(r[i]) for i in range(r.info.rows)], dtype="float64")
    r.close()

    # GRASS nulls come back as NaN for float types; replace with _NO_DATA
    data[np.isnan(data)] = _NO_DATA

    return rd.rdarray(data, no_data=_NO_DATA, geotransform=geotransform)


def rdarray_to_grass(rda, name, overwrite=False):
    """Write a RichDEM rdarray to a GRASS raster map."""
    data = np.array(rda, dtype="float64")
    # Restore null cells: no_data values become GRASS nulls (NaN for DCELL)
    data[data == rda.no_data] = np.nan

    w = RasterRow(name)
    w.open("w", mtype="DCELL", overwrite=overwrite)
    for row in data:
        buf = Buffer(row.shape, mtype="DCELL")
        buf[:] = row
        w.put_row(buf)
    w.close()
