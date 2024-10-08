#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# make merge meshes snapshot setup for each selected mesh
# ================================


import modo
import lx
import modo.constants as c
from typing import Iterable

from h3d_utilites.scripts.h3d_utils import itype_str, parent_items_to
from h3d_utilites.scripts.h3d_debug import H3dDebug


WORKSPACE_NAME = '_Geometry Snapshot'
MERGED_NONREPLICATORS_NAME = 'merged non-replicators'
MERGED_REPLICATORS_NAME = 'merged replicators'


def main():
    selected: set[modo.Item] = set(modo.Scene().selected)

    working_geometry_items = filter_working(selected)

    replicators, nonreplicators = get_grouped_by_replicators(working_geometry_items)
    if nonreplicators:
        merged_nonreplicators = setup_merge_meshes(nonreplicators, is_replicators=False)
    if replicators:
        merged_replicators = setup_merge_meshes(replicators, is_replicators=True)

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


def get_grouped_by_replicators(items: Iterable[modo.Item]) -> tuple[tuple[modo.Item, ...], tuple[modo.Item, ...]]:
    items_set = set(items)
    replicators: set[modo.Item] = {i for i in items_set if i.type == itype_str(c.REPLICATOR_TYPE)}
    nonreplicators: set[modo.Item] = items_set - replicators

    return tuple(replicators), tuple(nonreplicators)


def get_workspace_assembly(name: str) -> modo.Item:
    """Returns an existing workspace assembly, creates a new one if the assembly does not exist

    Args:
        name (str): name of the worspace assembly

    Raises:
        ValueError: if no name provided

    Returns:
        modo.Item: workspace assembly
    """
    printd('enter get_workspace_assembly()')
    if not name:
        raise ValueError('name is empty')

    # try to find a workspace by name
    assemblies = modo.Scene().getGroups('assembly')
    for workspace in assemblies:
        if workspace.name == name:

            return workspace

    # create a new one if not found
    lx.eval(f'schematic.createWorkspace "{name}" true')

    return get_workspace_assembly(name)


def view_workspace_assembly(workspace: modo.Item):
    lx.eval(f'schematic.viewAssembly group:{workspace.id}')


def setup_merge_meshes(items: tuple[modo.Item, ...], is_replicators: bool) -> modo.Item:
    MERGED_NAME = {
        False: MERGED_NONREPLICATORS_NAME,
        True: MERGED_REPLICATORS_NAME,
    }
    workspace_assembly = get_workspace_assembly(WORKSPACE_NAME)
    view_workspace_assembly(workspace_assembly)

    add_to_schematic(items, workspace_assembly)
    merged_mesh_item = modo.Scene().addMesh(MERGED_NAME[is_replicators])
    parent_items_to([merged_mesh_item,], None, 0)  # type: ignore
    add_to_schematic((merged_mesh_item,), workspace_assembly)
    merged_mesh_item.select(replace=True)

    preset_browser_opened = open_preset_browser()
    lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
    lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
    lx.eval('preset.do')
    restore_preset_browser(preset_browser_opened)

    merge_meshes_meshop = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
    lx.eval('item.channel pmodel.meshmerge$copyNormal true')
    if is_replicators:
        lx.eval('item.channel pmodel.meshmerge$world false')
    link_to_merge_meshes(items, merge_meshes_meshop)

    return merged_mesh_item


def add_to_schematic(items: tuple[modo.Item, ...], workspace: modo.Item):
    for item in items:
        item.select(replace=True)
        lx.eval('select.drop schmNode')
        lx.eval('select.drop link')
        lx.eval(f'schematic.addItem {{{item.id}}} {workspace.id} true')
        lx.eval(f'schematic.addChannel group:{workspace.id}')


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


def link_to_merge_meshes(items: tuple[modo.Item, ...], merge_mesh_meshop: modo.Item):
    printi(items, 'link_to_merge_meshes() input items', 3)
    for item in items:
        printd(f'{item.name=}')
        lx.eval(f'item.link pmodel.meshmerge.graph {{{item.id}}} {{{merge_mesh_meshop.id}}} replace:false')


class NodeSelection():
    ADD = 'add'
    SET = 'set'
    REMOVE = 'remove'
    TOGGLE = 'toggle'


def select_schematic_nodes(items: list[modo.Item], mode: str = NodeSelection.ADD):
    for item in items:
        schematic_node = item.itemGraph('schmItem').forward()[-1]  # type: ignore
        evalstr = f'select.node {schematic_node.id} {mode} {schematic_node.id}'
        print(evalstr)
        lx.eval(evalstr)


h3dd = H3dDebug(enable=True, file=modo.Scene().filename+'.log')
printi = h3dd.print_items
printd = h3dd.print_debug

if __name__ == '__main__':
    main()
