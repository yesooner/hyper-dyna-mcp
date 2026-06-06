# LS-DYNA R13 *LOAD_SEGMENT
# Category: load
# Entity type: loadcols
# Card image: LOAD_SEGMENT
# Parameters: LCID(int), SF(float)

*createentity loadcols name="LOAD_SEGMENT_{{LCID}}" cardimage=LOAD_SEGMENT
*createmark loadcols 1 "by name" "LOAD_SEGMENT_{{LCID}}"
set _lc_ids [hm_getmark loadcols 1]
set _lc_id [lindex $_lc_ids end]
if {$_lc_id eq ""} { error "Failed to create LOAD_SEGMENT" }
*setvalue loadcols id=$_lc_id STATUS=2
*setvalue loadcols id=$_lc_id dataname=LCID value={{LCID}}
*setvalue loadcols id=$_lc_id dataname=SF value={{SF}}
puts "HM_KEYWORD_CREATED keyword=LOAD_SEGMENT entity=loadcols id=$_lc_id"
