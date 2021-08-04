import json
import os

from BuildsOfExile.data_classes import NodeGroup, TreeNode, SkillTree
from BuildsOfExile.exceptions import SkillTreeLoadingException
from BuildsOfExile.tree_graph import TreeGraph


class SkillTreeService:
    skill_trees: dict[str, SkillTree] = {}
    tree_graphs: dict[str, TreeGraph] = {}

    def __init__(self, trees_dir='BuildsOfExile/trees'):
        for f in os.scandir(trees_dir):
            if f.is_dir():
                version = f.path.split('\\')[-1]
                skill_tree = _read_tree_data_file(f.path + '/data.json')
                self.skill_trees[version] = skill_tree
                self.tree_graphs[version] = TreeGraph(skill_tree)
                print(f'loaded tree {version=}')

    def get_html_with_taken_nodes(self, taken_node_ids, tree_version):
        self.tree_graphs[tree_version].to_html_with_taken_nodes(taken_node_ids)


def _read_tree_data_file(filepath: str) -> SkillTree:
    try:
        with open(filepath, 'r') as f:
            skill_tree_json = json.load(f)

        groups = _parse_node_groups(skill_tree_json)
        nodes, asc_start_nodes = _parse_nodes(skill_tree_json)
        skill_tree = SkillTree(
            max_x=skill_tree_json['max_x'],
            max_y=skill_tree_json['max_y'],
            min_x=skill_tree_json['min_x'],
            min_y=skill_tree_json['min_y'],
            skills_per_orbit=skill_tree_json['constants']['skillsPerOrbit'],
            orbit_radii=skill_tree_json['constants']['orbitRadii'],
            node_groups=groups,
            nodes=nodes,
            asc_start_nodes=asc_start_nodes
        )
    except Exception as e:
        raise SkillTreeLoadingException(e)
    return skill_tree


def _parse_nodes(skill_tree_json):
    nodes = {}
    asc_start_nodes = {}
    for node_id, node_json in skill_tree_json['nodes'].items():
        if node_id == 'root' or 'orbit' not in node_json:
            continue
        new_node = TreeNode(id=node_json['skill'], name=node_json['name'],
                            ascendancy_name=node_json.get('ascendancyName', ''),
                            is_keystone=node_json.get('isKeystone', False),
                            is_mastery=node_json.get('isMastery', False),
                            is_notable=node_json.get('isNotable', False), orbit_radii=node_json['orbit'],
                            orbit_index=node_json['orbitIndex'], connected_nodes=node_json['out'],
                            class_start_index=node_json.get('classStartIndex', -1),
                            is_ascendancy_start=node_json.get('isAscendancyStart', False))
        nodes[node_id] = new_node
        if new_node.is_ascendancy_start:
            asc_start_nodes[new_node.ascendancy_name] = node_id
    return nodes, asc_start_nodes


def _parse_node_groups(skill_tree_json):
    groups = {}
    for group_id, group_json in skill_tree_json['groups'].items():
        groups[group_id] = NodeGroup(x=group_json['x'],
                                     y=group_json['y'],
                                     orbitals=group_json['orbits'],
                                     node_ids=group_json['nodes'])
    return groups
