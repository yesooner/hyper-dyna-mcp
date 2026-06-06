# HyperMesh GUI Listener - Restart Script
# Source this file in HyperMesh Tcl console to restart the listener

# Close existing server if running
if {[info exists ::mcp_hm_server]} {
    catch {close $::mcp_hm_server}
    unset -nocomplain ::mcp_hm_server
    after 200
}

# Configuration
set ::mcp_hm_host "127.0.0.1"
set ::mcp_hm_port 47882

# Restore puts command if corrupted
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

# Accept connection handler
proc ::mcp_hm_accept {chan addr client_port} {
    fconfigure $chan -blocking 1 -translation binary -encoding utf-8
    set script [read $chan]

    if {[string trim $script] eq ""} {
        puts $chan "ERROR: empty script"
        flush $chan
        close $chan
        return
    }

    # Hook puts to capture output
    set ::mcp_capture ""
    proc ::mcp_hm_capture_puts {args} {
        append ::mcp_capture [join $args " "] "\n"
    }
    if {[llength [info commands puts]] > 0} {
        catch {rename puts ::_mcp_base_puts}
    }
    rename ::mcp_hm_capture_puts puts

    set code [catch {uplevel #0 $script} result options]

    # Restore puts
    catch {rename puts ""}
    catch {rename ::_mcp_base_puts puts}

    if {$code == 0 || $code == 2} {
        puts $chan "OK"
        if {$::mcp_capture ne ""} { puts $chan $::mcp_capture }
        if {$result ne ""} { puts $chan $result }
    } else {
        puts $chan "ERROR"
        puts $chan $result
        if {[info exists options(-errorinfo)]} {
            puts $chan $options(-errorinfo)
        }
    }
    flush $chan
    close $chan
}

# Start server
set ::mcp_hm_server [socket -server ::mcp_hm_accept -myaddr $::mcp_hm_host $::mcp_hm_port]
puts "Dyna-mcp GUI listener ready on $::mcp_hm_host:$::mcp_hm_port"
puts "Waiting for connections..."
