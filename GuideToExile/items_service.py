import copy
import json
from collections import defaultdict

from django.contrib.staticfiles import finders

from GuideToExile.settings import ASSET_DIR, BASE_ITEMS_LOOKUP_FILE, UNIQUE_ITEMS_LOOKUP_FILE


class AssetMapping:
    def __init__(self):
        base_items_lookup_file = finders.find(BASE_ITEMS_LOOKUP_FILE)
        unique_items_lookup_file = finders.find(UNIQUE_ITEMS_LOOKUP_FILE)
        self.mapping = {}
        with open(base_items_lookup_file, 'r', encoding='utf-8') as file:
            data = json.load(file, object_pairs_hook=_dict_skip_duplicates)
            for details in data.values():
                for name in details['names'].values():
                    if 'artName' in details:
                        self.mapping[name] = f'{ASSET_DIR}/{details["artName"]}.png'

        with open(unique_items_lookup_file, 'r', encoding='utf-8') as file:
            data = json.load(file, object_pairs_hook=_dict_skip_duplicates)
            for lang in data.values():
                for name, art_name in lang.items():
                    self.mapping[name] = f'{ASSET_DIR}/{art_name}.png'

    def get_asset_name_for_gem(self, gem_name):
        return self.mapping.get(gem_name, None)

    def get_asset_name_for_gear(self, item):
        if item.rarity == 'UNIQUE':
            return self.mapping.get(item.name, None)
        if item.rarity == 'RARE':
            return self.mapping.get(item.base_name, None)

        # hacks for dealing with prefix and suffix
        name = item.base_name
        if x := self.mapping.get(name, None):
            return x
        prefixless_name = name.split(' ', maxsplit=1)[1]
        if x := self.mapping.get(prefixless_name, None):
            return x
        suffixless_name = name.split(' of ')[0]
        if x := self.mapping.get(suffixless_name, None):
            return x
        stripped_name = prefixless_name.split(' of ')[0]
        if x := self.mapping.get(stripped_name, None):
            return x


def _dict_skip_duplicates(ordered_pairs):
    """Reject duplicate keys."""
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            continue
        else:
            d[k] = v
    return d


def assign_skills_to_items(item_sets, skill_groups):
    item_sets = copy.deepcopy(item_sets)
    skill_groups_by_slot = defaultdict(list)
    for skill_group in skill_groups:
        slot_name = skill_group.slot.lower().replace(' ', '-')
        skill_groups_by_slot[slot_name].append(skill_group)

    for item_set in item_sets:
        for slot_name, item in item_set.slots.items():
            item.skill_groups = []
            if slot_name in skill_groups_by_slot:
                skill_groups = copy.deepcopy(skill_groups_by_slot[slot_name])
                for skill_group in skill_groups:
                    skill_group.gems.extend(item.support_gems)
                item.skill_groups.extend(skill_groups)
        item_set.unassigned_skill_groups = {k: v for k, v in skill_groups_by_slot.items() if k not in item_set.slots}
    return item_sets
