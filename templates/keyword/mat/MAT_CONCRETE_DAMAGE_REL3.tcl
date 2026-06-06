# LS-DYNA R13 *MAT_CONCRETE_DAMAGE_REL3 (*MAT_072R3)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_CONCRETE_DAMAGE_REL3_{{MID}}" cardimage=MAT_CONCRETE_DAMAGE_REL3
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}