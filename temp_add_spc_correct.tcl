# Correct SPC creation using *loadcreate with type=1

# First, activate LS-DYNA template
set template_path {E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key}
*templatefileset $template_path
puts "Template activated: [hm_info templatetype]"

# Create SPC load collector
catch {*createentity loadcols cardimage=SPC name=FIX_BASE} err
puts "Created FIX_BASE: $err"

# Set as current collector
*currentcollector loadcols "FIX_BASE"
puts "Current load collector: [hm_info currentcollector loadcols]"

# Select base nodes (Z=0)
*createmark nodes 1 "by box" 7200 720 -10 9540 3060 10 0 inside 0 0 0
set base_nodes [hm_getmark nodes 1]
set node_count [llength $base_nodes]
puts "Base nodes found: $node_count"

# Apply SPC using *loadcreate with type=1
# Format: *loadcreate <type> <node_id> <sys_id> <dof_x> <dof_y> <dof_z> <dof_rx> <dof_ry> <dof_rz>
set count 0
foreach nid $base_nodes {
    *loadcreate 1 $nid 0 1 1 1 1 1 1
    incr count
}
puts "Applied SPC to $count nodes"

# Verify
*createmark loads 1 "all"
set load_count [llength [hm_getmark loads 1]]
puts "Total loads created: $load_count"

# Show sample loads
if {$load_count > 0} {
    puts "=== SAMPLE LOADS ==="
    set show_count 0
    foreach lid [hm_getmark loads 1] {
        if {$show_count >= 5} break
        puts "  LOAD_$lid"
        incr show_count
    }
}
