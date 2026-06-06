# LS-DYNA R13 *MAT_PLASTIC_KINEMATIC
# Category: mat
# Parameters: MID, RHO, E, PR, SIGY, ETAN, BETA

*createentity mats name="MAT_PLASTIC_KINEMATIC_{{MID}}" cardimage=MAT_PLASTIC_KINEMATIC
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}
*setvalue mats id={{MID}} dataname=SIGY value={{SIGY}}
*setvalue mats id={{MID}} dataname=ETAN value={{ETAN}}
*setvalue mats id={{MID}} dataname=BETA value={{BETA}}