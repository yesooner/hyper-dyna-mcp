# LS-DYNA R13 *ELEMENT_BEAM
# Category: element
# Parameters: EID, PID, N1, N2, N3, N4, RT1, RR1, RT2, RR2

*createmark nodes 1 {{N1}} {{N2}} {{N3}} {{N4}}
*element 1 0 {{PID}} {{N1}} {{N2}} {{N3}} {{N4}}