# LS-DYNA R13 *CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
# Category: contact
# Parameters: SSID, MSID, SSTYP, MSTYP

*createentity groups name="CONTACT_S2S_{{SSID}}_{{MSID}}" cardimage=CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
*setvalue groups id=next STATUS=2
*setvalue groups id=next dataname=SSID value={{SSID}}
*setvalue groups id=next dataname=MSID value={{MSID}}
*setvalue groups id=next dataname=SSTYP value={{SSTYP}}
*setvalue groups id=next dataname=MSTYP value={{MSTYP}}
