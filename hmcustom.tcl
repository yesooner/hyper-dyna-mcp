# hyper-dyna-mcp for HyperMesh
if {[info exists ::env(HDM_HOME)]} {
    set ::HDM_ROOT [string map [list \\ /] $::env(HDM_HOME)]
} else {
    set ::HDM_ROOT "F:/hyper-dyna-mcp"
}

if {![info exists ::mcp_hm_port]} {
    set ::mcp_hm_port 47882
}

# Guard: only load once
if {[info exists ::_hdm_loaded]} { return }
set ::_hdm_loaded 1

# === Error logging ===
set ::_hdm_error_log "$::HDM_ROOT/logs/hm_errors/[clock format [clock seconds] -format {%Y%m%d_%H%M%S}].log"

proc hdm_log_error {msg} {
    set fp [open $::_hdm_error_log a]
    puts $fp "\[[clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]\] $msg"
    close $fp
}

# Trap bgerror — catches segfaults and unhandled Tcl errors
proc bgerror {msg} {
    hdm_log_error "BGERROR: $msg"
    hdm_log_error "STACK: [info level]"
    puts stderr "HDM ERROR: $msg (logged to $::_hdm_error_log)"
}

# Trap unknown commands
if {[catch {rename ::unknown ::_orig_unknown}]} {
    # unknown already exists, wrap it
}
proc unknown {args} {
    hdm_log_error "UNKNOWN CMD: $args"
    catch {return [uplevel 1 ::_orig_unknown $args]}
}

# === Socket mode ===

proc mcp_start {} {
    if {[info exists ::mcp_hm_server]} {
        catch {close $::mcp_hm_server}
        unset -nocomplain ::mcp_hm_server
        after 200
    }
    set port $::mcp_hm_port
    if {![catch {set sock [socket 127.0.0.1 $port]; close $sock} err]} {
        puts "Port $port occupied, attempting cleanup..."
        catch {close $::mcp_hm_server}
        unset -nocomplain ::mcp_hm_server
        after 300
    }
    if {[catch {source "$::HDM_ROOT/runs/mcp.tcl"} err]} {
        hdm_log_error "mcp_start: $err"
        puts "ERROR: $err"
    }
}

proc mcp_status {} {
    set port $::mcp_hm_port
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

proc mcp_loop {} {
    if {[catch {
        puts "Starting file IPC loop (blocking)..."
        cd $::HDM_ROOT
        exec python -m program.plugin_loop &
        puts "IPC loop started."
    } err]} {
        hdm_log_error "mcp_loop: $err"
        puts "ERROR: $err"
    }
}

proc mcp_stop {} {
    if {[catch {
        set flag "$::HDM_ROOT/ipc/stop.flag"
        set fp [open $flag w]
        puts $fp "stop"
        close $fp
        puts "Stop flag written. Loop will exit."
    } err]} {
        hdm_log_error "mcp_stop: $err"
        puts "ERROR: $err"
    }
}

# === GUI Tab ===

proc mcp_create_tab {} {
    if {[winfo exists .mcp_tab]} { return }
    frame .mcp_tab
    hm_framework addtab MCP .mcp_tab

    grid columnconfigure .mcp_tab 0 -weight 1
    grid rowconfigure .mcp_tab 2 -weight 1

    label .mcp_tab.title -text "Hyper-Dyna-MCP" -font {Arial 12 bold}
    grid .mcp_tab.title -row 0 -column 0 -pady 10 -sticky n

    label .mcp_tab.status -text "Status: Ready" -fg gray
    grid .mcp_tab.status -row 1 -column 0 -pady 5 -sticky n

    frame .mcp_tab.btns
    grid .mcp_tab.btns -row 2 -column 0 -pady 10 -sticky nsew
    grid columnconfigure .mcp_tab.btns {0 1} -weight 1 -uniform btn

    button .mcp_tab.btns.start -text "Start MCP" -command {
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
}

# === Init ===
catch {mcp_create_tab}
puts "Hyper-Dyna-MCP loaded from: $::HDM_ROOT/hmcustom.tcl"
