# LS-DYNA R13 *INITIAL_VELOCITY_GENERATION
# Category: initial
# Entity type: groups
# Card image: INITIAL_VELOCITY_GENERATION
# Parameters: SETID(int), STYP(int), VNX(float), VNY(float), VNZ(float), IRID(int), OMEGA(float)

*createentity groups name="INITIAL_VELOCITY_GENERATION_{{SETID}}" cardimage=INITIAL_VELOCITY_GENERATION
*createmark groups 1 "by name" "INITIAL_VELOCITY_GENERATION_{{SETID}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
if {$_grp_id eq ""} { error "Failed to create INITIAL_VELOCITY_GENERATION" }
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=SETID value={{SETID}}
*setvalue groups id=$_grp_id dataname=STYP value={{STYP}}
*setvalue groups id=$_grp_id dataname=VNX value={{VNX}}
*setvalue groups id=$_grp_id dataname=VNY value={{VNY}}
*setvalue groups id=$_grp_id dataname=VNZ value={{VNZ}}
*setvalue groups id=$_grp_id dataname=IRID value={{IRID}}
*setvalue groups id=$_grp_id dataname=OMEGA value={{OMEGA}}
puts "HM_KEYWORD_CREATED keyword=INITIAL_VELOCITY_GENERATION entity=groups id=$_grp_id"
