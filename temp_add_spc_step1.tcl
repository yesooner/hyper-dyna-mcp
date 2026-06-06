# Step 1: Activate LS-DYNA template
set template_path {E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key}
if {![file exists $template_path]} {
    puts "ERROR: Template not found: $template_path"
    return
}
*templatefileset $template_path
puts "Template activated: [hm_info templatetype]"
