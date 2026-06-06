# LS-DYNA R13 *CONTROL_ENERGY
# Category: control
# Entity type: cards (global control card)
# Card image: Energy (HyperMesh mapping)
# Parameters: HGEN(int), RWEN(int), SLNTEN(int), RYLEN(int)

*createentity cards name="CONTROL_ENERGY" cardimage=Energy
*createmark cards 1 "by name" "CONTROL_ENERGY"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create CONTROL_ENERGY" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_HGEN value={{HGEN}}
*setvalue cards id=$_card_id dataname=LSD_RWEN value={{RWEN}}
*setvalue cards id=$_card_id dataname=LSD_SLNTEN value={{SLNTEN}}
*setvalue cards id=$_card_id dataname=LSD_RYLEN value={{RYLEN}}
puts "HM_KEYWORD_CREATED keyword=CONTROL_ENERGY entity=cards id=$_card_id cardimage=Energy"
