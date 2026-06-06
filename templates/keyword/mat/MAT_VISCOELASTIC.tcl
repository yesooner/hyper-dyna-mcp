# LS-DYNA R13 *MAT_VISCOELASTIC
# Category: mat
# Parameters: MID, RHO, G0, GI, BETA, PR

*createentity mats name="MAT_VISCOELASTIC_{{MID}}" cardimage=MAT_VISCOELASTIC
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=G0 value={{G0}}
*setvalue mats id={{MID}} dataname=GI value={{GI}}
*setvalue mats id={{MID}} dataname=BETA value={{BETA}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}