# LS-DYNA R13 *MAT_PITZER_CRUSHABLE_FOAM (*MAT_144)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_PITZER_CRUSHABLE_FOAM_{{MID}}" cardimage=MAT_PITZER_CRUSHABLE_FOAM
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}