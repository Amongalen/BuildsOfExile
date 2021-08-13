# manage.py runscript ladder_imports
import json
import logging
from time import sleep

from GuideToExile import settings, pob_import, skill_tree
from GuideToExile.build_guide import create_build_guide
from GuideToExile.models import UserProfile
from apps.pob_wrapper import PathOfBuilding


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
    title = 'Auto-imported build ' + str(count)
    text = 'Auto-imported build ' + str(count)
    author = UserProfile.objects.get_or_create(user__username='Importer')[0]
    author.save()
    pob_string = pob_import.xml_to_base64(build_xml)

    create_build_guide(author, build_details, pob_string, skill_tree_service, text, title)


def run():
    skill_tree_service = skill_tree.SkillTreeService()
    path = 'GuideToExile/scripts/ssf_expedition_ladder.json'
    with open(path, 'r') as f:
        ladder_json = json.load(f)
    chars = get_acc_and_chars_from_json(ladder_json)
    for count, char in enumerate(chars):
        save_as_guide(*char, count, skill_tree_service)
        sleep(1)
