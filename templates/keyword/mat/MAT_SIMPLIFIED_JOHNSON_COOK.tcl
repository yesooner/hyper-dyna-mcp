# LS-DYNA R13 *MAT_SIMPLIFIED_JOHNSON_COOK (*MAT_098)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_SIMPLIFIED_JOHNSON_COOK_{{MID}}" cardimage=MAT_SIMPLIFIED_JOHNSON_COOK
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}