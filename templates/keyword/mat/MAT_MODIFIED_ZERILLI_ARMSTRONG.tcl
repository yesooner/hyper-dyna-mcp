# LS-DYNA R13 *MAT_MODIFIED_ZERILLI_ARMSTRONG (*MAT_065)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_MODIFIED_ZERILLI_ARMSTRONG_{{MID}}" cardimage=MAT_MODIFIED_ZERILLI_ARMSTRONG
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}