# hyper-dyna-mcp for HyperMesh
# Usage: source "F:/hyper-dyna-mcp/hmcustom.tcl"
# Then type: mcp_start

proc mcp_start {} {
    source "F:/hyper-dyna-mcp/runs/mcp.tcl"
}

proc mcp_status {} {
    if {[catch {set sock [socket 127.0.0.1 47881]; close $sock} err]} {
        puts "MCP: NOT running"
    } else {
        puts "MCP: Active on port 47881"
    }
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
    wm geometry .mcp_panel 250x180
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
    pack .mcp_panel.btns -pady 10

    button .mcp_panel.btns.start -text "Start MCP" -width 12 -command {
        source "F:/hyper-dyna-mcp/runs/mcp.tcl"
        .mcp_panel.status_frame.ind configure -text "Running" -fg green
    }
    pack .mcp_panel.btns.start -side left -padx 5

    button .mcp_panel.btns.check -text "Check Status" -width 12 -command {
        if {[catch {set sock [socket 127.0.0.1 47881]; close $sock} err]} {
            .mcp_panel.status_frame.ind configure -text "Stopped" -fg red
        } else {
            .mcp_panel.status_frame.ind configure -text "Running" -fg green
        }
    }
    pack .mcp_panel.btns.check -side left -padx 5

    button .mcp_panel.close -text "Close" -command {destroy .mcp_panel}
    pack .mcp_panel.close -pady 5

    after 500 {
        if {[catch {set sock [socket 127.0.0.1 47881]; close $sock} err]} {
            .mcp_panel.status_frame.ind configure -text "Stopped" -fg red
        } else {
            .mcp_panel.status_frame.ind configure -text "Running" -fg green
        }
    }
}

puts "Hyper-Dyna-MCP loaded. Commands:"
puts "  mcp_start    - Start listener"
puts "  mcp_status   - Check status"
puts "  mcp_load f   - Start + load model"
puts "  mcp_panel    - Open GUI panel"
