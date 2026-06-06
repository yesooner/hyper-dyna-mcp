# Try creating SPC with *loadcreate after template activation

# First, activate LS-DYNA template
set template_path {E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key}
*templatefileset $template_path
puts "Template activated: [hm_info templatetype]"

# Create SPC load collector
*createentity loadcols cardimage=SPC name=FIX_BASE
puts "Created FIX_BASE load collector"

# Set as current collector
*currentcollector loadcols "FIX_BASE"
puts "Current load collector: [hm_info currentcollector loadcols]"

# Select base nodes (Z=0)
*createmark nodes 1 "by box" 7200 720 -10 9540 3060 10 0 inside 0 0 0
set base_nodes [hm_getmark nodes 1]
set node_count [llength $base_nodes]
puts "Base nodes found: $node_count"

# Try *loadcreate with correct syntax
# Format: *loadcreate <type> <node_id> <sys_id> <dof_x> <dof_y> <dof_z> <dof_rx> <dof_ry> <dof_rz>
set count 0
foreach nid $base_nodes {
    *loadcreate 0 $nid 0 1 1 1 1 1 1
    incr count
    if {$count >= 10} break
}
puts "Tried *loadcreate on $count nodes"

# Check loads
*createmark loads 1 "all"
set load_count [llength [hm_getmark loads 1]]
puts "Total loads: $load_count"

# If no loads, try different approach
if {$load_count == 0} {
    puts "=== TRYING ALTERNATIVE: *loadcreateonentity ==="
    foreach nid $base_nodes {
        *loadcreateonentity nodes $nid 0 1 1 1 1 1 1
        incr count
        if {$count >= 20} break
    }
    *createmark loads 1 "all"
    set load_count [llength [hm_getmark loads 1]]
    puts "Total loads after loadcreateonentity: $load_count"
}

# If still no loads, try using *setvalue on loadcols
if {$load_count == 0} {
    puts "=== TRYING ALTERNATIVE: *setvalue on loadcols ==="
    *createmark loadcols 1 "by name" "FIX_BASE"
    set lc_id [lindex [hm_getmark loadcols 1] 0]

    # Try to set SPC data using *setvalue
    *setvalue loadcols id=$lc_id STATUS=2
    *setvalue loadcols id=$lc_id dataname=NODEID value=[lindex $base_nodes 0]
    *setvalue loadcols id=$lc_id dataname=CID value=0
    *setvalue loadcols id=$lc_id dataname=DOFX value=1
    *setvalue loadcols id=$lc_id dataname=DOFY value=1
    *setvalue loadcols id=$lc_id dataname=DOFZ value=1
    *setvalue loadcols id=$lc_id dataname=DOFRX value=1
    *setvalue loadcols id=$lc_id dataname=DOFRY value=1
    *setvalue loadcols id=$lc_id dataname=DOFRZ value=1
    puts "Tried *setvalue on loadcols"

    *createmark loads 1 "all"
    set load_count [llength [hm_getmark loads 1]]
    puts "Total loads after setvalue: $load_count"
}

# Final check
puts "=== FINAL LOAD COUNT ==="
*createmark loads 1 "all"
puts "Total loads: [llength [hm_getmark loads 1]]"
