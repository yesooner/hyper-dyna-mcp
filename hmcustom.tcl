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

proc mcp_load {filename} {
    source "F:/hyper-dyna-mcp/runs/mcp.tcl"
    *readfile $filename
    puts "MCP: Loaded $filename"
}

proc mcp_panel {} {
    if {[winfo exists .mcp_panel]} {
        raise .mcp_panel
        return
    }

    toplevel .mcp_panel
    wm title .mcp_panel "Hyper-Dyna-MCP"
    wm geometry .mcp_panel 280x220
    wm resizable .mcp_panel 0 0

    label .mcp_panel.title -text "Hyper-Dyna-MCP" -font {Arial 12 bold}
    pack .mcp_panel.title -pady 10

    frame .mcp_panel.status_frame
    pack .mcp_panel.status_frame -pady 5
    label .mcp_panel.status_frame.lbl -text "Status:"
    pack .mcp_panel.status_frame.lbl -side left
    label .mcp_panel.status_frame.ind -text "Checking..." -fg gray
    pack .mcp_panel.status_frame.ind -side left

    frame .mcp_panel.btns
    pack .mcp_panel.btns -pady 5

    button .mcp_panel.btns.socket -text "Socket Start" -width 12 -command {
        source "F:/hyper-dyna-mcp/runs/mcp.tcl"
        .mcp_panel.status_frame.ind configure -text "Socket OK" -fg green
    }
    pack .mcp_panel.btns.socket -side left -padx 3

    button .mcp_panel.btns.ipc -text "IPC Loop" -width 12 -command {
        mcp_loop
        .mcp_panel.status_frame.ind configure -text "IPC Running" -fg green
    }
    pack .mcp_panel.btns.ipc -side left -padx 3

    frame .mcp_panel.btns2
    pack .mcp_panel.btns2 -pady 5

    button .mcp_panel.btns2.check -text "Check Status" -width 12 -command {
        mcp_status
    }
    pack .mcp_panel.btns2.check -side left -padx 3

    button .mcp_panel.btns2.stop -text "Stop IPC" -width 12 -command {
        mcp_stop
        .mcp_panel.status_frame.ind configure -text "Stopped" -fg red
    }
    pack .mcp_panel.btns2.stop -side left -padx 3

    button .mcp_panel.close -text "Close" -command {destroy .mcp_panel}
    pack .mcp_panel.close -pady 5

    after 500 {
        if {[catch {set sock [socket 127.0.0.1 47881]; close $sock} err]} {
            .mcp_panel.status_frame.ind configure -text "Idle" -fg gray
        } else {
            .mcp_panel.status_frame.ind configure -text "Socket OK" -fg green
        }
    }
}

puts "Hyper-Dyna-MCP loaded. Commands:"
puts "  mcp_start    - Start socket listener"
puts "  mcp_loop     - Start file IPC loop (blocking)"
puts "  mcp_status   - Check status"
puts "  mcp_stop     - Stop IPC loop"
puts "  mcp_load f   - Load model"
puts "  mcp_panel    - Open GUI panel"
