import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, List, Dict

from GuideToExile.data_classes import NodeGroup, TreeNode, SkillTree
from GuideToExile.settings.common import ASC_TREE_X, ASC_TREE_Y


@dataclass(frozen=True)
class GraphElement(ABC):
    is_taken: bool
    is_hidden: bool

    @property
    def color(self):
        return "#FF0000" if self.is_taken else "#736d6a"

    @property
    @abstractmethod
    def svg_string(self):
        pass


@dataclass(frozen=True)
class TreeGraphNode(GraphElement):
    node_id: str
    pos_x: float
    pos_y: float
    size: int

    @property
    def pos(self):
        return self.pos_x, self.pos_y

    @property
    def svg_string(self):
        if self.is_hidden:
            return ''
        return f'<circle cx="{self.pos_x}" cy="{self.pos_y}" r="{self.size}" fill="{self.color}" data-id="{self.node_id}"/>\n'


@dataclass(frozen=True)
class TreeGraphPath(GraphElement):
    start_node_id: str
    end_node_id: str
    start_pos: Tuple[float, float]
    end_pos: Tuple[float, float]
    is_curved: bool
    radius: int
    is_clockwise: bool

    def __eq__(self, other):
        if isinstance(other, TreeGraphPath):
            return ((self.start_node_id == other.start_node_id and self.end_node_id == other.end_node_id) or
                    (self.start_node_id == other.end_node_id and self.end_node_id == other.start_node_id))
        return False

    @property
    def svg_string(self):
        if self.is_hidden:
            return ''
        if self.is_curved:
            reverse = 0 if self.is_clockwise else 1
            return f'<path d="M {self.start_pos[0]} {self.start_pos[1]} A {self.radius} {self.radius} 0 0 {reverse} {self.end_pos[0]} {self.end_pos[1]}" fill="transparent" stroke="{self.color}" stroke-width="24"/>\n'
        else:
            return f'<line fill="transparent" stroke="{self.color}" stroke-width="24" x1="{self.start_pos[0]}" y1="{self.start_pos[1]}" x2="{self.end_pos[0]}" y2="{self.end_pos[1]}"/>\n'


