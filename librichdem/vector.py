"""Conversion between GRASS vector maps and RichDEM depression hierarchy objects."""

import sqlite3
import numpy as np
import grass.script as gs
from richdem.depression_hierarchy import Depression, OCEAN, NO_DEP


def depressions_to_grass(deps, labels, flowdirs, map_name, overwrite=False):
    """Write a RichDEM depression hierarchy to a GRASS vector map.

    Layer 1 (depressions table): one feature per depression.
      - Leaf depressions: area polygon (from labels raster) + centroid at pit_cell.
      - Metadepressions: point at out_cell.
    Layer 2 (ocean_links table): one row per ocean_linked entry.
    """
    raise NotImplementedError("depressions_to_grass not yet implemented")


def depressions_from_grass(map_name):
    """Read a GRASS depression hierarchy vector map back into a Depression list."""
    db_info = gs.vector_db(map=map_name)
    if 1 not in db_info:
        gs.fatal(f"Vector map {map_name} has no layer 1 attribute table.")

    db_path = db_info[1]["database"]
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT dep_label, pit_cell, out_cell, parent, odep, lchild, rchild,
               geolink, pit_elev, out_elev, ocean_parent, cell_count,
               dep_vol, water_vol, total_elevation
        FROM depressions
        ORDER BY dep_label
    """)
    rows = cur.fetchall()

    cur.execute("SELECT dep_label, linked_label FROM ocean_links ORDER BY dep_label")
    from collections import defaultdict
    ocean_linked = defaultdict(list)
    for dep_label, linked_label in cur.fetchall():
        ocean_linked[dep_label].append(linked_label)

    conn.close()

    deps = []
    for row in rows:
        (dep_label, pit_cell, out_cell, parent, odep, lchild, rchild,
         geolink, pit_elev, out_elev, ocean_parent, cell_count,
         dep_vol, water_vol, total_elevation) = row

        d = Depression()
        d.dep_label       = dep_label
        d.pit_cell        = pit_cell
        d.out_cell        = out_cell
        d.parent          = parent
        d.odep            = odep
        d.lchild          = lchild
        d.rchild          = rchild
        d.geolink         = geolink
        d.pit_elev        = pit_elev
        d.out_elev        = out_elev
        d.ocean_parent    = bool(ocean_parent)
        d.cell_count      = cell_count
        d.dep_vol         = dep_vol
        d.water_vol       = water_vol
        d.total_elevation = total_elevation
        d.ocean_linked    = ocean_linked.get(dep_label, [])
        deps.append(d)

    return deps


def update_water_vol(deps, map_name):
    """Write updated water_vol values from Depression list back to the vector map."""
    db_info = gs.vector_db(map=map_name)
    db_path = db_info[1]["database"]
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executemany(
        "UPDATE depressions SET water_vol = ? WHERE dep_label = ?",
        [(d.water_vol, d.dep_label) for d in deps],
    )
    conn.commit()
    conn.close()
