"""Keyword field definitions for LS-DYNA .k file field-level parsing.

Based on LS-DYNA Keyword User's Manual Volume I & II (R13).
Each keyword family has a list of (field_name, field_type) tuples.
"""

from __future__ import annotations

# --- NODE ---

NODE_FIELDS = [
    ("NID", int), ("X", float), ("Y", float), ("Z", float),
    ("TC", int), ("RC", int),
]

# --- ELEMENT ---

ELEMENT_SHELL_FIELDS = [
    ("EID", int), ("PID", int),
    ("N1", int), ("N2", int), ("N3", int), ("N4", int),
]

ELEMENT_SOLID_FIELDS = [
    ("EID", int), ("PID", int),
    ("N1", int), ("N2", int), ("N3", int), ("N4", int),
    ("N5", int), ("N6", int), ("N7", int), ("N8", int),
]

ELEMENT_BEAM_FIELDS = [
    ("EID", int), ("PID", int),
    ("N1", int), ("N2", int), ("N3", int), ("N4", int),
    ("RT1", float), ("RR1", float), ("RT2", float), ("RR2", float),
]

ELEMENT_TSHELL_FIELDS = [
    ("EID", int), ("PID", int),
    ("N1", int), ("N2", int), ("N3", int), ("N4", int),
    ("N5", int), ("N6", int), ("N7", int), ("N8", int),
]

# --- PART ---

PART_TITLE_FIELDS = [("HEADING", str)]

PART_DATA_FIELDS = [
    ("PID", int), ("SECID", int), ("MID", int),
    ("EOSID", int), ("HGID", int),
    ("GRAV", float), ("ADPOPT", int), ("TMID", int),
]

# --- SECTION ---

SECTION_SOLID_FIELDS = [
    ("SECID", int), ("ELFORM", int), ("AET", int),
]

SECTION_SHELL_FIELDS = [
    ("SECID", int), ("ELFORM", int), ("SHRF", float), ("NIP", int),
]

SECTION_BEAM_FIELDS = [
    ("SECID", int), ("ELFORM", int),
]

SECTION_TSHELL_FIELDS = [
    ("SECID", int), ("ELFORM", int), ("SHRF", float), ("NIP", int),
]

# --- MATERIAL ---

MAT_ELASTIC_FIELDS = [
    ("MID", int), ("RHO", float), ("E", float), ("PR", float),
    ("DA", float), ("DB", float),
]

MAT_RIGID_FIELDS = [
    ("MID", int), ("RHO", float), ("E", float), ("PR", float),
    ("N", int), ("COUPLE", int), ("M", int), ("TLOG", int),
]

MAT_PIECEWISE_LINEAR_PLASTICITY_FIELDS = [
    ("MID", int), ("RHO", float), ("E", float), ("PR", float),
    ("SIGY", float), ("ETAN", float), ("FAIL", float), ("TDEL", float),
]

MAT_PLASTIC_KINEMATIC_FIELDS = [
    ("MID", int), ("RHO", float), ("E", float), ("PR", float),
    ("SIGY", float), ("ETAN", float), ("BETA", float),
]

MAT_NULL_FIELDS = [
    ("MID", int), ("RHO", float), ("E", float), ("PR", float),
]

MAT_HIGH_EXPLOSIVE_BURN_FIELDS = [
    ("MID", int), ("RHO", float), ("D", float), ("PCJ", float),
    ("BETA", float), ("K", float), ("G", float), ("SIGY", float),
]

MAT_JOHNSON_COOK_FIELDS = [
    ("MID", int), ("RHO", float), ("G", float), ("E", float),
    ("PR", float), ("A", float), ("B", float), ("N", float),
]

MAT_VISCOELASTIC_FIELDS = [
    ("MID", int), ("RHO", float), ("G0", float), ("GI", float),
    ("BETA", float), ("PR", float),
]

# Generic MAT fallback (first 8 fields)
MAT_GENERIC_FIELDS = [
    ("MID", int), ("RHO", float), ("E", float), ("PR", float),
]

# --- EOS ---

