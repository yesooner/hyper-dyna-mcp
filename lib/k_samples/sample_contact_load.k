$# LS-DYNA Keyword file created by LS-PrePost(R) V4.10.5-23Jun2023
$# Created on Apr-11-2024 (14:55:26)
*KEYWORD   
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_ID
  10001001AS2S_BALL_to_FOAMconcrete
  20001001  30001001         3         3  30001001         0         0         0
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
       1.0       1.0       0.0       0.0       1.0       1.0       1.0       1.0
*DEFINE_CURVE_TITLE
gravity
  10001001         0       1.0    0.0098       0.0       0.0         0         0
                 0.0                 0.0
                 0.2                 1.0
                30.0                 1.0
*LOAD_BODY_Z
  10001001       1.0         0       0.0       0.0       0.0         0
*RIGIDWALL_PLANAR_ID
  10001001rigidwall_ground
         0         0         0       0.0       0.01.00000E20       1.0
       0.0       0.0       0.0       0.0       0.0       1.0       0.2       0.0
*END
