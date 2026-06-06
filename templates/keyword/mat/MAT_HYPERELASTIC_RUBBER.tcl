# LS-DYNA R13 *MAT_HYPERELASTIC_RUBBER (*MAT_077_H)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_HYPERELASTIC_RUBBER_{{MID}}" cardimage=MAT_HYPERELASTIC_RUBBER
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}