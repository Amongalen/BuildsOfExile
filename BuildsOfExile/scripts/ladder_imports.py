# manage.py runscript ladder_imports
import json
import logging
from time import sleep

import jsonpickle

from BuildsOfExile import settings, pob_import, skill_tree
from BuildsOfExile.models import BuildGuide, Keystone, UniqueItem, UserProfile
from pob_wrapper import PathOfBuilding


def get_acc_and_chars_from_json(ladder_json):
    result = [(entry['account']['name'], entry['character']['name']) for entry in ladder_json['entries'] if
              'public' in entry]
    return result


def get_pob_xml(acc_name, char_name):
    pob = PathOfBuilding(settings.POB_PATH, settings.POB_PATH, verbose=True)
    xml = pob.import_build_as_xml(acc_name, char_name)
    pob.kill()
    return xml


def save_as_guide(acc_name, char_name, count, skill_tree_service):
    logging.info(f'{count} converting to guide: {acc_name=}, {char_name=}')
    build_xml = get_pob_xml(acc_name, char_name)
    if not build_xml:
        return
    build_details = pob_import.parse_pob_details(build_xml)

    tree = build_details.tree_specs[0]
    all_nodes = skill_tree_service.skill_trees[tree.tree_version].nodes
    keystone_names = [all_nodes[node_id].name for node_id in tree.nodes if
                      node_id in all_nodes and all_nodes[node_id].is_keystone]
    keystones = [Keystone.objects.get_or_create(name=name)[0] for name in keystone_names]
    for keystone in keystones:
        keystone.save()

    unique_items_names = [item.name for item in build_details.items if item.rarity == 'UNIQUE']
    unique_items = [UniqueItem.objects.get_or_create(name=name)[0] for name in unique_items_names]
    for item in unique_items:
        item.save()

    author = UserProfile.objects.get_or_create(user__username='Importer')[0]
    author.save()

    build_details_dict = jsonpickle.decode(jsonpickle.encode(build_details, unpicklable=False))
    new_guide = BuildGuide(title='Auto-imported build ' + str(count),
                           pob_details=build_details_dict,
                           pob_string=pob_import.xml_to_base64(build_xml),
                           text='Auto-imported build ' + str(count),
                           )
    new_guide.save()
    new_guide.author = author
    new_guide.keystones.set(keystones)
    new_guide.unique_items.set(unique_items)


def run():
    skill_tree_service = skill_tree.SkillTreeService()
    path = 'BuildsOfExile/scripts/ssf_expedition_ladder.json'
    with open(path, 'r') as f:
        ladder_json = json.load(f)
    chars = get_acc_and_chars_from_json(ladder_json)
    for count, char in enumerate(chars):
        save_as_guide(*char, count, skill_tree_service)
        sleep(1)
