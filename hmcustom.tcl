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

# === GUI Tab (auto-create) ===

proc mcp_create_tab {} {
    if {[winfo exists .mcp_tab]} {
        puts "MCP tab already exists"
        return
    }
    frame .mcp_tab
    hm_framework addtab MCP .mcp_tab

    label .mcp_tab.title -text "Hyper-Dyna-MCP" -font {Arial 12 bold}
    pack .mcp_tab.title -pady 10

    label .mcp_tab.status -text "Status: Ready" -fg gray
    pack .mcp_tab.status -pady 5

    frame .mcp_tab.btns
    pack .mcp_tab.btns -pady 10

    button .mcp_tab.btns.start -text "Start MCP" -width 15 -command {
        source "$::HDM_ROOT/hmcustom.tcl"
        catch {mcp_start}
        .mcp_tab.status configure -text "Status: Running" -fg green
    }
    pack .mcp_tab.btns.start -side left -padx 5

    button .mcp_tab.btns.check -text "Check Status" -width 15 -command {
        mcp_status
    }
    pack .mcp_tab.btns.check -side left -padx 5

    button .mcp_tab.btns.loop -text "Start Loop" -width 15 -command {
        mcp_loop
        .mcp_tab.status configure -text "Status: Loop Running" -fg blue
    }
    pack .mcp_tab.btns.loop -side left -padx 5

    button .mcp_tab.btns.stop -text "Stop IPC" -width 15 -command {
        mcp_stop
        .mcp_tab.status configure -text "Status: Stopped" -fg red
    }
    pack .mcp_tab.btns.stop -side left -padx 5

    puts "MCP tab created in HyperMesh menu"
}

# Auto-create tab
catch {mcp_create_tab}

puts "Hyper-Dyna-MCP loaded. Commands:"
puts "  mcp_start    - Start socket listener"
puts "  mcp_loop     - Start file IPC loop (blocking)"
puts "  mcp_status   - Check status"
puts "  mcp_stop     - Stop IPC loop"
puts "  mcp_create_tab - Create MCP GUI tab"
