import json
from dataclasses import dataclass, field

from BuildsOfExile.exceptions import SkillTreeLoadingException


@dataclass
class NodeGroup:
    x: int
    y: int
    orbitals: list[int] = field(default_factory=list)
    node_ids: list[str] = field(default_factory=list)


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
    class_start_index: int
    is_ascendancy_start: bool
    connected_nodes: list[str] = field(default_factory=list)

    @property
    def is_class_start_node(self):
        return self.class_start_index != -1

    @property
    def size(self):
        if self.is_keystone:
            return 54
        if self.is_notable:
            return 46
        return 28

    def is_connected_to(self, other_node: "TreeNode"):
        return (not self.is_mastery) and (not self.is_class_start_node) and (not other_node.is_mastery) and (
            not other_node.is_class_start_node) and (self.ascendancy_name == other_node.ascendancy_name)


@dataclass()
class SkillTree:
    max_x: int
    max_y: int
    min_x: int
    min_y: int
    asc_start_nodes: dict[str, str]
    node_groups: dict[str, NodeGroup] = field(default_factory=dict)
    nodes: dict[str, TreeNode] = field(default_factory=dict)
    skills_per_orbit: list[int] = field(default_factory=list)
    orbit_radii: list[int] = field(default_factory=list)

    def find_group_containing_node(self, node_id):
        for group in self.node_groups.values():
            if node_id in group.node_ids:
                return group


def read_tree_data_file(filepath: str) -> SkillTree:
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
