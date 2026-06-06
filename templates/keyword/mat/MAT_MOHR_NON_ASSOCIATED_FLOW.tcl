# LS-DYNA R13 *MAT_MOHR_NON_ASSOCIATED_FLOW (*MAT_260B)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_MOHR_NON_ASSOCIATED_FLOW_{{MID}}" cardimage=MAT_MOHR_NON_ASSOCIATED_FLOW
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}