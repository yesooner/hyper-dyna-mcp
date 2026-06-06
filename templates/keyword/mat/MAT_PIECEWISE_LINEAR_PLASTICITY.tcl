# LS-DYNA R13 *MAT_PIECEWISE_LINEAR_PLASTICITY
# Category: mat
# Parameters: MID, RHO, E, PR, SIGY, ETAN, FAIL, TDEL

*createentity mats name="MAT_PIECEWISE_LINEAR_PLASTICITY_{{MID}}" cardimage=MAT_PIECEWISE_LINEAR_PLASTICITY
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}
*setvalue mats id={{MID}} dataname=SIGY value={{SIGY}}
*setvalue mats id={{MID}} dataname=ETAN value={{ETAN}}
*setvalue mats id={{MID}} dataname=FAIL value={{FAIL}}
*setvalue mats id={{MID}} dataname=TDEL value={{TDEL}}