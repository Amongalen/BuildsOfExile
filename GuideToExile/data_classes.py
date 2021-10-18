from dataclasses import dataclass, field
from typing import Union, Optional, List, Dict

from GuideToExile import items_service

assetService = items_service.AssetsService()


@dataclass
class SkillGem:
    is_enabled: bool
    name: str
    is_active_skill: bool
    level: int
    quality: int
    alt_quality_pref: str = field(default='')
    is_item_provided: bool = field(default=False)

    @property
    def asset(self):
        return assetService.get_asset_name_for_gem(self.name)


@dataclass
class SkillGroup:
    slot: Optional[str]
    source: Optional[str]
    is_enabled: bool
    main_active_skill_index: int
    gems: List[SkillGem]
    is_ignored: bool = field(default=False)


@dataclass
class TreeSpec:
    title: str
    nodes: List[str]
    url: str
    tree_version: str


@dataclass
class Item:
    item_id_in_itemset: int
    name: str
    base_name: str
    rarity: str
    display_html: str
    support_gems: List[SkillGem]
    is_broken: bool = field(default=False)

    @property
    def asset(self):
        return assetService.get_asset_name_for_gear(self)


@dataclass
class ItemSet:
    set_id: int
    title: str
    slots: Dict[str, Item]


@dataclass
class PobDetails:
    build_stats: Dict[str, Union[int, float]]
    class_name: str
    ascendancy_name: str
    skill_groups: List[SkillGroup]
    main_active_skills: List[str]
    imported_primary_skill: str
    tree_specs: List[TreeSpec]
    active_tree_spec_index: int
    items: List[Item]
    item_sets: List[ItemSet]
    active_item_set_id: str
    used_jewels: Dict[str, List[Item]]


@dataclass
class NodeGroup:
    group_id: int
    x: int
    y: int
    orbitals: List[int] = field(default_factory=list)
    node_ids: List[str] = field(default_factory=list)


@dataclass
class TreeNode:
    id: int
    name: str
    ascendancy_name: str
    is_keystone: bool
    is_mastery: bool
    is_notable: bool
    orbit_radii: int
    orbit_index: int
    class_start_index: int
    is_ascendancy_start: bool
    stats: List[str] = field(default_factory=list)
    connected_out_nodes: List[str] = field(default_factory=list)
    connected_in_nodes: List[str] = field(default_factory=list)

    @property
    def is_class_start_node(self):
        return self.class_start_index != -1

    @property
    def size(self):
        if self.is_keystone:
            return 48
        if self.is_mastery:
            return 40
        if self.is_notable:
            return 32
        return 28

    def is_connected_to(self, other_node: "TreeNode"):
        return (not self.is_mastery) and (not self.is_class_start_node) and (not other_node.is_mastery) and (
            not other_node.is_class_start_node) and (self.ascendancy_name == other_node.ascendancy_name)


@dataclass
class SkillTree:
    max_x: int
    max_y: int
    min_x: int
    min_y: int
    asc_start_nodes: Dict[str, str]
    node_groups: Dict[str, NodeGroup]
    nodes: Dict[str, TreeNode]
    skills_per_orbit: List[int]
    orbit_radii: List[int]

    def find_group_containing_node(self, node_id):
        for group in self.node_groups.values():
            if node_id in group.node_ids:
                return group
