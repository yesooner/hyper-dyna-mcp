*KEYWORD
*TITLE
Missing Material Error - For Validation Testing
*CONTROL_TERMINATION
$    ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS
     0.0010         0 0.000E+00 0.000E+00 0.000E+00
*SECTION_SOLID
$    SECID    ELFORM       AET
         1         1
*PART
No Material Part
$    PID     SECID       MID
       1         1        99
*NODE
$   NODE               X               Y               Z      TC      RC
       1       0.0000000       0.0000000       0.0000000
       2      10.0000000       0.0000000       0.0000000
       3      10.0000000      10.0000000       0.0000000
       4       0.0000000      10.0000000       0.0000000
*ELEMENT_SOLID
$   EID     PID      N1      N2      N3      N4      N5      N6      N7      N8
       1       1       1       2       3       3       1       2       3       3
*END
