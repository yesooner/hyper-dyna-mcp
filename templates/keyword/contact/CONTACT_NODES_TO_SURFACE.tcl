# LS-DYNA R13 *CONTACT_NODES_TO_SURFACE
# Category: contact
# Entity type: groups
# Card image: CONTACT_NODES_TO_SURFACE
# Parameters: SSID(int), MSID(int), SSTYP(int), MSTYP(int)

*createentity groups name="CONTACT_NODES_TO_SURFACE_{{SSID}}" cardimage=CONTACT_NODES_TO_SURFACE
*createmark groups 1 "by name" "CONTACT_NODES_TO_SURFACE_{{SSID}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
if {$_grp_id eq ""} { error "Failed to create CONTACT_NODES_TO_SURFACE" }
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=SSID value={{SSID}}
*setvalue groups id=$_grp_id dataname=MSID value={{MSID}}
*setvalue groups id=$_grp_id dataname=SSTYP value={{SSTYP}}
*setvalue groups id=$_grp_id dataname=MSTYP value={{MSTYP}}
puts "HM_KEYWORD_CREATED keyword=CONTACT_NODES_TO_SURFACE entity=groups id=$_grp_id"
