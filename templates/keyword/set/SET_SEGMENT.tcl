# LS-DYNA R13 *SET_SEGMENT
# Category: set
# Entity type: groups
# Card image: SET_SEGMENT
# Parameters: SID(int)
# Note: Data lines (N1,N2,N3,N4,EL) are appended separately after creation

*createentity groups name="SET_SEGMENT_{{SID}}" cardimage=SET_SEGMENT
*createmark groups 1 "by name" "SET_SEGMENT_{{SID}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
if {$_grp_id eq ""} { error "Failed to create SET_SEGMENT" }
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=SID value={{SID}}
puts "HM_KEYWORD_CREATED keyword=SET_SEGMENT entity=groups id=$_grp_id"
