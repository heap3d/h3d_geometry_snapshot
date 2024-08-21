#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# make merge selected meshes snapshot
# ================================


import modo
import lx


WORKSPACE_NAME = '_Geometry Snapshot'
GEOMETRY_SNAPSHOT_NAME = 'geometry snapshot'


class NodeSelection():
    ADD = 'add'
    SET = 'set'
    REMOVE = 'remove'
    TOGGLE = 'toggle'


def select_schematic_nodes(items: list[modo.Item], mode: str = NodeSelection.ADD) -> None:
    for item in items:
        schematic_node = item.itemGraph('schmItem').forward()[-1]  # type: ignore
        evalstr = f'select.node {schematic_node.id} {mode} {schematic_node.id}'
        print(evalstr)
        lx.eval(evalstr)


def get_workspace(name: str) -> modo.Item:
    if not name:
        raise ValueError('name is empty')
    # try to find workspace by name
    assemblies = modo.Scene().getGroups('assembly')
    for workspace in assemblies:
        if workspace.name == name:
            return workspace

    # create new if not found
    lx.eval(f'schematic.createWorkspace "{name}" true')
    return get_workspace(name)


def view_workspace(workspace: modo.Item):
    lx.eval(f'schematic.viewAssembly group:{workspace.id}')


def add_to_schematic(items: list[modo.Item], workspace: modo.Item) -> None:
    for item in items:
        item.select(replace=True)
        lx.eval('select.drop schmNode')
        lx.eval('select.drop link')
        lx.eval(f'schematic.addItem {{{item.id}}} {workspace.id} true')
        lx.eval(f'schematic.addChannel group:{workspace.id}')


def link_to_merge_meshes(items: list[modo.Item], merge_mesh_meshop: modo.Item):
    for item in items:
        lx.eval(f'item.link pmodel.meshmerge.graph {{{item.id}}} {merge_mesh_meshop.id} replace:false')


def open_preset_browser() -> bool:
    preset_browser_opened = lx.eval('layout.createOrClose PresetBrowser presetBrowserPalette ?')
    if not preset_browser_opened:
        lx.eval(
            'layout.createOrClose PresetBrowser presetBrowserPalette true Presets '
            'width:800 height:600 persistent:true style:palette'
        )

    return preset_browser_opened


def restore_preset_browser(opened: bool) -> None:
    if not opened:
        lx.eval(
            'layout.createOrClose PresetBrowser presetBrowserPalette false Presets width:800 height:600 '
            'persistent:true style:palette'
        )


def main():
    # filter geometry items
    lx.eval('selectPattern.lookAtSelect true')
    lx.eval('selectPattern.none')
    lx.eval('selectPattern.toggleMesh true')
    lx.eval('selectPattern.toggleInstance true')
    lx.eval('selectPattern.toggleReplic true')
    lx.eval('selectPattern.apply set')
    selected_geometry = modo.Scene().selected

    workspace = get_workspace(WORKSPACE_NAME)
    view_workspace(workspace)
    add_to_schematic(selected_geometry, workspace)
    geometry_snapshot = modo.Scene().addMesh(GEOMETRY_SNAPSHOT_NAME)
    add_to_schematic((geometry_snapshot,), workspace)
    geometry_snapshot.select(replace=True)

    preset_browser_opened = open_preset_browser()
    lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
    lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
    lx.eval('preset.do')
    restore_preset_browser(preset_browser_opened)

    merge_meshes_meshop = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
    lx.eval('item.channel pmodel.meshmerge$copyNormal true')
    link_to_merge_meshes(selected_geometry, merge_meshes_meshop)

    geometry_snapshot.select(replace=True)


if __name__ == '__main__':
    main()
