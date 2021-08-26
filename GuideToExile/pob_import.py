import base64
import logging
import re
import xml.etree.ElementTree as ET
import zlib

import requests

from GuideToExile import items_service
from GuideToExile.data_classes import SkillGem, SkillGroup, TreeSpec, ItemSet, Item, PobDetails
from GuideToExile.exceptions import PastebinImportException, BuildXmlParsingException
from GuideToExile.settings import POB_PATH
from apps.pob_wrapper import PathOfBuilding

logger = logging.getLogger('guidetoexile')

SLOTS_ORDER = ['Weapon 1', 'Weapon 2', 'Body Armour', 'Gloves', 'Helmet', 'Boots', 'Amulet', 'Ring 1', 'Ring 2',
               'Belt', 'Unassigned']

GEM_MAPPING = items_service.GemMapping()


def import_from_pastebin(url: str):
    logger.debug('Importing from Pastebin: %s', url)
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
    logger.debug('Parsing PoB XML')
    try:
        xml_root = ET.fromstring(xml)
    except Exception as err:
        raise BuildXmlParsingException(err)

    skill_groups = extract_skills_groups(xml_root)

    # sorting must be after picking main skill, in the xml they use index for that, not id
    main_active_skill = get_main_active_skill(skill_groups, xml_root)
    skill_groups.sort(key=lambda x: SLOTS_ORDER.index(x.slot))

    tree_specs = extract_tree_specs(xml_root)
    items = extract_items(xml_root)
    item_sets = extract_item_sets(xml_root, items)
    used_jewels = extract_used_jewels(xml_root, items)
    logger.debug('Parsed PoB XML')
    return PobDetails(
        build_stats=(extract_stats(xml_root)),
        class_name=(xml_root.find('Build').get('className')),
        ascendancy_name=(xml_root.find('Build').get('ascendClassName')),
        skill_groups=skill_groups,
        main_active_skills=[main_active_skill] if main_active_skill else [],
        imported_primary_skill=main_active_skill,
        tree_specs=tree_specs,
        active_tree_spec_index=(int(xml_root.find('Tree').get('activeSpec')) - 1),
        items=items,
        item_sets=item_sets,
        active_item_set_index=extract_active_item_set_index(xml_root),
        used_jewels=used_jewels)


def extract_used_jewels(xml_root, items):
    logger.debug('Extracting jewels')
    jewels_in_tree = set(item_id for spec_xml in xml_root.find('Tree')
                         for socket_xml in spec_xml.find('Sockets')
                         if (item_id := int(socket_xml.get('itemId'))) != 0)
    jewels_in_items = set(item_id for item_set_xml in xml_root.find('Items').findall('ItemSet')
                          for slot_xml in item_set_xml
                          if (item_id := int(slot_xml.get('itemId'))) != 0
                          and 'Abyssal' in slot_xml.get('name'))
    all_jewels = jewels_in_items | jewels_in_tree

    items_by_id = {item.item_id_in_itemset: item for item in items}
    used_jewels = {'abyssal': [],
                   'normal': [],
                   'cluster': []}
    for jewel_id in all_jewels:
        jewel = items_by_id[jewel_id]
        if 'Eye' in jewel.base_name:
            used_jewels['abyssal'].append(jewel)
        elif 'Cluster' in jewel.base_name:
            used_jewels['cluster'].append(jewel)
        else:
            used_jewels['normal'].append(jewel)

    return used_jewels


def extract_active_item_set_index(xml_root):
    return int(active_item_set_index) - 1 if (active_item_set_index := xml_root.find('Items').get(
        'activeItemSet')) != 'nil' else 0


def extract_stats(xml_root):
    stats = {}
    for stat in xml_root.find('Build'):
        value_str = stat.get('value')
        name_pref = 'minion_' if stat.tag == 'MinionStat' else ''
        if value_str is None:
            continue
        try:
            value = int(value_str)
            name = name_pref + stat.get('stat').lower().replace(":", '_')
            stats[name] = value
            continue
        except ValueError:
            pass
        try:
            value = round(float(value_str), 1)
            name = name_pref + stat.get('stat').lower().replace(":", '_')
            stats[name] = value
        except ValueError:
            pass
    return stats


