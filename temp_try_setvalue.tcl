# Try using *setvalue on loadcols to create SPC

# First, activate LS-DYNA template
set template_path {E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key}
*templatefileset $template_path
puts "Template activated: [hm_info templatetype]"

# Create SPC load collector using *createentity with cardimage=BOUNDARY_SPC
catch {*createentity loadcols name=FIX_BASE cardimage=BOUNDARY_SPC} err
puts "Create result: $err"

# Set status
catch {*setvalue loadcols name=FIX_BASE STATUS=2} err
puts "Status result: $err"

# Set SPC parameters for node 611
catch {*setvalue loadcols name=FIX_BASE dataname=NODEID value=611} err
puts "NODEID result: $err"

catch {*setvalue loadcols name=FIX_BASE dataname=CID value=0} err
puts "CID result: $err"

catch {*setvalue loadcols name=FIX_BASE dataname=DOFX value=1} err
puts "DOFX result: $err"

catch {*setvalue loadcols name=FIX_BASE dataname=DOFY value=1} err
puts "DOFY result: $err"

catch {*setvalue loadcols name=FIX_BASE dataname=DOFZ value=1} err
puts "DOFZ result: $err"

catch {*setvalue loadcols name=FIX_BASE dataname=DOFRX value=1} err
puts "DOFRX result: $err"

catch {*setvalue loadcols name=FIX_BASE dataname=DOFRY value=1} err
puts "DOFRY result: $err"

catch {*setvalue loadcols name=FIX_BASE dataname=DOFRZ value=1} err
puts "DOFRZ result: $err"

# Check loads
*createmark loads 1 "all"
set load_count [llength [hm_getmark loads 1]]
puts "Total loads: $load_count"
