# LS-DYNA R13 *MAT_HIGH_EXPLOSIVE_BURN
# Category: mat
# Parameters: MID, RHO, D, PCJ, BETA, K, G, SIGY

*createentity mats name="MAT_HIGH_EXPLOSIVE_BURN_{{MID}}" cardimage=MAT_HIGH_EXPLOSIVE_BURN
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=D value={{D}}
*setvalue mats id={{MID}} dataname=PCJ value={{PCJ}}
*setvalue mats id={{MID}} dataname=BETA value={{BETA}}
*setvalue mats id={{MID}} dataname=K value={{K}}
*setvalue mats id={{MID}} dataname=G value={{G}}
*setvalue mats id={{MID}} dataname=SIGY value={{SIGY}}