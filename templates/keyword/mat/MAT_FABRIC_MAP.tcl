# LS-DYNA R13 *MAT_FABRIC_MAP (*MAT_034M)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_FABRIC_MAP_{{MID}}" cardimage=MAT_FABRIC_MAP
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}