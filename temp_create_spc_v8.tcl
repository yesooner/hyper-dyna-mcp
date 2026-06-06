# Try creating SPC using the hm_model_writer approach

# First, activate LS-DYNA template
set template_path {E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key}
*templatefileset $template_path
puts "Template activated: [hm_info templatetype]"

# Create SPC load collector using *createentity with cardimage
*createentity loadcols name=FIX_BASE cardimage=BOUNDARY_SPC
puts "Created FIX_BASE load collector with BOUNDARY_SPC card image"

# Set status
*setvalue loadcols name=FIX_BASE STATUS=2
puts "Set STATUS=2"

# Set SPC parameters
*setvalue loadcols name=FIX_BASE dataname=NODEID value=611
*setvalue loadcols name=FIX_BASE dataname=CID value=0
*setvalue loadcols name=FIX_BASE dataname=DOFX value=1
*setvalue loadcols name=FIX_BASE dataname=DOFY value=1
*setvalue loadcols name=FIX_BASE dataname=DOFZ value=1
*setvalue loadcols name=FIX_BASE dataname=DOFRX value=1
*setvalue loadcols name=FIX_BASE dataname=DOFRY value=1
*setvalue loadcols name=FIX_BASE dataname=DOFRZ value=1
puts "Set SPC parameters for node 611"

# Check loads
*createmark loads 1 "all"
set load_count [llength [hm_getmark loads 1]]
puts "Total loads: $load_count"

# If no loads, try using *setvalue with different parameters
if {$load_count == 0} {
    puts "=== TRYING DIFFERENT SETVALUE ==="
    *setvalue loadcols name=FIX_BASE dataname=NODEID value=611
    *setvalue loadcols name=FIX_BASE dataname=CID value=0
    *setvalue loadcols name=FIX_BASE dataname=DOFX value=1
    *setvalue loadcols name=FIX_BASE dataname=DOFY value=1
    *setvalue loadcols name=FIX_BASE dataname=DOFZ value=1
    *setvalue loadcols name=FIX_BASE dataname=DOFRX value=1
    *setvalue loadcols name=FIX_BASE dataname=DOFRY value=1
    *setvalue loadcols name=FIX_BASE dataname=DOFRZ value=1
    puts "Tried again"

    *createmark loads 1 "all"
    set load_count [llength [hm_getmark loads 1]]
    puts "Total loads after retry: $load_count"
}

# Check load collectors
puts "=== LOAD COLLECTORS ==="
*createmark loadcols 1 "all"
foreach lid [hm_getmark loadcols 1] {
    set lname [hm_getcollectorname loadcols $lid]
    puts "  LC_$lid = $lname"
}
