# LS-DYNA R13 *MAT_RIGID
# Category: mat
# Entity type: mats
# Card image: MATL20 (verified HyperMesh mapping)
# Parameters: MID(int), RHO(float), E(float), PR(float), N(int), COUPLE(int), M(int), TLOG(int)

*createentity mats name="MAT_RIGID_{{MID}}" cardimage=MATL20
*createmark mats 1 "by name" "MAT_RIGID_{{MID}}"
set _mat_ids [hm_getmark mats 1]
set _mat_id [lindex $_mat_ids end]
if {$_mat_id eq ""} { error "Failed to create MAT_RIGID" }
*setvalue mats id=$_mat_id STATUS=2
*setvalue mats id=$_mat_id Rho={{RHO}}
*setvalue mats id=$_mat_id E={{E}}
*setvalue mats id=$_mat_id Nu={{PR}}
*setvalue mats id=$_mat_id N={{N}}
*setvalue mats id=$_mat_id COUPLE={{COUPLE}}
*setvalue mats id=$_mat_id M={{M}}
*setvalue mats id=$_mat_id TLOG={{TLOG}}
puts "HM_KEYWORD_CREATED keyword=MAT_RIGID entity=mats id=$_mat_id cardimage=MATL20"
