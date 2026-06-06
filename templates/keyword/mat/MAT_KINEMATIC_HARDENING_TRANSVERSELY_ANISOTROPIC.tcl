# LS-DYNA R13 *MAT_KINEMATIC_HARDENING_TRANSVERSELY_ANISOTROPIC (*MAT_125)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_KINEMATIC_HARDENING_TRANSVERSELY_ANISOTROPIC_{{MID}}" cardimage=MAT_KINEMATIC_HARDENING_TRANSVERSELY_ANISOTROPIC
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}