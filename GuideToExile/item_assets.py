import json


class AssetMapping:
    def __init__(self, asset_dir, base_items_lookup_file, unique_items_lookup_file):
        self.mapping = {}
        with open(base_items_lookup_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for details in data.values():
                for name in details['names'].values():
                    if 'artName' in details:
                        self.mapping[name] = f'{asset_dir}/{details["artName"]}'

        with open(unique_items_lookup_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for lang in data.values():
                for name, art_name in lang.items():
                    self.mapping[name] = art_name
