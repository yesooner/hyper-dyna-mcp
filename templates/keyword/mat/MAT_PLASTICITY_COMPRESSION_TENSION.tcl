# LS-DYNA R13 *MAT_PLASTICITY_COMPRESSION_TENSION (*MAT_124)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_PLASTICITY_COMPRESSION_TENSION_{{MID}}" cardimage=MAT_PLASTICITY_COMPRESSION_TENSION
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}