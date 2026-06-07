# LS-DYNA R13 *CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
# Category: contact
# Parameters: SSID, MSID, SSTYP, MSTYP

*createentity groups name="CONTACT_S2S_{{SSID}}_{{MSID}}" cardimage=CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
*createmark groups 1 "by name" "CONTACT_S2S_{{SSID}}_{{MSID}}"
set _grp_ids [hm_getmark groups 1]
set _grp_id [lindex $_grp_ids end]
*setvalue groups id=$_grp_id STATUS=2
*setvalue groups id=$_grp_id dataname=SSID value={{SSID}}
*setvalue groups id=$_grp_id dataname=MSID value={{MSID}}
*setvalue groups id=$_grp_id dataname=SSTYP value={{SSTYP}}
*setvalue groups id=$_grp_id dataname=MSTYP value={{MSTYP}}
