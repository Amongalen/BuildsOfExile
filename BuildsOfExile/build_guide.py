import jsonpickle

from BuildsOfExile.models import BuildGuide, UniqueItem, Keystone


def create_build_guide(author, build_details, pob_string, skill_tree_service, text='', title='') -> BuildGuide:
    build_tree = build_details.tree_specs[0]
    keystones = get_or_create_keystones(build_details, skill_tree_service)
    unique_items = get_or_create_unique_items(build_details)
    build_details_dict = jsonpickle.decode(jsonpickle.encode(build_details, unpicklable=False))
    new_guide = BuildGuide(title=title,
                           pob_details=build_details_dict,
                           pob_string=pob_string,
                           text=text,
                           )
    new_guide.save()
    new_guide.author = author
    new_guide.keystones.set(keystones)
    new_guide.unique_items.set(unique_items)

    return new_guide


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
