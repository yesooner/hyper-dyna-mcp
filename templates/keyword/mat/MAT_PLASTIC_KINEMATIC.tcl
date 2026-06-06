# LS-DYNA R13 *MAT_PLASTIC_KINEMATIC
# Category: mat
# Entity type: mats
# Card image: MATL3 (verified HyperMesh mapping)
# Parameters: MID(int), RHO(float), E(float), PR(float), SIGY(float), ETAN(float), BETA(float)

*createentity mats name="MAT_PLASTIC_KINEMATIC_{{MID}}" cardimage=MATL3
*createmark mats 1 "by name" "MAT_PLASTIC_KINEMATIC_{{MID}}"
set _mat_ids [hm_getmark mats 1]
set _mat_id [lindex $_mat_ids end]
if {$_mat_id eq ""} { error "Failed to create MAT_PLASTIC_KINEMATIC" }
*setvalue mats id=$_mat_id STATUS=2
*setvalue mats id=$_mat_id Rho={{RHO}}
*setvalue mats id=$_mat_id E={{E}}
*setvalue mats id=$_mat_id Nu={{PR}}
*setvalue mats id=$_mat_id SIGY={{SIGY}}
*setvalue mats id=$_mat_id ETAN={{ETAN}}
*setvalue mats id=$_mat_id BETA={{BETA}}
puts "HM_KEYWORD_CREATED keyword=MAT_PLASTIC_KINEMATIC entity=mats id=$_mat_id cardimage=MATL3"
