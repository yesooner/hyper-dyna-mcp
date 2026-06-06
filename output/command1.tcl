*begin "version 2021.0.0.33  6-6-2026  0:50:11"
*createstringarray 17 " 0 penalty value              0.00    0.00    0.80    1.00   10.00" \
  "  1 min length        1 1.0  10.000   9.000   4.000   2.000   1.000    1   59    0" \
  "  2 max length        1 1.0  10.000  12.000  15.000  20.000  30.000    0   39    1" \
  "  3 aspect ratio      1 1.0   1.000   2.000   4.400   5.000  10.000    0   41    2" \
  "  4 warpage           1 1.0   0.000   5.000  13.000  15.000  30.000    0   56    3" \
  "  5 max angle quad    1 1.0  90.000 110.000 134.000 140.000 160.000    0   28    4" \
  "  6 min angle quad    1 1.0  90.000  70.000  46.000  40.000  20.000    0   61    5" \
  "  7 max angle tria    1 1.0  60.000  80.000 112.000 120.000 150.000    0   19    6" \
  "  8 min angle tria    1 1.0  60.000  50.000  34.000  30.000  15.000    0   22    7" \
  "  9 skew              1 1.0   0.000  10.000  34.000  40.000  70.000    0   46    8" \
  " 10 jacobian          1 1.0   1.000   0.900   0.700   0.600   0.300    0   57    9" \
  " 11 chordal dev       0 1.0   0.000   0.300   0.800   1.000   2.000    0   29   10" \
  " 12 taper             1 1.0   0.000   0.200   0.500   0.600   0.900    0   53   11" \
  " 13 % of trias        1 1.0   0.000   6.000  10.000  15.000  20.000    0    0   -1" \
  " 14 QI color legend            32      32       7       6       3           3   -1" \
  " 15 time_step         1      10.000                   0.010            0   59   12" \
  "   Global_solver 0"
*setqualitycriteria 1 17 0
*menufilterset "*"
*menufilterdisable 
*viewset 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 10 10
*viewset 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 10 10
*readfile "F:\\Dyna-mcp\\output\\bracket_test.hm"
*setgeomrefinelevel 1
*menufont 2
*setsolverusessegmentsets 0
*ME_CoreBehaviorAdjust "allowable_actions_policy=TC_lite"
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 16
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 1
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 16
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*clearmarkall 3
*clearmark collections 1
*clearmark collections 2
*clearmark controllers 1
*loaddefaultattributevaluesfromxml 
*setentitytypesupportedbyenggid 1 0
*ME_CoreBehaviorAdjust "containment_rules_policy=strict"
*setoption part_editor_mode=0
*setoption part_editor_sync=0
*setsolverusessegmentsets 1
*ME_CoreBehaviorAdjust "allowable_actions_policy=TC_lite"
*elementchecksettings 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
*entitybundleregister "__AUTOCONTACT_PREVIEW_BUNDLE_LSDYNA" "groups groups contactsurfs contactsurfs sets sets" 0
*setmacrofile "E:/HM2021/2021/hwdesktop/hm/scripts/UserProfiles/../dynakey/dyna_key.mac"
*enablemacromenu 1
*templatefileset "E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key"
*clearmarkall 3
*clearmarkall 3
*clearmark collections 1
*clearmark collections 2
*clearmark controllers 1
*loaddefaultattributevaluesfromxml 
*startnotehistorystate {Changed move options}
*endnotehistorystate {Changed move options}
*readfile "F:/Dyna-mcp/lib/hypermesh_samples/bracket.hm"
*setgeomrefinelevel 1
*writefile "F:/Dyna-mcp/output/bracket_from_gui.hm" 1
*readfile "F:/Dyna-mcp/output/model_original.k"
*setgeomrefinelevel 1
*feinput "F:/Dyna-mcp/output/model_original.k" "" 0 0 0 0 0
*begin "version 2021.0.0.33  6-6-2026  1:45:10"
*createstringarray 17 " 0 penalty value              0.00    0.00    0.80    1.00   10.00" \
  "  1 min length        1 1.0  10.000   9.000   4.000   2.000   1.000    1   59    0" \
  "  2 max length        1 1.0  10.000  12.000  15.000  20.000  30.000    0   39    1" \
  "  3 aspect ratio      1 1.0   1.000   2.000   4.400   5.000  10.000    0   41    2" \
  "  4 warpage           1 1.0   0.000   5.000  13.000  15.000  30.000    0   56    3" \
  "  5 max angle quad    1 1.0  90.000 110.000 134.000 140.000 160.000    0   28    4" \
  "  6 min angle quad    1 1.0  90.000  70.000  46.000  40.000  20.000    0   61    5" \
  "  7 max angle tria    1 1.0  60.000  80.000 112.000 120.000 150.000    0   19    6" \
  "  8 min angle tria    1 1.0  60.000  50.000  34.000  30.000  15.000    0   22    7" \
  "  9 skew              1 1.0   0.000  10.000  34.000  40.000  70.000    0   46    8" \
  " 10 jacobian          1 1.0   1.000   0.900   0.700   0.600   0.300    0   57    9" \
  " 11 chordal dev       0 1.0   0.000   0.300   0.800   1.000   2.000    0   29   10" \
  " 12 taper             1 1.0   0.000   0.200   0.500   0.600   0.900    0   53   11" \
  " 13 % of trias        1 1.0   0.000   6.000  10.000  15.000  20.000    0    0   -1" \
  " 14 QI color legend            32      32       7       6       3           3   -1" \
  " 15 time_step         1      10.000                   0.010            0   59   12" \
  "   Global_solver 0"
