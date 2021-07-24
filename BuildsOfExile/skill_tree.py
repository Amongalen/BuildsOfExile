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
    is_class_starting_node: bool
    connected_nodes: list[int] = field(default_factory=list)

    @property
    def size(self):
        if self.is_keystone:
            return 54
        if self.is_notable:
            return 46
        return 28

    def is_connected_to(self, other_node: "TreeNode"):
        return (not self.is_mastery) and (not self.is_class_starting_node) and (not other_node.is_mastery) and (
            not other_node.is_class_starting_node) and (self.ascendancy_name == other_node.ascendancy_name)


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
        skill_tree_json = json.load(f)

    groups = _parse_node_groups(skill_tree_json)
    nodes = _parse_nodes(skill_tree_json)
    asc_classes = _parse_asc_data_json(skill_tree_json)
    skill_tree = SkillTree(
        max_x=skill_tree_json['max_x'],
        max_y=skill_tree_json['max_y'],
        min_x=skill_tree_json['min_x'],
        min_y=skill_tree_json['min_y'],
        skills_per_orbit=skill_tree_json['constants']['skillsPerOrbit'],
        orbit_radii=skill_tree_json['constants']['orbitRadii'],
        node_groups=groups,
        nodes=nodes,
        asc_classes=asc_classes
    )
    return skill_tree


def _parse_asc_data_json(skill_tree_json):
    return {class_id: {asc_id: ascendancy['id'] for asc_id, ascendancy in enumerate(class_data['ascendancies'])}
            for class_id, class_data in enumerate(skill_tree_json['classes'])}


def _parse_nodes(skill_tree_json):
    nodes = {}
    for node_id, node_json in skill_tree_json['nodes'].items():
        if node_id == 'root' or 'orbit' not in node_json:
            continue
        nodes[node_id] = TreeNode(
            id=node_json['skill'],
            name=node_json['name'],
            ascendancy_name=node_json.get('ascendancyName', ''),
            is_keystone=node_json.get('isKeystone', False),
            is_mastery=node_json.get('isMastery', False),
            is_notable=node_json.get('isNotable', False),
            orbit_radii=node_json['orbit'],
            orbit_index=node_json['orbitIndex'],
            connected_nodes=node_json['out'],
            is_class_starting_node=('classStartIndex' in node_json)
        )
    return nodes


def _parse_node_groups(skill_tree_json):
    groups = {}
    for group_id, group_json in skill_tree_json['groups'].items():
        groups[group_id] = NodeGroup(x=group_json['x'],
                                     y=group_json['y'],
                                     orbitals=group_json['orbits'],
                                     node_ids=group_json['nodes'])
    return groups
