# LS-DYNA R13 *MAT_ELASTIC_WITH_VISCOSITY_CURVE (*MAT_060C)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_ELASTIC_WITH_VISCOSITY_CURVE_{{MID}}" cardimage=MAT_ELASTIC_WITH_VISCOSITY_CURVE
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}