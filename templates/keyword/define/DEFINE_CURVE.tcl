# LS-DYNA R13 *DEFINE_CURVE
# Category: define
# Entity type: groups
# Card image: DEFINE_CURVE
# Parameters: LCID(int), SIDR(int), SFA(float), SFO(float), OFFA(float), OFFO(float), DTIME(float)
# Note: Curve data points (A,O pairs) are appended separately after creation

*createentity groups name="DEFINE_CURVE_{{LCID}}" cardimage=DEFINE_CURVE
*createmark groups 1 "by name" "DEFINE_CURVE_{{LCID}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
if {$_grp_id eq ""} { error "Failed to create DEFINE_CURVE" }
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=LCID value={{LCID}}
*setvalue groups id=$_grp_id dataname=SIDR value={{SIDR}}
*setvalue groups id=$_grp_id dataname=SFA value={{SFA}}
*setvalue groups id=$_grp_id dataname=SFO value={{SFO}}
*setvalue groups id=$_grp_id dataname=OFFA value={{OFFA}}
*setvalue groups id=$_grp_id dataname=OFFO value={{OFFO}}
*setvalue groups id=$_grp_id dataname=DTIME value={{DTIME}}
puts "HM_KEYWORD_CREATED keyword=DEFINE_CURVE entity=groups id=$_grp_id"
