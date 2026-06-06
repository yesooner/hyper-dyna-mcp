# LS-DYNA R13 *MAT_VISCOPLASTIC_MIXED_HARDENING (*MAT_225)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_VISCOPLASTIC_MIXED_HARDENING_{{MID}}" cardimage=MAT_VISCOPLASTIC_MIXED_HARDENING
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}