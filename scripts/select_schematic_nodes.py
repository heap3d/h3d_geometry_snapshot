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
from scripts.merge_meshes_snapshot import select_schematic_nodes


def main():
    selected_items = modo.Scene().selected
    select_schematic_nodes(selected_items)


if __name__ == '__main__':
    main()
