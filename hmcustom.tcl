# hyper-dyna-mcp for HyperMesh
if {[info exists ::env(HDM_HOME)]} {
    set ::HDM_ROOT [string map [list \\ /] $::env(HDM_HOME)]
} elseif {[info script] ne ""} {
    set ::HDM_ROOT [string map [list \\ /] [file normalize [file dirname [info script]]]]
} else {
    set ::HDM_ROOT [string map [list \\ /] [pwd]]
}

if {[info exists ::env(HDM_GUI_PORT)]} {
    set ::mcp_hm_port [expr {int($::env(HDM_GUI_PORT))}]
} else {
    set ::mcp_hm_port 47883
}

if {[info exists ::env(HDM_AUTO_START)]} {
    set ::HDM_AUTO_START [expr {int($::env(HDM_AUTO_START))}]
} else {
    set ::HDM_AUTO_START 1
}

if {[info exists ::env(HDM_PYTHON_EXE)]} {
    set ::HDM_PYTHON_EXE [string map [list \\ /] $::env(HDM_PYTHON_EXE)]
} else {
    set ::HDM_PYTHON_EXE "python"
}

# Guard: only load once
if {[info exists ::_hdm_loaded]} { return }
set ::_hdm_loaded 1

# === Error logging ===
set ::_hdm_error_log "$::HDM_ROOT/logs/hm_errors/[clock format [clock seconds] -format {%Y%m%d_%H%M%S}].log"
file mkdir [file dirname $::_hdm_error_log]

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

proc mcp_hm_channels {} {
    if {[catch {set names [chan names]}]} {
        if {[catch {set names [file channels]}]} {
            return {}
        }
    }
    return $names
}

proc mcp_hm_configure_socket {sock} {
    catch {fconfigure $sock -blocking 0}
    catch {fconfigure $sock -buffering none}
    catch {fconfigure $sock -translation binary}
    # Some HyperMesh 2024-era Tcl builds reject -encoding on binary sockets.
    catch {fconfigure $sock -encoding utf-8}
}

proc mcp_hm_close_port {port} {
    set closed 0
    if {[info exists ::mcp_hm_server]} {
        catch {close $::mcp_hm_server}
        unset -nocomplain ::mcp_hm_server
        incr closed
    }
    foreach ch [mcp_hm_channels] {
        set sockname ""
        if {[catch {set sockname [fconfigure $ch -sockname]}]} {
            continue
        }
        if {[llength $sockname] >= 3 && [lindex $sockname 2] == $port} {
            catch {close $ch}
            incr closed
        }
    }
    return $closed
}

proc mcp_start {} {
    if {[info exists ::env(HDM_GUI_PORT)]} {
        set ::mcp_hm_port [expr {int($::env(HDM_GUI_PORT))}]
    } else {
        set ::mcp_hm_port 47883
    }
    mcp_start_on_port $::mcp_hm_port
}

proc mcp_listener_file_for_port {port} {
    set port [expr {int($port)}]
    set specific "$::HDM_ROOT/runs/hm_gui_listener_${port}.tcl"
    if {[file exists $specific]} {
        return $specific
    }
    if {$port == 47883} {
        set default_listener "$::HDM_ROOT/runs/hm_gui_listener.tcl"
        if {[file exists $default_listener]} {
            return $default_listener
        }
        return "$::HDM_ROOT/runs/mcp.tcl"
    }
    return $specific
}

