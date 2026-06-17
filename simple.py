
import math
import os
import re
import sys
from dataclasses import dataclass, field
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

import pygame


# ============================================================
# GEDCOM ANCESTRY TREE VIEWER
# - root, siblings, spouse, children, parents, grandparents,
#   aunts, uncles, first cousins, grandchildren only
# - excludes adopted relatives from the visible tree
# - auto-sizes boxes from text
# - auto-fits the canvas/window to the tree
# - supports pan, zoom, click-to-select, and screenshot save
# ============================================================


BG = (243, 234, 215)          # tan
PANEL_BG = (236, 224, 200)
GRID = (214, 201, 181)
TEXT = (32, 28, 23)
MUTED = (90, 80, 66)

ROOT_FILL = (223, 184, 84)
ROOT_BORDER = (120, 86, 20)

ANCESTOR_FILL = (170, 199, 235)
ANCESTOR_BORDER = (60, 95, 145)

SIDE_FILL = (196, 174, 222)
SIDE_BORDER = (105, 76, 140)

DESC_FILL = (190, 226, 186)
DESC_BORDER = (72, 120, 72)

SPOUSE_FILL = (238, 206, 178)
SPOUSE_BORDER = (150, 100, 58)

SELECT_FILL = (255, 245, 170)
SELECT_BORDER = (156, 126, 0)

LINK = (85, 72, 55)
LINK_SOFT = (140, 126, 107)

MIN_WIN_W = 1100
MIN_WIN_H = 780
PANEL_W = 320
MARGIN = 60

ROW_GAP = 92
SIBLING_GAP = 28
COLLATERAL_GAP = 40

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


@dataclass
class NodeLayout:
    pid: str
    x: float
    y: float
    w: int
    h: int
    relation: str


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
                    people.setdefault(current_pid, Person(pid=current_pid))
                elif tag == "FAM" and x:
                    current_fid = xref(x)
                    families.setdefault(current_fid, Family(fid=current_fid))
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
                if tag == "HUSB":
                    fam.husband = xref(value)
                elif tag == "WIFE":
                    fam.wife = xref(value)
                elif tag == "CHIL":
                    child = xref(value)
                    if child:
                        fam.children.append(child)

    return people, families


