# Step 1: Activate LS-DYNA template (REQUIRED before any cardimage operations)
set template_path {E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key}
if {![file exists $template_path]} {
    error "LS-DYNA template not found: $template_path"
}
set code [catch {*templatefileset $template_path} err]
puts "TEMPLATE_RESULT=$code"
puts "TEMPLATE_MESSAGE=$err"
catch {puts "SOLVER=[hm_getsolver]"}
catch {puts "TEMPLATE_TYPE=[hm_info templatetype]"}
