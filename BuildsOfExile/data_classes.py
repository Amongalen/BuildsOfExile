from dataclasses import dataclass


@dataclass
class SkillGem:
    is_enabled: bool
    name: str


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
    rarity: str
    display_html: str


@dataclass
class PobDetails:
    build_stats: dict[str, str]
    class_name: str
    ascendancy_name: str
    skill_groups: list[SkillGroup]
    main_active_skills: list[str]
    tree_specs: list[TreeSpec]
    active_tree_spec_index: int
    items: list[Item]
    item_sets: list[ItemSet]
    active_item_set_index: int
