#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# make merge meshes snapshot for selected meshes
# ================================


import modo
import lx

from h3d_utilites.scripts.h3d_utils import parent_items_to
from h3d_utilites.scripts.h3d_debug import H3dDebug

from h3d_geometry_snapshot.scripts.merge_meshes_snapshot import (
    WORKSPACE_NAME,
    get_workspace_assembly,
    add_to_schematic,
    view_workspace_assembly,
    open_preset_browser,
    restore_preset_browser,
    link_to_merge_meshes,
    filter_working,
    get_grouped_by_replicators,
)


MERGED_NAME_SUFFIX = 'merged'


def main():
    selected: set[modo.Item] = set(modo.Scene().selected)
    printi(selected, 'selected:')

    working_geometry_items = filter_working(selected)
    printi(working_geometry_items, 'working_geometry_items:')

    new_items: list[modo.Item] = []
    # dict(original_item: copy_item)
    copies: dict[modo.Item, modo.Item] = dict()

    preset_browser_opened = open_preset_browser()

    replicators, nonreplicators = get_grouped_by_replicators(working_geometry_items)
    printi(replicators, 'replicators:')
    printi(nonreplicators, 'nonreplicators:')
    if nonreplicators:
        printd('non-replicators branch:')
        merged_tmp, copies_tmp = setup_merge_meshes_individual(nonreplicators, is_replicators=False)
        printi(merged_tmp, 'nonreplicators merged_tmp:')
        printi(copies_tmp, 'nonreplicators copies_tmp:')
        new_items.extend(merged_tmp)
        printd('new_items extended')
        copies.update(copies_tmp)
        printd('copies extended')
    if replicators:
        printd('replicators branch:')
        merged_tmp, copies_tmp = setup_merge_meshes_individual(replicators, is_replicators=True)
        printi(merged_tmp, 'replicators merged_tmp:')
        printi(copies_tmp, 'replicators copies_tmp:')
        new_items.extend(merged_tmp)
        printd('new_items extended')
        copies.update(copies_tmp)
        printd('copies extended')

    printd('parent items:')
    for item in (nonreplicators + replicators):
        printd(f'{item.name=} {item=}', 1)
        parent_items_to([copies[item],], copies.get(item.parent, None))  # type: ignore
        printd(f'{item.name=} parented', 2)

    restore_preset_browser(preset_browser_opened)
    printd('preset browser restored')

    printd('select items:')
    modo.Scene().deselect()
    for item in new_items:
        printd(f'{item.name=} {item=}', 1)
        item.select()


def setup_merge_meshes_individual(items: tuple[modo.Item, ...], is_replicators: bool) -> tuple[
    tuple[modo.Item, ...], dict[modo.Item, modo.Item]
]:
    workspace = get_workspace_assembly(WORKSPACE_NAME)
    view_workspace_assembly(workspace)
    new_items: list[modo.Item] = []
    # dict(original_item: copy_item)
    copies: dict[modo.Item, modo.Item] = dict()
    printi(items, 'setup_merge_meshes_individual input items:', 1)

    for item in items:
        printd(f'item: {item.name=} {item=}', 1)
        add_to_schematic((item,), workspace)
        printd(f'{item=} added to schematic', 2)
        merged_item = modo.Scene().addMesh(rename(item.name))
        printd(f'{merged_item.name=}', 2)
        add_to_schematic((merged_item,), workspace)
        printd(f'{merged_item.name=} added to schematic', 2)
        merged_item.select(replace=True)
        printd(f'{merged_item.name=} selected', 2)

        lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
        lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
        lx.eval('preset.do')
        printd('preset.do', 2)

        merge_meshes_meshop = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
        printd(f'{merge_meshes_meshop.name=}', 2)
        lx.eval('item.channel pmodel.meshmerge$copyNormal true')
        if is_replicators:
            lx.eval('item.channel pmodel.meshmerge$world false')
        printd(f'{merge_meshes_meshop.name=} copyNormal=true + world=false', 2)
        link_to_merge_meshes((merged_item,), merge_meshes_meshop)
        printd(f'{merge_meshes_meshop.name=} link_to_merge_meshes() done', 2)
        new_items.append(merged_item)
        printd(f'{merge_meshes_meshop.name=} append to new_items done', 2)
        copies[item] = merged_item
        printd(f'{merge_meshes_meshop.name=} append to copies done', 2)
    printd('items loop exit', 2)

    printd('exiting from setup_merge_meshes_individual()', 1)
    return (tuple(new_items), copies)


def rename(name: str) -> str:
    return f'{name} {MERGED_NAME_SUFFIX}'


h3dd = H3dDebug(enable=True, file=modo.Scene().filename+'.log')
printi = h3dd.print_items
printd = h3dd.print_debug

if __name__ == '__main__':
    main()
