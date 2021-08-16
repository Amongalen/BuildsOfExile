from dataclasses import dataclass, field


@dataclass
class SkillGem:
    is_enabled: bool
    name: str
    is_active_skill: bool
    level: int
    quality: int
    is_item_provided: bool


@dataclass
class SkillGroup:
    is_enabled: bool
    main_active_skill_index: int
    gems: list[SkillGem]


@dataclass
class TreeSpec:
    title: str
    nodes: list[str]
    url: str
    tree_version: str


@dataclass
class ItemSet:
    set_id: int
    title: str
    slots: dict[str, int]


@dataclass
class Item:
    item_id_in_itemset: int
    name: str
    base_name: str
    rarity: str
    display_html: str


@dataclass
class PobDetails:
    build_stats: dict[str, str]
    class_name: str
    ascendancy_name: str
    skill_groups: list[SkillGroup]
    main_active_skills: list[str]
    imported_primary_skill: str
    tree_specs: list[TreeSpec]
    active_tree_spec_index: int
    items: list[Item]
    item_sets: list[ItemSet]
    active_item_set_index: int


@dataclass
class NodeGroup:
    group_id: int
    x: int
    y: int
    orbitals: list[int] = field(default_factory=list)
    node_ids: list[str] = field(default_factory=list)


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
    stats: list[str] = field(default_factory=list)
    connected_nodes: list[str] = field(default_factory=list)

    @property
    def is_class_start_node(self):
        return self.class_start_index != -1

    @property
    def size(self):
        if self.is_keystone:
            return 48
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
    asc_start_nodes: dict[str, str]
    node_groups: dict[str, NodeGroup]
    nodes: dict[str, TreeNode]
    skills_per_orbit: list[int]
    orbit_radii: list[int]

    def find_group_containing_node(self, node_id):
        for group in self.node_groups.values():
            if node_id in group.node_ids:
                return group
