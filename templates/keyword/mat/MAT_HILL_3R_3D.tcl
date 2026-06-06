# LS-DYNA R13 *MAT_HILL_3R_3D (*MAT_122_3D)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_HILL_3R_3D_{{MID}}" cardimage=MAT_HILL_3R_3D
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}