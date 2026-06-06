# LS-DYNA R13 *LOAD_RIGID_BODY
# Category: load
# Entity type: loadcols
# Card image: LOAD_RIGID_BODY
# Parameters: PID(int), DOF(int), LCID(int), SF(float), CID(int)

*createentity loadcols name="LOAD_RIGID_BODY_{{PID}}" cardimage=LOAD_RIGID_BODY
*createmark loadcols 1 "by name" "LOAD_RIGID_BODY_{{PID}}"
set _lc_ids [hm_getmark loadcols 1]
set _lc_id [lindex $_lc_ids end]
if {$_lc_id eq ""} { error "Failed to create LOAD_RIGID_BODY" }
*setvalue loadcols id=$_lc_id STATUS=2
*setvalue loadcols id=$_lc_id dataname=PID value={{PID}}
*setvalue loadcols id=$_lc_id dataname=DOF value={{DOF}}
*setvalue loadcols id=$_lc_id dataname=LCID value={{LCID}}
*setvalue loadcols id=$_lc_id dataname=SF value={{SF}}
*setvalue loadcols id=$_lc_id dataname=CID value={{CID}}
puts "HM_KEYWORD_CREATED keyword=LOAD_RIGID_BODY entity=loadcols id=$_lc_id"
