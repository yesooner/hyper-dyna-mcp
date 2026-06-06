# LS-DYNA R13 *MAT_THERMO_ELASTO_VISCOPLASTIC_CREEP (*MAT_188)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_THERMO_ELASTO_VISCOPLASTIC_CREEP_{{MID}}" cardimage=MAT_THERMO_ELASTO_VISCOPLASTIC_CREEP
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}