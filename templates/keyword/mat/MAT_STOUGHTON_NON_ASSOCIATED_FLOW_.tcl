# LS-DYNA R13 *MAT_STOUGHTON_NON_ASSOCIATED_FLOW_ (*MAT_260A)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_STOUGHTON_NON_ASSOCIATED_FLOW__{{MID}}" cardimage=MAT_STOUGHTON_NON_ASSOCIATED_FLOW_
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}