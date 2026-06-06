# LS-DYNA R13 *BOUNDARY_PRESCRIBED_MOTION_NODE
# Category: boundary
# Entity type: loadcols
# Card image: BOUNDARY_PRESCRIBED_MOTION_NODE
# Parameters: NID(int), DOF(int), VAD(int), LCID(int), SF(float), VID(int), DEATH(float), BIRTH(float)

*createentity loadcols name="BOUNDARY_PRESCRIBED_MOTION_NODE_{{NID}}" cardimage=BOUNDARY_PRESCRIBED_MOTION_NODE
*createmark loadcols 1 "by name" "BOUNDARY_PRESCRIBED_MOTION_NODE_{{NID}}"
set _lc_ids [hm_getmark loadcols 1]
set _lc_id [lindex $_lc_ids end]
if {$_lc_id eq ""} { error "Failed to create BOUNDARY_PRESCRIBED_MOTION_NODE" }
*setvalue loadcols id=$_lc_id STATUS=2
*setvalue loadcols id=$_lc_id dataname=NID value={{NID}}
*setvalue loadcols id=$_lc_id dataname=DOF value={{DOF}}
*setvalue loadcols id=$_lc_id dataname=VAD value={{VAD}}
*setvalue loadcols id=$_lc_id dataname=LCID value={{LCID}}
*setvalue loadcols id=$_lc_id dataname=SF value={{SF}}
*setvalue loadcols id=$_lc_id dataname=VID value={{VID}}
*setvalue loadcols id=$_lc_id dataname=DEATH value={{DEATH}}
*setvalue loadcols id=$_lc_id dataname=BIRTH value={{BIRTH}}
puts "HM_KEYWORD_CREATED keyword=BOUNDARY_PRESCRIBED_MOTION_NODE entity=loadcols id=$_lc_id"
