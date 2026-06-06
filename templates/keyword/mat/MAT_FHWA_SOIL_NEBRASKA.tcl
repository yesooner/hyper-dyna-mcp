# LS-DYNA R13 *MAT_FHWA_SOIL_NEBRASKA (*MAT_147_N)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_FHWA_SOIL_NEBRASKA_{{MID}}" cardimage=MAT_FHWA_SOIL_NEBRASKA
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}