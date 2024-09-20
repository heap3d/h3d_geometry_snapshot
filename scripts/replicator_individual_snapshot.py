#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# make individual replicator for each selected items snapshot
# ================================


import modo
import lx
import modo.constants as c

from typing import Union

from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import match_pos_rot, itype_str, parent_items_to

from h3d_geometry_snapshot.scripts.replicator_snapshot import (
    VERTEX_ZERO_NAME,
    WORKSPACE_NAME,
    get_vertex_zero,
    get_workspace_assembly,
    view_workspace_assembly,
    add_to_schematic,
)


REPLICATOR_NAME_SUFFIX = 'SNAPSHOT'
ALLOWED_TYPES = (
    itype_str(c.MESH_TYPE),
    itype_str(c.MESHINST_TYPE),
    itype_str(c.DEFERREDMESH_TYPE),
    itype_str(c.REPLICATOR_TYPE),
    'deferredSubMesh',
)


def main():
    selected: list[modo.Item] = modo.Scene().selected
    replicators: list[modo.Item] = []
    for item in selected:
        replicator = replicate_nonparent(item)
        if not replicator:
            continue
        match_pos_rot(replicator, item)
        replicators.append(replicator)

    modo.Scene().deselect()
    for item in replicators:
        item.select()


def replicate_nonparent(item: modo.Item) -> Union[modo.Item, None]:
    printd(f'{item.name=} {item.id=} {item.type=} {item=}')
    if item.type not in ALLOWED_TYPES:
        return None
    if item.type == itype_str(c.REPLICATOR_TYPE):
        replicator_copy: modo.Item = modo.Scene().duplicateItem(item)  # type: ignore
        replicator_copy.name = rename(item.name)
        parent_items_to((replicator_copy,), None, -1)  # type: ignore

        return replicator_copy

    vertex_zero = get_vertex_zero(VERTEX_ZERO_NAME)
    replicator = modo.Scene().addItem(itype='replicator', name=rename(item.name))

    workspace = get_workspace_assembly(WORKSPACE_NAME)
    view_workspace_assembly(workspace)
    add_to_schematic((vertex_zero, replicator,), workspace)  # type: ignore
    lx.eval(f'item.link particle.source {{{vertex_zero.id}}} {{{replicator.id}}} replace:false')
    lx.eval(f'item.link particle.proto {{{item.id}}} {{{replicator.id}}} replace:false')

    return replicator


def rename(name: str) -> str:
    return f'{name} {REPLICATOR_NAME_SUFFIX}'


if __name__ == '__main__':
    h3dd = H3dDebug(enable=False, file=modo.Scene().filename + '.log')
    printd = h3dd.print_debug
    main()
