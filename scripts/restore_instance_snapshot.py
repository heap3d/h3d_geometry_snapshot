#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# restore instance relations for snapshot items
# calling external replace_with_instance.py from h3d_propagate_tools
# ================================

from typing import Sequence, Optional

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import get_description_tag
from h3d_geometry_snapshot.scripts.merge_meshes_individual_snapshot import (
    SNAPSHOT_NAME_SUFFIX, MESHINNST_NAME_SUFFIX, MESHINST_INFO_TAG, snapshot_name
)

from h3d_utilites.scripts.h3d_debug import h3dd, prints, fn_in, fn_out


CMD_SELECTED = "selected"


class Snapshots:
    def __init__(self, items: Sequence[modo.Item]) -> None:
        self.items = items
        self.instances: list[modo.Item] = []
        self.relations: dict[str, list[modo.Item]] = dict()

        self.init_snapshot_instances()
        self.build_relations()

    def init_snapshot_instances(self):
        self.instances = [item for item in self.items if self.is_snapshot_instance(item)]

    def is_snapshot_instance(self, item: modo.Item) -> bool:
        if item.type != 'mesh':
            return False

        if SNAPSHOT_NAME_SUFFIX not in item.name:
            return False

        if MESHINNST_NAME_SUFFIX not in item.name:
            return False

        return True

    def build_relations(self):
        for instance in self.instances:
            self.add_relation(self.get_meshinst_tag(instance), instance)

    def add_relation(self, source_name: str, item: modo.Item):
        if source_name not in self.relations:
            self.relations[source_name] = []
        self.relations[source_name].append(item)

    def get_meshinst_tag(self, item: modo.Item) -> str:
        description = get_description_tag(item)

        if not description:
            return ''

        if MESHINST_INFO_TAG not in description:
            return ''

        for desc in description.splitlines():
            if desc.startswith(MESHINST_INFO_TAG):
                return desc.split(MESHINST_INFO_TAG)[1]

        return ''

    def get_instances(self, source_name: str) -> list[modo.Item]:
        return self.relations[source_name]

    def get_source_name(self, item: modo.Item) -> str:
        return get_description_tag(item)

    def source_names(self) -> list[str]:
        return list(self.relations.keys())

    def get_source_item(self, source_name: str) -> Optional[modo.Item]:
        instances = self.get_instances(source_name)
        if not instances:
            return None
        try:
            return modo.Scene().item(snapshot_name(source_name))
        except LookupError:
            return instances[0]


# TODO Work with meshref items with changed name
def main():
    args = lx.args()
    selected_mode = False
    if args:
        selected_mode = args[0] == CMD_SELECTED

    if selected_mode:
        items = modo.Scene().selectedByType(c.LOCATOR_TYPE, superType=True)
    else:
        items = modo.Scene().items(c.LOCATOR_TYPE, superType=True)

    snapshots = Snapshots(items)
    snapshot_source_names = snapshots.source_names()
    prints(snapshot_source_names)
    for source_name in snapshot_source_names:
        prints(source_name)
        make_instances(snapshots.get_source_item(source_name), snapshots.get_instances(source_name))


def make_instances(source: Optional[modo.Item], items: Optional[Sequence[modo.Item]]):
    fn_in()
    prints(source)
    prints(items)
    if not source:
        return

    if not items:
        return

    modo.Scene().deselect()
    for item in items:
        item.select()
    source.select()
    prints('before replace_with_instance.py call')
    lx.eval('@scripts/replace_with_instance.py')

    fn_out()


if __name__ == '__main__':
    h3dd.enable_debug_output(False)
    main()
