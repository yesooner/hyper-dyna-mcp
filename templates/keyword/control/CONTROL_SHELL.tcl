# LS-DYNA R13 *CONTROL_SHELL
# Category: control
# Entity type: cards (global control card)
# Card image: Shell (HyperMesh mapping)
# Parameters: WRCOMP(int), ISTUPD(int), FAILURE(int), PSHELL(int), MITER(int), PROJ(int)

*createentity cards name="CONTROL_SHELL" cardimage=Shell
*createmark cards 1 "by name" "CONTROL_SHELL"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create CONTROL_SHELL" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_WRCOMP value={{WRCOMP}}
*setvalue cards id=$_card_id dataname=LSD_ISTUPD value={{ISTUPD}}
*setvalue cards id=$_card_id dataname=LSD_FAILURE value={{FAILURE}}
*setvalue cards id=$_card_id dataname=LSD_PSHELL value={{PSHELL}}
*setvalue cards id=$_card_id dataname=LSD_MITER value={{MITER}}
*setvalue cards id=$_card_id dataname=LSD_PROJ value={{PROJ}}
puts "HM_KEYWORD_CREATED keyword=CONTROL_SHELL entity=cards id=$_card_id cardimage=Shell"
