
# Dyna-mcp HyperMesh GUI listener
# Listener version: 2024-compat-v3
# Source this file inside a visible HyperMesh session
set ::mcp_hm_listener_version "2024-compat-v3"
if {![info exists ::mcp_hm_host]} {
    set ::mcp_hm_host "127.0.0.1"
}
# Force the generated project port so stale Tcl session variables cannot
# override path/hypermesh_paths.yaml.
set ::mcp_hm_port 47884

proc ::mcp_hm_restore_puts {} {
    if {[llength [info commands ::_mcp_orig_puts]] > 0} {
        catch {rename puts ""}
        catch {rename ::_mcp_orig_puts puts}
    }
    if {[llength [info commands ::_mcp_base_puts]] > 0} {
        catch {rename puts ""}
        catch {rename ::_mcp_base_puts puts}
    }
}
::mcp_hm_restore_puts

proc ::mcp_hm_channels {} {
    if {[catch {set names [chan names]}]} {
        if {[catch {set names [file channels]}]} {
            return {}
        }
    }
    return $names
}

proc ::mcp_hm_errorinfo {options} {
    if {[catch {set info [dict get $options -errorinfo]}] == 0} {
        return $info
    }
    if {[info exists ::errorInfo]} {
        return $::errorInfo
    }
    return ""
}

proc ::mcp_hm_configure_socket {chan} {
    catch {fconfigure $chan -blocking 0}
    catch {fconfigure $chan -buffering none}
    catch {fconfigure $chan -translation binary}
    # HyperMesh 2024 Tcl builds may reject -encoding on binary sockets.
    catch {fconfigure $chan -encoding utf-8}
}

proc ::mcp_hm_read_request {chan} {
    set script ""
    set deadline [expr {[clock milliseconds] + 3000}]
    set quiet_deadline 0
    while {[clock milliseconds] < $deadline} {
        set chunk ""
        if {![catch {set chunk [read $chan]}] && $chunk ne ""} {
            append script $chunk
            set quiet_deadline [expr {[clock milliseconds] + 250}]
        }
        if {[catch {eof $chan} _mcp_eof]} {
            break
        }
        if {$_mcp_eof} {
            break
        }
        if {$script ne "" && $quiet_deadline > 0 && [clock milliseconds] >= $quiet_deadline} {
            break
        }
        update
        after 20
    }
    return $script
}

proc ::mcp_hm_close_port {port} {
    set closed 0
    if {[info exists ::mcp_hm_server]} {
        catch {close $::mcp_hm_server}
        unset -nocomplain ::mcp_hm_server
        incr closed
    }
    foreach ch [::mcp_hm_channels] {
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

proc ::mcp_hm_accept {chan addr client_port} {
    set fatal [catch {
        ::mcp_hm_configure_socket $chan
        set script [::mcp_hm_read_request $chan]

        if {[string trim $script] eq ""} {
            puts $chan "ERROR: empty script"
            flush $chan
            close $chan
            return
        }

        if {[string trim $script] eq "__HDM_PING__"} {
            puts $chan "OK"
            puts $chan "HYPERMESH_MCP_PONG"
            puts $chan "LISTENER_VERSION=$::mcp_hm_listener_version"
            catch {puts $chan "TCL_VERSION=[info tclversion]"}
            catch {puts $chan "TCL_PATCHLEVEL=[info patchlevel]"}
            flush $chan
            close $chan
            return
        }

        # Hook puts to capture script output.
        set ::mcp_capture ""
        proc ::mcp_hm_capture_puts {args} {
            append ::mcp_capture [join $args " "] "\n"
        }
        if {[llength [info commands puts]] > 0} {
            catch {rename puts ::_mcp_base_puts}
        }
        rename ::mcp_hm_capture_puts puts

        set code [catch {uplevel #0 $script} result options]

        # Restore puts before writing to the socket.
        catch {rename puts ""}
        catch {rename ::_mcp_base_puts puts}

        # HyperMesh commands often return non-zero (e.g. *setvalue returns 1).
        # Only treat as error if result contains error keywords.
        set is_error 0
        if {$code == 1} {
            set lower_result [string tolower $result]
            if {[string match "*error*" $lower_result] ||                  [string match "*invalid*" $lower_result] ||                  [string match "*failed*" $lower_result] ||                  [string match "*not found*" $lower_result]} {
                set is_error 1
            }
        }
        if {$is_error} {
            puts $chan "ERROR"
            puts $chan $result
            set _mcp_errorinfo [::mcp_hm_errorinfo $options]
            if {$_mcp_errorinfo ne ""} {
                puts $chan $_mcp_errorinfo
            }
        } else {
            puts $chan "OK"
            if {$::mcp_capture ne ""} { puts $chan $::mcp_capture }
            if {$result ne ""} { puts $chan $result }
        }
        flush $chan
        close $chan
    } fatal_msg fatal_options]

    if {$fatal} {
        ::mcp_hm_restore_puts
        catch {puts $chan "ERROR"}
        catch {puts $chan "Listener fatal error: $fatal_msg"}
        set _mcp_fatal_errorinfo [::mcp_hm_errorinfo $fatal_options]
        if {$_mcp_fatal_errorinfo ne ""} {
            catch {puts $chan $_mcp_fatal_errorinfo}
        }
        catch {flush $chan}
        catch {close $chan}
    }
}

set _mcp_closed [::mcp_hm_close_port $::mcp_hm_port]
if {$_mcp_closed > 0} {
    after 300
}
if {[catch {
    set ::mcp_hm_server [socket -server ::mcp_hm_accept -myaddr $::mcp_hm_host $::mcp_hm_port]
} _mcp_bind_err]} {
    set _mcp_closed [::mcp_hm_close_port $::mcp_hm_port]
    if {$_mcp_closed > 0} { after 300 }
    if {[catch {
        set ::mcp_hm_server [socket -server ::mcp_hm_accept -myaddr $::mcp_hm_host $::mcp_hm_port]
    } _mcp_bind_err2]} {
        error "Cannot start HyperMesh MCP listener on $::mcp_hm_host:$::mcp_hm_port: $_mcp_bind_err2. Run mcp_stop, or generate and source runs/hm_gui_listener_<free_port>.tcl for another port."
    }
}
puts "Dyna-mcp GUI listener ready on $::mcp_hm_host:$::mcp_hm_port"
