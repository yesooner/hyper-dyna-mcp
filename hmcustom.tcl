# hyper-dyna-mcp for HyperMesh
# Usage: source "F:/hyper-dyna-mcp/hmcustom.tcl"

# === Socket mode (existing) ===

proc mcp_start {} {
    source "F:/hyper-dyna-mcp/runs/mcp.tcl"
}

proc mcp_status {} {
    if {[catch {set sock [socket 127.0.0.1 47881]; close $sock} err]} {
        puts "Socket: NOT running"
    } else {
        puts "Socket: Active on port 47881"
    }
    # Also check file IPC status
    set status_file "F:/hyper-dyna-mcp/ipc/status.json"
    if {[file exists $status_file]} {
        set fp [open $status_file r]
        set data [read $fp]
        close $fp
        puts "IPC: $data"
    } else {
        puts "IPC: not initialized"
    }
}

# === File IPC mode ===

proc mcp_loop {} {
    puts "Starting file IPC loop (blocking)..."
    cd "F:/hyper-dyna-mcp"
    exec python -m program.plugin_loop &
    puts "IPC loop started."
}

proc mcp_stop {} {
    set flag "F:/hyper-dyna-mcp/ipc/stop.flag"
    set fp [open $flag w]
    puts $fp "stop"
    close $fp
    puts "Stop flag written. Loop will exit."
}

puts "Hyper-Dyna-MCP loaded. Commands:"
puts "  mcp_start    - Start socket listener"
puts "  mcp_loop     - Start file IPC loop (blocking)"
puts "  mcp_status   - Check status"
puts "  mcp_stop     - Stop IPC loop"
