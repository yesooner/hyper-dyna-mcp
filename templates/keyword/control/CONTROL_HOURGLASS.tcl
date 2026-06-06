# LS-DYNA R13 *CONTROL_HOURGLASS
# Category: control
# Entity type: cards (global control card)
# Card image: Hourglass (HyperMesh mapping)
# Parameters: IHQ(int), QH(float)

*createentity cards name="CONTROL_HOURGLASS" cardimage=Hourglass
*createmark cards 1 "by name" "CONTROL_HOURGLASS"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create CONTROL_HOURGLASS" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_IHQ value={{IHQ}}
*setvalue cards id=$_card_id dataname=LSD_QH value={{QH}}
puts "HM_KEYWORD_CREATED keyword=CONTROL_HOURGLASS entity=cards id=$_card_id cardimage=Hourglass"
