# LS-DYNA R13 *SECTION_SOLID
# Category: section
# Parameters: SECID, ELFORM, AET

*createentity props name="SECTION_SOLID_{{SECID}}" cardimage=SECTION_SOLID
*setvalue props id={{SECID}} STATUS=2
*setvalue props id={{SECID}} dataname=ELFORM value={{ELFORM}}
*setvalue props id={{SECID}} dataname=AET value={{AET}}