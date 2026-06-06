# LS-DYNA R13 *MAT_DISCRETE_BEAM_POINT_CONTACT (*MAT_205)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_DISCRETE_BEAM_POINT_CONTACT_{{MID}}" cardimage=MAT_DISCRETE_BEAM_POINT_CONTACT
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}