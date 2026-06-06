# LS-DYNA R13 *MAT_GEPLASTIC_SRATE_2000a (*MAT_101)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_GEPLASTIC_SRATE_2000a_{{MID}}" cardimage=MAT_GEPLASTIC_SRATE_2000a
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}