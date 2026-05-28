*KEYWORD
*TITLE
Minimal Solid Element Test
*CONTROL_TERMINATION
$    ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS
     0.0010         0 0.000E+00 0.000E+00 0.000E+00
*DATABASE_BINARY_D3PLOT
$      DT    LCDT      BEAM     NPLTC
 0.000100       0         0         0
*MAT_ELASTIC
$    MID        RHO         E        PR      DA      DB
       1  7.850E-09 2.100E+05     0.300
*SECTION_SOLID
$    SECID    ELFORM       AET
         1         1
*PART
Solid Part
$    PID     SECID       MID
       1         1         1
*NODE
$   NODE               X               Y               Z      TC      RC
       1       0.0000000       0.0000000       0.0000000
       2      10.0000000       0.0000000       0.0000000
       3      10.0000000      10.0000000       0.0000000
       4       0.0000000      10.0000000       0.0000000
       5       0.0000000       0.0000000      10.0000000
       6      10.0000000       0.0000000      10.0000000
       7      10.0000000      10.0000000      10.0000000
       8       0.0000000      10.0000000      10.0000000
*ELEMENT_SOLID
$   EID     PID      N1      N2      N3      N4      N5      N6      N7      N8
       1       1       1       2       3       4       5       6       7       8
*BOUNDARY_SPC_SET
$    NSID       CID      DOFX      DOFY      DOFZ     DOFRX     DOFRY     DOFRZ
       1         0         1         1         1         0         0         0
*SET_NODE_LIST
$     SID
       1
$    N1      N2      N3      N4
       1       2       3       4
*END
