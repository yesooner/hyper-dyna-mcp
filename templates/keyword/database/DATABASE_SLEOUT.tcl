# LS-DYNA R13 *DATABASE_SLEOUT
# Category: database
# Entity type: cards (global database card)
# Card image: DBsleo (HyperMesh mapping)
# Parameters: DT(float)

*createentity cards name="DATABASE_SLEOUT" cardimage=DBsleo
*createmark cards 1 "by name" "DATABASE_SLEOUT"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create DATABASE_SLEOUT" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_DT value={{DT}}
puts "HM_KEYWORD_CREATED keyword=DATABASE_SLEOUT entity=cards id=$_card_id cardimage=DBsleo"
