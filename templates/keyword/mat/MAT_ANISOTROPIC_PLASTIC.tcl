# LS-DYNA R13 *MAT_ANISOTROPIC_PLASTIC (*MAT_103_P)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_ANISOTROPIC_PLASTIC_{{MID}}" cardimage=MAT_ANISOTROPIC_PLASTIC
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}