*KEYWORD
*TITLE
Minimum Verification Model - 2 Parts Contact Load BC Curve
*CONTROL_TERMINATION
$    ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS
     0.0050         0 0.000E+00 0.000E+00 0.000E+00
*DATABASE_BINARY_D3PLOT
$      DT    LCDT      BEAM     NPLTC
   0.000100       0         0         0
*MAT_PIECEWISE_LINEAR_PLASTICITY
$    MID        RHO         E        PR      DA      DB
        1  7.850E-09  2.100E+05      0.300
*MAT_RIGID
$    MID        RHO         E        PR      DA      DB
        2  7.850E-09  2.100E+05      0.300
*END
