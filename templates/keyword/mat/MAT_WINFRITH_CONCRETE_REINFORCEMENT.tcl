# LS-DYNA R13 *MAT_WINFRITH_CONCRETE_REINFORCEMENT (*MAT_084_REINF)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_WINFRITH_CONCRETE_REINFORCEMENT_{{MID}}" cardimage=MAT_WINFRITH_CONCRETE_REINFORCEMENT
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}