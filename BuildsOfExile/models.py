from dataclasses import dataclass

from django.db import models


# Create your models here.

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


@dataclass
class ItemSet:
    set_id: int
    title: str
    slots: list[tuple[str, int]]


@dataclass
class Item:
    item_id: int
    name: str
    rarity: str
    display_html: str
