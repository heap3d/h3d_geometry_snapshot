#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select mesh items from selected
# ================================

import modo
from typing import Iterable


def main():
    items = modo.Scene().selected

    meshes = get_meshes_from(items)

    modo.Scene().deselect()
    for mesh in meshes:
        mesh.select()


def get_meshes_from(items: Iterable[modo.Item]) -> list[modo.Item]:
    meshes = [i for i in items if i.type == 'mesh']
    meshes = [i for i in meshes if ':' not in i.id]
    meshes = [i for i in meshes if i.channel('visible').get() == 'default']  # type: ignore
    meshes = [i for i in meshes if all([p.channel('visible').get() == 'default' for p in i.parents])]  # type: ignore
    meshes = [i for i in meshes if i.geometry.polygons]
    return meshes


if __name__ == '__main__':
    main()
