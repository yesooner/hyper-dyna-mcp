# LS-DYNA R13 *ELEMENT_TSHELL
# Category: element
# Entity type: elements
# Parameters: EID(int), PID(int), N1(int), N2(int), N3(int), N4(int), N5(int), N6(int), N7(int), N8(int)
# Note: Thick shell elements are created via *element command with node marks

*createmark nodes 1 {{N1}} {{N2}} {{N3}} {{N4}} {{N5}} {{N6}} {{N7}} {{N8}}
*element 1 0 {{PID}} {{N1}} {{N2}} {{N3}} {{N4}} {{N5}} {{N6}} {{N7}} {{N8}}
puts "HM_KEYWORD_CREATED keyword=ELEMENT_TSHELL entity=elements eid={{EID}} pid={{PID}}"
