#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# make merge meshes snapshot for selected meshes
# ================================


from typing import Iterable

import modo
import lx
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import itype_str, parent_items_to

from h3d_geometry_snapshot.scripts.merge_meshes_snapshot import (
    WORKSPACE_NAME,
    get_workspace_assembly,
    add_to_schematic,
    view_workspace_assembly,
    open_preset_browser,
    restore_preset_browser,
    link_to_merge_meshes,
    filter_working,
)


MERGED_NAME_SUFFIX = 'merged'


def main():
    selected: tuple[modo.Item] = modo.Scene().selected  # type: ignore
    selected_geometry = filter_working(selected)
    nonreplicators = filter_nonreplicators(selected_geometry)
    replicators = filter_replicators(selected_geometry)

    if not selected_geometry:
        return

    workspace = get_workspace_assembly(WORKSPACE_NAME)
    view_workspace_assembly(workspace)
    preset_browser_opened = open_preset_browser()

    new_nonreplicators = new_nonreplicators_in_schematic(nonreplicators, workspace)
    copies = dict(zip(nonreplicators, new_nonreplicators))

    new_replicators = new_replicators_in_schematic(replicators, workspace)
    copies.update(zip(replicators, new_replicators))

    restore_preset_browser(preset_browser_opened)

    for item in nonreplicators + replicators:
        parent_items_to([copies[item],], copies.get(item.parent, None))  # type: ignore

    modo.Scene().deselect()
    for item in new_nonreplicators + new_replicators:
        item.select()


def snapshot_name(name: str) -> str:
    return f'{name} {MERGED_NAME_SUFFIX}'


def new_nonreplicators_in_schematic(items: Iterable[modo.Item], workspace: modo.Item) -> list[modo.Item]:
    add_to_schematic(items, workspace)
    new_items: list[modo.Item] = []
    for item in items:
        merged_nonreplicator = modo.Scene().addMesh(snapshot_name(item.name))
        add_to_schematic((merged_nonreplicator,), workspace)
        merged_nonreplicator.select(replace=True)

        lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
        lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
        lx.eval('preset.do')

        merge_meshes_meshop_nonreplicator = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
        lx.eval('item.channel pmodel.meshmerge$copyNormal true')
        link_to_merge_meshes((item,), merge_meshes_meshop_nonreplicator)
        new_items.append(merged_nonreplicator)

    return new_items


def new_replicators_in_schematic(items: Iterable[modo.Item], workspace: modo.Item) -> list[modo.Item]:
    add_to_schematic(items, workspace)
    new_items: list[modo.Item] = []
    for item in items:
        merged_replicator = modo.Scene().addMesh(snapshot_name(item.name))
        add_to_schematic((merged_replicator,), workspace)
        merged_replicator.select(replace=True)

        lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
        lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
        lx.eval('preset.do')

        merge_meshes_meshop_replicator = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
        lx.eval('item.channel pmodel.meshmerge$copyNormal true')
        lx.eval('item.channel pmodel.meshmerge$world false')
        link_to_merge_meshes((item,), merge_meshes_meshop_replicator)
        new_items.append(merged_replicator)

    return new_items


def filter_nonreplicators(items: Iterable[modo.Item]) -> tuple[modo.Item]:
    return tuple(i for i in items if i.type != itype_str(c.REPLICATOR_TYPE))  # type:ignore


def filter_replicators(items: Iterable[modo.Item]) -> tuple[modo.Item]:
    return tuple(i for i in items if i.type == itype_str(c.REPLICATOR_TYPE))  # type:ignore


if __name__ == '__main__':
    main()
