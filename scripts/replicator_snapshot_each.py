#!/usr/bin/python
# ================================
# (C)2025-2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# run replicator_snapshot for each selected item
# ================================

import modo
import modo.constants as c

from scripts.replicator_snapshot import replicate

from h3d_utilites.scripts.h3d_utils import execution_time_alarm


@execution_time_alarm('Replicator Snapshot Each')
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
