# LS-DYNA R13 *MAT_THERMAL_ISOTROPIC_TD (*MAT_T03)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_THERMAL_ISOTROPIC_TD_{{MID}}" cardimage=MAT_THERMAL_ISOTROPIC_TD
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}