# LS-DYNA R13 *MAT_JOHNSON_COOK
# Category: mat
# Entity type: mats
# Card image: MATL15 (verified HyperMesh mapping)
# Parameters: MID(int), RHO(float), G(float), E(float), PR(float), A(float), B(float), N(float)

*createentity mats name="MAT_JOHNSON_COOK_{{MID}}" cardimage=MATL15
*createmark mats 1 "by name" "MAT_JOHNSON_COOK_{{MID}}"
set _mat_ids [hm_getmark mats 1]
set _mat_id [lindex $_mat_ids end]
if {$_mat_id eq ""} { error "Failed to create MAT_JOHNSON_COOK" }
*setvalue mats id=$_mat_id STATUS=2
*setvalue mats id=$_mat_id Rho={{RHO}}
*setvalue mats id=$_mat_id G={{G}}
*setvalue mats id=$_mat_id E={{E}}
*setvalue mats id=$_mat_id Nu={{PR}}
*setvalue mats id=$_mat_id A={{A}}
*setvalue mats id=$_mat_id B={{B}}
*setvalue mats id=$_mat_id N={{N}}
puts "HM_KEYWORD_CREATED keyword=MAT_JOHNSON_COOK entity=mats id=$_mat_id cardimage=MATL15"
