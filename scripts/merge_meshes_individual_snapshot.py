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

from h3d_utilites.scripts.h3d_utils import itype_str
from h3d_utilites.scripts.h3d_debug import H3dDebug

from h3d_geometry_snapshot.scripts.merge_meshes_snapshot import (
    WORKSPACE_NAME,
    get_workspace_assembly,
    add_to_schematic,
    view_workspace_assembly,
    open_preset_browser,
    restore_preset_browser,
    link_to_merge_meshes,
)


MERGED_NAME_SUFFIX = 'merged'


def main():
    # filter geometry items
    lx.eval('selectPattern.lookAtSelect true')
    lx.eval('selectPattern.none')
    lx.eval('selectPattern.toggleMesh true')
    lx.eval('selectPattern.toggleInstance true')
    lx.eval('selectPattern.toggleReplic true')
    lx.eval('selectPattern.apply set')
    selected_geometry: tuple[modo.Item] = modo.Scene().selected  # type:ignore
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

    for nonreplicator in nonreplicators:
        add_to_schematic((nonreplicator,), workspace)
        merged_nonreplicators = modo.Scene().addMesh(rename(nonreplicator.name))
        add_to_schematic((merged_nonreplicators,), workspace)
        merged_nonreplicators.select(replace=True)

        lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
        lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
        lx.eval('preset.do')

        merge_meshes_meshop_nonreplicators = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
        lx.eval('item.channel pmodel.meshmerge$copyNormal true')
        link_to_merge_meshes((nonreplicator,), merge_meshes_meshop_nonreplicators)
        new_items.append(merged_nonreplicators)

    for replicator in replicators:
        add_to_schematic(replicators, workspace)
        merged_replicators = modo.Scene().addMesh(rename(replicator.name))
        add_to_schematic((merged_replicators,), workspace)
        merged_replicators.select(replace=True)

        lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
        lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
        lx.eval('preset.do')

        merge_meshes_meshop_replicators = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
        lx.eval('item.channel pmodel.meshmerge$copyNormal true')
        lx.eval('item.channel pmodel.meshmerge$world false')
        link_to_merge_meshes((replicator,), merge_meshes_meshop_replicators)
        new_items.append(merged_replicators)

    restore_preset_browser(preset_browser_opened)
    modo.Scene().deselect()
    for item in new_items:
        item.select()


def rename(name: str) -> str:
    return f'{name} {MERGED_NAME_SUFFIX}'


if __name__ == '__main__':
    h3dd = H3dDebug(enable=False, file=modo.Scene().filename+'.log')
    main()
