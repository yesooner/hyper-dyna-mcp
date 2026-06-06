# LS-DYNA R13 *MAT_RIGID
# Category: mat
# Parameters: MID, RHO, E, PR, N, COUPLE, M, TLOG

*createentity mats name="MAT_RIGID_{{MID}}" cardimage=MAT_RIGID
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}
*setvalue mats id={{MID}} dataname=N value={{N}}
*setvalue mats id={{MID}} dataname=COUPLE value={{COUPLE}}
*setvalue mats id={{MID}} dataname=M value={{M}}
*setvalue mats id={{MID}} dataname=TLOG value={{TLOG}}