class TreeBuilder:
    def __init__(self, people: dict[str, Person], families: dict[str, Family]):
        self.people = people
        self.families = families

    def name_of(self, pid: str) -> str:
        return self.people.get(pid, Person(pid)).name

    def visible(self, pid: str, root: str) -> bool:
        if pid == root:
            return True
        p = self.people.get(pid)
        if not p:
            return False
        return not (p.adopted or p.adopted_in)

    def is_adopted_child_in_family(self, pid: str, fid: str) -> bool:
        p = self.people.get(pid)
        if not p:
            return True
        if p.adopted:
            return True
        return fid in p.adopted_in

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

    def build_visible_graph(self, root: str):
        root = root
        parents = sorted(self.parents_of(root, root=root), key=self.name_of)
        siblings = sorted(self.siblings_of(root, root=root), key=self.name_of)
        spouses = sorted(self.spouses_of(root, root=root), key=self.name_of)
        children = sorted(self.children_of(root, root=root), key=self.name_of)
        grandparents = sorted(self.grandparents_of(root, root=root), key=self.name_of)
        aunts_uncles = sorted(self.aunts_uncles_of(root, root=root), key=self.name_of)
        cousins = sorted(self.cousins_of(root, root=root), key=self.name_of)
        grandchildren = sorted(self.grandchildren_of(root, root=root), key=self.name_of)

        visible = {root}
        for group in [parents, siblings, spouses, children, grandparents, aunts_uncles, cousins, grandchildren]:
            visible.update(group)

        edges = set()
        marriage_edges = set()

        # biological parent-child edges only, excluding adopted children
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

        # marriage edges
        for pid in visible:
            for spouse in self.spouses_of(pid, root=root):
                if spouse in visible:
                    pair = tuple(sorted((pid, spouse)))
                    marriage_edges.add(pair)

        return {
            "root": root,
            "parents": parents,
            "siblings": siblings,
            "spouses": spouses,
            "children": children,
            "grandparents": grandparents,
            "aunts_uncles": aunts_uncles,
            "cousins": cousins,
            "grandchildren": grandchildren,
            "visible": visible,
            "edges": edges,
            "marriages": marriage_edges,
        }


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
        self.data = self.builder.build_visible_graph(root_pid)

        self.root_pid = root_pid
        self.selected_pid = root_pid

        self.font_name = pygame.font.SysFont("arial", NAME_FONT_SIZE, bold=True)
        self.font_date = pygame.font.SysFont("arial", DATE_FONT_SIZE, bold=True)
        self.font_ui = pygame.font.SysFont("arial", 18, bold=True)
        self.font_small = pygame.font.SysFont("arial", 14, bold=False)

        self.clock = pygame.time.Clock()
        self.dragging = False
        self.drag_start = (0, 0)
        self.offset = [0.0, 0.0]
        self.user_zoom = 1.0
        self.auto_zoom = 1.0

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
            self.node_colors[pid] = (self.fill_color(relation), self.border_color(relation))

        # row construction
        rows = {
            -3: self.data["grandparents"],
            -2: self.data["aunts_uncles"],
            -1: self.data["parents"],
             1: self.data["children"],
             2: self.data["grandchildren"],
        }

        # centered rows
        for level, nodes in rows.items():
            nodes = sorted(nodes, key=lambda pid: (self.person(pid).name.lower(), pid))
            if not nodes:
                continue

            y = level * ROW_GAP
            total_w = 0
            widths = []
            heights = []
            for pid in nodes:
                w, h = self.measure_box(pid)
                widths.append(w)
                heights.append(h)
                total_w += w
            total_w += COLLATERAL_GAP * max(0, len(nodes) - 1)

            x = -total_w / 2
            for pid, w, h in zip(nodes, widths, heights):
                self.node_layouts[pid] = NodeLayout(pid, x + w / 2, y, w, h, self.relation_type(pid))
                x += w + COLLATERAL_GAP

        # level 0 special layout: siblings left, root center, spouses right, cousins farther right
        y0 = 0
        root_layout = self.node_layouts[root]
        self.node_layouts[root] = NodeLayout(root, 0, y0, root_layout.w, root_layout.h, "root")

        # place siblings to the left
        left_cursor = -root_layout.w / 2 - SIBLING_GAP
        for pid in sorted(self.data["siblings"], key=lambda pid: (self.person(pid).name.lower(), pid), reverse=True):
            w, h = self.measure_box(pid)
            left_cursor -= w / 2
            self.node_layouts[pid] = NodeLayout(pid, left_cursor, y0, w, h, "side")
            left_cursor -= w / 2 + SIBLING_GAP

        # place spouses to the right
        right_cursor = root_layout.w / 2 + SIBLING_GAP
        for pid in sorted(self.data["spouses"], key=lambda pid: (self.person(pid).name.lower(), pid)):
            w, h = self.measure_box(pid)
            right_cursor += w / 2
            self.node_layouts[pid] = NodeLayout(pid, right_cursor, y0, w, h, "spouse")
            right_cursor += w / 2 + SIBLING_GAP

        # place cousins farther right of spouses
        if self.data["cousins"]:
            right_cursor += COLLATERAL_GAP
        for pid in sorted(self.data["cousins"], key=lambda pid: (self.person(pid).name.lower(), pid)):
            w, h = self.measure_box(pid)
            right_cursor += w / 2
            self.node_layouts[pid] = NodeLayout(pid, right_cursor, y0, w, h, "side")
            right_cursor += w / 2 + COLLATERAL_GAP

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
        pygame.display.set_caption(f"Ancestry Family Tree — {self.person(self.root_pid).name}")

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

    def draw_marriage(self, surface, a: NodeLayout, b: NodeLayout):
        ax, ay = self.world_to_screen(a.x, a.y)
        bx, by = self.world_to_screen(b.x, b.y)

        y = min(ay, by) - 10
        start = (ax + a.w / 2 * self.auto_zoom * self.user_zoom, ay + a.h / 2 * self.auto_zoom * self.user_zoom)
        end = (bx - b.w / 2 * self.auto_zoom * self.user_zoom, by + b.h / 2 * self.auto_zoom * self.user_zoom)

        pygame.draw.line(surface, LINK, (start[0], y), (end[0], y), 3)
        pygame.draw.circle(surface, LINK, (int((start[0] + end[0]) / 2), int(y)), 5)

    def draw_parent_child(self, surface, parent: NodeLayout, child: NodeLayout):
        px, py = self.world_to_screen(parent.x, parent.y)
        cx, cy = self.world_to_screen(child.x, child.y)

        zoom = self.auto_zoom * self.user_zoom
        start = (px, py + parent.h / 2 * zoom)
        end = (cx, cy - child.h / 2 * zoom)
        self.draw_elbow(surface, start, end, LINK, width=max(2, int(3 * zoom)))

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

        title = self.font_ui.render("ANCESTRY TREE", True, TEXT)
        surface.blit(title, (panel.left + 20, 22))

        sub = self.font_small.render(f"Root: {root.name}", True, MUTED)
        surface.blit(sub, (panel.left + 20, 54))

        sel_title = self.font_ui.render("Selected", True, TEXT)
        surface.blit(sel_title, (panel.left + 20, 96))

        lines = [
            f"Name: {sel.name}",
            f"Birth–Death: {sel.label_line()}",
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
            "Drag: pan",
            "Wheel: zoom",
            "R: refit",
            "S: save PNG",
            "Click a box: select",
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

        counts = [
            ("Ancestors", len(self.data["parents"]) + len(self.data["grandparents"])),
            ("Sides", len(self.data["siblings"]) + len(self.data["aunts_uncles"]) + len(self.data["cousins"])),
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
            pygame.draw.line(surface, (231, 219, 197), (x, 0), (x, self.viewport_h), 1)
        for y in range(0, self.viewport_h, 120):
            pygame.draw.line(surface, (231, 219, 197), (0, y), (left_w, y), 1)

    def render(self):
        self.draw_background(self.screen)

        # draw marriages first
        for a_id, b_id in sorted(self.data["marriages"]):
            if a_id in self.node_layouts and b_id in self.node_layouts:
                self.draw_marriage(self.screen, self.node_layouts[a_id], self.node_layouts[b_id])

        # draw parent-child links next
        for parent_id, child_id in sorted(self.data["edges"]):
            if parent_id in self.node_layouts and child_id in self.node_layouts:
                self.draw_parent_child(self.screen, self.node_layouts[parent_id], self.node_layouts[child_id])

        # draw boxes on top
        draw_order = []
        for level in (-3, -2, -1, 0, 1, 2):
            if level == 0:
                continue
        # explicit order: ancestors, sides, root, spouses, descendants
        ordered_ids = []
        ordered_ids.extend(sorted(self.data["grandparents"], key=lambda pid: (self.person(pid).name.lower(), pid)))
        ordered_ids.extend(sorted(self.data["aunts_uncles"], key=lambda pid: (self.person(pid).name.lower(), pid)))
        ordered_ids.extend(sorted(self.data["parents"], key=lambda pid: (self.person(pid).name.lower(), pid)))
        ordered_ids.extend(sorted(self.data["siblings"], key=lambda pid: (self.person(pid).name.lower(), pid)))
        ordered_ids.append(self.root_pid)
        ordered_ids.extend(sorted(self.data["spouses"], key=lambda pid: (self.person(pid).name.lower(), pid)))
        ordered_ids.extend(sorted(self.data["cousins"], key=lambda pid: (self.person(pid).name.lower(), pid)))
        ordered_ids.extend(sorted(self.data["children"], key=lambda pid: (self.person(pid).name.lower(), pid)))
        ordered_ids.extend(sorted(self.data["grandchildren"], key=lambda pid: (self.person(pid).name.lower(), pid)))

        seen = set()
        for pid in ordered_ids:
            if pid in seen or pid not in self.node_layouts:
                continue
            seen.add(pid)
            self.draw_box(self.screen, self.node_layouts[pid])

        self.draw_panel(self.screen)

        pygame.display.flip()

    def save_screenshot(self):
        path = os.path.join(os.path.dirname(__file__), "ancestry_tree_screenshot.png")
        pygame.image.save(self.screen, path)
        return path

    def select_at_point(self, pos):
        x, y = pos
        if x >= self.viewport_w - PANEL_W:
            return
        for pid, rect in self.rects.items():
            if rect.collidepoint(x, y):
                self.selected_pid = pid
                return

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.fit_tree(initial=False)
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
                        self.dragging = True
                        self.drag_start = event.pos
                        self.select_at_point(event.pos)
                    elif event.button == 4:
                        self.user_zoom = min(3.2, self.user_zoom * 1.08)
                    elif event.button == 5:
                        self.user_zoom = max(0.35, self.user_zoom / 1.08)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        dx = event.rel[0]
                        dy = event.rel[1]
                        zoom = self.auto_zoom * self.user_zoom
                        if zoom > 0:
                            self.offset[0] += dx / zoom
                            self.offset[1] += dy / zoom

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
