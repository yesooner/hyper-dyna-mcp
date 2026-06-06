# LS-DYNA R13 *ELEMENT_SHELL
# Category: element
# Parameters: EID, PID, N1, N2, N3, N4

*createmark nodes 1 {{N1}} {{N2}} {{N3}} {{N4}}
*element 1 0 {{PID}} {{N1}} {{N2}} {{N3}} {{N4}}