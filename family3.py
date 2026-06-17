
import math
import os
import re
from dataclasses import dataclass, field
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

import pygame


# ============================================================
# ROOT-CENTERED GEDCOM GRAPH EXPLORER
# - renders immediate and extended biological relationships
# - preserves gender, adoption, file order, and family identity
# - supports pan, cursor zoom, node dragging, and double-click
#   re-rooting without duplicating people in the visible graph
# ============================================================


BG = (247, 248, 246)
PANEL_BG = (235, 239, 238)
GRID = (218, 226, 223)
TEXT = (28, 34, 35)
MUTED = (91, 103, 107)

ROOT_FILL = (255, 219, 112)
ROOT_BORDER = (126, 88, 18)

ANCESTOR_FILL = (191, 218, 246)
ANCESTOR_BORDER = (55, 105, 159)

SIDE_FILL = (221, 205, 238)
SIDE_BORDER = (110, 84, 148)

DESC_FILL = (193, 230, 205)
DESC_BORDER = (63, 128, 88)

SPOUSE_FILL = (246, 207, 184)
SPOUSE_BORDER = (159, 87, 54)

ADOPTED_FILL = (233, 233, 233)
ADOPTED_BORDER = (115, 115, 115)

MALE_ACCENT = (44, 106, 179)
FEMALE_ACCENT = (178, 81, 130)
UNKNOWN_ACCENT = (97, 107, 116)

SELECT_FILL = (255, 248, 190)
SELECT_BORDER = (150, 110, 0)

LINK = (70, 82, 82)
LINK_SOFT = (137, 150, 150)

MIN_WIN_W = 1100
MIN_WIN_H = 780
PANEL_W = 320
MARGIN = 60

GEN_GAP = 210
ROW_GAP = 132
SIBLING_GAP = 56
COLLATERAL_GAP = 92
ROW_NODE_GAP = 96
EXT_BUTTON_R = 15

BOX_PAD_X = 18
BOX_PAD_Y = 12
NAME_FONT_SIZE = 18
DATE_FONT_SIZE = 14

MAX_BOX_W = 360
MIN_BOX_W = 140
MIN_BOX_H = 60

FPS = 60


@dataclass
class Person:
    pid: str
    name: str = "Unknown"
    sex: str = ""
    birth: str = ""
    death: str = ""
    deceased_flag: bool = False
    fams: set = field(default_factory=set)
    famc: set = field(default_factory=set)
    adopted: bool = False
    adopted_in: set = field(default_factory=set)
    raw_note: str = ""
    file_order: int = 0

    def label_line(self) -> str:
        if self.birth or self.death:
            return f"{self.birth or ''} - {self.death or ''}"
        return "Deceased" if self.deceased_flag else "Living"


@dataclass
class Family:
    fid: str
    husband: str | None = None
    wife: str | None = None
    children: list[str] = field(default_factory=list)
    marriage: str = ""
    file_order: int = 0


@dataclass
class NodeLayout:
    pid: str
    x: float
    y: float
    w: int
    h: int
    relation: str


@dataclass
class ExtensionButton:
    rect: pygame.Rect
    source: str
    target: str
    direction: str


def year_from_date(value: str) -> int | None:
    """Extract a stable genealogical sort year from loose GEDCOM dates."""
    if not value:
        return None
    years = re.findall(r"(?<!\d)(\d{3,4})(?!\d)", value)
    if not years:
        return None
    year = int(years[-1])
    return year if 0 < year < 3000 else None


def clean_name(raw: str) -> str:
    raw = raw.replace("/", " ")
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw if raw else "Unknown"


