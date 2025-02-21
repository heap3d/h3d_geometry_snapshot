#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# make merge meshes snapshot for selected meshes
# ================================


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
    nonreplicators: tuple[modo.Item] = tuple(
        i for i in selected_geometry
        if i.type != itype_str(c.REPLICATOR_TYPE)
        )  # type:ignore
    replicators: tuple[modo.Item] = tuple(
        i for i in selected_geometry
        if i.type == itype_str(c.REPLICATOR_TYPE)
        )  # type:ignore

    if not selected_geometry:
        return
    workspace = get_workspace_assembly(WORKSPACE_NAME)
    view_workspace_assembly(workspace)
    preset_browser_opened = open_preset_browser()
    new_items: list[modo.Item] = []

    # dict(original: copy)
    copies: dict[modo.Item, modo.Item] = dict()

    for nonreplicator in nonreplicators:
        add_to_schematic((nonreplicator,), workspace)
        merged_nonreplicator = modo.Scene().addMesh(rename(nonreplicator.name))
        add_to_schematic((merged_nonreplicator,), workspace)
        merged_nonreplicator.select(replace=True)

        lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
        lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
        lx.eval('preset.do')

        merge_meshes_meshop_nonreplicator = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
        lx.eval('item.channel pmodel.meshmerge$copyNormal true')
        link_to_merge_meshes((nonreplicator,), merge_meshes_meshop_nonreplicator)
        new_items.append(merged_nonreplicator)

        copies[nonreplicator] = merged_nonreplicator

    for replicator in replicators:
        add_to_schematic(replicators, workspace)
        merged_replicator = modo.Scene().addMesh(rename(replicator.name))
        add_to_schematic((merged_replicator,), workspace)
        merged_replicator.select(replace=True)

        lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
        lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
        lx.eval('preset.do')

        merge_meshes_meshop_replicator = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
        lx.eval('item.channel pmodel.meshmerge$copyNormal true')
        lx.eval('item.channel pmodel.meshmerge$world false')
        link_to_merge_meshes((replicator,), merge_meshes_meshop_replicator)
        new_items.append(merged_replicator)

        copies[replicator] = merged_replicator

    restore_preset_browser(preset_browser_opened)

    for item in nonreplicators:
        parent_items_to([copies[item],], copies.get(item.parent, None))  # type: ignore

    for item in replicators:
        parent_items_to([copies[item],], copies.get(item.parent, None))  # type: ignore

    modo.Scene().deselect()
    for item in new_items:
        item.select()


def rename(name: str) -> str:
    return f'{name} {MERGED_NAME_SUFFIX}'


def new_nonreplicator_snapshot():
    add_to_schematic((nonreplicator,), workspace)
    merged_nonreplicator = modo.Scene().addMesh(rename(nonreplicator.name))
    add_to_schematic((merged_nonreplicator,), workspace)
    merged_nonreplicator.select(replace=True)

    lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
    lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
    lx.eval('preset.do')

    merge_meshes_meshop_nonreplicator = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
    lx.eval('item.channel pmodel.meshmerge$copyNormal true')
    link_to_merge_meshes((nonreplicator,), merge_meshes_meshop_nonreplicator)
    new_items.append(merged_nonreplicator)

    copies[nonreplicator] = merged_nonreplicator


def new_replicator_snapshot():
    add_to_schematic(replicators, workspace)
    merged_replicator = modo.Scene().addMesh(rename(replicator.name))
    add_to_schematic((merged_replicator,), workspace)
    merged_replicator.select(replace=True)

    lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
    lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
    lx.eval('preset.do')

    merge_meshes_meshop_replicator = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
    lx.eval('item.channel pmodel.meshmerge$copyNormal true')
    lx.eval('item.channel pmodel.meshmerge$world false')
    link_to_merge_meshes((replicator,), merge_meshes_meshop_replicator)
    new_items.append(merged_replicator)

    copies[replicator] = merged_replicator


def filter_nonreplicators():
    ...


def filter_replicators():
    ...


if __name__ == '__main__':
    main()
