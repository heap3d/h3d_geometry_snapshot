#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select schematic nodes for selected items
# ================================


import modo
from .merge_selected_meshes_snapshot import select_schematic_nodes, Node


def main():
    selected_items = modo.Scene().selected
    select_schematic_nodes(selected_items, Node.SET)


if __name__ == '__main__':
    main()
