# LS-DYNA R13 *MAT_ELASTIC
# Category: mat
# Entity type: mats
# Card image: MATL1 (verified HyperMesh mapping)
# Parameters: MID(int), RHO(float), E(float), PR(float), DA(float), DB(float)
# Note: HyperMesh uses Rho/E/Nu internally; DA,DB not exposed in basic mode

*createentity mats name="MAT_ELASTIC_{{MID}}" cardimage=MATL1
*createmark mats 1 "by name" "MAT_ELASTIC_{{MID}}"
set _mat_ids [hm_getmark mats 1]
set _mat_id [lindex $_mat_ids end]
if {$_mat_id eq ""} { error "Failed to create MAT_ELASTIC" }
*setvalue mats id=$_mat_id STATUS=2
*setvalue mats id=$_mat_id Rho={{RHO}}
*setvalue mats id=$_mat_id E={{E}}
*setvalue mats id=$_mat_id Nu={{PR}}
puts "HM_KEYWORD_CREATED keyword=MAT_ELASTIC entity=mats id=$_mat_id cardimage=MATL1"
