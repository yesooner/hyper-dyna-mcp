# LS-DYNA R13 *BOUNDARY_SPC
# Category: boundary
# Parameters: NODEID, CID, DOFX, DOFY, DOFZ, DOFRX, DOFRY, DOFRZ

*createentity groups name="SPC_{{SID}}" cardimage=BOUNDARY_SPC
*setvalue groups id={{SID}} dataname=NODEID value={{NODEID}}
*setvalue groups id={{SID}} dataname=CID value={{CID}}
*setvalue groups id={{SID}} dataname=DOFX value={{DOFX}}
*setvalue groups id={{SID}} dataname=DOFY value={{DOFY}}
*setvalue groups id={{SID}} dataname=DOFZ value={{DOFZ}}
*setvalue groups id={{SID}} dataname=DOFRX value={{DOFRX}}
*setvalue groups id={{SID}} dataname=DOFRY value={{DOFRY}}
*setvalue groups id={{SID}} dataname=DOFRZ value={{DOFRZ}}