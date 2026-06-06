# LS-DYNA R13 *MAT_NULL
# Category: mat
# Parameters: MID, RHO, E, PR

*createentity mats name="MAT_NULL_{{MID}}" cardimage=MAT_NULL
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}