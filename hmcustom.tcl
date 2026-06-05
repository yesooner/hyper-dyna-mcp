# Dyna-mcp for HyperMesh
# Usage: source "F:/Dyna-mcp/hmcustom.tcl"
# Then type: mcp

proc mcp {} {
    source "F:/Dyna-mcp/runs/mcp.tcl"
}

proc mcp_status {} {
    if {[catch {set sock [socket 127.0.0.1 47881]; close $sock} err]} {
        puts "MCP: NOT running"
    } else {
        puts "MCP: Active on port 47881"
    }
}

proc mcp_load {filename} {
    source "F:/Dyna-mcp/runs/mcp.tcl"
    *readfile $filename
    puts "MCP: Loaded $filename"
}

puts "Dyna-mcp loaded. Type 'mcp' to start listener."
