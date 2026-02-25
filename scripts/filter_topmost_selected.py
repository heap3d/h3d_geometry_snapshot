#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# filter topmost selected items in the hierarchy
# ================================

from typing import Iterable

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import select_if_exists


def main():
    selected_items: list[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    topmost_items = get_topmost_items(selected_items)
    select_if_exists(topmost_items)


def get_topmost_items(items: Iterable[modo.Item]) -> list[modo.Item]:
    if not items:
        return []

    topmost_items = set()

    for item in items:
        filtered_parents = [p for p in item.parents if p in items]
        if not filtered_parents:
            topmost_items.add(item)
        else:
            topmost_items.add(filtered_parents[-1])

    return list(topmost_items)


if __name__ == '__main__':
    main()
