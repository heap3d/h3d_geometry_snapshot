#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select top-level parents for selected items or keep selection if item at the root of the hierarchy
# ================================

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import select_if_exists


def main():
    selected_items: list[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)

    item_parents = set()
    for item in selected_items:
        parents = item.parents
        if parents is not None:
            item_parents.add(parents[-1])
        else:
            item_parents.add(item)

    select_if_exists(item_parents)


if __name__ == '__main__':
    main()
