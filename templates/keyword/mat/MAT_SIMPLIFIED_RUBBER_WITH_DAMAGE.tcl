# LS-DYNA R13 *MAT_SIMPLIFIED_RUBBER_WITH_DAMAGE (*MAT_183)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_SIMPLIFIED_RUBBER_WITH_DAMAGE_{{MID}}" cardimage=MAT_SIMPLIFIED_RUBBER_WITH_DAMAGE
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}