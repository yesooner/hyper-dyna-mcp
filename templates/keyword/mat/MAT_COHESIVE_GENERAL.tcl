# LS-DYNA R13 *MAT_COHESIVE_GENERAL (*MAT_186)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_COHESIVE_GENERAL_{{MID}}" cardimage=MAT_COHESIVE_GENERAL
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}