proc mcp_start_on_port {port} {
    set port [expr {int($port)}]
    if {$port < 1024 || $port > 65535} {
        puts "ERROR: invalid MCP listener port: $port"
        return 0
    }
    set ::mcp_hm_port $port
    set closed [mcp_hm_close_port $port]
    if {$closed > 0} {
        puts "Closed stale socket channels on port $port: $closed"
        after 200
    }
    if {![catch {set sock [socket 127.0.0.1 $port]; close $sock} err]} {
        puts "Port $port occupied, attempting one more cleanup..."
        set closed [mcp_hm_close_port $port]
        if {$closed > 0} {
            puts "Closed stale socket channels on port $port: $closed"
        }
        after 300
    }
    set listener [mcp_listener_file_for_port $port]
    if {![file exists $listener]} {
        puts "ERROR: listener Tcl not found for port $port: $listener"
        return 0
    }
    if {[catch {source $listener} err]} {
        hdm_log_error "mcp_start: $err"
        puts "ERROR: $err"
        return 0
    }
    after 300
    if {[mcp_socket_ping]} {
        puts "MCP listener verified on port $port"
        return 1
    }
    hdm_log_error "mcp_start_on_port: listener sourced but no MCP PONG on port $port"
    puts "ERROR: listener was sourced but no MCP PONG was received on port $port"
    puts "Run mcp_status. If the TCP port is occupied without PONG, run mcp_stop or choose another port."
    return 0
}

proc mcp_status {} {
    set port $::mcp_hm_port
    if {[mcp_socket_ping]} {
        puts "Socket: HyperMesh MCP listener active on port $port"
    } elseif {[catch {set sock [socket 127.0.0.1 $port]; close $sock} err]} {
        puts "Socket: NOT running"
    } else {
        puts "Socket: TCP port $port accepts connections but no MCP PONG was received"
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

proc mcp_socket_ping {} {
    set port $::mcp_hm_port
    if {[catch {
        set sock [socket 127.0.0.1 $port]
        mcp_hm_configure_socket $sock
        puts -nonewline $sock "__HDM_PING__"
        flush $sock
        set response ""
        set deadline [expr {[clock milliseconds] + 1500}]
        while {[clock milliseconds] < $deadline} {
            update
            after 50
            append response [read $sock]
            if {[string first "HYPERMESH_MCP_PONG" $response] >= 0} {
                close $sock
                return 1
            }
        }
        close $sock
    } err]} {
        return 0
    }
    return 0
}

proc mcp_ensure_listener {} {
    if {[mcp_socket_ping]} {
        puts "MCP listener already active on port $::mcp_hm_port"
        return 1
    }
    puts "MCP listener not active; starting on port $::mcp_hm_port..."
    catch {mcp_start_on_port $::mcp_hm_port} err
    after 300
    if {[mcp_socket_ping]} {
        puts "MCP listener active on port $::mcp_hm_port"
        return 1
    }
    hdm_log_error "mcp_ensure_listener failed: $err"
    puts "ERROR: MCP listener did not become active on port $::mcp_hm_port"
    return 0
}

proc mcp_clear_stop_flag {} {
    set flag "$::HDM_ROOT/ipc/stop.flag"
    if {[file exists $flag]} {
        if {[catch {file delete -force $flag} err]} {
            hdm_log_error "mcp_clear_stop_flag: $err"
            puts "WARNING: could not remove stale stop flag: $err"
            return 0
        }
        puts "Removed stale stop flag."
    }
    return 1
}

proc mcp_loop {} {
    if {[catch {
        puts "Starting file IPC loop (blocking)..."
        cd $::HDM_ROOT
        file mkdir "$::HDM_ROOT/ipc"
        mcp_clear_stop_flag
        if {![file exists $::HDM_PYTHON_EXE]} {
            error "Python executable not found: $::HDM_PYTHON_EXE"
        }
        exec $::HDM_PYTHON_EXE -m program.plugin_loop &
        puts "IPC loop started."
    } err]} {
        hdm_log_error "mcp_loop: $err"
        puts "ERROR: $err"
    }
}

proc mcp_stop {} {
    if {[catch {
        set flag "$::HDM_ROOT/ipc/stop.flag"
        file mkdir [file dirname $flag]
        set fp [open $flag w]
        puts $fp "stop"
        close $fp
        puts "Stop flag written. Loop will exit."
        set closed [mcp_hm_close_port $::mcp_hm_port]
        puts "Socket listener closed on port $::mcp_hm_port (closed=$closed)."
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
if {$::HDM_AUTO_START} {
    after 1000 {catch {mcp_ensure_listener}}
}
puts "Hyper-Dyna-MCP loaded from: $::HDM_ROOT/hmcustom.tcl"
