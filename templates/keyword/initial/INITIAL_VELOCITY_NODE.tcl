# LS-DYNA R13 *INITIAL_VELOCITY_NODE
# Category: initial
# Parameters: NID, VX, VY, VZ, VRX, VRY, VRZ

*createentity groups name="VELOCITY_NODE_{{SETID}}" cardimage=INITIAL_VELOCITY_NODE
*setvalue groups id={{SETID}} dataname=NID value={{NID}}
*setvalue groups id={{SETID}} dataname=VX value={{VX}}
*setvalue groups id={{SETID}} dataname=VY value={{VY}}
*setvalue groups id={{SETID}} dataname=VZ value={{VZ}}
*setvalue groups id={{SETID}} dataname=VRX value={{VRX}}
*setvalue groups id={{SETID}} dataname=VRY value={{VRY}}
*setvalue groups id={{SETID}} dataname=VRZ value={{VRZ}}