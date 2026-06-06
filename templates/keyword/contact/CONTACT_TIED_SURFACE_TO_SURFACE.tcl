# LS-DYNA R13 *CONTACT_TIED_SURFACE_TO_SURFACE
# Category: contact
# Entity type: groups
# Card image: CONTACT_TIED_SURFACE_TO_SURFACE
# Parameters: SSID(int), MSID(int), SSTYP(int), MSTYP(int), SBOXID(int), MBOXID(int), SPR(int), MPR(int)

*createentity groups name="CONTACT_TIED_SURFACE_TO_SURFACE_{{SSID}}" cardimage=CONTACT_TIED_SURFACE_TO_SURFACE
*createmark groups 1 "by name" "CONTACT_TIED_SURFACE_TO_SURFACE_{{SSID}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
if {$_grp_id eq ""} { error "Failed to create CONTACT_TIED_SURFACE_TO_SURFACE" }
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=SSID value={{SSID}}
*setvalue groups id=$_grp_id dataname=MSID value={{MSID}}
*setvalue groups id=$_grp_id dataname=SSTYP value={{SSTYP}}
*setvalue groups id=$_grp_id dataname=MSTYP value={{MSTYP}}
*setvalue groups id=$_grp_id dataname=SBOXID value={{SBOXID}}
*setvalue groups id=$_grp_id dataname=MBOXID value={{MBOXID}}
*setvalue groups id=$_grp_id dataname=SPR value={{SPR}}
*setvalue groups id=$_grp_id dataname=MPR value={{MPR}}
puts "HM_KEYWORD_CREATED keyword=CONTACT_TIED_SURFACE_TO_SURFACE entity=groups id=$_grp_id"
