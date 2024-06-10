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
        lx.eval(f'schematic.addItem {item.id} {workspace.id} true')
        lx.eval(f'schematic.addChannel group:{workspace.id}')


def main():
    # TODO filter mesh items
    selected = modo.Scene().selected
    workspace = get_workspace(WORKSPACE_NAME)
    view_workspace(workspace)

    add_to_schematic(selected, workspace)


if __name__ == '__main__':
    main()
