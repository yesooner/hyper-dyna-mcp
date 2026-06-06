# LS-DYNA R13 *ELEMENT_BEAM
# Category: element
# Entity type: elements
# Parameters: EID(int), PID(int), N1(int), N2(int), N3(int), N4(int), RT1(float), RR1(float), RT2(float), RR2(float)
# Note: Beam elements use N1,N2 as endpoints, N3 as orientation node, N4 optional

*createmark nodes 1 {{N1}} {{N2}} {{N3}} {{N4}}
*element 1 0 {{PID}} {{N1}} {{N2}} {{N3}} {{N4}}
puts "HM_KEYWORD_CREATED keyword=ELEMENT_BEAM entity=elements eid={{EID}} pid={{PID}}"