*setqualitycriteria 1 17 0
*menufilterset "*"
*menufilterdisable 
*viewset 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 10 10
*viewset 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 10 10
*readfile "F:\\Dyna-mcp\\output\\test1.hm"
*setgeomrefinelevel 1
*menufont 2
*setsolverusessegmentsets 0
*ME_CoreBehaviorAdjust "allowable_actions_policy=TC_lite"
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*startnotehistorystate {Synchronized Library}
*ME_ModulesHierarchyLibrarySync 2 "updatesignal=1, libraryname=PartLibrary"
*endnotehistorystate {Synchronized Library}
*clearmarkall 3
*setelementcolormode 16
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 1
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 16
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*clearmarkall 3
*clearmark collections 1
*clearmark collections 2
*clearmark controllers 1
*loaddefaultattributevaluesfromxml 
*rotateabout 0 0 0 0
*rotateabout 0 0 0 0
# Session ended at "6-6-2026  1:45:58"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  1:46:06"
*createstringarray 17 " 0 penalty value              0.00    0.00    0.80    1.00   10.00" \
  "  1 min length        1 1.0  10.000   9.000   4.000   2.000   1.000    1   59    0" \
  "  2 max length        1 1.0  10.000  12.000  15.000  20.000  30.000    0   39    1" \
  "  3 aspect ratio      1 1.0   1.000   2.000   4.400   5.000  10.000    0   41    2" \
  "  4 warpage           1 1.0   0.000   5.000  13.000  15.000  30.000    0   56    3" \
  "  5 max angle quad    1 1.0  90.000 110.000 134.000 140.000 160.000    0   28    4" \
  "  6 min angle quad    1 1.0  90.000  70.000  46.000  40.000  20.000    0   61    5" \
  "  7 max angle tria    1 1.0  60.000  80.000 112.000 120.000 150.000    0   19    6" \
  "  8 min angle tria    1 1.0  60.000  50.000  34.000  30.000  15.000    0   22    7" \
  "  9 skew              1 1.0   0.000  10.000  34.000  40.000  70.000    0   46    8" \
  " 10 jacobian          1 1.0   1.000   0.900   0.700   0.600   0.300    0   57    9" \
  " 11 chordal dev       0 1.0   0.000   0.300   0.800   1.000   2.000    0   29   10" \
  " 12 taper             1 1.0   0.000   0.200   0.500   0.600   0.900    0   53   11" \
  " 13 % of trias        1 1.0   0.000   6.000  10.000  15.000  20.000    0    0   -1" \
  " 14 QI color legend            32      32       7       6       3           3   -1" \
  " 15 time_step         1      10.000                   0.010            0   59   12" \
  "   Global_solver 0"
