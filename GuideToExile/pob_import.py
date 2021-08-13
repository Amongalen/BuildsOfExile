import base64
import xml.etree.ElementTree as ET
import zlib

import requests

from GuideToExile.data_classes import SkillGem, SkillGroup, TreeSpec, ItemSet, Item, PobDetails
from GuideToExile.exceptions import PastebinImportException, BuildXmlParsingException
from GuideToExile.settings.development import POB_PATH
from apps.pob_wrapper import PathOfBuilding


def import_from_pastebin(url: str):
    parts = url.rsplit('/', maxsplit=1)
    if parts[0] != 'https://pastebin.com':
        raise PastebinImportException('Incorrect Pastebin URL - must start with "https://pastebin.com/"')
    final_url = parts[0] + '/raw/' + parts[1]
    response = requests.get(final_url)
    response.raise_for_status()
    return response.text


def base64_to_xml(base64_str):
    compressed_bytes = base64.urlsafe_b64decode(base64_str)
    return zlib.decompress(compressed_bytes).decode('utf-8')


def xml_to_base64(xml):
    compressed_bytes = zlib.compress(xml.encode('utf-8'), level=9)
    return base64.urlsafe_b64encode(compressed_bytes).decode('utf-8')


def parse_pob_details(xml: str):
    try:
        xml_root = ET.fromstring(xml)
    except Exception as err:
        raise BuildXmlParsingException(err)

    build_stats = {stat.get('stat'): stat.get('value') for stat in xml_root.find('Build')}
    class_name = xml_root.find('Build').get('className')
    ascendancy_name = xml_root.find('Build').get('ascendClassName')
    skill_groups, main_active_skills = extract_skills(xml_root)
    tree_specs, active_tree_spec_index = extract_tree_specs(xml_root)
    items, item_sets, active_item_set_index = extract_items(xml_root)
    return PobDetails(
        build_stats=build_stats,
        class_name=class_name,
        ascendancy_name=ascendancy_name,
        skill_groups=skill_groups,
        main_active_skills=main_active_skills,
        tree_specs=tree_specs,
        active_tree_spec_index=active_tree_spec_index,
        items=items,
        item_sets=item_sets,
        active_item_set_index=active_item_set_index)


def extract_items(xml_root):
    item_sets = []
    for item_set_xml in xml_root.find('Items').findall('ItemSet'):
        title = item_set_xml.get('title')
        set_id = item_set_xml.get('id')
        slots = {}
        for slot_xml in item_set_xml:
            item_id = int(slot_xml.get('itemId'))
            if item_id != 0:
                slot_name = slot_xml.get('name')
                slots[slot_name] = item_id
        item_sets.append(ItemSet(title=title,
                                 set_id=set_id,
                                 slots=slots))

    items = []
    pob = PathOfBuilding(POB_PATH, POB_PATH)
    for item_xml in xml_root.find('Items').findall('Item'):
        item_id = int(item_xml.get('id'))
        item_str = item_xml.text.strip()
        parts = item_str.split('\n')
        item_rarity = parts[0].split(': ')[1].strip()
        item_name = parts[1].strip()

        item_display_html = pob.item_as_html(item_str)
        items.append(Item(item_id_in_itemset=item_id,
                          name=item_name,
                          rarity=item_rarity,
                          display_html=item_display_html))
    pob.kill()

    active_item_set_index = xml_root.find('Items').get('activeItemSet')
    active_item_set_index = int(active_item_set_index) if active_item_set_index != 'nil' else 0
    return items, item_sets, active_item_set_index


def extract_tree_specs(xml_root):
    tree_specs = []
    for spec_xml in xml_root.find('Tree'):
        nodes = list(map(str, spec_xml.get('nodes').split(',')))
        tree_specs.append(TreeSpec(title=spec_xml.get('title'),
                                   nodes=nodes,
                                   url=spec_xml.find('URL'),
                                   tree_version=spec_xml.get('treeVersion')))
    active_tree_spec_index = int(xml_root.find('Tree').get('activeSpec'))
    return tree_specs, active_tree_spec_index


def extract_skills(xml_root):
    skill_groups = []
    for group_xml in xml_root.find('Skills'):
        gems = []
        for gem_xml in group_xml:
            is_gem_enabled = parse_bool(gem_xml.get('enabled'))
            gems.append(SkillGem(name=gem_xml.get('nameSpec'), is_enabled=is_gem_enabled))
        is_group_enabled = parse_bool(group_xml.get('enabled'))
        main_active_skill_index = group_xml.get('mainActiveSkill')
        main_active_skill_index = int(main_active_skill_index) if not main_active_skill_index == 'nil' else 1
        skill_groups.append(SkillGroup(is_enabled=is_group_enabled,
                                       main_active_skill_index=main_active_skill_index,
                                       gems=gems))
    main_socket_group_index = int(xml_root.find('Build').get('mainSocketGroup'))

    if len(skill_groups) == 0:
        return skill_groups, []

    main_skill_index_within_group = skill_groups[main_socket_group_index].main_active_skill_index
    main_active_skill = skill_groups[main_socket_group_index - 1].gems[main_skill_index_within_group - 1].name

    return skill_groups, [main_active_skill]


def parse_bool(xml):
    return True if xml == 'true' else False
