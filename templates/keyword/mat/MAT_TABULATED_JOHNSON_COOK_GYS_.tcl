# LS-DYNA R13 *MAT_TABULATED_JOHNSON_COOK_GYS_ (*MAT_224_GYS)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_TABULATED_JOHNSON_COOK_GYS__{{MID}}" cardimage=MAT_TABULATED_JOHNSON_COOK_GYS_
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}