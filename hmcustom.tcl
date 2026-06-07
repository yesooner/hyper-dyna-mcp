# hyper-dyna-mcp for HyperMesh
# Auto-detects project path from this file's location

# Auto-detect project root from this file's location
set ::HDM_ROOT [file dirname [info script]]
if {![info exists ::mcp_hm_port]} {
    set ::mcp_hm_port 47882
}

# === Socket mode ===

proc mcp_start {} {
    # Close existing listener if any
    if {[info exists ::mcp_hm_server]} {
        catch {close $::mcp_hm_server}
        unset -nocomplain ::mcp_hm_server
        after 200
    }
    # Check if port is occupied by stale process
    set port $::mcp_hm_port
    if {![catch {set sock [socket 127.0.0.1 $port]; close $sock} err]} {
        puts "Port $port occupied, attempting cleanup..."
        catch {close $::mcp_hm_server}
        unset -nocomplain ::mcp_hm_server
        after 300
    }
    source "$::HDM_ROOT/runs/mcp.tcl"
}

proc mcp_status {} {
    set port 47882
    if {[info exists ::mcp_hm_port]} {
        set port $::mcp_hm_port
    }
    if {[catch {set sock [socket 127.0.0.1 $port]; close $sock} err]} {
        puts "Socket: NOT running"
    } else {
        puts "Socket: Active on port $port"
    }
    set status_file "$::HDM_ROOT/ipc/status.json"
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
    cd $::HDM_ROOT
    exec python -m program.plugin_loop &
    puts "IPC loop started."
}

proc mcp_stop {} {
    set flag "$::HDM_ROOT/ipc/stop.flag"
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
