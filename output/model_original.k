*KEYWORD
*TITLE
Minimum Verification Model - 2 Parts Contact Load BC Curve
$ ============================================================
$ Parts: Plate (shell) + Impactor (rigid shell)
$ Material: MAT_PIECEWISE_LINEAR_PLASTICITY + MAT_RIGID
$ Section: SECTION_SHELL
$ Contact: AUTOMATIC_SURFACE_TO_SURFACE
$ Load: Prescribed velocity on impactor
$ Boundary: Fixed edges on plate
$ Curve: Load curve for velocity
$ ============================================================
$
$ --- CONTROL ---
*CONTROL_TERMINATION
$    ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS
     0.0050         0 0.000E+00 0.000E+00 0.000E+00
*CONTROL_TIMESTEP
$      DTMIN    DTMAX     SCALC     EOS
 0.000E+00 0.900E+00 0.000E+00
*CONTROL_HOURGLASS
$    IHQ     QH      QB     QW     QV
         1 0.100E+00
$
$ --- DATABASE ---
*DATABASE_BINARY_D3PLOT
$      DT    LCDT      BEAM     NPLTC
 0.000100       0         0         0
*DATABASE_BINARY_D3PHT
$      DT    LCDT
 0.000100       0
*DATABASE_GLSTAT
$      DT
 0.000050
*DATABASE_MATSUM
$      DT
 0.000050
*DATABASE_SLEOUT
$      DT
 0.000050
$
$ --- MATERIALS ---
*MAT_PIECEWISE_LINEAR_PLASTICITY
$    MID        RHO        E       PR     SIGY      ETAN      FAIL      EPS1
       1 7.850E-09 2.100E+05 0.300E+00 2.500E+02 1.000E+03 0.100E+01
$    EPS2      EPS3      EPS4      EPS5      EPS6      EPS7      EPS8     EPS9
 0.200E+00 0.400E+00 0.600E+00 0.800E+00 0.100E+01 0.000E+00 0.000E+00 0.000E+00
$     ES1       ES2       ES3       ES4       ES5       ES6       ES7       ES8
 0.000E+00 0.000E+00 0.000E+00 0.000E+00 0.000E+00 0.000E+00 0.000E+00 0.000E+00
*MAT_RIGID
$    MID        RHO        E       PR       N       COUPLE      MAlias     TLOG
       2 7.850E-09 2.100E+05 0.300E+00 0.000E+00 0.000E+00 0.000E+00 0.000E+00
$    XMO      YMO      ZMO
 0.000E+00 0.000E+00 0.000E+00
$
$ --- SECTION ---
*SECTION_SHELL
$    SECID    ELFORM      SHRF       NIP     PROPT       QR      ICOMP
         1         0 0.000E+00 0.000E+00 0.000E+00 0.000E+00
$      T1        T2        T3        T4      NSM
 1.000E+00 1.000E+00 1.000E+00 1.000E+00 0.000E+00
*SECTION_SHELL
$    SECID    ELFORM      SHRF       NIP     PROPT       QR      ICOMP
         2         0 0.000E+00 0.000E+00 0.000E+00 0.000E+00
$      T1        T2        T3        T4      NSM
 2.000E+00 2.000E+00 2.000E+00 2.000E+00 0.000E+00
$
$ --- PARTS ---
*PART
Steel Plate
$    PID     SECID       MID     EOSID      HGID
       1         1         1         0         0
*PART
Rigid Impactor
$    PID     SECID       MID     EOSID      HGID
       2         2         2         0         0
$
$ --- NODES ---
*NODE
$   NID               X               Y               Z
       1       0.000E+00       0.000E+00       0.000E+00
       2      10.000E+00       0.000E+00       0.000E+00
       3      10.000E+00      10.000E+00       0.000E+00
       4       0.000E+00      10.000E+00       0.000E+00
       5       5.000E+00       5.000E+00       2.000E+00
       6       6.000E+00       5.000E+00       2.000E+00
       7       6.000E+00       6.000E+00       2.000E+00
       8       5.000E+00       6.000E+00       2.000E+00
$
$ --- ELEMENTS ---
*ELEMENT_SHELL
$   EID     PID      N1      N2      N3      N4
       1       1       1       2       3       4
*ELEMENT_SHELL
$   EID     PID      N1      N2      N3      N4
       2       2       5       6       7       8
$
$ --- SETS ---
*SET_PART_LIST
$     SID
       1
$    PID1      PID2      PID3      PID4      PID5      PID6      PID7      PID8
       1
*SET_PART_LIST
$     SID
       2
$    PID1      PID2      PID3      PID4      PID5      PID6      PID7      PID8
       2
*SET_NODE_LIST
$     SID
       3
$    N1        N2        N3        N4        N5        N6        N7        N8
       1       2       3       4
*SET_SEGMENT
$     SID
       4
$    N1        N2        N3        N4      PID
       1       2       3       4       1
*SET_SEGMENT
$     SID
       5
$    N1        N2        N3        N4      PID
       5       6       7       8       2
$
$ --- CONTACT ---
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$    SSID      MSID     SSTYP     MSTYP      SBOXID     MBOXID       SPROR       MUN
       5         4         0         0         0         0         0         0
$     FS        FD        DC        VC        VDC        PENCHECK    ORTEN       MFLAG
 0.300E+00 0.300E+00 0.000E+00 0.000E+00 0.000E+00 0.000E+00 0.000E+00 0
$    SLSFAC     RWPNAL     ISLDOF     CKIN      CFRIC      EDGE
 1.000E+00 0.000E+00 0.000E+00 0.000E+00 0.000E+00 0
$
$ --- BOUNDARY CONDITIONS ---
*BOUNDARY_SPC_SET
$    NSID       CID      DOFX      DOFY      DOFZ     DOFRX     DOFRY     DOFRZ
       3         0         1         1         1         1         1         1
$
$ --- DEFINE CURVE ---
*DEFINE_CURVE
$     LCID       SIDR       SFA       SFO      OFFA      OFFO     DTIME
       1         0 1.000E+00 1.000E+00 0.000E+00 0.000E+00 0.000E+00
$                A1                  O1
       0.000E+00       0.000E+00
       1.000E-03      -1.000E+01
       2.000E-03      -1.000E+01
       5.000E-03       0.000E+00
$
$ --- LOADS ---
*LOAD_PRESCRIBED_VELOCITY_SET
$     SID       DOF      LCID        SF       VID     DEATH      BIRTH
       3         3       1      1.000E+00       0 1.000E+30 0.000E+00
$
$ --- INITIAL VELOCITY ---
*INITIAL_VELOCITY_GENERATION
$    SETID     STYP      VNX      VNY      VNZ      IRID      OMEGA
       2         0 0.000E+00 0.000E+00-1.000E+01 0         0
$   XC       YC       ZC      NODE1     NODE2
 5.500E+00 5.500E+00 2.000E+00
$
*END
