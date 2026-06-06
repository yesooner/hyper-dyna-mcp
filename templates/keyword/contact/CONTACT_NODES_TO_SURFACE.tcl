# LS-DYNA R13 *CONTACT_NODES_TO_SURFACE
# Category: contact
# Parameters: SSID, MSID, SSTYP, MSTYP

*createentity groups name="NODES_TO_SURFACE_{{SID}}" cardimage=CONTACT_NODES_TO_SURFACE
*setvalue groups id={{SID}} dataname=SSID value={{SSID}}
*setvalue groups id={{SID}} dataname=MSID value={{MSID}}
*setvalue groups id={{SID}} dataname=SSTYP value={{SSTYP}}
*setvalue groups id={{SID}} dataname=MSTYP value={{MSTYP}}