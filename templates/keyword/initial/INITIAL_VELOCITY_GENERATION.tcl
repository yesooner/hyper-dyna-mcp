# LS-DYNA R13 *INITIAL_VELOCITY_GENERATION
# Category: initial
# Parameters: SETID, STYP, VNX, VNY, VNZ, IRID, OMEGA

*createentity groups name="VELOCITY_GENERATION_{{SETID}}" cardimage=INITIAL_VELOCITY_GENERATION
*setvalue groups id={{SETID}} dataname=SETID value={{SETID}}
*setvalue groups id={{SETID}} dataname=STYP value={{STYP}}
*setvalue groups id={{SETID}} dataname=VNX value={{VNX}}
*setvalue groups id={{SETID}} dataname=VNY value={{VNY}}
*setvalue groups id={{SETID}} dataname=VNZ value={{VNZ}}
*setvalue groups id={{SETID}} dataname=IRID value={{IRID}}
*setvalue groups id={{SETID}} dataname=OMEGA value={{OMEGA}}