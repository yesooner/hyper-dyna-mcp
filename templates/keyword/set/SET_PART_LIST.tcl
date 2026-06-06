# LS-DYNA R13 *SET_PART_LIST
# Category: set
# Entity type: groups
# Card image: SET_PART_LIST
# Parameters: SID(int)
# Note: Data lines (PID list) are appended separately after creation

*createentity groups name="SET_PART_LIST_{{SID}}" cardimage=SET_PART_LIST
*createmark groups 1 "by name" "SET_PART_LIST_{{SID}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
if {$_grp_id eq ""} { error "Failed to create SET_PART_LIST" }
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=SID value={{SID}}
puts "HM_KEYWORD_CREATED keyword=SET_PART_LIST entity=groups id=$_grp_id"
