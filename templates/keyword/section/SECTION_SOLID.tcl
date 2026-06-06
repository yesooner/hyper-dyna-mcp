# LS-DYNA R13 *SECTION_SOLID
# Category: section
# Entity type: props
# Card image: SectSld (verified HyperMesh mapping)
# Parameters: SECID(int), ELFORM(int), AET(int)
# Note: ELFORM/AET may not be directly settable via dataname in HyperMesh

*createentity props name="SECTION_SOLID_{{SECID}}" cardimage=SectSld
*createmark props 1 "by name" "SECTION_SOLID_{{SECID}}"
set _prop_ids [hm_getmark props 1]
set _prop_id [lindex $_prop_ids end]
if {$_prop_id eq ""} { error "Failed to create SECTION_SOLID" }
*setvalue props id=$_prop_id STATUS=2
puts "HM_KEYWORD_CREATED keyword=SECTION_SOLID entity=props id=$_prop_id cardimage=SectSld"
