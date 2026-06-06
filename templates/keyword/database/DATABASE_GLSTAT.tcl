# LS-DYNA R13 *DATABASE_GLSTAT
# Category: database
# Entity type: cards (global database card)
# Card image: DBglst (HyperMesh mapping)
# Parameters: DT(float)

*createentity cards name="DATABASE_GLSTAT" cardimage=DBglst
*createmark cards 1 "by name" "DATABASE_GLSTAT"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create DATABASE_GLSTAT" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_DT value={{DT}}
puts "HM_KEYWORD_CREATED keyword=DATABASE_GLSTAT entity=cards id=$_card_id cardimage=DBglst"
