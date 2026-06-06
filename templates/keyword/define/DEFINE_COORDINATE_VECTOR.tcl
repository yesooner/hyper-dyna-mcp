# LS-DYNA R13 *DEFINE_COORDINATE_VECTOR
# Category: define
# Entity type: groups
# Card image: DEFINE_COORDINATE_VECTOR
# Parameters: CID(int), XT(float), YT(float), ZT(float), XL(float), YL(float), ZL(float)

*createentity groups name="DEFINE_COORDINATE_VECTOR_{{CID}}" cardimage=DEFINE_COORDINATE_VECTOR
*createmark groups 1 "by name" "DEFINE_COORDINATE_VECTOR_{{CID}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
if {$_grp_id eq ""} { error "Failed to create DEFINE_COORDINATE_VECTOR" }
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=CID value={{CID}}
*setvalue groups id=$_grp_id dataname=XT value={{XT}}
*setvalue groups id=$_grp_id dataname=YT value={{YT}}
*setvalue groups id=$_grp_id dataname=ZT value={{ZT}}
*setvalue groups id=$_grp_id dataname=XL value={{XL}}
*setvalue groups id=$_grp_id dataname=YL value={{YL}}
*setvalue groups id=$_grp_id dataname=ZL value={{ZL}}
puts "HM_KEYWORD_CREATED keyword=DEFINE_COORDINATE_VECTOR entity=groups id=$_grp_id"
