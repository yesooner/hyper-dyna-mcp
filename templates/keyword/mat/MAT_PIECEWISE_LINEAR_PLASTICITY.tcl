# LS-DYNA R13 *MAT_PIECEWISE_LINEAR_PLASTICITY
# Category: mat
# Entity type: mats
# Card image: MATL24 (verified HyperMesh mapping)
# Parameters: MID(int), RHO(float), E(float), PR(float), SIGY(float), ETAN(float), FAIL(float), TDEL(float)

*createentity mats name="MAT_PIECEWISE_LINEAR_PLASTICITY_{{MID}}" cardimage=MATL24
*createmark mats 1 "by name" "MAT_PIECEWISE_LINEAR_PLASTICITY_{{MID}}"
set _mat_ids [hm_getmark mats 1]
set _mat_id [lindex $_mat_ids end]
if {$_mat_id eq ""} { error "Failed to create MAT_PIECEWISE_LINEAR_PLASTICITY" }
*setvalue mats id=$_mat_id STATUS=2
*setvalue mats id=$_mat_id Rho={{RHO}}
*setvalue mats id=$_mat_id E={{E}}
*setvalue mats id=$_mat_id Nu={{PR}}
*setvalue mats id=$_mat_id SIGY={{SIGY}}
*setvalue mats id=$_mat_id ETAN={{ETAN}}
*setvalue mats id=$_mat_id FAIL={{FAIL}}
*setvalue mats id=$_mat_id TDEL={{TDEL}}
puts "HM_KEYWORD_CREATED keyword=MAT_PIECEWISE_LINEAR_PLASTICITY entity=mats id=$_mat_id cardimage=MATL24"
