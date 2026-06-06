# LS-DYNA R13 *MAT_OPTIONTROPIC_ELASTIC_PHASE_CHANGE (*MAT_217)
# Category: mat
# Parameters: MID, RHO, E, PR
# Note: Generic template - may need additional fields for specific material models

*createentity mats name="MAT_OPTIONTROPIC_ELASTIC_PHASE_CHANGE_{{MID}}" cardimage=MAT_OPTIONTROPIC_ELASTIC_PHASE_CHANGE
*setvalue mats id={{MID}} STATUS=2
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}