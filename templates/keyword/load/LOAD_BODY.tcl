# LS-DYNA R13 *LOAD_BODY
# Category: load
# Parameters: LCID, SF

*createentity groups name="BODY_{{SID}}" cardimage=LOAD_BODY
*setvalue groups id={{SID}} dataname=LCID value={{LCID}}
*setvalue groups id={{SID}} dataname=SF value={{SF}}