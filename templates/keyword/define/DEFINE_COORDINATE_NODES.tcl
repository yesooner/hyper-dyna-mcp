# LS-DYNA R13 *DEFINE_COORDINATE_NODES
# Category: define
# Entity type: groups
# Card image: DEFINE_COORDINATE_NODES
# Parameters: CID(int), N1(int), N2(int), N3(int)

*createentity groups name="DEFINE_COORDINATE_NODES_{{CID}}" cardimage=DEFINE_COORDINATE_NODES
*createmark groups 1 "by name" "DEFINE_COORDINATE_NODES_{{CID}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
if {$_grp_id eq ""} { error "Failed to create DEFINE_COORDINATE_NODES" }
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=CID value={{CID}}
*setvalue groups id=$_grp_id dataname=N1 value={{N1}}
*setvalue groups id=$_grp_id dataname=N2 value={{N2}}
*setvalue groups id=$_grp_id dataname=N3 value={{N3}}
puts "HM_KEYWORD_CREATED keyword=DEFINE_COORDINATE_NODES entity=groups id=$_grp_id"
