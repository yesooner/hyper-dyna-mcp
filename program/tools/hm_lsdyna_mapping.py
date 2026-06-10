"""Verified LS-DYNA keyword mappings for HyperMesh Tcl.

The generated templates under templates/keyword are broad but not always valid
for HyperMesh 2021. This module records mappings that were verified against the
local LS-DYNA profile loaded from templates/feoutput/ls-dyna971/dyna.key.
"""

from __future__ import annotations

from dataclasses import dataclass
from string import Formatter
from typing import Any


@dataclass(frozen=True)
class HmKeywordMapping:
    keyword: str
    entity_type: str
    cardimage: str | None
    id_param: str | None
    name_template: str
    fields: dict[str, str]
    optional_fields: dict[str, str] | None = None
    unsupported_fields: tuple[str, ...] = ()

    @property
    def placeholders(self) -> list[str]:
        names = {
            *self.name_params,
            *self.fields.keys(),
            *(self.optional_fields or {}).keys(),
            *self.unsupported_fields,
        }
        if self.id_param:
            names.add(self.id_param)
        return sorted(names)

    @property
    def name_params(self) -> tuple[str, ...]:
        fields = []
        for _, field_name, _, _ in Formatter().parse(self.name_template):
            if field_name:
                fields.append(field_name)
        return tuple(fields)


