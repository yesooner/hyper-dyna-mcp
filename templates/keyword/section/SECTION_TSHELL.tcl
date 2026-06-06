# LS-DYNA R13 *SECTION_TSHELL
# Category: section
# Entity type: props
# Card image: SectTSh (verified HyperMesh mapping)
# Parameters: SECID(int), ELFORM(int), SHRF(float), NIP(int)

*createentity props name="SECTION_TSHELL_{{SECID}}" cardimage=SectTSh
*createmark props 1 "by name" "SECTION_TSHELL_{{SECID}}"
set _prop_ids [hm_getmark props 1]
set _prop_id [lindex $_prop_ids end]
if {$_prop_id eq ""} { error "Failed to create SECTION_TSHELL" }
*setvalue props id=$_prop_id STATUS=2
*setvalue props id=$_prop_id ELFORM={{ELFORM}}
*setvalue props id=$_prop_id SHRF={{SHRF}}
*setvalue props id=$_prop_id NIP={{NIP}}
puts "HM_KEYWORD_CREATED keyword=SECTION_TSHELL entity=props id=$_prop_id cardimage=SectTSh"
