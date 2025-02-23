#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# make merge meshes snapshot setup for each selected mesh
# ================================


from typing import Iterable

import modo
import lx
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import itype_str, parent_items_to
from h3d_utilites.scripts.h3d_debug import H3dDebug


WORKSPACE_NAME = '_Geometry Snapshot'
MERGED_NONREPLICATORS_NAME = 'merged non-replicators'
MERGED_REPLICATORS_NAME = 'merged replicators'


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
    workspace_assembly = get_workspace_assembly(WORKSPACE_NAME)
    view_workspace_assembly(workspace_assembly)
    if nonreplicators:
        add_to_schematic(nonreplicators, workspace_assembly)
        merged_nonreplicators = modo.Scene().addMesh(MERGED_NONREPLICATORS_NAME)
        parent_items_to([merged_nonreplicators, ], parent=None, index=0)  # type: ignore
        add_to_schematic((merged_nonreplicators,), workspace_assembly)
        merged_nonreplicators.select(replace=True)

        preset_browser_opened = open_preset_browser()
        lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
        lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
        lx.eval('preset.do')
        restore_preset_browser(preset_browser_opened)

        merge_meshes_meshop_nonreplicators = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
        lx.eval('item.channel pmodel.meshmerge$copyNormal true')
        link_to_merge_meshes(nonreplicators, merge_meshes_meshop_nonreplicators)

    if replicators:
        add_to_schematic(replicators, workspace_assembly)
        merged_replicators = modo.Scene().addMesh(MERGED_REPLICATORS_NAME)
        parent_items_to([merged_replicators, ], parent=None, index=0)  # type: ignore
        add_to_schematic((merged_replicators,), workspace_assembly)
        merged_replicators.select(replace=True)

        preset_browser_opened = open_preset_browser()
        lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
        lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
        lx.eval('preset.do')
        restore_preset_browser(preset_browser_opened)

        merge_meshes_meshop_replicators = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
        lx.eval('item.channel pmodel.meshmerge$copyNormal true')
        lx.eval('item.channel pmodel.meshmerge$world false')
        link_to_merge_meshes(replicators, merge_meshes_meshop_replicators)

    modo.Scene().deselect()
    if nonreplicators:
        merged_nonreplicators.select()
    if replicators:
        merged_replicators.select()


def filter_working(items: Iterable[modo.Item]) -> tuple[modo.Item, ...]:
    WORKING_TYPES = (
        'mesh',
        'meshInst',
        'replicator',
    )
    return tuple(i for i in items if i.type in WORKING_TYPES)


def get_workspace_assembly(name: str) -> modo.Item:
    if not name:
        raise ValueError('name is empty')

    assemblies = modo.Scene().getGroups('assembly')
    for workspace in assemblies:
        if workspace.name == name:
            return workspace

    lx.eval(f'schematic.createWorkspace "{name}" true')
    return get_workspace_assembly(name)


def view_workspace_assembly(workspace: modo.Item):
    lx.eval(f'schematic.viewAssembly group:{{{workspace.id}}}')


def add_to_schematic(items: Iterable[modo.Item], workspace: modo.Item):
    for item in items:
        item.select(replace=True)
        lx.eval('select.drop schmNode')
        lx.eval('select.drop link')
        lx.eval(f'schematic.addItem {{{item.id}}} {{{workspace.id}}} true')
        lx.eval(f'schematic.addChannel group:{{{workspace.id}}}')


def open_preset_browser() -> bool:
    preset_browser_opened = lx.eval('layout.createOrClose PresetBrowser presetBrowserPalette ?')
    if not preset_browser_opened:
        lx.eval(
            'layout.createOrClose PresetBrowser presetBrowserPalette true Presets '
            'width:800 height:600 persistent:true style:palette'
        )

    return bool(preset_browser_opened)


def restore_preset_browser(opened: bool):
    if not opened:
        lx.eval(
            'layout.createOrClose PresetBrowser presetBrowserPalette false Presets width:800 height:600 '
            'persistent:true style:palette'
        )


def link_to_merge_meshes(items: tuple[modo.Item], merge_mesh_meshop: modo.Item):
    for item in items:
        lx.eval(f'item.link pmodel.meshmerge.graph {{{item.id}}} {{{merge_mesh_meshop.id}}} replace:false')


class NodeSelection():
    ADD = 'add'
    SET = 'set'
    REMOVE = 'remove'
    TOGGLE = 'toggle'


def select_schematic_nodes(items: list[modo.Item], mode: str = NodeSelection.ADD) -> None:
    for item in items:
        schematic_node = item.itemGraph('schmItem').forward()[-1]  # type: ignore
        evalstr = f'select.node {{{schematic_node.id}}} {mode} {{{schematic_node.id}}}'
        print(evalstr)
        lx.eval(evalstr)


if __name__ == '__main__':
    h3dd = H3dDebug(enable=False, file=modo.Scene().filename+'.log')
    main()
