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


WORKSPACE_NAME = '_Geometry Snapshot'
MERGED_NONREPLICATORS_NAME = 'non-replicators snapshot'
MERGED_REPLICATORS_NAME = 'replicators snapshot'

TYPE_MESH = 'mesh'
TYPE_MESHINST = 'meshInst'
TYPE_REPLICATOR = 'replicator'
TYPE_STATICMESH = 'triSurf'
TYPE_GROUPLOCATOR = 'groupLocator'
TYPE_LOCATOR = 'locator'


def main():
    selected: tuple[modo.Item] = modo.Scene().selected  # type: ignore
    selected_geometry = filter_working(selected)
    if not selected_geometry:
        return

    nonreplicators = filter_nonreplicators(selected_geometry)
    staticmeshes = filter_staticmeshes(selected_geometry)
    converted_staticmeshes = convert_to_mesh(staticmeshes)
    nonreplicators += converted_staticmeshes
    replicators = filter_replicators(selected_geometry)

    workspace_assembly = get_workspace_assembly(WORKSPACE_NAME)
    view_workspace_assembly(workspace_assembly)

    if nonreplicators:
        merged_nonreplicator = new_nonreplicators(nonreplicators, workspace_assembly)

    if replicators:
        merged_replicator = new_replicators(replicators, workspace_assembly)

    modo.Scene().deselect()
    if nonreplicators:
        merged_nonreplicator.select()
    if replicators:
        merged_replicator.select()


def filter_working(items: Iterable[modo.Item]) -> tuple[modo.Item, ...]:
    WORKING_TYPES = (
        'mesh',
        'meshInst',
        'replicator',
        'triSurf',
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


def link_to_merge_meshes(items: Iterable[modo.Item], merge_mesh_meshop: modo.Item):
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


def filter_nonreplicators(items: Iterable[modo.Item]) -> list[modo.Item]:
    NONREPLICATORS_TYPES = (
        TYPE_REPLICATOR,
        TYPE_STATICMESH
    )
    return [i for i in items if i.type not in NONREPLICATORS_TYPES]


def filter_replicators(items: Iterable[modo.Item]) -> list[modo.Item]:
    return [i for i in items if i.type == itype_str(c.REPLICATOR_TYPE)]


def filter_staticmeshes(items: Iterable[modo.Item]) -> list[modo.Item]:
    return [i for i in items if i.type == TYPE_STATICMESH]


def convert_to_mesh(items: Iterable[modo.Item]) -> list[modo.Item]:
    if not items:
        return []

    modo.Scene().deselect()
    for item in items:
        if not item:
            continue
        item.select()
    lx.eval('item.setType mesh locator')

    return modo.Scene().selected


def new_nonreplicators(items: Iterable[modo.Item], workspace: modo.Item) -> modo.Item:
    add_to_schematic(items, workspace)
    merged_nonreplicators = modo.Scene().addMesh(MERGED_NONREPLICATORS_NAME)
    parent_items_to([merged_nonreplicators, ], parent=None, index=0)
    add_to_schematic((merged_nonreplicators,), workspace)
    merged_nonreplicators.select(replace=True)

    preset_browser_opened = open_preset_browser()
    lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
    lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
    lx.eval('preset.do')
    restore_preset_browser(preset_browser_opened)

    merge_meshes_meshop_nonreplicators = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
    lx.eval('item.channel pmodel.meshmerge$copyNormal true')
    link_to_merge_meshes(items, merge_meshes_meshop_nonreplicators)

    mesh_id = merged_nonreplicators.id
    meshop_id = merge_meshes_meshop_nonreplicators
    lx.eval(f'deformer.freeze false deformer:{meshop_id} mesh:{{{mesh_id}}}')

    return merged_nonreplicators


def new_replicators(items: Iterable[modo.Item], workspace: modo.Item) -> modo.Item:
    add_to_schematic(items, workspace)
    merged_replicators = modo.Scene().addMesh(MERGED_REPLICATORS_NAME)
    parent_items_to([merged_replicators, ], parent=None, index=0)
    add_to_schematic((merged_replicators,), workspace)
    merged_replicators.select(replace=True)

    preset_browser_opened = open_preset_browser()
    lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
    lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
    lx.eval('preset.do')
    restore_preset_browser(preset_browser_opened)

    merge_meshes_meshop_replicators = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
    lx.eval('item.channel pmodel.meshmerge$copyNormal true')
    lx.eval('item.channel pmodel.meshmerge$world false')
    link_to_merge_meshes(items, merge_meshes_meshop_replicators)

    mesh_id = merged_replicators.id
    meshop_id = merge_meshes_meshop_replicators
    lx.eval(f'deformer.freeze false deformer:{meshop_id} mesh:{{{mesh_id}}}')

    return merged_replicators


if __name__ == '__main__':
    main()
