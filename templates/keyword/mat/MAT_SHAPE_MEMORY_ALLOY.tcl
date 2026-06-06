# LS-DYNA R13 *MAT_SHAPE_MEMORY_ALLOY (*MAT_291)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_SHAPE_MEMORY_ALLOY_{{MID}}" cardimage=MAT_SHAPE_MEMORY_ALLOY
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}