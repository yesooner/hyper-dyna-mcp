# LS-DYNA R13 *SECTION_SHELL
# Category: section
# Parameters: SECID, ELFORM, SHRF, NIP

*createentity props name="SECTION_SHELL_{{SECID}}" cardimage=SECTION_SHELL
*setvalue props id={{SECID}} STATUS=2
*setvalue props id={{SECID}} dataname=ELFORM value={{ELFORM}}
*setvalue props id={{SECID}} dataname=SHRF value={{SHRF}}
*setvalue props id={{SECID}} dataname=NIP value={{NIP}}