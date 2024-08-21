#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# make replicator for selected items snapshot
# ================================


import modo
import lx

from h3d_geometry_snapshot.scripts.merge_meshes_snapshot import (
    WORKSPACE_NAME,
    get_workspace,
    view_workspace,
    add_to_schematic,
)

from h3d_utilites.scripts.h3d_utils import parent_items_to
from h3d_utilites.scripts.h3d_debug import H3dDebug


REPLICATOR_NAME = 'replicator snapshot'
PARENT_MESH_NAME = 'parent mesh'
VERTEX_ZERO_NAME = 'vertex_ZERO'


def create_vertex_at_zero(name: str) -> modo.Item:
    vertex_zero_mesh = modo.Scene().addMesh(name)
    vertex_zero_mesh.select(replace=True)
    lx.eval('tool.set prim.makeVertex on 0')
    lx.eval('tool.apply')
    lx.eval('tool.set prim.makeVertex off 0')
    return vertex_zero_mesh


def replicator_link_prototype(item: modo.Item, replicator: modo.Item) -> None:
    lx.eval(f'item.link particle.proto {item.id} {replicator.id} replace:false')


def get_vertex_zero(name: str) -> modo.Item:
    try:
        return modo.Scene().item(name)
    except LookupError:
        return create_vertex_at_zero(name)


def main():
    selected = modo.Scene().selected

    vertex_zero = get_vertex_zero(VERTEX_ZERO_NAME)
    parent_mesh = modo.Scene().addMesh(PARENT_MESH_NAME)
    parent_items_to(selected, parent_mesh)
    replicator = modo.Scene().addItem(itype='replicator', name=REPLICATOR_NAME)
    replicator.channel('hierarchy').set(True)

    workspace = get_workspace(WORKSPACE_NAME)
    view_workspace(workspace)
    add_to_schematic((vertex_zero, parent_mesh, replicator), workspace)
    lx.eval(f'item.link particle.source {vertex_zero.id} {replicator.id} replace:false')
    lx.eval(f'item.link particle.proto {parent_mesh.id} {replicator.id} replace:false')

    replicator.select(replace=True)


if __name__ == '__main__':
    h3dd = H3dDebug(enable=False, file='replicator snapshot.log')
    main()
