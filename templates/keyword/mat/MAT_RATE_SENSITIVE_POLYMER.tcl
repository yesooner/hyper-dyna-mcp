# LS-DYNA R13 *MAT_RATE_SENSITIVE_POLYMER (*MAT_141)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_RATE_SENSITIVE_POLYMER_{{MID}}" cardimage=MAT_RATE_SENSITIVE_POLYMER
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}