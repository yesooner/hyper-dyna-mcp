# LS-DYNA R13 *DEFINE_TRANSFORMATION
# Category: define
# Entity type: groups
# Card image: DEFINE_TRANSFORMATION
# Parameters: ITRAN(int), NSET(int), IDIR(int), FX(float), FY(float), FZ(float)

*createentity groups name="DEFINE_TRANSFORMATION_{{ITRAN}}" cardimage=DEFINE_TRANSFORMATION
*createmark groups 1 "by name" "DEFINE_TRANSFORMATION_{{ITRAN}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
if {$_grp_id eq ""} { error "Failed to create DEFINE_TRANSFORMATION" }
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=ITRAN value={{ITRAN}}
*setvalue groups id=$_grp_id dataname=NSET value={{NSET}}
*setvalue groups id=$_grp_id dataname=IDIR value={{IDIR}}
*setvalue groups id=$_grp_id dataname=FX value={{FX}}
*setvalue groups id=$_grp_id dataname=FY value={{FY}}
*setvalue groups id=$_grp_id dataname=FZ value={{FZ}}
puts "HM_KEYWORD_CREATED keyword=DEFINE_TRANSFORMATION entity=groups id=$_grp_id"
