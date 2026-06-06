# LS-DYNA R13 *CONTROL_TERMINATION
# Category: control
# Entity type: cards (global control card)
# Card image: Termin (verified HyperMesh mapping)
# Parameters: ENDTIM(float), ENDCYC(int), DTMIN(float), ENDENG(float), ENDMAS(float)
# HyperMesh datanames: LSD_ENDTIM, LSD_ENDCYCLE, LSD_TSMIN, LSD_TERMRAT, LSD_PERMASS

*createentity cards name="CONTROL_TERMINATION" cardimage=Termin
*createmark cards 1 "by name" "CONTROL_TERMINATION"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create CONTROL_TERMINATION" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_ENDTIM value={{ENDTIM}}
*setvalue cards id=$_card_id dataname=LSD_ENDCYCLE value={{ENDCYC}}
*setvalue cards id=$_card_id dataname=LSD_TSMIN value={{DTMIN}}
*setvalue cards id=$_card_id dataname=LSD_TERMRAT value={{ENDENG}}
*setvalue cards id=$_card_id dataname=LSD_PERMASS value={{ENDMAS}}
puts "HM_KEYWORD_CREATED keyword=CONTROL_TERMINATION entity=cards id=$_card_id cardimage=Termin"
