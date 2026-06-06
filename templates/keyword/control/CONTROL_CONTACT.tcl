# LS-DYNA R13 *CONTROL_CONTACT
# Category: control
# Entity type: cards (global control card)
# Card image: Contact (HyperMesh mapping)
# Parameters: SLSFAC(float), RWPNAL(float), ISLCHK(int), SHLTHK(int), SNLOG(int), ISLDT(int), IRTH(int), IGAP(int), PENOPT(int)

*createentity cards name="CONTROL_CONTACT" cardimage=Contact
*createmark cards 1 "by name" "CONTROL_CONTACT"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create CONTROL_CONTACT" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_SLSFAC value={{SLSFAC}}
*setvalue cards id=$_card_id dataname=LSD_RWPNAL value={{RWPNAL}}
*setvalue cards id=$_card_id dataname=LSD_ISLCHK value={{ISLCHK}}
*setvalue cards id=$_card_id dataname=LSD_SHLTHK value={{SHLTHK}}
*setvalue cards id=$_card_id dataname=LSD_SNLOG value={{SNLOG}}
*setvalue cards id=$_card_id dataname=LSD_ISLDT value={{ISLDT}}
*setvalue cards id=$_card_id dataname=LSD_IRTH value={{IRTH}}
*setvalue cards id=$_card_id dataname=LSD_IGAP value={{IGAP}}
*setvalue cards id=$_card_id dataname=LSD_PENOPT value={{PENOPT}}
puts "HM_KEYWORD_CREATED keyword=CONTROL_CONTACT entity=cards id=$_card_id cardimage=Contact"
