# LS-DYNA R13 *DATABASE_MATSUM
# Category: database
# Entity type: cards (global database card)
# Card image: DBmats (HyperMesh mapping)
# Parameters: DT(float)

*createentity cards name="DATABASE_MATSUM" cardimage=DBmats
*createmark cards 1 "by name" "DATABASE_MATSUM"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create DATABASE_MATSUM" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_DT value={{DT}}
puts "HM_KEYWORD_CREATED keyword=DATABASE_MATSUM entity=cards id=$_card_id cardimage=DBmats"
