# LS-DYNA R13 *CONTROL_ACCURACY
# Category: control
# Entity type: cards (global control card)
# Card image: Accuracy (HyperMesh mapping)
# Parameters: OSU(int), INU(int), PIDs(int), IRATE(int)

*createentity cards name="CONTROL_ACCURACY" cardimage=Accuracy
*createmark cards 1 "by name" "CONTROL_ACCURACY"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create CONTROL_ACCURACY" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_OSU value={{OSU}}
*setvalue cards id=$_card_id dataname=LSD_INU value={{INU}}
*setvalue cards id=$_card_id dataname=LSD_PIDs value={{PIDs}}
*setvalue cards id=$_card_id dataname=LSD_IRATE value={{IRATE}}
puts "HM_KEYWORD_CREATED keyword=CONTROL_ACCURACY entity=cards id=$_card_id cardimage=Accuracy"
