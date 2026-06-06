# LS-DYNA R13 *MAT_JOHNSON_HOLMQUIST_JH1 (*MAT_241)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_JOHNSON_HOLMQUIST_JH1_{{MID}}" cardimage=MAT_JOHNSON_HOLMQUIST_JH1
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}