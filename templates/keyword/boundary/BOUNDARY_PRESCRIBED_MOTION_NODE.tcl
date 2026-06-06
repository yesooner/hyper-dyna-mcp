# LS-DYNA R13 *BOUNDARY_PRESCRIBED_MOTION_NODE
# Category: boundary
# Parameters: NID, DOF, VAD, LCID, SF, VID, DEATH, BIRTH

*createentity groups name="PRESCRIBED_MOTION_NODE_{{SID}}" cardimage=BOUNDARY_PRESCRIBED_MOTION_NODE
*setvalue groups id={{SID}} dataname=NID value={{NID}}
*setvalue groups id={{SID}} dataname=DOF value={{DOF}}
*setvalue groups id={{SID}} dataname=VAD value={{VAD}}
*setvalue groups id={{SID}} dataname=LCID value={{LCID}}
*setvalue groups id={{SID}} dataname=SF value={{SF}}
*setvalue groups id={{SID}} dataname=VID value={{VID}}
*setvalue groups id={{SID}} dataname=DEATH value={{DEATH}}
*setvalue groups id={{SID}} dataname=BIRTH value={{BIRTH}}