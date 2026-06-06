# LS-DYNA R13 *MAT_PML_ELASTIC_FLUID (*MAT_230_FLUID)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_PML_ELASTIC_FLUID_{{MID}}" cardimage=MAT_PML_ELASTIC_FLUID
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}