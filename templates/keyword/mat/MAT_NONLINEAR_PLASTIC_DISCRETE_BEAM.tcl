# LS-DYNA R13 *MAT_NONLINEAR_PLASTIC_DISCRETE_BEAM (*MAT_068)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_NONLINEAR_PLASTIC_DISCRETE_BEAM_{{MID}}" cardimage=MAT_NONLINEAR_PLASTIC_DISCRETE_BEAM
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}