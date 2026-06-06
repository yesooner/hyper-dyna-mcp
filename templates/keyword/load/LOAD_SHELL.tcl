# LS-DYNA R13 *LOAD_SHELL
# Category: load
# Parameters: LCID, SF

*createentity groups name="SHELL_{{SID}}" cardimage=LOAD_SHELL
*setvalue groups id={{SID}} dataname=LCID value={{LCID}}
*setvalue groups id={{SID}} dataname=SF value={{SF}}