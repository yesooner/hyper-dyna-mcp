# LS-DYNA R13 *MAT_BRAIN_LINEAR_VISCOELASTIC (*MAT_164)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_BRAIN_LINEAR_VISCOELASTIC_{{MID}}" cardimage=MAT_BRAIN_LINEAR_VISCOELASTIC
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}