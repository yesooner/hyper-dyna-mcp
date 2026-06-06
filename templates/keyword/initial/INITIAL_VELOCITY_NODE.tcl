# LS-DYNA R13 *INITIAL_VELOCITY_NODE
# Category: initial
# Entity type: groups
# Card image: INITIAL_VELOCITY_NODE
# Parameters: NID(int), VX(float), VY(float), VZ(float), VRX(float), VRY(float), VRZ(float)

*createentity groups name="INITIAL_VELOCITY_NODE_{{NID}}" cardimage=INITIAL_VELOCITY_NODE
*createmark groups 1 "by name" "INITIAL_VELOCITY_NODE_{{NID}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
if {$_grp_id eq ""} { error "Failed to create INITIAL_VELOCITY_NODE" }
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=NID value={{NID}}
*setvalue groups id=$_grp_id dataname=VX value={{VX}}
*setvalue groups id=$_grp_id dataname=VY value={{VY}}
*setvalue groups id=$_grp_id dataname=VZ value={{VZ}}
*setvalue groups id=$_grp_id dataname=VRX value={{VRX}}
*setvalue groups id=$_grp_id dataname=VRY value={{VRY}}
*setvalue groups id=$_grp_id dataname=VRZ value={{VRZ}}
puts "HM_KEYWORD_CREATED keyword=INITIAL_VELOCITY_NODE entity=groups id=$_grp_id"
