# LS-DYNA R13 *LOAD_SEGMENT
# Category: load
# Parameters: LCID, SF

*createentity groups name="SEGMENT_{{SID}}" cardimage=LOAD_SEGMENT
*setvalue groups id={{SID}} dataname=LCID value={{LCID}}
*setvalue groups id={{SID}} dataname=SF value={{SF}}