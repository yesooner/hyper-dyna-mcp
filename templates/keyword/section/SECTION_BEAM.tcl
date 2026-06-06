# LS-DYNA R13 *SECTION_BEAM
# Category: section
# Parameters: SECID, ELFORM

*createentity props name="SECTION_BEAM_{{SECID}}" cardimage=SECTION_BEAM
*setvalue props id={{SECID}} STATUS=2
*setvalue props id={{SECID}} dataname=ELFORM value={{ELFORM}}