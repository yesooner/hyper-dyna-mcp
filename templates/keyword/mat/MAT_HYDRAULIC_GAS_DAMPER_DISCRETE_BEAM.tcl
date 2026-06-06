# LS-DYNA R13 *MAT_HYDRAULIC_GAS_DAMPER_DISCRETE_BEAM (*MAT_070)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_HYDRAULIC_GAS_DAMPER_DISCRETE_BEAM_{{MID}}" cardimage=MAT_HYDRAULIC_GAS_DAMPER_DISCRETE_BEAM
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}