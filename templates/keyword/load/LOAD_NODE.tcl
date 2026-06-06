# LS-DYNA R13 *LOAD_NODE
# Category: load
# Parameters: NID, DOF, LCID, SF, CID, M1, M2, M3

*createentity groups name="NODE_{{SID}}" cardimage=LOAD_NODE
*setvalue groups id={{SID}} dataname=NID value={{NID}}
*setvalue groups id={{SID}} dataname=DOF value={{DOF}}
*setvalue groups id={{SID}} dataname=LCID value={{LCID}}
*setvalue groups id={{SID}} dataname=SF value={{SF}}
*setvalue groups id={{SID}} dataname=CID value={{CID}}
*setvalue groups id={{SID}} dataname=M1 value={{M1}}
*setvalue groups id={{SID}} dataname=M2 value={{M2}}
*setvalue groups id={{SID}} dataname=M3 value={{M3}}