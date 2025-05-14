#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# extract deferred mesh surfaces to mesh items
# select deferred mesh items, run command
# ================================

import modo
import modo.constants as c
import lx
from pathlib import PurePath, Path
import shutil

from h3d_utilites.scripts.h3d_utils import itype_str


BACKUP_SUFFIX = ' --- EMPTY ---'


def main():
    items: list[modo.Item] = modo.Scene().selectedByType(itype=c.DEFERREDMESH_TYPE)
    if not items:
        return

    converted_surfaces: list[modo.Item] = []
    for item in items:
        converted_surfaces.extend(convert_deferred_mesh(item))

    modo.Scene().deselect()
    for item in converted_surfaces:
        item.select()


def convert_deferred_mesh(item: modo.Item) -> tuple[modo.Item, ...]:
    if not item:
        raise ValueError('No item provided')
    if item.type != itype_str(c.DEFERREDMESH_TYPE):
        raise TypeError('Provided item is not DeferredMesh type')

    filename_channel = item.channel('filename')
    if not filename_channel:
        raise LookupError('No filename channel found')

    original_name = item.name
    original_filename = str(filename_channel.get())
    tmp_filename = create_tmp_deferred_mesh(original_filename)
    link_meshref(item, tmp_filename)

    converted_surfaces: list[modo.Item] = []
    surface_names = get_defmesh_surface_names(item)
    for surface_name in surface_names:
        converted_surfaces.append(extract_defmesh_surface(item, surface_name))

    item.select(replace=True)
    lx.eval('item.setType groupLocator locator')
    lx.eval(f'item.name {{{original_name}}}')

    return tuple(converted_surfaces)


def create_tmp_deferred_mesh(filename: str) -> str:
    if not filename:
        raise ValueError('No filename provided')

    backup_filename = get_unique_name(filename)
    shutil.copy(filename, backup_filename)

    return backup_filename


def link_meshref(item: modo.Item, filename: str):
    if not item:
        raise ValueError('No item provided')

    filename_channel = item.channel('filename')
    if not filename_channel:
        raise LookupError('No filename channel found')

    filename_channel.set(filename)


def get_defmesh_surface_names(item: modo.Item) -> list[str]:
    item.select(replace=True)
    lx.eval('deferredMesh.setCurrent ...')
    i = 0
    names = []
    while True:
        lx.eval(f'deferredMesh.setCurrent ?+{i}')
        surface = lx.eval('deferredMesh.setCurrent ?')
        i += 1
        if surface in names:
            break

        names.append(surface)

    return names


def extract_defmesh_surface(item: modo.Item, name: str) -> modo.Item:
    if not item:
        raise ValueError('No item provided')
    if not name:
        raise ValueError('No name provided')

    before_children = set(item.childrenByType(c.TRISURF_TYPE))

    item.select(replace=True)
    lx.eval(f'deferredMesh.removeGeometry static {name}')

    after_children = set(item.childrenByType(c.TRISURF_TYPE))
    new_children = list(after_children - before_children)

    if not new_children:
        raise ValueError('Failed to detect extracted surface: none new item found')

    if len(new_children) > 1:
        raise ValueError('Failed to detect extracted surface: too many new items')

    return new_children[0]


def get_unique_name(filename: str) -> str:
    if not filename:
        raise ValueError('No name provided')

    path = PurePath(filename)
    while Path(path).exists():
        path = path.with_stem(path.stem + BACKUP_SUFFIX)

    return str(path)


if __name__ == '__main__':
    main()
