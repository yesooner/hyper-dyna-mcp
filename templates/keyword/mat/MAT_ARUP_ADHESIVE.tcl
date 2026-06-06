# LS-DYNA R13 *MAT_ARUP_ADHESIVE (*MAT_169)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_ARUP_ADHESIVE_{{MID}}" cardimage=MAT_ARUP_ADHESIVE
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}