#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# make merge meshes snapshot for selected meshes
# ================================


from typing import Iterable

import modo
import lx

from h3d_utilites.scripts.h3d_utils import (
    parent_items_to,
    match_pos_rot,
    match_scl,
    get_source_of_instance,
    set_description_tag,
    get_user_value,
    get_parent_index,
)

from h3d_geometry_snapshot.scripts.merge_meshes_snapshot import (
    WORKSPACE_NAME,
    get_workspace_assembly,
    add_to_schematic,
    view_workspace_assembly,
    open_preset_browser,
    restore_preset_browser,
    link_to_merge_meshes,
    filter_nonreplicators,
    filter_replicators,
    filter_staticmeshes,
    convert_to_mesh,
    TYPE_MESH,
    TYPE_MESHINST,
    TYPE_STATICMESH,
    TYPE_REPLICATOR,
    TYPE_LOCATOR,
    TYPE_GROUPLOCATOR,
)

from h3d_utilites.scripts.h3d_debug import h3dd, prints, fn_in, fn_out


SNAPSHOT_NAME_SUFFIX = '_snapshot'
MESHINNST_NAME_SUFFIX = '_meshInst'
MESHINST_INFO_TAG = 'meshInst:'
FREEZE_MESHOP = 'h3d_gss_freeze'


def main():
    selected: tuple[modo.Item] = modo.Scene().selected  # type: ignore
    selected_geometry = filter_working_hierarchy(selected)
    if not selected_geometry:
        return

    nonreplicators = filter_nonreplicators(selected_geometry)
    staticmeshes = filter_staticmeshes(selected_geometry)
    converted_staticmeshes = convert_to_mesh(staticmeshes)
    nonreplicators += converted_staticmeshes
    prints(nonreplicators)
    replicators = filter_replicators(selected_geometry)
    freeze = get_user_value(FREEZE_MESHOP)

    workspace = get_workspace_assembly(WORKSPACE_NAME)
    view_workspace_assembly(workspace)
    preset_browser_opened = open_preset_browser()

    new_nonreplicators = new_individual_nonreplicators(nonreplicators, workspace, freeze)
    copies = dict(zip(nonreplicators, new_nonreplicators))

    new_replicators = new_individual_replicators(replicators, workspace, freeze)
    copies.update(zip(replicators, new_replicators))

    restore_preset_browser(preset_browser_opened)

    for item in nonreplicators + replicators:
        parent_items_to([copies[item],], copies.get(item.parent, None), get_parent_index(item))  # type: ignore

    modo.Scene().deselect()
    for item in new_nonreplicators + new_replicators:
        item.select()


def filter_working_hierarchy(items: Iterable[modo.Item]):
    WORKING_TYPES = (
        TYPE_MESH,
        TYPE_MESHINST,
        TYPE_REPLICATOR,
        TYPE_STATICMESH,
        TYPE_GROUPLOCATOR,
        TYPE_LOCATOR,
    )

    return tuple(i for i in items if i.type in WORKING_TYPES)


def is_hierarchy_item(item: modo.Item) -> bool:
    HIERARCHY_TYPES = (
        TYPE_GROUPLOCATOR,
        TYPE_LOCATOR,
    )

    return item.type in HIERARCHY_TYPES


def snapshot_name(name: str) -> str:
    return f'{name}{SNAPSHOT_NAME_SUFFIX}'


def new_individual_nonreplicators(items: Iterable[modo.Item], workspace: modo.Item, freeze: bool) -> list[modo.Item]:
    add_to_schematic(items, workspace)
    new_items: list[modo.Item] = []
    for item in items:
        if not is_hierarchy_item(item):
            new_items.append(new_nonreplicator(item, workspace, freeze))
        else:
            new_items.append(new_hierarchy_item(item))

    return new_items


def new_nonreplicator(item: modo.Item, workspace: modo.Item, freeze: bool) -> modo.Item:
    fn_in()
    prints(item)
    merged_nonreplicator = modo.Scene().addMesh(snapshot_name(item.name))
    prints(merged_nonreplicator)

    add_to_schematic((merged_nonreplicator,), workspace)
    merged_nonreplicator.select(replace=True)

    match_pos_rot(merged_nonreplicator, item)
    match_scl(merged_nonreplicator, item)

    if item.type == TYPE_MESHINST:
        instance_source = get_source_of_instance(item)
        if instance_source:
            instance_info = f'{MESHINST_INFO_TAG}{instance_source.name}'
            set_description_tag(merged_nonreplicator, instance_info)
            merged_nonreplicator.name = f'{merged_nonreplicator.name}{MESHINNST_NAME_SUFFIX}'

    lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
    lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
    lx.eval('preset.do')

    merge_meshes_meshop_nonreplicator = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
    lx.eval('item.channel pmodel.meshmerge$copyNormal true')
    lx.eval('item.channel pmodel.meshmerge$world false')
    link_to_merge_meshes((item,), merge_meshes_meshop_nonreplicator)

    if freeze:
        mesh_id = merged_nonreplicator.id
        meshop_id = merge_meshes_meshop_nonreplicator
        lx.eval(f'deformer.freeze false deformer:{meshop_id} mesh:{{{mesh_id}}}')

    fn_out()
    return merged_nonreplicator


def new_hierarchy_item(item: modo.Item) -> modo.Item:
    hierarchy_item = modo.Scene().addItem(itype=item.type, name=snapshot_name(item.name))
    match_pos_rot(hierarchy_item, item)
    match_scl(hierarchy_item, item)
    return hierarchy_item


def new_individual_replicators(items: Iterable[modo.Item], workspace: modo.Item, freeze: bool) -> list[modo.Item]:
    add_to_schematic(items, workspace)
    new_items: list[modo.Item] = []
    for item in items:
        new_items.append(new_replicator(item, workspace, freeze))

    return new_items


def new_replicator(item: modo.Item, workspace: modo.Item, freeze: bool) -> modo.Item:
    merged_replicator = modo.Scene().addMesh(snapshot_name(item.name))
    add_to_schematic((merged_replicator,), workspace)
    merged_replicator.select(replace=True)

    lx.eval('select.filepath "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" set')
    lx.eval('select.preset "[itemtypes]:MeshOperations/edit/pmodel.meshmerge.itemtype" mode:set')
    lx.eval('preset.do')

    merge_meshes_meshop_replicator = modo.Scene().selectedByType(itype='pmodel.meshmerge')[0]
    lx.eval('item.channel pmodel.meshmerge$copyNormal true')
    lx.eval('item.channel pmodel.meshmerge$world false')
    link_to_merge_meshes((item,), merge_meshes_meshop_replicator)

    if freeze:
        mesh_id = merged_replicator.id
        meshop_id = merge_meshes_meshop_replicator
        lx.eval(f'deformer.freeze false deformer:{meshop_id} mesh:{{{mesh_id}}}')

    return merged_replicator


if __name__ == '__main__':
    h3dd.enable_debug_output(False)
    main()