EOS_GRUNEISEN_FIELDS = [
    ("EOSID", int), ("C", float), ("S1", float), ("S2", float),
    ("S3", float), ("GAMAO", float), ("A", float), ("E0", float),
]

EOS_LINEAR_POLYNOMIAL_FIELDS = [
    ("EOSID", int), ("C0", float), ("C1", float), ("C2", float),
    ("C3", float), ("C4", float), ("C5", float), ("C6", float),
]

EOS_IDEAL_GAS_FIELDS = [
    ("EOSID", int), ("GAMMA", float), ("E0", float),
]

# --- CONTROL ---

CONTROL_TERMINATION_FIELDS = [
    ("ENDTIM", float), ("ENDCYC", int), ("DTMIN", float),
    ("ENDENG", float), ("ENDMAS", float),
]

CONTROL_TIMESTEP_FIELDS = [
    ("DTINIT", float), ("TSSFAC", int), ("ISDO", int), ("TSLIMT", float),
    ("DT2MS", float), ("LCTM", int), ("ERODE", int), ("MS1ST", int),
]

CONTROL_HOURGLASS_FIELDS = [
    ("IHQ", int), ("QH", float),
]

CONTROL_CONTACT_FIELDS = [
    ("SLSFAC", float), ("RWPNAL", float), ("ISLCHK", int),
    ("SHLTHK", int), ("SNLOG", int), ("ISLDT", int),
    ("IRTH", int), ("IGAP", int), ("PENOPT", int),
]

CONTROL_ACCURACY_FIELDS = [
    ("OSU", int), ("INU", int), ("PIDs", int), ("IRATE", int),
]

CONTROL_ENERGY_FIELDS = [
    ("HGEN", int), ("RWEN", int), ("SLNTEN", int), ("RYLEN", int),
]

CONTROL_SHELL_FIELDS = [
    ("WRCOMP", int), ("ISTUPD", int), ("FAILURE", int),
    ("PSHELL", int), ("MITER", int), ("PROJ", int),
]

# --- DATABASE ---

DATABASE_BINARY_D3PLOT_FIELDS = [
    ("DT", float), ("LCDT", int), ("BEAM", int), ("NPLTC", int),
]

DATABASE_GLSTAT_FIELDS = [("DT", float)]
DATABASE_MATSUM_FIELDS = [("DT", float)]
DATABASE_SLEOUT_FIELDS = [("DT", float)]
DATABASE_ELOUT_FIELDS = [("DT", float)]
DATABASE_RCFORC_FIELDS = [("DT", float)]
DATABASE_ABSTAT_FIELDS = [("DT", float)]
DATABASE_JNTFORC_FIELDS = [("DT", float)]

# --- SET ---

SET_NODE_LIST_HEADER = [("SID", int)]
SET_NODE_LIST_DATA = [("NID", int)]

SET_NODE_LIST_TITLE = [("SID", int), ("TITLE", str)]

SET_SEGMENT_HEADER = [("SID", int)]
SET_SEGMENT_DATA = [
    ("N1", int), ("N2", int), ("N3", int), ("N4", int), ("EL", int),
]

SET_PART_LIST_HEADER = [("SID", int)]
SET_PART_LIST_DATA = [("PID", int)]

SET_SHELL_LIST_HEADER = [("SID", int)]
SET_SHELL_LIST_DATA = [("EID", int)]

SET_SOLID_LIST_HEADER = [("SID", int)]
SET_SOLID_LIST_DATA = [("EID", int)]

# --- CONTACT ---

CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_FIELDS = [
    ("SSID", int), ("MSID", int), ("SSTYP", int), ("MSTYP", int),
    ("SBOXID", int), ("MBOXID", int), ("SPR", int), ("MPR", int),
]

CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_OPT = [
    ("FS", float), ("FD", float), ("DC", float), ("VC", float),
    ("VDC", float), ("PENCHK", int), ("BT", float), ("DT", float),
    ("SFS", float), ("SFM", float), ("SST", float), ("MST", float),
    ("SFST", float), ("SFMT", float),
]

