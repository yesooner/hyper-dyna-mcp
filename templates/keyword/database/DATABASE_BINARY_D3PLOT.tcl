# LS-DYNA R13 *DATABASE_BINARY_D3PLOT
# Category: database
# Entity type: cards (global database card)
# Card image: DBplot (verified HyperMesh mapping)
# Parameters: DT(float), LCDT(int), BEAM(int), NPLTC(int)
# HyperMesh datanames: LSD_DT, LSD_LCID, LSD_NOBEAM, LSD_NPLTC

*createentity cards name="DATABASE_BINARY_D3PLOT" cardimage=DBplot
*createmark cards 1 "by name" "DATABASE_BINARY_D3PLOT"
set _card_ids [hm_getmark cards 1]
set _card_id [lindex $_card_ids end]
if {$_card_id eq ""} { error "Failed to create DATABASE_BINARY_D3PLOT" }
*setvalue cards id=$_card_id STATUS=2
*setvalue cards id=$_card_id dataname=LSD_DT value={{DT}}
*setvalue cards id=$_card_id dataname=LSD_LCID value={{LCDT}}
*setvalue cards id=$_card_id dataname=LSD_NOBEAM value={{BEAM}}
*setvalue cards id=$_card_id dataname=LSD_NPLTC value={{NPLTC}}
puts "HM_KEYWORD_CREATED keyword=DATABASE_BINARY_D3PLOT entity=cards id=$_card_id cardimage=DBplot"