class TreeGraph:
    nodes: Dict[str, TreeGraphNode]
    paths: List[TreeGraphPath]
    skill_tree: SkillTree

    def __init__(self, skill_tree):
        self.nodes = {}
        self.paths = []
        self.skill_tree = skill_tree
        self._init_nodes()
        self._init_paths()

    def _init_nodes(self):
        groups = self.skill_tree.node_groups.values()
        tree_nodes = self.skill_tree.nodes
        for group in groups:
            for node_id in group.node_ids:
                node = tree_nodes[node_id]
                if node.is_mastery or node.is_class_start_node:
                    continue
                pos_x, pos_y = self._calculate_node_position(group, node)
                self.nodes[node_id] = TreeGraphNode(node_id=node_id, pos_x=pos_x, pos_y=pos_y, size=node.size,
                                                    is_taken=False, is_hidden=False)

    def _init_paths(self):
        paths_list = []
        for node_id, node in self.skill_tree.nodes.items():
            if node.is_mastery or node.is_class_start_node:
                continue
            for connected_node_id in node.connected_nodes:
                connected_node = self.skill_tree.nodes[connected_node_id]
                if not node.is_connected_to(connected_node):
                    continue
                start_pos = self.nodes[node_id].pos
                end_position = self.nodes[connected_node_id].pos
                start_node_group = self.skill_tree.find_group_containing_node(node_id)
                end_node_group = self.skill_tree.find_group_containing_node(connected_node_id)
                is_curved = (start_node_group == end_node_group) and node.orbit_radii == connected_node.orbit_radii
                radius = self.skill_tree.orbit_radii[node.orbit_radii]
                is_path_clockwise = _are_nodes_clockwise(start_pos, end_position, start_node_group)

                new_path = TreeGraphPath(start_node_id=node_id, end_node_id=connected_node_id, start_pos=start_pos,
                                         end_pos=end_position, is_curved=is_curved, radius=radius, is_taken=False,
                                         is_clockwise=is_path_clockwise, is_hidden=False)
                paths_list.append(new_path)
        self.paths = list(set(paths_list))

    @property
    def tree_dimensions(self):
        min_x = self.skill_tree.min_x
        min_y = self.skill_tree.min_y
        size_x = self.skill_tree.max_x - min_x
        size_y = self.skill_tree.max_y - min_y
        return min_x + 2400, min_y + 800, size_x - 2800, size_y - 1100

    def as_html_with_taken_nodes(self, taken_node_ids: List[str]) -> str:
        min_x, min_y, size_x, size_y = self.tree_dimensions
        html = f'<svg style="background-color: transparent;" viewBox="{min_x} {min_y} {size_x} {size_y}">\n'
        asc_tree_x = ASC_TREE_X
        asc_tree_y = ASC_TREE_Y
        asc_name = self._find_asc_name(taken_node_ids)
        if asc_name:
            html += f'<circle cx="{asc_tree_x}" cy="{asc_tree_y}" r="700" fill="#35383B"/>\n'
        graph_elements = self._get_all_graph_elements_including_taken_nodes(taken_node_ids)
        graph_elements.sort(key=lambda v: v.is_taken)
        html += ''.join(el.svg_string for el in graph_elements)
        html += '</svg>\n'
        return html

    def _get_all_graph_elements_including_taken_nodes(self, taken_node_ids: List[str]) -> List[GraphElement]:
        asc_name = self._find_asc_name(taken_node_ids)
        nodes = self._get_nodes_including_taken_nodes(taken_node_ids, asc_name)
        paths = self._get_paths_including_taken_nodes(taken_node_ids, asc_name)

        return nodes + paths

    def _get_nodes_including_taken_nodes(self, taken_node_ids: List[str], asc_name: str) -> List[GraphElement]:
        nodes = []
        for node_id, node in self.nodes.items():
            is_hidden = (self.skill_tree.nodes[node_id].ascendancy_name != ''
                         and self.skill_tree.nodes[node_id].ascendancy_name != asc_name)
            new_node = TreeGraphNode(node_id=node_id,
                                     pos_x=node.pos_x,
                                     pos_y=node.pos_y,
                                     size=node.size,
                                     is_taken=(node_id in taken_node_ids),
                                     is_hidden=is_hidden)
            nodes.append(new_node)
        return nodes

    def _get_paths_including_taken_nodes(self, taken_node_ids: List[str], asc_name: str) -> List[GraphElement]:
        paths = []
        for path in self.paths:
            is_taken = path.start_node_id in taken_node_ids and path.end_node_id in taken_node_ids
            is_hidden = (self.skill_tree.nodes[path.start_node_id].ascendancy_name != ''
                         and self.skill_tree.nodes[path.start_node_id].ascendancy_name != asc_name
                         and self.skill_tree.nodes[path.end_node_id].ascendancy_name != ''
                         and self.skill_tree.nodes[path.end_node_id].ascendancy_name != asc_name)
            paths.append(TreeGraphPath(start_node_id=path.start_node_id,
                                       end_node_id=path.end_node_id,
                                       start_pos=path.start_pos,
                                       end_pos=path.end_pos,
                                       is_curved=path.is_curved,
                                       radius=path.radius,
                                       is_clockwise=path.is_clockwise,
                                       is_taken=is_taken,
                                       is_hidden=is_hidden))
        return paths

    def _calculate_node_position(self, group: NodeGroup, node: TreeNode) -> Tuple[float, float]:
        nodes_per_orbit = self.skill_tree.skills_per_orbit[node.orbit_radii]
        orbit_radius = self.skill_tree.orbit_radii[node.orbit_radii]
        angle_degrees = (360.0 / nodes_per_orbit) * node.orbit_index - 90.0
        angle_radians = math.radians(angle_degrees)
        pos_x = math.cos(angle_radians) * orbit_radius + group.x
        pos_y = math.sin(angle_radians) * orbit_radius + group.y
        return pos_x, pos_y

    def _find_asc_name(self, taken_node_ids: List[str]) -> str:
        for name, node_id in self.skill_tree.asc_start_nodes.items():
            if node_id in taken_node_ids:
                return name
        return ''


def _are_nodes_clockwise(start_pos: Tuple[float, float], end_position: Tuple[float, float], node_group: NodeGroup):
    center_x = node_group.x
    center_y = node_group.y
    det = (start_pos[0] - center_x) * (end_position[1] - center_y) - (end_position[0] - center_x) * (
        start_pos[1] - center_y)
    return det <= 0