VERIFIED_MAPPINGS: dict[str, HmKeywordMapping] = {
    # LS-DYNA *MAT_ELASTIC is MATL1 in the HyperMesh LS-DYNA profile.
    # Verified in HyperMesh 2021:
    #   cardimage=MATL1
    #   *setvalue mats id=<id> Rho=<rho> E=<e> Nu=<pr>
    "MAT_ELASTIC": HmKeywordMapping(
        keyword="MAT_ELASTIC",
        entity_type="mats",
        cardimage="MATL1",
        id_param="MID",
        name_template="MAT_ELASTIC_{MID}",
        fields={
            "RHO": "Rho",
            "E": "E",
            "PR": "Nu",
        },
        unsupported_fields=("DA", "DB"),
    ),
    # Verified in HyperMesh 2021:
    #   cardimage=SectSld creates an LS-DYNA solid section property.
    # ELFORM/AET are not exposed through the simple dataname syntax tested so
    # far, so they are intentionally ignored until a real field mapping is found.
    "SECTION_SOLID": HmKeywordMapping(
        keyword="SECTION_SOLID",
        entity_type="props",
        cardimage="SectSld",
        id_param="SECID",
        name_template="SECTION_SOLID_{SECID}",
        fields={},
        unsupported_fields=("ELFORM", "AET"),
    ),
    # LS-DYNA *PART is represented by a HyperMesh component collector. It has
    # no independent card image in this profile; the important solver chain is
    # component.propertyid -> property and component.materialid -> material.
    "PART": HmKeywordMapping(
        keyword="PART",
        entity_type="comps",
        cardimage=None,
        id_param="PID",
        name_template="{HEADING}",
        fields={
            "SECID": "propertyid",
            "MID": "materialid",
        },
        unsupported_fields=("EOSID", "HGID", "GRAV", "ADPOPT", "TMID"),
    ),
    # LS-DYNA control cards are HyperMesh cards with profile-specific internal
    # datanames. Verified in HyperMesh 2021 against the ls-dyna971 template.
    "CONTROL_TERMINATION": HmKeywordMapping(
        keyword="CONTROL_TERMINATION",
        entity_type="cards",
        cardimage="Termin",
        id_param=None,
        name_template="CONTROL_TERMINATION",
        fields={
            "ENDTIM": "LSD_ENDTIM",
            "ENDCYC": "LSD_ENDCYCLE",
            "DTMIN": "LSD_TSMIN",
            "ENDENG": "LSD_TERMRAT",
            "ENDMAS": "LSD_PERMASS",
        },
        optional_fields={
            "NOSOL": "LSD_NOSOL",
        },
    ),
    "DATABASE_BINARY_D3PLOT": HmKeywordMapping(
        keyword="DATABASE_BINARY_D3PLOT",
        entity_type="cards",
        cardimage="DBplot",
        id_param=None,
        name_template="DATABASE_BINARY_D3PLOT",
        fields={
            "DT": "LSD_DT",
            "LCDT": "LSD_LCID",
            "BEAM": "LSD_NOBEAM",
            "NPLTC": "LSD_NPLTC",
            "PSETID": "LSD_PSID",
        },
        optional_fields={
            "IOOPT": "LSD_IOOPT",
        },
    ),

    # --- Verified from dyna971_R93.key *cardmenuitem + *menufield ---

    "CONTROL_TIMESTEP": HmKeywordMapping(
        keyword="CONTROL_TIMESTEP",
        entity_type="cards",
        cardimage="TimeStep",
        id_param=None,
        name_template="CONTROL_TIMESTEP",
        fields={
            "DTINIT": "LSD_DT2OLD",
            "TSSFAC": "LSD_TSSFAC",
            "DT2MS": "LSD_DT2MS",
        },
        optional_fields={
            "ISDO": "LSD_ISDO",
            "TSLIMT": "LSD_TSLIMIT",
            "LCTM": "LSD_LCID",
            "ERODE": "LSD_DTMIN",
            "MS1ST": "LSD_MASSSCL",
        },
    ),

    "CONTROL_ENERGY": HmKeywordMapping(
        keyword="CONTROL_ENERGY",
        entity_type="cards",
        cardimage="OutEner",
        id_param=None,
        name_template="CONTROL_ENERGY",
        fields={
            "HGEN": "LSD_IEHGC",
            "RWEN": "LSD_NRWO",
            "SLNTEN": "LSD_SLENGR",
            "RYLEN": "LSD_RAYDAMP",
        },
    ),

    "CONTROL_HOURGLASS": HmKeywordMapping(
        keyword="CONTROL_HOURGLASS",
        entity_type="cards",
        cardimage="HourGlass",
        id_param=None,
        name_template="CONTROL_HOURGLASS",
        fields={
            "IHQ": "LSD_IHQ",
            "QM": "LSD_QM",
        },
    ),

    "CONTROL_CONTACT": HmKeywordMapping(
        keyword="CONTROL_CONTACT",
        entity_type="cards",
        cardimage="Contact",
        id_param=None,
        name_template="CONTROL_CONTACT",
        fields={
            "SLSFAC": "LSD_SLSFAC",
            "RWPNAL": "LSD_RWPNAL",
            "ISLCHK": "LSD_ISLCHK",
            "SHLTHK": "LSD_SHLTHK",
            "PENOPT": "LSD_PENOPT",
            "THKOPT": "LSD_THKOPT",
            "ORIEN": "LSD_ORIEN",
        },
        optional_fields={
            "IGAP": "LSD_IGAP",
            "IGNORE": "LSD_IGNORE",
        },
    ),

    "DATABASE_EXTENT_BINARY": HmKeywordMapping(
        keyword="DATABASE_EXTENT_BINARY",
        entity_type="cards",
        cardimage="XtntBIN",
        id_param=None,
        name_template="DATABASE_EXTENT_BINARY",
        fields={
            "NEIPH": "LSD_NEIPH",
            "NEIPS": "LSD_NEIPS",
            "MAXINT": "LSD_MAXINT",
            "STRFLG": "LSD_STRFLG",
            "SIGFLG": "LSD_SIGFLG",
            "EPSFLG": "LSD_EPSFLG",
            "RLTFLG": "LSD_RLTFLG",
            "ENGFLG": "LSD_ENGFLG",
        },
        optional_fields={
            "CMPFLG": "LSD_CMPFLG",
            "IEVERP": "LSD_IEVERP",
            "BEAMIP": "LSD_BEAMIP",
        },
    ),

    # --- Materials (from *assigndictionarytogroup) ---

    "MAT_RIGID": HmKeywordMapping(
        keyword="MAT_RIGID",
        entity_type="mats",
        cardimage="MATL20",
        id_param="MID",
        name_template="MAT_RIGID_{MID}",
        fields={
            "RHO": "Rho",
            "E": "E",
            "PR": "Nu",
        },
    ),

    "MAT_PIECEWISE_LINEAR_PLASTICITY": HmKeywordMapping(
        keyword="MAT_PIECEWISE_LINEAR_PLASTICITY",
        entity_type="mats",
        cardimage="MATL24",
        id_param="MID",
        name_template="MAT_PLASTIC_KINEMATIC_{MID}",
        fields={
            "RHO": "Rho",
            "E": "E",
            "PR": "Nu",
            "SIGY": "Yield",
            "ETAN": "Etan",
        },
        optional_fields={
            "FAIL": "Fail",
            "C": "Cowper",
            "P": "Symonds",
        },
    ),

    "MAT_NULL": HmKeywordMapping(
        keyword="MAT_NULL",
        entity_type="mats",
        cardimage="MATL9",
        id_param="MID",
        name_template="MAT_NULL_{MID}",
        fields={
            "RHO": "Rho",
        },
        optional_fields={
            "E": "E",
            "PR": "Nu",
        },
    ),

    # --- Sections (from *assigndictionarytogroup) ---

    "SECTION_SHELL": HmKeywordMapping(
        keyword="SECTION_SHELL",
        entity_type="props",
        cardimage="SectShll",
        id_param="SECID",
        name_template="SECTION_SHELL_{SECID}",
        fields={
            "T1": "thickness",
        },
        optional_fields={
            "NIP": "NIP",
        },
        unsupported_fields=("ELFORM", "SHRF", "NLOC"),
    ),

    # --- Sets (from *cardmenuitem) ---

    "SET_NODE_LIST": HmKeywordMapping(
        keyword="SET_NODE_LIST",
        entity_type="groups",
        cardimage="SET_NODE_LIST",
        id_param="SID",
        name_template="SET_NODE_LIST_{SID}",
        fields={},
        unsupported_fields=("IDS",),
    ),

    "SET_SEGMENT": HmKeywordMapping(
        keyword="SET_SEGMENT",
        entity_type="groups",
        cardimage="SET_SEGMENT",
        id_param="SID",
        name_template="SET_SEGMENT_{SID}",
        fields={},
        unsupported_fields=("IDS",),
    ),

    "SET_PART_LIST": HmKeywordMapping(
        keyword="SET_PART_LIST",
        entity_type="groups",
        cardimage="SET_PART_LIST",
        id_param="SID",
        name_template="SET_PART_LIST_{SID}",
        fields={},
        unsupported_fields=("IDS",),
    ),
}


