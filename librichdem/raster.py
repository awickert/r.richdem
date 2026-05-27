"""Conversion between GRASS rasters and RichDEM rdarray objects."""

import numpy as np
import grass.script as gs
import richdem as rd


def rdarray_from_grass(name):
    """Read a GRASS raster map into a RichDEM rdarray."""
    info = gs.raster_info(name)
    no_data = info["null_value"] if info["null_value"] is not None else -9999
    region = gs.region()

    data = gs.array.array(mapname=name)
    data = np.array(data, dtype="float64")

    geotransform = np.array([
        region["w"],
        region["ewres"],
        0,
        region["n"],
        0,
        -region["nsres"],
    ])

    rda = rd.rdarray(data, no_data=no_data, geotransform=geotransform)
    return rda


def rdarray_to_grass(rda, name, overwrite=False):
    """Write a RichDEM rdarray to a GRASS raster map."""
    data = np.array(rda)
    data[data == rda.no_data] = None
    gs.array.array2raster(
        data,
        name,
        overwrite=overwrite,
    )
