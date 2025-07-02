#!/usr/bin/python
# ================================
# (C)2024-2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# make replicator for selected items snapshot
# ================================

import modo
import modo.constants as c
import lx

from h3d_utilites.scripts.h3d_utils import parent_items_to

from scripts.merge_meshes_snapshot import (
    WORKSPACE_NAME,
    get_workspace_assembly,
    view_workspace_assembly,
    add_to_schematic,
)


REPLICATOR_NAME_SUFFIX = '_snapshot'
PARENT_MESH_NAME_SUFFIX = '_container'
VERTEX_ZERO_NAME = 'vertex_ZERO'


def main():
    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    if not selected:
        return
    replicator = replicate(selected)
    replicator.select(replace=True)


def replicate(items: list[modo.Item]) -> modo.Item:
    if not items:
        raise ValueError('No items provided')

    basename = items[0].name
    vertex_zero = get_vertex_zero(VERTEX_ZERO_NAME)
    parent_mesh = new_mesh_vertex_at_zero(f'{basename}{PARENT_MESH_NAME_SUFFIX}')
    parent_items_to(items, parent_mesh)

    replicator: modo.Item = modo.Scene().addItem(itype='replicator', name=f'{basename}{REPLICATOR_NAME_SUFFIX}')
    activate_replicator_hierarchy(replicator)
    activate_oc_motion_blur(replicator)

    workspace = get_workspace_assembly(WORKSPACE_NAME)
    view_workspace_assembly(workspace)
    add_to_schematic((vertex_zero, parent_mesh, replicator), workspace)
    lx.eval(f'item.link particle.source {{{vertex_zero.id}}} {{{replicator.id}}} replace:false')
    lx.eval(f'item.link particle.proto {{{parent_mesh.id}}} {{{replicator.id}}} replace:false')

    return replicator


def get_vertex_zero(name: str) -> modo.Item:
    try:
        return modo.Scene().item(name)
    except LookupError:
        return new_mesh_vertex_at_zero(name)


def new_mesh_vertex_at_zero(name: str) -> modo.Item:
    vertex_zero_mesh = modo.Scene().addMesh(name)
    vertex_zero_mesh.select(replace=True)
    lx.eval('tool.set prim.makeVertex on 0')
    lx.eval('tool.attr prim.makeVertex cenX 0.0')
    lx.eval('tool.attr prim.makeVertex cenY 0.0')
    lx.eval('tool.attr prim.makeVertex cenZ 0.0')
    lx.eval('tool.apply')
    lx.eval('tool.set prim.makeVertex off 0')
    return vertex_zero_mesh


def activate_replicator_hierarchy(item: modo.Item):
    hierarchy = 'hierarchy'
    try:
        channel = item.channel(hierarchy)
        if channel:
            channel.set(True)
    except LookupError:
        print(f'channel {hierarchy} not found for item {item.name}')


def activate_oc_motion_blur(item: modo.Item):
    lx.eval(f'item.channel oc_objectMotionBlur true item:{{{item.id}}}')


if __name__ == '__main__':
    main()