def normalize_keyword(keyword: str) -> str:
    return keyword.upper().lstrip("*")


def get_verified_mapping(keyword: str) -> HmKeywordMapping | None:
    return VERIFIED_MAPPINGS.get(normalize_keyword(keyword))


def has_verified_mapping(keyword: str) -> bool:
    return get_verified_mapping(keyword) is not None


def render_verified_keyword(keyword: str, params: dict[str, Any]) -> str:
    mapping = get_verified_mapping(keyword)
    if mapping is None:
        raise KeyError(f"No verified HyperMesh mapping for {keyword}")

    required_names = [*mapping.name_params, *mapping.fields.keys()]
    if mapping.id_param:
        required_names.insert(0, mapping.id_param)
    missing = [name for name in required_names if name not in params]
    if missing:
        raise ValueError(f"Missing required parameters for {mapping.keyword}: {', '.join(missing)}")

    ignored = [name for name in mapping.unsupported_fields if name in params]
    name = mapping.name_template.format(**params)
    lines = [
        f"# Verified HyperMesh LS-DYNA mapping: *{mapping.keyword} -> {mapping.cardimage or mapping.entity_type}",
    ]
    if ignored:
        lines.append(f"# Ignored unsupported fields for HyperMesh Tcl mapping: {', '.join(ignored)}")

    create_line = f'*createentity {mapping.entity_type} name="{name}"'
    if mapping.cardimage:
        create_line += f" cardimage={mapping.cardimage}"

    lines.extend([
        create_line,
        f'*createmark {mapping.entity_type} 1 "by name" "{name}"',
        "set _hm_keyword_ids [hm_getmark {entity_type} 1]".format(entity_type=mapping.entity_type),
        "set _hm_keyword_id [lindex $_hm_keyword_ids end]",
        f'if {{$_hm_keyword_id eq ""}} {{ error "Failed to create *{mapping.keyword}" }}',
    ])

    for lsdyna_name, hm_name in mapping.fields.items():
        lines.append(f"*setvalue {mapping.entity_type} id=$_hm_keyword_id {hm_name}={params[lsdyna_name]}")
    for lsdyna_name, hm_name in (mapping.optional_fields or {}).items():
        if lsdyna_name in params:
            lines.append(f"*setvalue {mapping.entity_type} id=$_hm_keyword_id {hm_name}={params[lsdyna_name]}")

    if mapping.cardimage:
        lines.append(
            f'puts "HM_KEYWORD_CREATED keyword={mapping.keyword} entity={mapping.entity_type} id=$_hm_keyword_id cardimage={mapping.cardimage}"'
        )
    else:
        lines.append(
            f'puts "HM_KEYWORD_CREATED keyword={mapping.keyword} entity={mapping.entity_type} id=$_hm_keyword_id"'
        )
    return "\n".join(lines)
