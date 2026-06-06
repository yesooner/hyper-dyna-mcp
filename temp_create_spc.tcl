# Step 2: Create SPC constraints using *loadcreate (Approach 1)

# First, create SPC load collector
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

# Apply SPC using *loadcreate (9 arguments: type node_id sys_id dof_x dof_y dof_z dof_rx dof_ry dof_rz)
set count 0
foreach nid $base_nodes {
    *loadcreate 0 $nid 0 1 1 1 1 1 1
    incr count
}
puts "Applied SPC to $count nodes"

# Verify
*createmark loads 1 "all"
set load_count [llength [hm_getmark loads 1]]
puts "Total loads created: $load_count"

# Check load details
if {$load_count > 0} {
    puts "=== LOAD DETAILS ==="
    set show_count 0
    foreach lid [hm_getmark loads 1] {
        if {$show_count >= 5} break
        set lname [hm_getcollectorname loads $lid]
        puts "  LOAD_$lid = $lname"
        incr show_count
    }
}
