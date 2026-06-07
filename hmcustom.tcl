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
    puts "HDM source: $::HDM_ROOT/runs/mcp.tcl"
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

    # 让 .mcp_tab 内部随窗口缩放
    grid columnconfigure .mcp_tab 0 -weight 1
    grid rowconfigure .mcp_tab 2 -weight 1

    label .mcp_tab.title -text "Hyper-Dyna-MCP" -font {Arial 12 bold}
    grid .mcp_tab.title -row 0 -column 0 -pady 10 -sticky n

    label .mcp_tab.status -text "Status: Ready" -fg gray
    grid .mcp_tab.status -row 1 -column 0 -pady 5 -sticky n

    # 按钮区域 — grid 布局，列等宽随窗口缩放
    frame .mcp_tab.btns
    grid .mcp_tab.btns -row 2 -column 0 -pady 10 -sticky nsew
    grid columnconfigure .mcp_tab.btns {0 1} -weight 1 -uniform btn

    button .mcp_tab.btns.start -text "Start MCP" -command {
        source "$::HDM_ROOT/hmcustom.tcl"
        catch {mcp_start}
        .mcp_tab.status configure -text "Status: Running" -fg green
    }
    grid .mcp_tab.btns.start -row 0 -column 0 -padx 5 -pady 3 -sticky ew

    button .mcp_tab.btns.check -text "Check Status" -command {
        mcp_status
    }
    grid .mcp_tab.btns.check -row 0 -column 1 -padx 5 -pady 3 -sticky ew

    button .mcp_tab.btns.loop -text "Start Loop" -command {
        mcp_loop
        .mcp_tab.status configure -text "Status: Loop Running" -fg blue
    }
    grid .mcp_tab.btns.loop -row 1 -column 0 -padx 5 -pady 3 -sticky ew

    button .mcp_tab.btns.stop -text "Stop MCP" -command {
        mcp_stop
        .mcp_tab.status configure -text "Status: Stopped" -fg red
    }
    grid .mcp_tab.btns.stop -row 1 -column 1 -padx 5 -pady 3 -sticky ew

    puts "MCP tab created in HyperMesh menu"
}

# === Auto-refresh on new model ===
# HyperMesh calls *userprofile callback when a new file is opened
if {[info commands *userprofile] eq ""} {
    # No existing userprofile — install directly
    catch {rename ::*userprofile ::_orig_userprofile}
    proc *userprofile {args} {
        # Re-detect project root in case the file was moved
        set ::HDM_ROOT [file dirname [info script]]
        puts "HDM_ROOT refreshed: $::HDM_ROOT"
        if {[catch {_orig_userprofile {*}$args} err]} {
            # no original to call, ignore
        }
    }
} else {
    # Wrap existing userprofile
    catch {rename ::*userprofile ::_orig_userprofile}
    proc *userprofile {args} {
        set ::HDM_ROOT [file dirname [info script]]
        puts "HDM_ROOT refreshed: $::HDM_ROOT"
        catch {_orig_userprofile {*}$args}
    }
}

# Auto-create tab
catch {mcp_create_tab}

puts "Hyper-Dyna-MCP loaded from: $::HDM_ROOT"
puts "Commands:"
puts "  mcp_start    - Start socket listener"
puts "  mcp_loop     - Start file IPC loop (blocking)"
puts "  mcp_status   - Check status"
puts "  mcp_stop     - Stop MCP"
puts "  mcp_create_tab - Create MCP GUI tab"
