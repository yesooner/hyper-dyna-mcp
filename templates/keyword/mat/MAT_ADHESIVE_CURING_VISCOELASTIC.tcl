# LS-DYNA R13 *MAT_ADHESIVE_CURING_VISCOELASTIC (*MAT_277)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_ADHESIVE_CURING_VISCOELASTIC_{{MID}}" cardimage=MAT_ADHESIVE_CURING_VISCOELASTIC
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}