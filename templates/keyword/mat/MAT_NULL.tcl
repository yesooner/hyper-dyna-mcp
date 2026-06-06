# LS-DYNA R13 *MAT_NULL
# Category: mat
# Entity type: mats
# Card image: MATL9 (verified HyperMesh mapping)
# Parameters: MID(int), RHO(float), E(float), PR(float)

*createentity mats name="MAT_NULL_{{MID}}" cardimage=MATL9
*createmark mats 1 "by name" "MAT_NULL_{{MID}}"
set _mat_ids [hm_getmark mats 1]
set _mat_id [lindex $_mat_ids end]
if {$_mat_id eq ""} { error "Failed to create MAT_NULL" }
*setvalue mats id=$_mat_id STATUS=2
*setvalue mats id=$_mat_id Rho={{RHO}}
*setvalue mats id=$_mat_id E={{E}}
*setvalue mats id=$_mat_id Nu={{PR}}
puts "HM_KEYWORD_CREATED keyword=MAT_NULL entity=mats id=$_mat_id cardimage=MATL9"
