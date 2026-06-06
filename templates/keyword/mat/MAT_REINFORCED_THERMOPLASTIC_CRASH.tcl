# LS-DYNA R13 *MAT_REINFORCED_THERMOPLASTIC_CRASH (*MAT_249_CRASH)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_REINFORCED_THERMOPLASTIC_CRASH_{{MID}}" cardimage=MAT_REINFORCED_THERMOPLASTIC_CRASH
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}