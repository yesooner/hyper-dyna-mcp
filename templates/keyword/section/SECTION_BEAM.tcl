# LS-DYNA R13 *SECTION_BEAM
# Category: section
# Entity type: props
# Card image: SectBm (verified HyperMesh mapping)
# Parameters: SECID(int), ELFORM(int)

*createentity props name="SECTION_BEAM_{{SECID}}" cardimage=SectBm
*createmark props 1 "by name" "SECTION_BEAM_{{SECID}}"
set _prop_ids [hm_getmark props 1]
set _prop_id [lindex $_prop_ids end]
if {$_prop_id eq ""} { error "Failed to create SECTION_BEAM" }
*setvalue props id=$_prop_id STATUS=2
*setvalue props id=$_prop_id ELFORM={{ELFORM}}
puts "HM_KEYWORD_CREATED keyword=SECTION_BEAM entity=props id=$_prop_id cardimage=SectBm"
