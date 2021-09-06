from GuideToExile.models import BuildGuide, UniqueItem, Keystone, AscendancyClass


def create_build_guide(author, build_details, pob_string, skill_tree_service, text='Content',
                       title='Title') -> BuildGuide:
    keystones = get_or_create_keystones(build_details, skill_tree_service)
    unique_items = get_or_create_unique_items(build_details)
    asc_class = get_asc_class(build_details)

    new_guide = BuildGuide(title=title,
                           pob_details=build_details,
                           pob_string=pob_string,
                           text=text,
                           ascendancy_class=asc_class,
                           )
    new_guide.save()
    new_guide.author = author
    new_guide.keystones.set(keystones)
    new_guide.unique_items.set(unique_items)

    return new_guide


def get_asc_class(build_details):
    asc_name = build_details.ascendancy_name
    asc_name_id = AscendancyClass.AscClassName[asc_name.upper()]
    base_class_name = build_details.class_name
    base_class_name_id = AscendancyClass.BaseClassName[base_class_name.upper()]
    asc_class = AscendancyClass.objects.get(name=asc_name_id, base_class_name=base_class_name_id)

    return asc_class


def get_or_create_unique_items(build_details):
    unique_items_names = [item.name for item in build_details.items if item.rarity == 'UNIQUE']
    unique_items = [UniqueItem.objects.get_or_create(name=name)[0] for name in unique_items_names]
    for item in unique_items:
        item.save()
    return unique_items


def get_or_create_keystones(build_details, skill_tree_service):
    keystone_names = []
    for build_tree in build_details.tree_specs:
        all_nodes = skill_tree_service.skill_trees[build_tree.tree_version].nodes
        keystone_names.extend(all_nodes[node_id].name for node_id in build_tree.nodes if
                              node_id in all_nodes and all_nodes[node_id].is_keystone)

    keystones = [Keystone.objects.get_or_create(name=name)[0] for name in set(keystone_names)]
    for keystone in keystones:
        keystone.save()
    return keystones
