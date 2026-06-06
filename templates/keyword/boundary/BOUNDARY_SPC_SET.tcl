# LS-DYNA R13 *BOUNDARY_SPC_SET
# Category: boundary
# Entity type: loadcols
# Card image: BOUNDARY_SPC_SET
# Parameters: NSID(int), CID(int), DOFX(int), DOFY(int), DOFZ(int), DOFRX(int), DOFRY(int), DOFRZ(int)

*createentity loadcols name="BOUNDARY_SPC_SET_{{NSID}}" cardimage=BOUNDARY_SPC_SET
*createmark loadcols 1 "by name" "BOUNDARY_SPC_SET_{{NSID}}"
set _lc_ids [hm_getmark loadcols 1]
set _lc_id [lindex $_lc_ids end]
if {$_lc_id eq ""} { error "Failed to create BOUNDARY_SPC_SET" }
*setvalue loadcols id=$_lc_id STATUS=2
*setvalue loadcols id=$_lc_id dataname=NSID value={{NSID}}
*setvalue loadcols id=$_lc_id dataname=CID value={{CID}}
*setvalue loadcols id=$_lc_id dataname=DOFX value={{DOFX}}
*setvalue loadcols id=$_lc_id dataname=DOFY value={{DOFY}}
*setvalue loadcols id=$_lc_id dataname=DOFZ value={{DOFZ}}
*setvalue loadcols id=$_lc_id dataname=DOFRX value={{DOFRX}}
*setvalue loadcols id=$_lc_id dataname=DOFRY value={{DOFRY}}
*setvalue loadcols id=$_lc_id dataname=DOFRZ value={{DOFRZ}}
puts "HM_KEYWORD_CREATED keyword=BOUNDARY_SPC_SET entity=loadcols id=$_lc_id"
