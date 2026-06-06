# LS-DYNA R13 *MAT_WTM_STM_PLC (*MAT_135_PLC)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_WTM_STM_PLC_{{MID}}" cardimage=MAT_WTM_STM_PLC
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}