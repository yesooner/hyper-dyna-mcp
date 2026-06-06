# LS-DYNA R13 *LOAD_NODE
# Category: load
# Entity type: loadcols
# Card image: LOAD_NODE
# Parameters: NID(int), DOF(int), LCID(int), SF(float), CID(int), M1(float), M2(float), M3(float)

*createentity loadcols name="LOAD_NODE_{{NID}}" cardimage=LOAD_NODE
*createmark loadcols 1 "by name" "LOAD_NODE_{{NID}}"
set _lc_ids [hm_getmark loadcols 1]
set _lc_id [lindex $_lc_ids end]
if {$_lc_id eq ""} { error "Failed to create LOAD_NODE" }
*setvalue loadcols id=$_lc_id STATUS=2
*setvalue loadcols id=$_lc_id dataname=NID value={{NID}}
*setvalue loadcols id=$_lc_id dataname=DOF value={{DOF}}
*setvalue loadcols id=$_lc_id dataname=LCID value={{LCID}}
*setvalue loadcols id=$_lc_id dataname=SF value={{SF}}
*setvalue loadcols id=$_lc_id dataname=CID value={{CID}}
*setvalue loadcols id=$_lc_id dataname=M1 value={{M1}}
*setvalue loadcols id=$_lc_id dataname=M2 value={{M2}}
*setvalue loadcols id=$_lc_id dataname=M3 value={{M3}}
puts "HM_KEYWORD_CREATED keyword=LOAD_NODE entity=loadcols id=$_lc_id"
