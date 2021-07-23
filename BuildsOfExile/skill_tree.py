import base64
import json
import struct
from dataclasses import dataclass, field


@dataclass
class NodeGroup:
    x: int
    y: int
    orbitals: list[int] = field(default_factory=list)
    node_ids: list[int] = field(default_factory=list)


@dataclass()
class TreeNode:
    id: int
    name: str
    ascendancy_name: str
    is_keystone: bool
    is_mastery: bool
    is_notable: bool
    orbit_radii: int
    orbit_index: int
    starting_nodes_count: int
    connected_nodes: list[int] = field(default_factory=list)

    @property
    def has_starting_nodes(self):
        return self.starting_nodes_count != 0

    @property
    def size(self):
        if self.is_keystone:
            return 54
        if self.is_notable:
            return 46
        return 28

    def is_connected_to(self, other_node: "TreeNode"):
        return (not self.is_mastery) and (not self.has_starting_nodes) and (not other_node.is_mastery) and (
            not other_node.has_starting_nodes) and (self.ascendancy_name == other_node.ascendancy_name)


@dataclass()
class SkillTree:
    max_x: int
    max_y: int
    min_x: int
    min_y: int
    node_groups: dict[int, NodeGroup] = field(default_factory=dict)
    nodes: dict[int, TreeNode] = field(default_factory=dict)
    skills_per_orbit: list[int] = field(default_factory=list)
    orbit_radii: list[int] = field(default_factory=list)
    asc_classes: dict[int, str] = field(default_factory=dict)

    def find_group_containing_node(self, node_id):
        for group in self.node_groups.values():
            if node_id in group.node_ids:
                return group

    def parse_tree_url(self, tree_url: str) -> list[int]:
        tree_url = tree_url.rstrip('/')
        url_parts = tree_url.split('/')
        encoded_tree = url_parts[-1]
        byte_tree = base64.urlsafe_b64decode(encoded_tree)
        total_nodes = (len(byte_tree) - 7) // 2
        version, char_id, ascendancy_id, locked, *nodes = struct.unpack(f'iBBB{total_nodes}H', byte_tree)
        asc_start_node = self._get_asc_start_node_id(char_id, ascendancy_id)
        nodes.append(asc_start_node)
        return nodes

    def _get_asc_start_node_id(self, char_id, asc_id):
        asc_name = self.asc_classes[char_id][asc_id]
        for node in self.nodes.values():
            if node.name == asc_name:
                return node.id


def read_tree_data_file(filepath: str) -> SkillTree:
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('var passiveSkillTreeData = '):
                skill_tree_json = line[27:].rstrip(';')
            if line.startswith('ascClasses: '):
                asc_classes_json = line[12:].rstrip(',')

    skill_tree = _parse_skill_tree_json(skill_tree_json, asc_classes_json)
    return skill_tree


def _parse_skill_tree_json(skill_tree_json, asc_classes_json):
    skill_tree_data = json.loads(skill_tree_json)
    groups = _parse_node_groups(skill_tree_data)
    nodes = _parse_nodes(skill_tree_data)
    asc_classes = _parse_asc_data_json(asc_classes_json)
    skill_tree = SkillTree(
        max_x=skill_tree_data['max_x'],
        max_y=skill_tree_data['max_y'],
        min_x=skill_tree_data['min_x'],
        min_y=skill_tree_data['min_y'],
        skills_per_orbit=skill_tree_data['constants']['skillsPerOrbit'],
        orbit_radii=skill_tree_data['constants']['orbitRadii'],
        node_groups=groups,
        nodes=nodes,
        asc_classes=asc_classes
    )
    return skill_tree


def _parse_asc_data_json(asc_classes_json):
    asc_classes = json.loads(asc_classes_json)
    return {int(class_id): {int(asc_id): asc_json['name'] for asc_id, asc_json in class_json['classes'].items()}
            for class_id, class_json in asc_classes.items()}


def _parse_nodes(skill_tree):
    nodes = {}
    for node_id, node_json in skill_tree['nodes'].items():
        nodes[int(node_id)] = TreeNode(
            id=node_json['id'],
            name=node_json['dn'],
            ascendancy_name=node_json.get('ascendancyName', ''),
            is_keystone=node_json['ks'],
            is_mastery=node_json['m'],
            is_notable=node_json['not'],
            orbit_radii=node_json['o'],
            orbit_index=node_json['oidx'],
            connected_nodes=node_json['out'],
            starting_nodes_count=len(node_json['spc'])
        )
    return nodes


def _parse_node_groups(skill_tree):
    groups = {}
    for group_id, group_json in skill_tree['groups'].items():
        orbitals = [int(orbital) for orbital, value in group_json['oo'].items() if value]
        groups[group_id] = NodeGroup(x=group_json['x'],
                                     y=group_json['y'],
                                     orbitals=orbitals,
                                     node_ids=group_json['n'])
    return groups
