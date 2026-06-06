# LS-DYNA R13 *BOUNDARY_SPC
# Category: boundary
# Entity type: loadcols
# Card image: BOUNDARY_SPC
# Parameters: NODEID(int), CID(int), DOFX(int), DOFY(int), DOFZ(int), DOFRX(int), DOFRY(int), DOFRZ(int)

*createentity loadcols name="BOUNDARY_SPC_{{NODEID}}" cardimage=BOUNDARY_SPC
*createmark loadcols 1 "by name" "BOUNDARY_SPC_{{NODEID}}"
set _lc_ids [hm_getmark loadcols 1]
set _lc_id [lindex $_lc_ids end]
if {$_lc_id eq ""} { error "Failed to create BOUNDARY_SPC" }
*setvalue loadcols id=$_lc_id STATUS=2
*setvalue loadcols id=$_lc_id dataname=NODEID value={{NODEID}}
*setvalue loadcols id=$_lc_id dataname=CID value={{CID}}
*setvalue loadcols id=$_lc_id dataname=DOFX value={{DOFX}}
*setvalue loadcols id=$_lc_id dataname=DOFY value={{DOFY}}
*setvalue loadcols id=$_lc_id dataname=DOFZ value={{DOFZ}}
*setvalue loadcols id=$_lc_id dataname=DOFRX value={{DOFRX}}
*setvalue loadcols id=$_lc_id dataname=DOFRY value={{DOFRY}}
*setvalue loadcols id=$_lc_id dataname=DOFRZ value={{DOFRZ}}
puts "HM_KEYWORD_CREATED keyword=BOUNDARY_SPC entity=loadcols id=$_lc_id"
