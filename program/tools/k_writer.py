"""Generate LS-DYNA .k keyword files from structured data.

Based on LS-DYNA Keyword User's Manual Volume I (R13).
Supports standard format output (8 fields × 10 chars per line).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# --- Data classes ---


@dataclass
class Material:
    mid: int
    rho: float
    e: float
    pr: float
    mat_type: str = "ELASTIC"


@dataclass
class Section:
    secid: int
    sec_type: str = "SOLID"  # SOLID, SHELL, BEAM
    elform: int = 1
    shrf: float = 0.0  # shear factor (shell only)
    nip: int = 0  # integration points (shell only)


@dataclass
class Part:
    pid: int
    secid: int
    mid: int
    title: str = "Part"
    eosid: int = 0
    hgid: int = 0


@dataclass
class Node:
    nid: int
    x: float
    y: float
    z: float
    tc: int = 0  # translational constraint
    rc: int = 0  # rotational constraint


@dataclass
class SolidElement:
    eid: int
    pid: int
    nodes: list[int]


@dataclass
class ShellElement:
    eid: int
    pid: int
    nodes: list[int]  # 4 node IDs (n1, n2, n3, n4)


@dataclass
class BeamElement:
    eid: int
    pid: int
    nodes: list[int]  # 2 node IDs (n1, n2), optionally n3, n4


@dataclass
class BoundaryCondition:
    """SPC boundary condition set."""
    nsid: int  # node set ID
    dofx: int = 0
    dofy: int = 0
    dofz: int = 0
    dofrx: int = 0
    dofry: int = 0
    dofrz: int = 0


@dataclass
class LoadSegment:
    """Distributed pressure load on segment set."""
    lcid: int  # load curve ID
    sid: int  # segment set ID
    pressure: float = 0.0


@dataclass
class ContactAutomatic:
    """Automatic surface-to-surface contact."""
    ssid: int  # slave segment set ID
    msid: int  # master segment set ID
    sstyp: int = 0  # slave type
    mstyp: int = 0  # master type
    fs: float = 0.0  # static friction
    fd: float = 0.0  # dynamic friction
    contact_type: str = "AUTOMATIC_SURFACE_TO_SURFACE"


@dataclass
class DefineCurve:
    """Load curve definition."""
    lcid: int  # load curve ID
    sfa: float = 1.0  # scale factor for abscissa
    sfo: float = 1.0  # scale factor for ordinate
    points: list[tuple[float, float]] = field(default_factory=list)  # (A, O) pairs


@dataclass
class SetNodeList:
    """Node set definition."""
    sid: int  # set ID
    nodes: list[int] = field(default_factory=list)


@dataclass
class SetSegment:
    """Segment set definition."""
    sid: int  # set ID
    segments: list[list[int]] = field(default_factory=list)  # [[N1,N2,N3,N4,PID], ...]


@dataclass
class SetPartList:
    """Part set definition."""
    sid: int  # set ID
    parts: list[int] = field(default_factory=list)


@dataclass
class KModel:
    title: str = "Generated Model"
    materials: list[Material] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    parts: list[Part] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    solid_elements: list[SolidElement] = field(default_factory=list)
    shell_elements: list[ShellElement] = field(default_factory=list)
    beam_elements: list[BeamElement] = field(default_factory=list)
    boundaries: list[BoundaryCondition] = field(default_factory=list)
    loads: list[LoadSegment] = field(default_factory=list)
    contacts: list[ContactAutomatic] = field(default_factory=list)
    curves: list[DefineCurve] = field(default_factory=list)
    set_node_lists: list[SetNodeList] = field(default_factory=list)
    set_segments: list[SetSegment] = field(default_factory=list)
    set_part_lists: list[SetPartList] = field(default_factory=list)
    termination_time: float = 0.001
    d3plot_dt: float = 0.0001

    @property
    def elements(self) -> list[SolidElement]:
        """Backward compatibility: return solid elements."""
        return self.solid_elements


# --- Generators ---


def _gen_control(model: KModel) -> list[str]:
    lines = []
    lines.append("*CONTROL_TERMINATION")
    lines.append("$    ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS")
    lines.append(f" {model.termination_time:10.4f}         0 0.000E+00 0.000E+00 0.000E+00")
    return lines


def _gen_database(model: KModel) -> list[str]:
    lines = []
    lines.append("*DATABASE_BINARY_D3PLOT")
    lines.append("$      DT    LCDT      BEAM     NPLTC")
    lines.append(f" {model.d3plot_dt:10.6f}       0         0         0")
    return lines


def _gen_materials(model: KModel) -> list[str]:
    lines = []
    for mat in model.materials:
        lines.append(f"*MAT_{mat.mat_type.upper()}")
        lines.append("$    MID        RHO         E        PR      DA      DB")
        lines.append(f" {mat.mid:8d} {mat.rho:10.3E} {mat.e:10.3E} {mat.pr:10.3f}")
    return lines


def _gen_sections(model: KModel) -> list[str]:
    lines = []
    for sec in model.sections:
        if sec.sec_type.upper() == "SHELL":
            lines.append("*SECTION_SHELL")
            lines.append("$    SECID    ELFORM      SHRF       NIP")
            lines.append(
                f" {sec.secid:8d} {sec.elform:8d} {sec.shrf:10.4f} {sec.nip:8d}"
            )
        elif sec.sec_type.upper() == "BEAM":
            lines.append("*SECTION_BEAM")
            lines.append("$    SECID    ELFORM")
            lines.append(f" {sec.secid:8d} {sec.elform:8d}")
        else:
            lines.append("*SECTION_SOLID")
            lines.append("$    SECID    ELFORM       AET")
            lines.append(f" {sec.secid:8d} {sec.elform:8d}")
    return lines


def _gen_parts(model: KModel) -> list[str]:
    lines = []
    for part in model.parts:
        lines.append("*PART")
        lines.append(part.title)
        lines.append("$    PID     SECID       MID     EOSID      HGID")
        lines.append(
            f" {part.pid:8d} {part.secid:8d} {part.mid:8d} {part.eosid:8d} {part.hgid:8d}"
        )
    return lines


def _gen_nodes(model: KModel) -> list[str]:
    if not model.nodes:
        return []
    lines = ["*NODE"]
    lines.append("$   NODE               X               Y               Z      TC      RC")
    for n in model.nodes:
        if n.tc or n.rc:
            lines.append(
                f" {n.nid:8d} {n.x:15.7f} {n.y:15.7f} {n.z:15.7f} {n.tc:8d} {n.rc:8d}"
            )
        else:
            lines.append(f" {n.nid:8d} {n.x:15.7f} {n.y:15.7f} {n.z:15.7f}")
    return lines


def _gen_elements(model: KModel) -> list[str]:
    lines = []

    # Solid elements
    if model.solid_elements:
        lines.append("*ELEMENT_SOLID")
        lines.append(
            "$   EID     PID      N1      N2      N3      N4      N5      N6      N7      N8"
        )
        for e in model.solid_elements:
            nodes_str = "".join(f"{n:8d}" for n in e.nodes)
            lines.append(f" {e.eid:8d} {e.pid:8d}{nodes_str}")

    # Shell elements
    if model.shell_elements:
        lines.append("*ELEMENT_SHELL")
        lines.append("$   EID     PID      N1      N2      N3      N4")
        for e in model.shell_elements:
            nodes_str = "".join(f"{n:8d}" for n in e.nodes[:4])
            lines.append(f" {e.eid:8d} {e.pid:8d}{nodes_str}")

    # Beam elements
    if model.beam_elements:
        lines.append("*ELEMENT_BEAM")
        lines.append("$   EID     PID      N1      N2      N3      N4")
        for e in model.beam_elements:
            nids = e.nodes[:4] if len(e.nodes) >= 2 else e.nodes + [0] * (4 - len(e.nodes))
            nodes_str = "".join(f"{n:8d}" for n in nids)
            lines.append(f" {e.eid:8d} {e.pid:8d}{nodes_str}")

    return lines


def _gen_boundaries(model: KModel) -> list[str]:
    if not model.boundaries:
        return []
    lines = ["*BOUNDARY_SPC_SET"]
    lines.append("$    NSID       CID      DOFX      DOFY      DOFZ     DOFRX     DOFRY     DOFRZ")
    for bc in model.boundaries:
        lines.append(
            f" {bc.nsid:8d}         0 {bc.dofx:8d} {bc.dofy:8d} {bc.dofz:8d} {bc.dofrx:8d} {bc.dofry:8d} {bc.dofrz:8d}"
        )
    return lines


def _gen_loads(model: KModel) -> list[str]:
    if not model.loads:
        return []
    lines = ["*LOAD_SEGMENT"]
    lines.append("$     LCID       SID    PRESSURE")
    for load in model.loads:
        lines.append(
            f" {load.lcid:8d} {load.sid:8d} {load.pressure:10.4f}"
        )
    return lines


def _gen_contacts(model: KModel) -> list[str]:
    if not model.contacts:
        return []
    lines = ["*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE"]
    lines.append("$    SSID      MSID     SSTYP     MSTYP        FS        FD")
    for c in model.contacts:
        lines.append(
            f" {c.ssid:8d} {c.msid:8d} {c.sstyp:8d} {c.mstyp:8d} {c.fs:10.4f} {c.fd:10.4f}"
        )
    return lines


def _gen_curves(model: KModel) -> list[str]:
    if not model.curves:
        return []
    lines = []
    for curve in model.curves:
        lines.append("*DEFINE_CURVE")
        lines.append("$     LCID       SIDR       SFA       SFO      OFFA      OFFO")
        lines.append(
            f" {curve.lcid:8d}         0 {curve.sfa:10.4f} {curve.sfo:10.4f}       0.0       0.0"
        )
        for a, o in curve.points:
            lines.append(f" {a:20.6f} {o:20.6f}")
    return lines


def _gen_sets(model: KModel) -> list[str]:
    lines = []

    # Part sets
    for ps in model.set_part_lists:
        lines.append("*SET_PART_LIST")
        lines.append("$     SID")
        lines.append(f" {ps.sid:8d}")
        if ps.parts:
            parts_str = "".join(f"{p:8d}" for p in ps.parts)
            lines.append(parts_str)

    # Node sets
    for ns in model.set_node_lists:
        lines.append("*SET_NODE_LIST")
        lines.append("$     SID")
        lines.append(f" {ns.sid:8d}")
        if ns.nodes:
            nodes_str = "".join(f"{n:8d}" for n in ns.nodes)
            lines.append(nodes_str)

    # Segment sets
    for ss in model.set_segments:
        lines.append("*SET_SEGMENT")
        lines.append("$     SID")
        lines.append(f" {ss.sid:8d}")
        for seg in ss.segments:
            seg_str = "".join(f"{n:8d}" for n in seg)
            lines.append(seg_str)

    return lines


# --- Main API ---


def write_k_file(model: KModel, filepath: str | Path) -> str:
    """Write a KModel to a .k file. Returns the generated content string."""
    content = generate_k_content(model)
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    logger.info(f"Wrote K file: {path}")
    return content


def generate_k_content(model: KModel) -> str:
    """Generate .k file content string from a KModel.

    Output order follows LS-DYNA convention:
    *KEYWORD → *TITLE → CONTROL → DATABASE → MAT → SECTION → PART
    → SET → BOUNDARY → LOAD → CONTACT → NODE → ELEMENT → *END
    """
    blocks: list[list[str]] = []

    blocks.append(["*KEYWORD"])

    # Title
    blocks.append(["*TITLE", model.title])

    # Control & database
    blocks.append(_gen_control(model))
    blocks.append(_gen_database(model))

    # Materials
    if model.materials:
        blocks.append(_gen_materials(model))

    # Sections
    if model.sections:
        blocks.append(_gen_sections(model))

    # Parts
    if model.parts:
        blocks.append(_gen_parts(model))

    # Sets
    set_lines = _gen_sets(model)
    if set_lines:
        blocks.append(set_lines)

    # Boundary conditions
    bc_lines = _gen_boundaries(model)
    if bc_lines:
        blocks.append(bc_lines)

    # Loads
    load_lines = _gen_loads(model)
    if load_lines:
        blocks.append(load_lines)

    # Curves
    curve_lines = _gen_curves(model)
    if curve_lines:
        blocks.append(curve_lines)

    # Contacts
    contact_lines = _gen_contacts(model)
    if contact_lines:
        blocks.append(contact_lines)

    # Nodes
    node_lines = _gen_nodes(model)
    if node_lines:
        blocks.append(node_lines)

    # Elements
    elem_lines = _gen_elements(model)
    if elem_lines:
        blocks.append(elem_lines)

    blocks.append(["*END"])

    all_lines: list[str] = []
    for block in blocks:
        all_lines.extend(block)

    return "\n".join(all_lines) + "\n"
