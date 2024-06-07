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
from enum import Enum


class Node(Enum):
    ADD = 'add'
    SET = 'set'
    REMOVE = 'remove'
    TOGGLE = 'toggle'


def select_schematic_nodes(items: list[modo.Item], mode: str = Node.ADD) -> None:
    smart_mode = mode
    # drop selection
    if mode == Node.SET:
        smart_mode = Node.ADD
        lx.eval('select.clear item')
        lx.eval('select.drop schmNode')
        lx.eval('select.drop channel')
        lx.eval('select.drop link')

    # select items
    for item in items:
        schematic_node = item.itemGraph('schmItem').forward()[-1]  # type: ignore
        lx.eval(f'select.node {schematic_node.id} {smart_mode} {schematic_node.id}')


def main():
    ...


if __name__ == '__main__':
    main()