def xref(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    m = re.match(r"@([^@]+)@", value)
    return m.group(1) if m else value


def parse_gedcom(path: str) -> tuple[dict[str, Person], dict[str, Family]]:
    people: dict[str, Person] = {}
    families: dict[str, Family] = {}

    current_pid = None
    current_fid = None
    current_event = None
    last_famc = None
    person_order = 0
    family_order = 0

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            m = re.match(r"^(\d+)\s+(?:(@[^@]+@)\s+)?([A-Z0-9_]+)(?:\s+(.*))?$", line)
            if not m:
                continue

            level = int(m.group(1))
            tag = m.group(3)
            value = (m.group(4) or "").strip()
            x = m.group(2)

            if level == 0:
                current_event = None
                last_famc = None
                current_pid = None
                current_fid = None

                if tag == "INDI" and x:
                    current_pid = xref(x)
                    if current_pid not in people:
                        person_order += 1
                        people[current_pid] = Person(pid=current_pid, file_order=person_order)
                elif tag == "FAM" and x:
                    current_fid = xref(x)
                    if current_fid not in families:
                        family_order += 1
                        families[current_fid] = Family(fid=current_fid, file_order=family_order)
                continue

            if current_pid is not None:
                p = people[current_pid]

                if tag == "NAME":
                    p.name = clean_name(value)
                elif tag == "SEX":
                    p.sex = value[:1].upper()
                elif tag in {"BIRT", "CHR", "BAPM"}:
                    current_event = "BIRT"
                elif tag in {"DEAT", "BURI", "CREM"}:
                    current_event = "DEAT"
                    if value.upper() == "Y":
                        p.deceased_flag = True
                elif tag == "MARR":
                    current_event = "MARR"
                elif tag == "DATE":
                    if current_event == "BIRT" and not p.birth:
                        p.birth = value
                    elif current_event == "DEAT" and not p.death:
                        p.death = value
                        p.deceased_flag = True
                elif tag == "FAMS":
                    kid = xref(value)
                    if kid:
                        p.fams.add(kid)
                elif tag == "FAMC":
                    fam = xref(value)
                    if fam:
                        p.famc.add(fam)
                        last_famc = fam
                elif tag == "ADOP":
                    p.adopted = True
                elif tag == "PEDI" and value.lower() == "adopted":
                    p.adopted = True
                    if last_famc:
                        p.adopted_in.add(last_famc)
                elif "ADOP" in line.upper():
                    p.adopted = True

            if current_fid is not None:
                fam = families[current_fid]
                if tag == "MARR":
                    current_event = "MARR"
                if tag == "HUSB":
                    fam.husband = xref(value)
                elif tag == "WIFE":
                    fam.wife = xref(value)
                elif tag == "CHIL":
                    child = xref(value)
                    if child:
                        fam.children.append(child)
                elif tag == "DATE" and current_event == "MARR" and not fam.marriage:
                    fam.marriage = value

    return people, families


class TreeBuilder:
    def __init__(self, people: dict[str, Person], families: dict[str, Family]):
        self.people = people
        self.families = families
        self._cache: dict[tuple, dict] = {}
        self.include_adopted = True

    def name_of(self, pid: str) -> str:
        return self.people.get(pid, Person(pid)).name

    def sort_key(self, pid: str) -> tuple:
        p = self.people.get(pid)
        if not p:
            return (1, 999999, "unknown", pid)
        year = year_from_date(p.birth)
        return (
            0 if year is not None else 1,
            year if year is not None else p.file_order,
            p.file_order,
            p.name.lower(),
            pid,
        )

    def ordered(self, ids) -> list[str]:
        return sorted(set(ids), key=self.sort_key)

    def visible(self, pid: str, root: str) -> bool:
        # Every individual connected to the chosen root is visible, including
        # adopted relatives.  The flag is kept only for old cache keys.
        return pid in self.people

    def is_adopted_child_in_family(self, pid: str, fid: str) -> bool:
        # Adoption is a display attribute, not a filter. Adopted children keep
        # their parent-child edges so their family lines stay connected.
        return False

    def spouses_of(self, pid: str, root: str | None = None) -> set[str]:
        out = set()
        person = self.people.get(pid)
        if not person:
            return out
        for fid in person.fams:
            fam = self.families.get(fid)
            if not fam:
                continue
            other = fam.wife if fam.husband == pid else fam.husband if fam.wife == pid else None
            if other and (root is None or self.visible(other, root)):
                out.add(other)
        return out

    def parent_in_laws_of(self, pid: str, root: str | None = None) -> set[str]:
        out = set()
        for spouse in self.spouses_of(pid, root=root):
            out |= self.parents_of(spouse, root=root)
        return out

    def sibling_in_laws_of(self, pid: str, root: str | None = None) -> set[str]:
        out = set()
        for sibling in self.siblings_of(pid, root=root):
            out |= self.spouses_of(sibling, root=root)
        for spouse in self.spouses_of(pid, root=root):
            out |= self.siblings_of(spouse, root=root)
        out.discard(pid)
        return out

    def children_of(self, pid: str, root: str | None = None) -> set[str]:
        out = set()
        person = self.people.get(pid)
        if not person:
            return out
        for fid in person.fams:
            fam = self.families.get(fid)
            if not fam:
                continue
            for child in fam.children:
                if self.is_adopted_child_in_family(child, fid):
                    continue
                if root is None or self.visible(child, root):
                    out.add(child)
        return out

    def parents_of(self, pid: str, root: str | None = None) -> set[str]:
        out = set()
        person = self.people.get(pid)
        if not person:
            return out
        for fid in person.famc:
            if self.is_adopted_child_in_family(pid, fid):
                continue
            fam = self.families.get(fid)
            if not fam:
                continue
            for parent in (fam.husband, fam.wife):
                if parent and (root is None or self.visible(parent, root)):
                    out.add(parent)
        return out

    def siblings_of(self, pid: str, root: str | None = None) -> set[str]:
        sibs = set()
        parents = self.parents_of(pid, root=root)
        for par in parents:
            for child in self.children_of(par, root=root):
                if child != pid:
                    sibs.add(child)
        return sibs

    def grandparents_of(self, pid: str, root: str | None = None) -> set[str]:
        gps = set()
        for par in self.parents_of(pid, root=root):
            gps |= self.parents_of(par, root=root)
        return gps

    def aunts_uncles_of(self, pid: str, root: str | None = None) -> set[str]:
        out = set()
        for par in self.parents_of(pid, root=root):
            for sib in self.siblings_of(par, root=root):
                if sib != pid:
                    out.add(sib)
        return out

    def cousins_of(self, pid: str, root: str | None = None) -> set[str]:
        out = set()
        for aunt_uncle in self.aunts_uncles_of(pid, root=root):
            for child in self.children_of(aunt_uncle, root=root):
                out.add(child)
        return out

    def grandchildren_of(self, pid: str, root: str | None = None) -> set[str]:
        out = set()
        for child in self.children_of(pid, root=root):
            for gc in self.children_of(child, root=root):
                out.add(gc)
        return out

    def nieces_nephews_of(self, pid: str, root: str | None = None) -> set[str]:
        out = set()
        for sibling in self.siblings_of(pid, root=root):
            out |= self.children_of(sibling, root=root)
        return out

    def build_visible_graph(self, root: str, expanded: set[str] | None = None):
        expanded = expanded or set()
        cache_key = (root, self.include_adopted, tuple(sorted(expanded)))
        if cache_key in self._cache:
            return self._cache[cache_key]

        parents = self.ordered(self.parents_of(root, root=root))
        parent_in_laws = self.ordered(self.parent_in_laws_of(root, root=root))
        siblings = self.ordered(self.siblings_of(root, root=root))
        spouses = self.ordered(self.spouses_of(root, root=root))
        sibling_in_laws = self.ordered(
            self.sibling_in_laws_of(root, root=root) - set(siblings) - set(spouses) - {root}
        )
        children = self.ordered(self.children_of(root, root=root))
        grandparents = self.ordered(self.grandparents_of(root, root=root))
        aunts_uncles = self.ordered(self.aunts_uncles_of(root, root=root))
        nieces_nephews = self.ordered(self.nieces_nephews_of(root, root=root))
        cousins = self.ordered(self.cousins_of(root, root=root) - set(nieces_nephews))
        grandchildren = self.ordered(self.grandchildren_of(root, root=root))

        # Show the whole connected biological/spousal component around the
        # selected root, not just the immediate ego network. This mirrors the
        # Ancestry-style tree screenshots: users can pan/zoom across a broad,
        # heavily connected chart while each person still appears only once.
        visible = set()
        pending = [root]
        while pending:
            pid = pending.pop()
            if pid in visible or not self.visible(pid, root=root):
                continue
            visible.add(pid)
            relatives = (
                set(self.parents_of(pid, root=root))
                | set(self.children_of(pid, root=root))
                | set(self.spouses_of(pid, root=root))
                | set(self.siblings_of(pid, root=root))
            )
            for rel in relatives:
                if rel not in visible and self.visible(rel, root=root):
                    pending.append(rel)

        # Explicit expansions are still honored for files with disconnected
        # data or when future filters make some relatives reachable only after
        # opening a branch.
        for pid in expanded:
            if self.visible(pid, root=root):
                visible.add(pid)

        edges = set()
        family_edges = {}
        marriage_edges = set()

        # parent-child edges, including adopted children
        for pid in visible:
            if pid not in self.people:
                continue
            p = self.people[pid]
            for fid in p.fams:
                fam = self.families.get(fid)
                if not fam:
                    continue
                for child in fam.children:
                    if child not in visible:
                        continue
                    if self.is_adopted_child_in_family(child, fid):
                        continue
                    if pid in (fam.husband, fam.wife):
                        edges.add((pid, child))
                        family_edges.setdefault(fid, {"parents": [], "children": []})
                        if pid not in family_edges[fid]["parents"]:
                            family_edges[fid]["parents"].append(pid)
                        if child not in family_edges[fid]["children"]:
                            family_edges[fid]["children"].append(child)

        # marriage edges
        for pid in visible:
            for spouse in self.spouses_of(pid, root=root):
                if spouse in visible:
                    pair = tuple(sorted((pid, spouse)))
                    marriage_edges.add(pair)

        data = {
            "root": root,
            "parents": parents,
            "parent_in_laws": parent_in_laws,
            "siblings": siblings,
            "spouses": spouses,
            "sibling_in_laws": sibling_in_laws,
            "children": children,
            "grandparents": grandparents,
            "aunts_uncles": aunts_uncles,
            "cousins": cousins,
            "nieces_nephews": nieces_nephews,
            "grandchildren": grandchildren,
            "visible": visible,
            "edges": edges,
            "family_edges": family_edges,
            "marriages": marriage_edges,
        }
        self._cache[cache_key] = data
        return data


def pick_root_person(root_tk: tk.Tk, people: dict[str, Person]) -> str | None:
    if not people:
        return None

    sorted_ids = sorted(
        people.keys(),
        key=lambda pid: (people[pid].name.lower(), pid)
    )

    names = {pid: people[pid].name for pid in sorted_ids}

    query = simpledialog.askstring(
        "Root Person",
        "Type part of the root person's name.\nLeave blank to use the first person in the file:",
        parent=root_tk
    )

    if not query:
        return sorted_ids[0]

    q = query.strip().lower()
    if not q:
        return sorted_ids[0]

    exact = [pid for pid in sorted_ids if names[pid].lower() == q]
    if exact:
        return exact[0]

    matches = [pid for pid in sorted_ids if q in names[pid].lower()]
    if matches:
        return matches[0]

    messagebox.showinfo(
        "No Match",
        "No matching person was found. The first person in the file will be used.",
        parent=root_tk
    )
    return sorted_ids[0]


class FamilyTreeApp:
    def __init__(self, people: dict[str, Person], families: dict[str, Family], root_pid: str):
        pygame.init()
        pygame.font.init()

        self.people = people
        self.families = families
        self.builder = TreeBuilder(people, families)
        self.expanded_people: set[str] = set()
        self.data = self.builder.build_visible_graph(root_pid, self.expanded_people)

        self.root_pid = root_pid
        self.selected_pid = root_pid

        self.font_name = pygame.font.SysFont("arial", NAME_FONT_SIZE, bold=True)
        self.font_date = pygame.font.SysFont("arial", DATE_FONT_SIZE, bold=True)
        self.font_ui = pygame.font.SysFont("arial", 18, bold=True)
        self.font_small = pygame.font.SysFont("arial", 14, bold=False)

        self.clock = pygame.time.Clock()
        self.dragging_pan = False
        self.dragging_node: str | None = None
        self.offset = [0.0, 0.0]
        self.user_zoom = 1.0
        self.auto_zoom = 1.0
        self.manual_positions: dict[str, tuple[float, float]] = {}
        self.toggle_adopted_rect = pygame.Rect(0, 0, 0, 0)
        self.last_click_time = 0
        self.last_click_pid: str | None = None
        self.extension_buttons: list[ExtensionButton] = []
        self.hover_extension: ExtensionButton | None = None
        self.pressed_extension: ExtensionButton | None = None

        self.node_layouts: dict[str, NodeLayout] = {}
        self.node_colors: dict[str, tuple] = {}
        self.rects: dict[str, pygame.Rect] = {}

        self.base_tree_w = 0
        self.base_tree_h = 0
        self.viewport_w = MIN_WIN_W
        self.viewport_h = MIN_WIN_H
        self.screen = None

        self.base_surface = None

        self.compute_layout()
        self.configure_window()
        self.fit_tree(initial=True)
        self.running = True

    def person(self, pid: str) -> Person:
        return self.people.get(pid, Person(pid=pid))

    def text_width(self, font: pygame.font.Font, text: str) -> int:
        return font.size(text)[0]

    def measure_box(self, pid: str) -> tuple[int, int]:
        p = self.person(pid)
        name = p.name
        line2 = p.label_line()

        name_w = self.text_width(self.font_name, name)
        date_w = self.text_width(self.font_date, line2)

        width = max(name_w, date_w) + BOX_PAD_X * 2
        width = max(MIN_BOX_W, min(MAX_BOX_W, width))

        # allow a slightly taller box if the name is long
        name_lines = 1 if name_w <= MAX_BOX_W - BOX_PAD_X * 2 else 2
        height = BOX_PAD_Y * 2 + self.font_name.get_linesize() * name_lines + self.font_date.get_linesize() + 8
        height = max(MIN_BOX_H, height)
        return width, height

    def relation_type(self, pid: str) -> str:
        if pid == self.root_pid:
            return "root"
        if pid in self.data["parents"] or pid in self.data["grandparents"]:
            return "ancestor"
        if pid in self.data["children"] or pid in self.data["grandchildren"]:
            return "descendant"
        if pid in self.data["spouses"]:
            return "spouse"
        return "side"

    def fill_color(self, relation: str):
        return {
            "root": ROOT_FILL,
            "ancestor": ANCESTOR_FILL,
            "descendant": DESC_FILL,
            "spouse": SPOUSE_FILL,
            "side": SIDE_FILL,
        }.get(relation, SIDE_FILL)

    def border_color(self, relation: str):
        return {
            "root": ROOT_BORDER,
            "ancestor": ANCESTOR_BORDER,
            "descendant": DESC_BORDER,
            "spouse": SPOUSE_BORDER,
            "side": SIDE_BORDER,
        }.get(relation, SIDE_BORDER)

    def compute_layout(self):
        self.node_layouts.clear()
        self.node_colors.clear()

        root = self.root_pid
        root_w, root_h = self.measure_box(root)
        self.node_layouts[root] = NodeLayout(root, 0, 0, root_w, root_h, "root")

        # measure all visible nodes first
        for pid in self.data["visible"]:
            w, h = self.measure_box(pid)
            relation = self.relation_type(pid)
            p = self.person(pid)
            if p.adopted or p.adopted_in:
                self.node_colors[pid] = (ADOPTED_FILL, ADOPTED_BORDER)
            else:
                self.node_colors[pid] = (self.fill_color(relation), self.border_color(relation))

        def ordered_unique(nodes):
            seen = set()
            out = []
            for pid in nodes:
                if pid in seen or pid not in self.data["visible"]:
                    continue
                seen.add(pid)
                out.append(pid)
            return out

        def coupled_row(primary_nodes, y, relation=None, center_x=0):
            """Place a generation row while keeping spouses beside each other.

            The visual style mirrors a conventional family-tree chart: spouses
            sit shoulder-to-shoulder, children connect to the midpoint between
            parents, and each generation gets its own horizontal band.
            """
            groups = []
            used = set()
            for pid in ordered_unique(primary_nodes):
                if pid in used:
                    continue
                group = [pid]
                used.add(pid)
                for spouse in self.builder.ordered(self.builder.spouses_of(pid, root=self.root_pid)):
                    if spouse in self.data["visible"] and spouse not in used:
                        group.append(spouse)
                        used.add(spouse)
                groups.append(group)

            if not groups:
                return

            group_gap = ROW_NODE_GAP * 1.45
            spouse_gap = max(26, SIBLING_GAP // 2)
            widths = []
            for group in groups:
                widths.append(sum(self.measure_box(pid)[0] for pid in group) + spouse_gap * (len(group) - 1))
            total_w = sum(widths) + group_gap * max(0, len(groups) - 1)
            x = center_x - total_w / 2
            for group, width in zip(groups, widths):
                gx = x
                for pid in group:
                    w, h = self.measure_box(pid)
                    rel = relation or self.relation_type(pid)
                    self.node_layouts[pid] = NodeLayout(pid, gx + w / 2, y, w, h, rel)
                    gx += w + spouse_gap
                x += width + group_gap

        def assign_generations():
            levels = {root: 0}
            queue = [root]
            while queue:
                pid = queue.pop(0)
                level = levels[pid]
                neighbors = []
                neighbors.extend((parent, level - 1) for parent in self.builder.parents_of(pid, root=self.root_pid))
                neighbors.extend((child, level + 1) for child in self.builder.children_of(pid, root=self.root_pid))
                neighbors.extend((spouse, level) for spouse in self.builder.spouses_of(pid, root=self.root_pid))
                for other, other_level in neighbors:
                    if other not in self.data["visible"]:
                        continue
                    if other not in levels:
                        levels[other] = other_level
                        queue.append(other)

            # Any unusual connected leftovers stay near the root instead of
            # disappearing, which keeps the tree robust for imperfect GEDCOMs.
            for pid in self.data["visible"]:
                levels.setdefault(pid, 0)
            return levels

        # A clear, heavily connected family-tree layout: every visible person is
        # placed in a generation row. Couples stay adjacent, rows run from oldest
        # ancestors down to youngest descendants, and the whole chart remains
        # connected by the family-edge drawing pass.
        self.node_layouts.clear()
        levels = assign_generations()
        rows: dict[int, list[str]] = {}
        for pid, level in levels.items():
            rows.setdefault(level, []).append(pid)

        for level in sorted(rows):
            row = self.builder.ordered(rows[level])
            y = level * GEN_GAP
            relation = "ancestor" if level < 0 else "descendant" if level > 0 else None
            coupled_row(row, y, relation=relation)

        # Keep manually moved people at their own positions. Marriage lines are
        # drawn with elbows, so dragging one selected spouse bends the connector
        # while preserving the relationship.
        for pid, (x, y) in self.manual_positions.items():
            node = self.node_layouts.get(pid)
            if node:
                self.node_layouts[pid] = NodeLayout(pid, x, y, node.w, node.h, node.relation)

        # compute bounds
        xs = []
        ys = []
        for node in self.node_layouts.values():
            xs.extend([node.x - node.w / 2, node.x + node.w / 2])
            ys.extend([node.y - node.h / 2, node.y + node.h / 2])

        self.tree_min_x = min(xs) if xs else -100
        self.tree_max_x = max(xs) if xs else 100
        self.tree_min_y = min(ys) if ys else -100
        self.tree_max_y = max(ys) if ys else 100

        self.base_tree_w = self.tree_max_x - self.tree_min_x
        self.base_tree_h = self.tree_max_y - self.tree_min_y

    def configure_window(self):
        info = pygame.display.Info()
        max_w = max(900, info.current_w - 80)
        max_h = max(650, info.current_h - 120)

        content_w = int(self.base_tree_w + MARGIN * 2 + PANEL_W)
        content_h = int(self.base_tree_h + MARGIN * 2 + 120)

        self.viewport_w = max(MIN_WIN_W, min(content_w, max_w))
        self.viewport_h = max(MIN_WIN_H, min(content_h, max_h))

        self.screen = pygame.display.set_mode((self.viewport_w, self.viewport_h), pygame.RESIZABLE)
        pygame.display.set_caption(f"Ancestry Graph Explorer - {self.person(self.root_pid).name}")

    def fit_tree(self, initial=False):
        tree_w = max(1.0, self.base_tree_w)
        tree_h = max(1.0, self.base_tree_h)

        usable_w = max(1, self.viewport_w - PANEL_W - MARGIN * 2)
        usable_h = max(1, self.viewport_h - MARGIN * 2)

        self.auto_zoom = min(usable_w / tree_w, usable_h / tree_h, 1.0)

        if initial:
            self.user_zoom = 1.0
            self.offset = [0.0, 0.0]

        self.center_tree()

    def center_tree(self):
        # Center the tree in the left pane, keeping the side panel reserved.
        cx = (self.tree_min_x + self.tree_max_x) / 2
        cy = (self.tree_min_y + self.tree_max_y) / 2

        self.offset[0] = -cx
        self.offset[1] = -cy

    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        zoom = self.auto_zoom * self.user_zoom
        left_w = self.viewport_w - PANEL_W

        sx = (x + self.offset[0]) * zoom + left_w / 2
        sy = (y + self.offset[1]) * zoom + self.viewport_h / 2
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        zoom = self.auto_zoom * self.user_zoom
        left_w = self.viewport_w - PANEL_W
        x = (sx - left_w / 2) / zoom - self.offset[0]
        y = (sy - self.viewport_h / 2) / zoom - self.offset[1]
        return x, y

    def draw_elbow(self, surface, start, end, color, width=3):
        x1, y1 = start
        x2, y2 = end
        mid_y = (y1 + y2) / 2
        pygame.draw.line(surface, color, (x1, y1), (x1, mid_y), width)
        pygame.draw.line(surface, color, (x1, mid_y), (x2, mid_y), width)
        pygame.draw.line(surface, color, (x2, mid_y), (x2, y2), width)

    def marriage_connector(self, a: NodeLayout, b: NodeLayout) -> tuple[float, float]:
        ax, ay = self.world_to_screen(a.x, a.y)
        bx, by = self.world_to_screen(b.x, b.y)
        return ((ax + bx) / 2, (ay + by) / 2)

    def draw_marriage(self, surface, a: NodeLayout, b: NodeLayout):
        ax, ay = self.world_to_screen(a.x, a.y)
        bx, by = self.world_to_screen(b.x, b.y)
        zoom = self.auto_zoom * self.user_zoom
        if ax <= bx:
            start = (ax + a.w / 2 * zoom, ay)
            end = (bx - b.w / 2 * zoom, by)
        else:
            start = (bx + b.w / 2 * zoom, by)
            end = (ax - a.w / 2 * zoom, ay)
        mid_x = (start[0] + end[0]) / 2
        pygame.draw.line(surface, LINK, start, (mid_x, start[1]), 3)
        pygame.draw.line(surface, LINK, (mid_x, start[1]), (mid_x, end[1]), 3)
        pygame.draw.line(surface, LINK, (mid_x, end[1]), end, 3)
        pygame.draw.circle(surface, LINK, (int(mid_x), int((start[1] + end[1]) / 2)), 5)

    def draw_family_children(self, surface, fid: str, family):
        children = [self.node_layouts[c] for c in family["children"] if c in self.node_layouts]
        parents = [self.node_layouts[p] for p in family["parents"] if p in self.node_layouts]
        if not children or not parents:
            return
        zoom = self.auto_zoom * self.user_zoom
        if len(parents) >= 2:
            start = self.marriage_connector(parents[0], parents[1])
        else:
            px, py = self.world_to_screen(parents[0].x, parents[0].y)
            start = (px, py + parents[0].h / 2 * zoom)
        child_tops = []
        for child in children:
            cx, cy = self.world_to_screen(child.x, child.y)
            child_tops.append((cx, cy - child.h / 2 * zoom))
        trunk_y = min(y for _, y in child_tops) - max(22, int(36 * zoom))
        pygame.draw.line(surface, LINK, start, (start[0], trunk_y), max(2, int(3 * zoom)))
        if len(child_tops) > 1:
            pygame.draw.line(surface, LINK, (min(x for x, _ in child_tops), trunk_y), (max(x for x, _ in child_tops), trunk_y), max(2, int(3 * zoom)))
        for end in child_tops:
            pygame.draw.line(surface, LINK, (end[0], trunk_y), end, max(2, int(3 * zoom)))
            self.draw_arrowhead(surface, (end[0], trunk_y), end, LINK, max(8, int(11 * zoom)))

    def draw_parent_child(self, surface, parent: NodeLayout, child: NodeLayout):
        px, py = self.world_to_screen(parent.x, parent.y)
        cx, cy = self.world_to_screen(child.x, child.y)

        zoom = self.auto_zoom * self.user_zoom
        start = (px, py + parent.h / 2 * zoom)
        end = (cx, cy - child.h / 2 * zoom)
        self.draw_elbow(surface, start, end, LINK, width=max(2, int(3 * zoom)))
        self.draw_arrowhead(surface, start, end, LINK, max(8, int(11 * zoom)))

    def draw_arrowhead(self, surface, start, end, color, size):
        x1, y1 = start
        x2, y2 = end
        angle = math.atan2(y2 - y1, x2 - x1)
        left = (x2 - size * math.cos(angle - math.pi / 6), y2 - size * math.sin(angle - math.pi / 6))
        right = (x2 - size * math.cos(angle + math.pi / 6), y2 - size * math.sin(angle + math.pi / 6))
        pygame.draw.polygon(surface, color, [(x2, y2), left, right])

    def hidden_parent_targets(self, pid: str) -> list[str]:
        return self.builder.ordered(
            parent for parent in self.builder.parents_of(pid)
            if parent not in self.data["visible"]
        )

    def hidden_child_targets(self, pid: str) -> list[str]:
        return self.builder.ordered(
            child for child in self.builder.children_of(pid)
            if child not in self.data["visible"]
        )

    def draw_extension_button(self, surface, center, direction, source, target):
        zoom = self.auto_zoom * self.user_zoom
        radius = max(10, int(EXT_BUTTON_R * zoom))
        rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        rect.center = (int(center[0]), int(center[1]))
        button = ExtensionButton(rect, source, target, direction)
        self.extension_buttons.append(button)

        pressed = (
            self.pressed_extension is not None
            and self.pressed_extension.source == source
            and self.pressed_extension.target == target
            and self.pressed_extension.direction == direction
        )
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        fill = (204, 216, 214) if not pressed else (162, 182, 178)
        border = LINK if not hovered else SELECT_BORDER
        pygame.draw.circle(surface, fill, rect.center, radius)
        pygame.draw.circle(surface, border, rect.center, radius, max(2, int(2 * zoom)))

        cx, cy = rect.center
        size = max(6, int(8 * zoom))
        if direction == "up":
            points = [(cx, cy - size), (cx - size, cy + size * 0.65), (cx + size, cy + size * 0.65)]
        else:
            points = [(cx, cy + size), (cx - size, cy - size * 0.65), (cx + size, cy - size * 0.65)]
        pygame.draw.polygon(surface, LINK, points)

    def draw_extension_arrows(self, surface):
        self.extension_buttons.clear()
        zoom = self.auto_zoom * self.user_zoom
        for pid, node in self.node_layouts.items():
            x, y = self.world_to_screen(node.x, node.y)
            half_h = node.h / 2 * zoom
            size = max(8, int(12 * zoom))
            parent_targets = self.hidden_parent_targets(pid)
            if parent_targets:
                tip = (x, y - half_h - size * 2.3)
                base_y = y - half_h - 2
                pygame.draw.line(surface, LINK_SOFT, (x, base_y), tip, max(1, int(2 * zoom)))
                self.draw_extension_button(surface, tip, "up", pid, parent_targets[0])
            child_targets = self.hidden_child_targets(pid)
            if child_targets:
                tip = (x, y + half_h + size * 2.3)
                base_y = y + half_h + 2
                pygame.draw.line(surface, LINK_SOFT, (x, base_y), tip, max(1, int(2 * zoom)))
                self.draw_extension_button(surface, tip, "down", pid, child_targets[0])

    def draw_box(self, surface, node: NodeLayout):
        p = self.person(node.pid)
        fill, border = self.node_colors.get(node.pid, (SIDE_FILL, SIDE_BORDER))

        x, y = self.world_to_screen(node.x, node.y)
        zoom = self.auto_zoom * self.user_zoom

        w = max(1, int(node.w * zoom))
        h = max(1, int(node.h * zoom))
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (int(x), int(y))

        self.rects[node.pid] = rect

        is_selected = node.pid == self.selected_pid
        rect_fill = SELECT_FILL if is_selected else fill
        rect_border = SELECT_BORDER if is_selected else border

        pygame.draw.rect(surface, rect_fill, rect, border_radius=max(8, int(14 * zoom)))
        pygame.draw.rect(surface, rect_border, rect, width=max(2, int(3 * zoom)), border_radius=max(8, int(14 * zoom)))
        accent = UNKNOWN_ACCENT
        if p.sex == "M":
            accent = MALE_ACCENT
        elif p.sex == "F":
            accent = FEMALE_ACCENT
        stripe = pygame.Rect(rect.left, rect.top, max(4, int(7 * zoom)), rect.height)
        pygame.draw.rect(surface, accent, stripe, border_top_left_radius=max(8, int(14 * zoom)), border_bottom_left_radius=max(8, int(14 * zoom)))
        if p.adopted or p.adopted_in:
            inset = max(5, int(8 * zoom))
            pygame.draw.rect(surface, ADOPTED_BORDER, rect.inflate(-inset, -inset), width=max(1, int(2 * zoom)), border_radius=max(6, int(10 * zoom)))

        # name line
        name = p.name
        date_line = p.label_line()

        name_font_size = max(11, int(NAME_FONT_SIZE * zoom))
        date_font_size = max(9, int(DATE_FONT_SIZE * zoom))
        name_font = pygame.font.SysFont("arial", name_font_size, bold=True)
        date_font = pygame.font.SysFont("arial", date_font_size, bold=True)

        name_surf = name_font.render(name, True, TEXT)
        date_surf = date_font.render(date_line, True, MUTED)

        name_rect = name_surf.get_rect(center=(rect.centerx, rect.centery - max(6, int(10 * zoom))))
        date_rect = date_surf.get_rect(center=(rect.centerx, rect.centery + max(8, int(10 * zoom))))

        # If the name is too wide, shrink it more until it fits.
        if name_surf.get_width() > rect.width - 12:
            fit_size = name_font_size
            while fit_size > 9:
                test_font = pygame.font.SysFont("arial", fit_size, bold=True)
                test_surf = test_font.render(name, True, TEXT)
                if test_surf.get_width() <= rect.width - 14:
                    name_font = test_font
                    name_surf = test_surf
                    name_rect = name_surf.get_rect(center=(rect.centerx, rect.centery - max(6, int(10 * zoom))))
                    break
                fit_size -= 1

        if date_surf.get_width() > rect.width - 12:
            fit_size = date_font_size
            while fit_size > 8:
                test_font = pygame.font.SysFont("arial", fit_size, bold=True)
                test_surf = test_font.render(date_line, True, MUTED)
                if test_surf.get_width() <= rect.width - 14:
                    date_font = test_font
                    date_surf = test_surf
                    date_rect = date_surf.get_rect(center=(rect.centerx, rect.centery + max(8, int(10 * zoom))))
                    break
                fit_size -= 1

        surface.blit(name_surf, name_rect)
        surface.blit(date_surf, date_rect)

    def draw_panel(self, surface):
        panel = pygame.Rect(self.viewport_w - PANEL_W, 0, PANEL_W, self.viewport_h)
        pygame.draw.rect(surface, PANEL_BG, panel)

        pygame.draw.line(surface, GRID, (panel.left, 0), (panel.left, self.viewport_h), 3)

        root = self.person(self.root_pid)
        sel = self.person(self.selected_pid)

        title = self.font_ui.render("ANCESTRY GRAPH", True, TEXT)
        surface.blit(title, (panel.left + 20, 22))

        sub = self.font_small.render(f"Root: {root.name}", True, MUTED)
        surface.blit(sub, (panel.left + 20, 54))

        sel_title = self.font_ui.render("Selected", True, TEXT)
        surface.blit(sel_title, (panel.left + 20, 96))

        lines = [
            f"Name: {sel.name}",
            f"Gender: {sel.sex or 'Unknown'}",
            f"Birth–Death: {sel.label_line()}",
            f"Adopted: {'Yes' if sel.adopted or sel.adopted_in else 'No'}",
            f"Spouses: {len(self.builder.spouses_of(self.selected_pid, root=self.root_pid))}",
            f"Children: {len(self.builder.children_of(self.selected_pid, root=self.root_pid))}",
            f"Parents: {len(self.builder.parents_of(self.selected_pid, root=self.root_pid))}",
            f"Siblings: {len(self.builder.siblings_of(self.selected_pid, root=self.root_pid))}",
        ]

        y = 130
        for line in lines:
            surf = self.font_small.render(line, True, TEXT)
            surface.blit(surf, (panel.left + 20, y))
            y += 26

        y += 12
        help_title = self.font_ui.render("Controls", True, TEXT)
        surface.blit(help_title, (panel.left + 20, y))
        y += 34

        controls = [
            "Drag empty: pan",
            "Drag box: reposition",
            "Wheel: cursor zoom",
            "Double-click: new root",
            "Arrow buttons: expand branch",
            "S: save unique PNG",
            "Click a box: select",
            "Drag selected box: move it",
            "ESC / Q: quit",
        ]
        for line in controls:
            surf = self.font_small.render(line, True, TEXT)
            surface.blit(surf, (panel.left + 20, y))
            y += 22

        y += 14
        counts_title = self.font_ui.render("Visible counts", True, TEXT)
        surface.blit(counts_title, (panel.left + 20, y))
        y += 34

        all_count = self.font_small.render(f"All individuals in file: {len(self.people)}", True, TEXT)
        surface.blit(all_count, (panel.left + 20, y))
        y += 28
        visible_count = self.font_small.render(f"Individuals in this tree: {len(self.data['visible'])}", True, TEXT)
        surface.blit(visible_count, (panel.left + 20, y))
        y += 34

        counts = [
            ("Parents", len(self.data["parents"])),
            ("Parent-in-laws", len(self.data["parent_in_laws"])),
            ("Sibling-in-laws", len(self.data["sibling_in_laws"])),
            ("Sides", len(self.data["siblings"]) + len(self.data["aunts_uncles"]) + len(self.data["cousins"]) + len(self.data["nieces_nephews"])),
            ("Descendants", len(self.data["children"]) + len(self.data["grandchildren"])),
        ]
        for label, value in counts:
            surf = self.font_small.render(f"{label}: {value}", True, TEXT)
            surface.blit(surf, (panel.left + 20, y))
            y += 22

    def draw_background(self, surface):
        surface.fill(BG)

        # subtle guide line in the tree area
        left_w = self.viewport_w - PANEL_W
        for x in range(0, left_w, 120):
            pygame.draw.line(surface, GRID, (x, 0), (x, self.viewport_h), 1)
        for y in range(0, self.viewport_h, 120):
            pygame.draw.line(surface, GRID, (0, y), (left_w, y), 1)

    def render(self):
        self.rects.clear()
        self.draw_background(self.screen)

        # draw marriages first
        for a_id, b_id in sorted(self.data["marriages"]):
            if a_id in self.node_layouts and b_id in self.node_layouts:
                self.draw_marriage(self.screen, self.node_layouts[a_id], self.node_layouts[b_id])

        # draw parent-child trunks from each parents' marriage connector.
        for fid, family in sorted(self.data["family_edges"].items()):
            self.draw_family_children(self.screen, fid, family)

        self.draw_extension_arrows(self.screen)

        # draw boxes on top
        # explicit order: ancestors, sides, root, spouses, descendants
        ordered_ids = []
        ordered_ids.extend(self.data["grandparents"])
        ordered_ids.extend(self.data["aunts_uncles"])
        ordered_ids.extend(self.data["parents"])
        ordered_ids.extend(self.data["parent_in_laws"])
        ordered_ids.extend(self.data["siblings"])
        ordered_ids.append(self.root_pid)
        ordered_ids.extend(self.data["spouses"])
        ordered_ids.extend(self.data["sibling_in_laws"])
        ordered_ids.extend(self.data["cousins"])
        ordered_ids.extend(self.data["nieces_nephews"])
        ordered_ids.extend(self.data["children"])
        ordered_ids.extend(self.data["grandchildren"])

        seen = set()
        for pid in ordered_ids:
            if pid in seen or pid not in self.node_layouts:
                continue
            seen.add(pid)
            self.draw_box(self.screen, self.node_layouts[pid])

        for pid in self.builder.ordered(self.node_layouts):
            if pid in seen:
                continue
            seen.add(pid)
            self.draw_box(self.screen, self.node_layouts[pid])

        self.draw_panel(self.screen)

        pygame.display.flip()

    def save_screenshot(self):
        folder = os.path.dirname(__file__)
        stem = "ancestry_tree_screenshot"
        path = os.path.join(folder, f"{stem}.png")
        index = 1
        while os.path.exists(path):
            path = os.path.join(folder, f"{stem}_{index:03d}.png")
            index += 1
        pygame.image.save(self.screen, path)
        return path

    def extension_at_point(self, pos) -> ExtensionButton | None:
        x, y = pos
        if x >= self.viewport_w - PANEL_W:
            return None
        for button in reversed(self.extension_buttons):
            if button.rect.collidepoint(x, y):
                return button
        return None

    def update_cursor(self):
        pos = pygame.mouse.get_pos()
        self.hover_extension = self.extension_at_point(pos)
        cursor = pygame.SYSTEM_CURSOR_ARROW
        if self.pressed_extension or self.hover_extension:
            cursor = pygame.SYSTEM_CURSOR_HAND
        elif self.dragging_node:
            cursor = pygame.SYSTEM_CURSOR_SIZEALL
        try:
            pygame.mouse.set_cursor(cursor)
        except pygame.error:
            pass

    def node_at_point(self, pos) -> str | None:
        x, y = pos
        if x >= self.viewport_w - PANEL_W:
            return None
        for pid, rect in reversed(list(self.rects.items())):
            if rect.collidepoint(x, y):
                return pid
        return None

    def select_at_point(self, pos):
        pid = self.node_at_point(pos)
        if pid:
            self.selected_pid = pid
        return pid

    def refresh_graph(self, reset_positions=False):
        self.data = self.builder.build_visible_graph(self.root_pid, self.expanded_people)
        if reset_positions:
            self.manual_positions.clear()
        else:
            self.manual_positions = {key: value for key, value in self.manual_positions.items() if key in self.data["visible"]}
        self.compute_layout()
        self.fit_tree(initial=reset_positions)
        pygame.display.set_caption(f"Ancestry Graph Explorer - {self.person(self.root_pid).name}")

    def set_root(self, pid: str):
        if pid not in self.people:
            return
        self.root_pid = pid
        self.selected_pid = pid
        self.expanded_people.clear()
        # A new root is a fresh screen: clear all dragged positions and reset zoom/pan.
        self.refresh_graph(reset_positions=True)

    def expand_branch(self, pid: str):
        if pid not in self.people:
            return
        self.expanded_people.add(pid)
        self.selected_pid = pid
        self.refresh_graph(reset_positions=False)

    def toggle_adopted(self):
        # Adopted relatives are always shown; keep this no-op so older key
        # bindings do not accidentally hide part of the family.
        self.builder.include_adopted = True
        self.builder._cache.clear()
        self.refresh_graph(reset_positions=False)

    def zoom_at(self, pos, factor):
        before = self.screen_to_world(*pos)
        self.user_zoom = max(1e-6, self.user_zoom * factor)
        zoom = self.auto_zoom * self.user_zoom
        left_w = self.viewport_w - PANEL_W
        if zoom <= 0:
            return
        self.offset[0] = (pos[0] - left_w / 2) / zoom - before[0]
        self.offset[1] = (pos[1] - self.viewport_h / 2) / zoom - before[1]

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        self.running = False
                    elif event.key == pygame.K_s:
                        saved = self.save_screenshot()
                        print(f"Saved screenshot to {saved}")

                elif event.type == pygame.VIDEORESIZE:
                    self.viewport_w = max(MIN_WIN_W, event.w)
                    self.viewport_h = max(MIN_WIN_H, event.h)
                    self.screen = pygame.display.set_mode((self.viewport_w, self.viewport_h), pygame.RESIZABLE)
                    self.fit_tree(initial=False)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        extension = self.extension_at_point(event.pos)
                        if extension:
                            self.pressed_extension = extension
                            self.dragging_node = None
                            self.dragging_pan = False
                            continue
                        pid = self.node_at_point(event.pos)
                        now = pygame.time.get_ticks()
                        double_click = (
                            pid is not None
                            and pid == self.last_click_pid
                            and now - self.last_click_time <= 420
                        )
                        self.last_click_time = now
                        self.last_click_pid = pid
                        if double_click:
                            self.set_root(pid)
                            self.dragging_node = None
                            self.dragging_pan = False
                            continue
                        if pid:
                            if pid == self.selected_pid:
                                self.dragging_node = pid
                            else:
                                self.selected_pid = pid
                                self.dragging_node = None
                        else:
                            self.dragging_pan = True
                    elif event.button == 4:
                        self.zoom_at(event.pos, 1.08)
                    elif event.button == 5:
                        self.zoom_at(event.pos, 1 / 1.08)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if self.pressed_extension:
                            released = self.extension_at_point(event.pos)
                            if (
                                released
                                and released.source == self.pressed_extension.source
                                and released.target == self.pressed_extension.target
                                and released.direction == self.pressed_extension.direction
                            ):
                                self.expand_branch(released.target)
                            self.pressed_extension = None
                        self.dragging_pan = False
                        self.dragging_node = None

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_node:
                        node = self.node_layouts.get(self.dragging_node)
                        zoom = self.auto_zoom * self.user_zoom
                        if node and zoom > 0:
                            dx = event.rel[0] / zoom
                            dy = event.rel[1] / zoom
                            new_pos = (node.x + dx, node.y + dy)
                            self.manual_positions[self.dragging_node] = new_pos
                            self.node_layouts[self.dragging_node] = NodeLayout(
                                node.pid, new_pos[0], new_pos[1], node.w, node.h, node.relation
                            )
                    elif self.dragging_pan:
                        dx = event.rel[0]
                        dy = event.rel[1]
                        zoom = self.auto_zoom * self.user_zoom
                        if zoom > 0:
                            self.offset[0] += dx / zoom
                            self.offset[1] += dy / zoom

            self.update_cursor()
            self.render()

        pygame.quit()


def main():
    tk_root = tk.Tk()
    tk_root.withdraw()
    tk_root.update()

    file_path = filedialog.askopenfilename(
        title="Select GEDCOM File",
        filetypes=[("GEDCOM files", "*.ged"), ("All files", "*.*")]
    )

    if not file_path:
        tk_root.destroy()
        return

    people, families = parse_gedcom(file_path)
    if not people:
        messagebox.showerror("No data", "No individuals were found in that GEDCOM file.", parent=tk_root)
        tk_root.destroy()
        return

    root_pid = pick_root_person(tk_root, people)
    tk_root.destroy()
    
    if not root_pid:
        return

    app = FamilyTreeApp(people, families, root_pid)
    app.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        try:
            import traceback
            traceback.print_exc()
        finally:
            raise