*setqualitycriteria 1 17 0
*menufilterset "*"
*menufilterdisable 
*viewset 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 10 10
*viewset 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 10 10
*readfile "F:\\Dyna-mcp\\output\\test2.hm"
*setgeomrefinelevel 1
*menufont 2
*setsolverusessegmentsets 0
*ME_CoreBehaviorAdjust "allowable_actions_policy=TC_lite"
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*startnotehistorystate {Synchronized Library}
*ME_ModulesHierarchyLibrarySync 2 "updatesignal=1, libraryname=PartLibrary"
*endnotehistorystate {Synchronized Library}
*clearmarkall 3
*setelementcolormode 16
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 1
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 16
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*clearmarkall 3
*clearmark collections 1
*clearmark collections 2
*clearmark controllers 1
*loaddefaultattributevaluesfromxml 
*rotateabout 0 0 0 0
*viewset 0.735468208 0.242989415 0.632489256 0 -0.461919471 0.862743718 0.205678582 0 -0.495698414 -0.443429161 0.746762118 0 -9.23838942 -2.74512564 4.11357165 1 -27.5000003 -53.0000004 27.5000003 13.0000004
# Session ended at "6-6-2026  1:47:13"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  1:49:13"
*createstringarray 17 " 0 penalty value              0.00    0.00    0.80    1.00   10.00" \
  "  1 min length        1 1.0  10.000   9.000   4.000   2.000   1.000    1   59    0" \
  "  2 max length        1 1.0  10.000  12.000  15.000  20.000  30.000    0   39    1" \
  "  3 aspect ratio      1 1.0   1.000   2.000   4.400   5.000  10.000    0   41    2" \
  "  4 warpage           1 1.0   0.000   5.000  13.000  15.000  30.000    0   56    3" \
  "  5 max angle quad    1 1.0  90.000 110.000 134.000 140.000 160.000    0   28    4" \
  "  6 min angle quad    1 1.0  90.000  70.000  46.000  40.000  20.000    0   61    5" \
  "  7 max angle tria    1 1.0  60.000  80.000 112.000 120.000 150.000    0   19    6" \
  "  8 min angle tria    1 1.0  60.000  50.000  34.000  30.000  15.000    0   22    7" \
  "  9 skew              1 1.0   0.000  10.000  34.000  40.000  70.000    0   46    8" \
  " 10 jacobian          1 1.0   1.000   0.900   0.700   0.600   0.300    0   57    9" \
  " 11 chordal dev       0 1.0   0.000   0.300   0.800   1.000   2.000    0   29   10" \
  " 12 taper             1 1.0   0.000   0.200   0.500   0.600   0.900    0   53   11" \
  " 13 % of trias        1 1.0   0.000   6.000  10.000  15.000  20.000    0    0   -1" \
  " 14 QI color legend            32      32       7       6       3           3   -1" \
  " 15 time_step         1      10.000                   0.010            0   59   12" \
  "   Global_solver 0"
*setqualitycriteria 1 17 0
*menufilterset "*"
*menufilterdisable 
*viewset 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 10 10
*viewset 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 10 10
*readfile "F:\\Dyna-mcp\\output\\test4.hm"
*setgeomrefinelevel 1
*menufont 2
*setsolverusessegmentsets 0
*ME_CoreBehaviorAdjust "allowable_actions_policy=TC_lite"
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*startnotehistorystate {Synchronized Library}
*ME_ModulesHierarchyLibrarySync 2 "updatesignal=1, libraryname=PartLibrary"
*endnotehistorystate {Synchronized Library}
*clearmarkall 3
*setelementcolormode 16
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 1
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 16
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*clearmarkall 3
*clearmark collections 1
*clearmark collections 2
*clearmark controllers 1
*loaddefaultattributevaluesfromxml 
# Session ended at "6-6-2026  1:50:51"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  2:17:31"
*createstringarray 17 " 0 penalty value              0.00    0.00    0.80    1.00   10.00" \
  "  1 min length        1 1.0  10.000   9.000   4.000   2.000   1.000    1   59    0" \
  "  2 max length        1 1.0  10.000  12.000  15.000  20.000  30.000    0   39    1" \
  "  3 aspect ratio      1 1.0   1.000   2.000   4.400   5.000  10.000    0   41    2" \
  "  4 warpage           1 1.0   0.000   5.000  13.000  15.000  30.000    0   56    3" \
  "  5 max angle quad    1 1.0  90.000 110.000 134.000 140.000 160.000    0   28    4" \
  "  6 min angle quad    1 1.0  90.000  70.000  46.000  40.000  20.000    0   61    5" \
  "  7 max angle tria    1 1.0  60.000  80.000 112.000 120.000 150.000    0   19    6" \
  "  8 min angle tria    1 1.0  60.000  50.000  34.000  30.000  15.000    0   22    7" \
  "  9 skew              1 1.0   0.000  10.000  34.000  40.000  70.000    0   46    8" \
  " 10 jacobian          1 1.0   1.000   0.900   0.700   0.600   0.300    0   57    9" \
  " 11 chordal dev       0 1.0   0.000   0.300   0.800   1.000   2.000    0   29   10" \
  " 12 taper             1 1.0   0.000   0.200   0.500   0.600   0.900    0   53   11" \
  " 13 % of trias        1 1.0   0.000   6.000  10.000  15.000  20.000    0    0   -1" \
  " 14 QI color legend            32      32       7       6       3           3   -1" \
  " 15 time_step         1      10.000                   0.010            0   59   12" \
  "   Global_solver 0"
*setqualitycriteria 1 17 0
*menufilterset "*"
*menufilterdisable 
*viewset 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 10 10
*viewset 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 10 10
*readfile "F:\\Dyna-mcp\\output\\test8_daota_lou.HM"
*setgeomrefinelevel 1
*menufont 2
*setsolverusessegmentsets 0
*ME_CoreBehaviorAdjust "allowable_actions_policy=TC_lite"
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 16
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 1
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*setelementcolormode 16
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*settopologydisplaymode 0
*clearmarkall 3
*clearmarkall 3
*clearmark collections 1
*clearmark collections 2
*clearmark controllers 1
*loaddefaultattributevaluesfromxml 
# Session ended at "6-6-2026  11:18:21"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
