# LS-DYNA R13 *DATABASE_JNTFORC
# Category: database
# Entity type: cards (global database card)
# Card image: DBjntf (HyperMesh mapping)
# Parameters: DT(float)

*createentity cards name="DATABASE_JNTFORC" cardimage=DBjntf
*createmark cards 1 "by name" "DATABASE_JNTFORC"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create DATABASE_JNTFORC" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_DT value={{DT}}
puts "HM_KEYWORD_CREATED keyword=DATABASE_JNTFORC entity=cards id=$_card_id cardimage=DBjntf"
