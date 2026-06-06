# LS-DYNA R13 *MAT_ANAND_VISCOPLASTICITY (*MAT_296)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_ANAND_VISCOPLASTICITY_{{MID}}" cardimage=MAT_ANAND_VISCOPLASTICITY
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}