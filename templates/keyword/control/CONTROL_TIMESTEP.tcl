# LS-DYNA R13 *CONTROL_TIMESTEP
# Category: control
# Entity type: cards (global control card)
# Card image: Timestep (HyperMesh mapping)
# Parameters: DTINIT(float), TSSFAC(int), ISDO(int), TSLIMT(float), DT2MS(float), LCTM(int), ERODE(int), MS1ST(int)

*createentity cards name="CONTROL_TIMESTEP" cardimage=Timestep
*createmark cards 1 "by name" "CONTROL_TIMESTEP"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create CONTROL_TIMESTEP" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_DTINIT value={{DTINIT}}
*setvalue cards id=$_card_id dataname=LSD_TSSFAC value={{TSSFAC}}
*setvalue cards id=$_card_id dataname=LSD_ISDO value={{ISDO}}
*setvalue cards id=$_card_id dataname=LSD_TSLIMT value={{TSLIMT}}
*setvalue cards id=$_card_id dataname=LSD_DT2MS value={{DT2MS}}
*setvalue cards id=$_card_id dataname=LSD_LCTM value={{LCTM}}
*setvalue cards id=$_card_id dataname=LSD_ERODE value={{ERODE}}
*setvalue cards id=$_card_id dataname=LSD_MS1ST value={{MS1ST}}
puts "HM_KEYWORD_CREATED keyword=CONTROL_TIMESTEP entity=cards id=$_card_id cardimage=Timestep"
