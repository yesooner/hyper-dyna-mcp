# LS-DYNA R13 *MAT_BARLAT_ANISOTROPIC_PLASTICITY (*MAT_033)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_BARLAT_ANISOTROPIC_PLASTICITY_{{MID}}" cardimage=MAT_BARLAT_ANISOTROPIC_PLASTICITY
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}