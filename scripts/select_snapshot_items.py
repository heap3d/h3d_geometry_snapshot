#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select items with the snapshot name mark
# ================================

import modo
import modo.constants as c

from h3d_geometry_snapshot.scripts.merge_meshes_individual_snapshot import SNAPSHOT_NAME_SUFFIX


def main():
    items = modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
    snapshots = [item for item in items if SNAPSHOT_NAME_SUFFIX in item.name]

    modo.Scene().deselect()
    for item in snapshots:
        item.select()


if __name__ == '__main__':
    main()