CONTACT_AUTOMATIC_SINGLE_SURFACE_FIELDS = [
    ("SSID", int), ("MSID", int), ("SSTYP", int), ("MSTYP", int),
    ("SBOXID", int), ("MBOXID", int), ("SPR", int), ("MPR", int),
]

CONTACT_TIED_SURFACE_TO_SURFACE_FIELDS = [
    ("SSID", int), ("MSID", int), ("SSTYP", int), ("MSTYP", int),
    ("SBOXID", int), ("MBOXID", int), ("SPR", int), ("MPR", int),
]

CONTACT_NODES_TO_SURFACE_FIELDS = [
    ("SSID", int), ("MSID", int), ("SSTYP", int), ("MSTYP", int),
]

# --- BOUNDARY ---

BOUNDARY_SPC_SET_FIELDS = [
    ("NSID", int), ("CID", int),
    ("DOFX", int), ("DOFY", int), ("DOFZ", int),
    ("DOFRX", int), ("DOFRY", int), ("DOFRZ", int),
]

BOUNDARY_SPC_FIELDS = [
    ("NODEID", int), ("CID", int),
    ("DOFX", int), ("DOFY", int), ("DOFZ", int),
    ("DOFRX", int), ("DOFRY", int), ("DOFRZ", int),
]

BOUNDARY_PRESCRIBED_MOTION_SET_FIELDS = [
    ("NSID", int), ("DOF", int), ("VAD", int),
    ("LCID", int), ("SF", float), ("VID", int),
    ("DEATH", float), ("BIRTH", float),
]

BOUNDARY_PRESCRIBED_MOTION_NODE_FIELDS = [
    ("NID", int), ("DOF", int), ("VAD", int),
    ("LCID", int), ("SF", float), ("VID", int),
    ("DEATH", float), ("BIRTH", float),
]

# --- LOAD ---

LOAD_NODE_FIELDS = [
    ("NID", int), ("DOF", int), ("LCID", int), ("SF", float),
    ("CID", int), ("M1", float), ("M2", float), ("M3", float),
]

LOAD_SEGMENT_FIELDS = [
    ("LCID", int), ("SF", float),
]

LOAD_SHELL_FIELDS = [
    ("LCID", int), ("SF", float),
]

LOAD_BODY_FIELDS = [
    ("LCID", int), ("SF", float),
]

LOAD_PRESCRIBED_MOTION_SET_FIELDS = [
    ("NSID", int), ("DOF", int), ("VAD", int),
    ("LCID", int), ("SF", float), ("VID", int),
    ("DEATH", float), ("BIRTH", float),
]

LOAD_RIGID_BODY_FIELDS = [
    ("PID", int), ("DOF", int), ("LCID", int), ("SF", float),
    ("CID", int),
]

# --- DEFINE ---

DEFINE_CURVE_HEADER = [
    ("LCID", int), ("SIDR", int), ("SFA", float), ("SFO", float),
    ("OFFA", float), ("OFFO", float), ("DTIME", float),
]

DEFINE_CURVE_POINT = [("A", float), ("O", float)]

DEFINE_COORDINATE_NODES_FIELDS = [
    ("CID", int), ("N1", int), ("N2", int), ("N3", int),
]

DEFINE_COORDINATE_VECTOR_FIELDS = [
    ("CID", int), ("XT", float), ("YT", float), ("ZT", float),
    ("XL", float), ("YL", float), ("ZL", float),
]

DEFINE_TRANSFORMATION_FIELDS = [
    ("ITRAN", int), ("NSET", int), ("IDIR", int),
    ("FX", float), ("FY", float), ("FZ", float),
]

# --- INITIAL ---

INITIAL_VELOCITY_GENERATION_FIELDS = [
    ("SETID", int), ("STYP", int), ("VNX", float), ("VNY", float),
    ("VNZ", float), ("IRID", int), ("OMEGA", float),
]

INITIAL_VELOCITY_NODE_FIELDS = [
    ("NID", int), ("VX", float), ("VY", float), ("VZ", float),
    ("VRX", float), ("VRY", float), ("VRZ", float),
]

