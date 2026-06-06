# LS-DYNA R13 *MAT_JOHNSON_COOK
# Category: mat
# Parameters: MID, RHO, G, E, PR, A, B, N

*createentity mats name="MAT_JOHNSON_COOK_{{MID}}" cardimage=MAT_JOHNSON_COOK
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=G value={{G}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}
*setvalue mats id={{MID}} dataname=A value={{A}}
*setvalue mats id={{MID}} dataname=B value={{B}}
*setvalue mats id={{MID}} dataname=N value={{N}}