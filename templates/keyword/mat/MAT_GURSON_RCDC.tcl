# LS-DYNA R13 *MAT_GURSON_RCDC (*MAT_120_RCDC)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_GURSON_RCDC_{{MID}}" cardimage=MAT_GURSON_RCDC
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}