# --- CONSTRAINED ---

CONSTRAINED_EXTRA_NODES_NODE_FIELDS = [
    ("NID", int), ("PID", int),
]

CONSTRAINED_NODAL_RIGID_BODY_FIELDS = [
    ("NSID", int), ("PID", int),
]

CONSTRAINED_SPOTWELD_FIELDS = [
    ("NID1", int), ("NID2", int), ("D", float), ("SN", float),
    ("SS", float), ("ATEN", float),
]

# --- RIGIDWALL ---

RIGIDWALL_PLANAR_FIELDS = [
    ("RWID", int), ("NID1", int), ("NID2", int), ("NID3", int),
    ("DGTOL", float), ("DLOAD", float),
]

# --- HOURGLASS ---

HOURGLASS_FIELDS = [
    ("HGID", int), ("IHQ", int), ("QM", float),
]

# --- KEYWORD FIELDS MAP ---

KEYWORD_FIELDS_MAP: dict[str, list[tuple[str, type]]] = {
    # Node
    "NODE": NODE_FIELDS,
    # Element
    "ELEMENT_SHELL": ELEMENT_SHELL_FIELDS,
    "ELEMENT_SOLID": ELEMENT_SOLID_FIELDS,
    "ELEMENT_BEAM": ELEMENT_BEAM_FIELDS,
    "ELEMENT_TSHELL": ELEMENT_TSHELL_FIELDS,
    # Part
    "PART_TITLE": PART_TITLE_FIELDS,
    "PART_DATA": PART_DATA_FIELDS,
    # Section
    "SECTION_SOLID": SECTION_SOLID_FIELDS,
    "SECTION_SHELL": SECTION_SHELL_FIELDS,
    "SECTION_BEAM": SECTION_BEAM_FIELDS,
    "SECTION_TSHELL": SECTION_TSHELL_FIELDS,
    # Material
    "MAT_ELASTIC": MAT_ELASTIC_FIELDS,
    "MAT_RIGID": MAT_RIGID_FIELDS,
    "MAT_PIECEWISE_LINEAR_PLASTICITY": MAT_PIECEWISE_LINEAR_PLASTICITY_FIELDS,
    "MAT_PLASTIC_KINEMATIC": MAT_PLASTIC_KINEMATIC_FIELDS,
    "MAT_NULL": MAT_NULL_FIELDS,
    "MAT_HIGH_EXPLOSIVE_BURN": MAT_HIGH_EXPLOSIVE_BURN_FIELDS,
    "MAT_JOHNSON_COOK": MAT_JOHNSON_COOK_FIELDS,
    "MAT_VISCOELASTIC": MAT_VISCOELASTIC_FIELDS,
    # Control
    "CONTROL_TERMINATION": CONTROL_TERMINATION_FIELDS,
    "CONTROL_TIMESTEP": CONTROL_TIMESTEP_FIELDS,
    "CONTROL_HOURGLASS": CONTROL_HOURGLASS_FIELDS,
    "CONTROL_CONTACT": CONTROL_CONTACT_FIELDS,
    "CONTROL_ACCURACY": CONTROL_ACCURACY_FIELDS,
    "CONTROL_ENERGY": CONTROL_ENERGY_FIELDS,
    "CONTROL_SHELL": CONTROL_SHELL_FIELDS,
    # Database
    "DATABASE_BINARY_D3PLOT": DATABASE_BINARY_D3PLOT_FIELDS,
    "DATABASE_GLSTAT": DATABASE_GLSTAT_FIELDS,
    "DATABASE_MATSUM": DATABASE_MATSUM_FIELDS,
    "DATABASE_SLEOUT": DATABASE_SLEOUT_FIELDS,
    "DATABASE_ELOUT": DATABASE_ELOUT_FIELDS,
    "DATABASE_RCFORC": DATABASE_RCFORC_FIELDS,
    "DATABASE_ABSTAT": DATABASE_ABSTAT_FIELDS,
    "DATABASE_JNTFORC": DATABASE_JNTFORC_FIELDS,
    # Set
    "SET_NODE_LIST": SET_NODE_LIST_HEADER,
    "SET_SEGMENT": SET_SEGMENT_HEADER,
    "SET_PART_LIST": SET_PART_LIST_HEADER,
    "SET_SHELL_LIST": SET_SHELL_LIST_HEADER,
    "SET_SOLID_LIST": SET_SOLID_LIST_HEADER,
    # Contact
    "CONTACT_AUTOMATIC_SURFACE_TO_SURFACE": CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_FIELDS,
    "CONTACT_AUTOMATIC_SINGLE_SURFACE": CONTACT_AUTOMATIC_SINGLE_SURFACE_FIELDS,
    "CONTACT_TIED_SURFACE_TO_SURFACE": CONTACT_TIED_SURFACE_TO_SURFACE_FIELDS,
    "CONTACT_NODES_TO_SURFACE": CONTACT_NODES_TO_SURFACE_FIELDS,
    # Boundary
    "BOUNDARY_SPC_SET": BOUNDARY_SPC_SET_FIELDS,
    "BOUNDARY_SPC": BOUNDARY_SPC_FIELDS,
    "BOUNDARY_PRESCRIBED_MOTION_SET": BOUNDARY_PRESCRIBED_MOTION_SET_FIELDS,
    "BOUNDARY_PRESCRIBED_MOTION_NODE": BOUNDARY_PRESCRIBED_MOTION_NODE_FIELDS,
    # Load
    "LOAD_NODE": LOAD_NODE_FIELDS,
    "LOAD_SEGMENT": LOAD_SEGMENT_FIELDS,
    "LOAD_SHELL": LOAD_SHELL_FIELDS,
    "LOAD_BODY": LOAD_BODY_FIELDS,
    "LOAD_PRESCRIBED_MOTION_SET": LOAD_PRESCRIBED_MOTION_SET_FIELDS,
    "LOAD_RIGID_BODY": LOAD_RIGID_BODY_FIELDS,
    # Define
    "DEFINE_CURVE": DEFINE_CURVE_HEADER,
    "DEFINE_COORDINATE_NODES": DEFINE_COORDINATE_NODES_FIELDS,
    "DEFINE_COORDINATE_VECTOR": DEFINE_COORDINATE_VECTOR_FIELDS,
    "DEFINE_TRANSFORMATION": DEFINE_TRANSFORMATION_FIELDS,
    # Initial
    "INITIAL_VELOCITY_GENERATION": INITIAL_VELOCITY_GENERATION_FIELDS,
    "INITIAL_VELOCITY_NODE": INITIAL_VELOCITY_NODE_FIELDS,
    # Constrained
    "CONSTRAINED_EXTRA_NODES_NODE": CONSTRAINED_EXTRA_NODES_NODE_FIELDS,
    "CONSTRAINED_NODAL_RIGID_BODY": CONSTRAINED_NODAL_RIGID_BODY_FIELDS,
    "CONSTRAINED_SPOTWELD": CONSTRAINED_SPOTWELD_FIELDS,
    # Rigidwall
    "RIGIDWALL_PLANAR": RIGIDWALL_PLANAR_FIELDS,
    # Hourglass
    "HOURGLASS": HOURGLASS_FIELDS,
}


def get_fields_for_keyword(keyword_name: str) -> list[tuple[str, type]] | None:
    """Get field definitions for a keyword name."""
    return KEYWORD_FIELDS_MAP.get(keyword_name)


def parse_fields(keyword_name: str, data_line: str) -> dict:
    """Parse a single data line into a dict of field values."""
    from program.tools.k_parser import _parse_data_line
    fields = KEYWORD_FIELDS_MAP.get(keyword_name)
    if not fields:
        return {}
    values = _parse_data_line(data_line)
    result = {}
    for i, (fname, ftype) in enumerate(fields):
        if i < len(values):
            try:
                result[fname] = ftype(values[i])
            except (ValueError, TypeError):
                result[fname] = None
    return result
