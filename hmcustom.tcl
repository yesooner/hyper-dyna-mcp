# Dyna-mcp for HyperMesh
# Source this file to add MCP commands and menu integration

# === MCP Core Commands ===
proc mcp {} {
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

# === MCP GUI Panel ===
proc mcp_panel {} {
    # Create or raise MCP panel
    if {[winfo exists .mcp_panel]} {
        raise .mcp_panel
        return
    }

    toplevel .mcp_panel
    wm title .mcp_panel "Dyna-mcp"
    wm geometry .mcp_panel 250x180
    wm resizable .mcp_panel 0 0

    # Title
    label .mcp_panel.title -text "Dyna-mcp Controller" -font {Arial 12 bold}
    pack .mcp_panel.title -pady 10

    # Status indicator
    frame .mcp_panel.status_frame
    pack .mcp_panel.status_frame -pady 5
    label .mcp_panel.status_frame.lbl -text "Status:"
    pack .mcp_panel.status_frame.lbl -side left
    label .mcp_panel.status_frame.ind -text "Checking..." -fg gray
    pack .mcp_panel.status_frame.ind -side left

    # Buttons
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

    # Close button
    button .mcp_panel.close -text "Close" -command {destroy .mcp_panel}
    pack .mcp_panel.close -pady 5

    # Auto-check status
    after 500 {
        if {[catch {set sock [socket 127.0.0.1 47881]; close $sock} err]} {
            .mcp_panel.status_frame.ind configure -text "Stopped" -fg red
        } else {
            .mcp_panel.status_frame.ind configure -text "Running" -fg green
        }
    }
}

# === Add to HyperMesh Menu ===
# Note: HyperMesh doesn't support adding to the main menu bar directly
# Use the panel approach instead

puts "Dyna-mcp loaded. Commands:"
puts "  mcp          - Start listener"
puts "  mcp_status   - Check status"
puts "  mcp_load f   - Start + load model"
puts "  mcp_panel    - Open GUI panel"
