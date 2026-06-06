# LS-DYNA R13 *CONTACT_TIED_SURFACE_TO_SURFACE
# Category: contact
# Parameters: SSID, MSID, SSTYP, MSTYP, SBOXID, MBOXID, SPR, MPR

*createentity groups name="TIED_SURFACE_TO_SURFACE_{{SID}}" cardimage=CONTACT_TIED_SURFACE_TO_SURFACE
*setvalue groups id={{SID}} dataname=SSID value={{SSID}}
*setvalue groups id={{SID}} dataname=MSID value={{MSID}}
*setvalue groups id={{SID}} dataname=SSTYP value={{SSTYP}}
*setvalue groups id={{SID}} dataname=MSTYP value={{MSTYP}}
*setvalue groups id={{SID}} dataname=SBOXID value={{SBOXID}}
*setvalue groups id={{SID}} dataname=MBOXID value={{MBOXID}}
*setvalue groups id={{SID}} dataname=SPR value={{SPR}}
*setvalue groups id={{SID}} dataname=MPR value={{MPR}}