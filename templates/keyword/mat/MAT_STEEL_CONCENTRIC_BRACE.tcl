# LS-DYNA R13 *MAT_STEEL_CONCENTRIC_BRACE (*MAT_171)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_STEEL_CONCENTRIC_BRACE_{{MID}}" cardimage=MAT_STEEL_CONCENTRIC_BRACE
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}