def extract_items(xml_root):
    logger.debug('Extracting items')
    items = []
    pob = PathOfBuilding(POB_PATH, POB_PATH)
    for item_xml in xml_root.find('Items').findall('Item'):
        item_id = int(item_xml.get('id'))
        item_str = item_xml.text.strip()
        parts = item_str.split('\n')
        item_rarity = parts[0].split(': ')[1].strip()
        item_name = parts[1].strip()
        if item_rarity in ['UNIQUE', 'RARE']:
            base_name = parts[2].strip()
        else:
            base_name = parts[1].strip()

        item_display_html = pob.item_as_html(item_str)
        items.append(Item(item_id_in_itemset=item_id,
                          name=item_name,
                          base_name=base_name,
                          rarity=item_rarity,
                          display_html=item_display_html,
                          support_gems=extract_support_gems_from_item(parts)))
    pob.kill()
    return items


def extract_support_gems_from_item(item_lines):
    result = []
    for line in item_lines:
        match = re.match(r'^Socketed Gems are Supported by Level (\d+) (.*)$', line)
        if match:
            level = int(match.group(1))
            name = f'{match.group(2)} Support'
            result.append(SkillGem(name=name, level=level, quality=0, is_enabled=True, is_active_skill=False,
                                   is_item_provided=True))
    return result


def extract_item_sets(xml_root, items):
    logger.debug('Extracting item sets')
    items_by_id = {item.item_id_in_itemset: item for item in items}
    item_sets = []
    for item_set_xml in xml_root.find('Items').findall('ItemSet'):
        title = title if (title := item_set_xml.get('title')) is not None else 'Default'
        set_id = item_set_xml.get('id')
        slots = {}
        for slot_xml in item_set_xml:
            item_id = int(slot_xml.get('itemId'))
            if item_id != 0:
                slot_name = slot_xml.get('name').lower().replace(' ', '-')
                slots[slot_name] = items_by_id[item_id]
        item_sets.append(ItemSet(title=title,
                                 set_id=set_id,
                                 slots=slots))
    return item_sets


def extract_tree_specs(xml_root):
    logger.debug('Extracting tree specs')
    tree_specs = []
    for spec_xml in xml_root.find('Tree'):
        nodes = list(map(str, spec_xml.get('nodes').split(',')))
        title = title if (title := spec_xml.get('title')) is not None else 'Default'
        tree_specs.append(TreeSpec(title=title,
                                   nodes=nodes,
                                   url=spec_xml.find('URL').text.strip(),
                                   tree_version=spec_xml.get('treeVersion')))

    return tree_specs


def extract_skills_groups(xml_root):
    logger.debug('Extracting skill groups')

    skill_groups = []
    for group_xml in xml_root.find('Skills'):
        source = group_xml.get('source')
        slot = slot if (slot := group_xml.get('slot')) else 'Unassigned'
        gems = extract_gems_in_group(group_xml)

        if not gems:
            continue
        if source is not None and 'Tree' in source:
            continue
        is_group_enabled = parse_bool(group_xml.get('enabled'))
        main_active_skill_index = group_xml.get('mainActiveSkill')
        main_active_skill_index = int(main_active_skill_index) - 1 if not main_active_skill_index == 'nil' else 0
        skill_groups.append(SkillGroup(is_enabled=is_group_enabled,
                                       main_active_skill_index=main_active_skill_index,
                                       gems=gems, source=source, slot=slot))
    return skill_groups


def extract_gems_in_group(group_xml):
    gems = []
    for gem_xml in group_xml:
        is_gem_enabled = parse_bool(gem_xml.get('enabled'))
        skill_id = gem_xml.get('skillId')
        if 'Enchantment' in skill_id:
            continue
        is_active_skill = skill_id is not None and 'Support' not in skill_id
        level = gem_xml.get('level')
        quality = gem_xml.get('quality')
        name = GEM_MAPPING.get_name(skill_id)
        gem_id = gem_xml.get('gemId')
        is_item_provided = True if gem_id is None else False
        gems.append(
            SkillGem(name=name, is_enabled=is_gem_enabled, is_active_skill=is_active_skill,
                     level=level, quality=quality, is_item_provided=is_item_provided))
    return gems


def get_main_active_skill(skill_groups, xml_root):
    if not len(skill_groups):
        return None
    main_socket_group_index = int(xml_root.find('Build').get('mainSocketGroup')) - 1
    main_socket_group = skill_groups[main_socket_group_index]
    main_skill_index_within_group = main_socket_group.main_active_skill_index
    active_gems_in_main_group = list(filter(lambda x: x.is_active_skill, main_socket_group.gems))
    main_active_skill = (active_gems_in_main_group[main_skill_index_within_group].name
                         if active_gems_in_main_group else None)
    return main_active_skill


def parse_bool(xml):
    return True if xml == 'true' else False
