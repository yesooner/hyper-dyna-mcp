# LS-DYNA R13 *MAT_HIGH_EXPLOSIVE_BURN
# Category: mat
# Entity type: mats
# Card image: MATL8 (verified HyperMesh mapping)
# Parameters: MID(int), RHO(float), D(float), PCJ(float), BETA(float), K(float), G(float), SIGY(float)

*createentity mats name="MAT_HIGH_EXPLOSIVE_BURN_{{MID}}" cardimage=MATL8
*createmark mats 1 "by name" "MAT_HIGH_EXPLOSIVE_BURN_{{MID}}"
set _mat_ids [hm_getmark mats 1]
set _mat_id [lindex $_mat_ids end]
if {$_mat_id eq ""} { error "Failed to create MAT_HIGH_EXPLOSIVE_BURN" }
*setvalue mats id=$_mat_id STATUS=2
*setvalue mats id=$_mat_id Rho={{RHO}}
*setvalue mats id=$_mat_id D={{D}}
*setvalue mats id=$_mat_id PCJ={{PCJ}}
*setvalue mats id=$_mat_id BETA={{BETA}}
*setvalue mats id=$_mat_id K={{K}}
*setvalue mats id=$_mat_id G={{G}}
*setvalue mats id=$_mat_id SIGY={{SIGY}}
puts "HM_KEYWORD_CREATED keyword=MAT_HIGH_EXPLOSIVE_BURN entity=mats id=$_mat_id cardimage=MATL8"
