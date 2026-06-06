# LS-DYNA R13 *LOAD_RIGID_BODY
# Category: load
# Parameters: PID, DOF, LCID, SF, CID

*createentity groups name="RIGID_BODY_{{SID}}" cardimage=LOAD_RIGID_BODY
*setvalue groups id={{SID}} dataname=PID value={{PID}}
*setvalue groups id={{SID}} dataname=DOF value={{DOF}}
*setvalue groups id={{SID}} dataname=LCID value={{LCID}}
*setvalue groups id={{SID}} dataname=SF value={{SF}}
*setvalue groups id={{SID}} dataname=CID value={{CID}}