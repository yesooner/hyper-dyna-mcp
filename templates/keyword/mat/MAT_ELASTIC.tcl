# LS-DYNA R13 *MAT_ELASTIC
# Category: mat
# Parameters: MID, RHO, E, PR, DA, DB

*createentity mats name="MAT_ELASTIC_{{MID}}" cardimage=MAT_ELASTIC
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}
*setvalue mats id={{MID}} dataname=DA value={{DA}}
*setvalue mats id={{MID}} dataname=DB value={{DB}}