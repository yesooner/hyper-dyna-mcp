# LS-DYNA R13 *MAT_ELASTIC_PLASTIC_THERMAL (*MAT_004)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_ELASTIC_PLASTIC_THERMAL_{{MID}}" cardimage=MAT_ELASTIC_PLASTIC_THERMAL
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}