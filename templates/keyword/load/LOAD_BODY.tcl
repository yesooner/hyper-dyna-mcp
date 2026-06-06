# LS-DYNA R13 *LOAD_BODY
# Category: load
# Entity type: loadcols
# Card image: LOAD_BODY
# Parameters: LCID(int), SF(float)

*createentity loadcols name="LOAD_BODY_{{LCID}}" cardimage=LOAD_BODY
*createmark loadcols 1 "by name" "LOAD_BODY_{{LCID}}"
set _lc_ids [hm_getmark loadcols 1]
set _lc_id [lindex $_lc_ids end]
if {$_lc_id eq ""} { error "Failed to create LOAD_BODY" }
*setvalue loadcols id=$_lc_id STATUS=2
*setvalue loadcols id=$_lc_id dataname=LCID value={{LCID}}
*setvalue loadcols id=$_lc_id dataname=SF value={{SF}}
puts "HM_KEYWORD_CREATED keyword=LOAD_BODY entity=loadcols id=$_lc_id"
