# Step 2: Create SPC load collector
*createentity loadcols cardimage=SPC name=FIX_BASE
puts "Created FIX_BASE load collector"

# Set as current collector
*currentcollector loadcols "FIX_BASE"
puts "Current load collector: [hm_info currentcollector loadcols]"
