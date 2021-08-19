import json

from django.contrib.staticfiles import finders

from GuideToExile.settings.development import ASSET_DIR, BASE_ITEMS_LOOKUP_FILE, UNIQUE_ITEMS_LOOKUP_FILE

COLOR_FOR_RARITY = {
    'UNIQUE': '#AF6025',
    'RARE': '#FFFF77',
    'MAGIC': '#8888FF',
    'NORMAL': '#FFFFFF',
}


class ItemsService:
    def __init__(self):
        self.asset_mapping = AssetMapping(ASSET_DIR, finders.find(BASE_ITEMS_LOOKUP_FILE),
                                          finders.find(UNIQUE_ITEMS_LOOKUP_FILE))

    @staticmethod
    def get_item_sets_details(guide):
        items = guide.pob_details.items
        item_sets = guide.pob_details.item_sets
        for item_set in item_sets:
            slots_with_items = {}
            item_set.title = item_set.title if item_set.title else 'Default'
            for slot, item_id in item_set.slots.items():
                for item in items:
                    if item.item_id_in_itemset == item_id:
                        slots_with_items[slot] = item
                        item.color = COLOR_FOR_RARITY[item.rarity]
                        break
            item_set.slots_with_items = slots_with_items
        return item_sets

    def assign_assets_to_items(self, items):
        for item in items:
            item.asset = self.asset_mapping.get_asset_name_for_gear(item)

    def assign_assets_to_gems(self, skill_groups):
        for skill_group in skill_groups:
            for gem in skill_group.gems:
                gem.asset = self.asset_mapping.get_asset_name_for_gem(gem)


class AssetMapping:
    def __init__(self, asset_dir, base_items_lookup_file, unique_items_lookup_file):
        self.mapping = {}
        with open(base_items_lookup_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for details in data.values():
                for name in details['names'].values():
                    if 'artName' in details:
                        self.mapping[name] = f'{asset_dir}/{details["artName"]}.png'

        with open(unique_items_lookup_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for lang in data.values():
                for name, art_name in lang.items():
                    self.mapping[name] = f'{asset_dir}/{art_name}.png'

    def get_asset_name_for_gem(self, gem):
        return self.mapping.get(gem.name, None)

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
