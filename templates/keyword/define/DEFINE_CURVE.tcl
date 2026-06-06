# LS-DYNA R13 *DEFINE_CURVE
# Category: define
# Parameters: LCID, SIDR, SFA, SFO, OFFA, OFFO, DTIME

*createentity groups name="CURVE_{{LCID}}" cardimage=DEFINE_CURVE
*setvalue groups id={{LCID}} dataname=LCID value={{LCID}}
*setvalue groups id={{LCID}} dataname=SIDR value={{SIDR}}
*setvalue groups id={{LCID}} dataname=SFA value={{SFA}}
*setvalue groups id={{LCID}} dataname=SFO value={{SFO}}
*setvalue groups id={{LCID}} dataname=OFFA value={{OFFA}}
*setvalue groups id={{LCID}} dataname=OFFO value={{OFFO}}
*setvalue groups id={{LCID}} dataname=DTIME value={{DTIME}}