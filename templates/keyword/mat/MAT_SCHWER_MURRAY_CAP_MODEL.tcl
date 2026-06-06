# LS-DYNA R13 *MAT_SCHWER_MURRAY_CAP_MODEL (*MAT_145)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_SCHWER_MURRAY_CAP_MODEL_{{MID}}" cardimage=MAT_SCHWER_MURRAY_CAP_MODEL
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}