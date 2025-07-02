#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# run replicator_snapshot for each selected item
# ================================

import modo
import modo.constants as c

from scripts.replicator_snapshot import replicate


def main():
    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    if not selected:
        return

    replicators: list[modo.Item] = []
    for item in selected:
        replicator = replicate([item,])
        replicators.append(replicator)

    if not replicators:
        return

    modo.Scene().deselect()
    for item in replicators:
        item.select()


if __name__ == '__main__':
    main()
