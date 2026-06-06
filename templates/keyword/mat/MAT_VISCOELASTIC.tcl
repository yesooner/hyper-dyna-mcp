# LS-DYNA R13 *MAT_VISCOELASTIC
# Category: mat
# Entity type: mats
# Card image: MATL6 (verified HyperMesh mapping)
# Parameters: MID(int), RHO(float), G0(float), GI(float), BETA(float), PR(float)

*createentity mats name="MAT_VISCOELASTIC_{{MID}}" cardimage=MATL6
*createmark mats 1 "by name" "MAT_VISCOELASTIC_{{MID}}"
set _mat_ids [hm_getmark mats 1]
set _mat_id [lindex $_mat_ids end]
if {$_mat_id eq ""} { error "Failed to create MAT_VISCOELASTIC" }
*setvalue mats id=$_mat_id STATUS=2
*setvalue mats id=$_mat_id Rho={{RHO}}
*setvalue mats id=$_mat_id G0={{G0}}
*setvalue mats id=$_mat_id GI={{GI}}
*setvalue mats id=$_mat_id BETA={{BETA}}
*setvalue mats id=$_mat_id Nu={{PR}}
puts "HM_KEYWORD_CREATED keyword=MAT_VISCOELASTIC entity=mats id=$_mat_id cardimage=MATL6"
