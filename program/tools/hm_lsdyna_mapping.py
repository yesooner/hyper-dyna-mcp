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
