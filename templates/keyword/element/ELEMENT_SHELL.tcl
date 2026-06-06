# LS-DYNA R13 *ELEMENT_SHELL
# Category: element
# Entity type: elements
# Parameters: EID(int), PID(int), N1(int), N2(int), N3(int), N4(int)
# Note: Shell elements are created via *element command with node marks

*createmark nodes 1 {{N1}} {{N2}} {{N3}} {{N4}}
*element 1 0 {{PID}} {{N1}} {{N2}} {{N3}} {{N4}}
puts "HM_KEYWORD_CREATED keyword=ELEMENT_SHELL entity=elements eid={{EID}} pid={{PID}}"
