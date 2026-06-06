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
*begin "version 2021.0.0.33  6-6-2026  13:56:30"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
# Session ended at "6-6-2026  14:00:44"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  14:00:56"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
*createentity mats name="MAT_ELASTIC_1" cardimage=MAT_ELASTIC
*setvalue mats id=1 STATUS=2
*setvalue mats id=1
# Session ended at "6-6-2026  14:41:47"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  14:42:12"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
*createentity mats name="MAT_ELASTIC_100" cardimage=MAT_ELASTIC
*setvalue mats id=100 STATUS=2
*createentity cards name="TERMINATION" cardimage=CONTROL_TERMINATION
*setvalue cards id=1
*rotateabout 0 0 0 0
*createentity mats name="MAT_ELASTIC_100" cardimage=MAT_ELASTIC
*setvalue mats id=100 STATUS=2
*setvalue mats id=100
*createentity mats name=TEST_MAT
*createentity mats name=TEST_MAT2 cardimage=MAT_ELASTIC
*createentity mats name="TEST_MAT3"
*createentity mats name=MAT_TEST_200 cardimage=MAT_ELASTIC
*createentity mats name=MAT_TEST_201 cardimage=MAT_ELASTIC
*setvalue mats id=201 STATUS=2
*createentity mats name=MAT_300 cardimage=MAT_ELASTIC
*setvalue mats id=300 STATUS=2
*setvalue mats id=300
*setvalue mats id=300
*setvalue mats id=300
*setvalue mats
*setvalue mats id=300
*setvalue mats id=300 STATUS=2
# Session ended at "6-6-2026  14:48:13"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  14:48:23"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
*createentity mats name=MAT_TEST_400 cardimage=MAT_ELASTIC
*setvalue mats id=400 STATUS=2
*createentity mats name="MAT_ELASTIC_500" cardimage=MAT_ELASTIC
*setvalue mats id=500 STATUS=2
*createentity props name="SECTION_SHELL_10" cardimage=SECTION_SHELL
*setvalue props id=10 STATUS=2
*createentity cards name="TERMINATION" cardimage=CONTROL_TERMINATION
*setvalue cards id=1
*createentity cards name="BINARY_D3PLOT" cardimage=DATABASE_BINARY_D3PLOT
*setvalue cards id=1
# Session ended at "6-6-2026  14:51:39"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  14:51:52"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
*createentity mats name="MAT_ELASTIC_600" cardimage=MAT_ELASTIC
*setvalue mats id=600 STATUS=2
*createentity mats name="MAT_RIGID_601" cardimage=MAT_RIGID
*setvalue mats id=601 STATUS=2
*createentity props name="SECTION_SHELL_600" cardimage=SECTION_SHELL
*setvalue props id=600 STATUS=2
*createentity props name="SECTION_SOLID_601" cardimage=SECTION_SOLID
*setvalue props id=601 STATUS=2
*createentity cards name="TERMINATION" cardimage=CONTROL_TERMINATION
*setvalue cards id=1
*createentity cards name="TIMESTEP" cardimage=CONTROL_TIMESTEP
*setvalue cards id=1
*createentity cards name="BINARY_D3PLOT" cardimage=DATABASE_BINARY_D3PLOT
*setvalue cards id=1
*createentity cards name="GLSTAT" cardimage=DATABASE_GLSTAT
*setvalue cards id=1
*currentcollector titles ""
*feoutputwithdata "F:/hyper-dyna-mcp/output/test8_export.k" "" 0 0 0 1 0
*feoutputwithdata "F:/hyper-dyna-mcp/output/test8_export.k" "" 0 0 0 1 0
*feinputwithdata "E:/HM2021/2021/hwdesktop/hm/templates/feoutput/lsdyna/lsyna.key" "" 0 0 0 0 0 1 0
*feinputwithdata "E:/HM2021/2021/hwdesktop/hm/templates/feoutput/lsdyna/lsyna.key" "" 0 0 0 0 0 1 0
*setvalue mats id=1 cardimage=MAT_ELASTIC
*setvalue mats id=1 cardimage=MAT_ELASTIC
*createentity mats name=TEST_LSDYNA cardimage=MAT_ELASTIC
*createentity mats name=TEST_LSDYNA cardimage=MAT_ELASTIC
*feinputwithdata "E:/HM2021/2021/hwdesktop/hm/templates/feoutput/lsdyna/lsyna.key" "" 0 0 0 0 0 1 0
*feinputwithdata "E:/HM2021/2021/hwdesktop/hm/templates/feoutput/lsdyna/lsyna.key" "" 0 0 0 0 0 1 0
*feinputwithdata "E:/HM2021/2021/hwdesktop/hm/templates/feoutput/lsdyna/lsyna.key" "" 0 0 0 0 0 1 0
*setvalue mats id=1 cardimage=MAT_ELASTIC
*setvalue mats id=2 cardimage=MAT_ELASTIC
*setvalue mats id=3 cardimage=MAT_ELASTIC
*setvalue mats id=4 cardimage=MAT_ELASTIC
*setvalue mats id=5 cardimage=MAT_ELASTIC
*setvalue mats id=6 cardimage=MAT_ELASTIC
*setvalue mats id=7 cardimage=MAT_ELASTIC
*setvalue props id=1 cardimage=SECTION_SOLID
*setvalue props id=2 cardimage=SECTION_SOLID
*setvalue mats id=1 cardimage=MAT_ELASTIC
*setvalue mats id=1 cardimage=MATL
*createmark materials 1 "mat_3"
*attributeupdatestringmark materials 1 0 0 0 0 ""
*attributeupdatestring materials 1 0 0 0 0 ""
*setvalue mats id=1 STATUS=ACTIVE
*setvalue mats id=1
*setvalue mats id=1 id=1 cardimage=MAT_ELASTIC
*setvalue mats id=1 STATUS=ACTIVE
*setvalue mats id=1
*setvalue mats id=1 cardimage=MATL1
*setvalue mats id=1 cardimage={/lsdyna/MATL1}
*setvalue mats id=1 cardimage=lsdyna/MATL1
*feinputwithdata "E:/HM2021/2021/hwdesktop/hm/templates/feoutput/lsdyna/lsyna.key" "" 0 0 0 0 0 1 0
*setvalue mats id=1 cardimage=MAT_ELASTIC
*feinputwithdata "" "" 0 0 0 0 0 1 0
*begin "version 2021.0.0.33  6-6-2026  17:21:17"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
# Session ended at "6-6-2026  17:48:51"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  17:49:55"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
# Session ended at "6-6-2026  17:55:50"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  17:57:36"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
# Session ended at "6-6-2026  18:00:18"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  18:10:44"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
# Session ended at "6-6-2026  18:13:21"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  18:14:06"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
# Session ended at "6-6-2026  18:17:02"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  18:17:13"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
# Session ended at "6-6-2026  18:18:54"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  18:22:27"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
# Session ended at "6-6-2026  18:25:07"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  18:25:22"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
# Session ended at "6-6-2026  19:04:21"
return; # Stop script and return to application 
# *quit 1; # Uncomment to exit application
*begin "version 2021.0.0.33  6-6-2026  19:08:44"
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
*readfile "F:\\hyper-dyna-mcp\\output\\test8_daota_lou.hm"
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
*feinputwithdata "E:/HM2021/2021/hwdesktop/hm/templates/feoutput/lsdyna/lsyna.key" "" 0 0 0 0 0 1 0
*templatefileset "E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key"
*templatefileset "E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key"
*createmark materials 1
*deletemark materials 1
*createentity mats name=CODEX_MCP_TEMP_MAT_47882 cardimage=MAT_ELASTIC
*setvalue mats id=5
*createmark materials 1 "CODEX_MCP_TEMP_MAT_47882"
*deletemark materials 1
*createmark materials 1
*deletemark materials 1
*createentity mats name=CODEX_MCP_TEMP_MATL1_47882 cardimage=MATL1
*setvalue mats id=5
*createmark materials 1 "CODEX_MCP_TEMP_MATL1_47882"
*deletemark materials 1
*createmark materials 1
*deletemark materials 1
*createentity mats name=CODEX_MCP_TEMP_SYNTAX_47882 cardimage=MATL1
*setvalue mats id=5 STATUS=2
*setvalue mats id=5 STATUS=1
*setvalue mats id=5 183=7.85e-9 1=210000 2=0.3
*setvalue mats id=5
*setvalue mats id=5 E=210000
*createmark materials 1 "CODEX_MCP_TEMP_SYNTAX_47882"
*deletemark materials 1
*createmark materials 1
*deletemark materials 1
*createentity mats name=CODEX_MCP_TEMP_FIELDS_47882 cardimage=MATL1
*setvalue mats id=5 Rho=7.85e-9
*setvalue mats id=5
*setvalue mats id=5
*setvalue mats id=5
*setvalue mats id=5 Nu=0.3
*setvalue mats id=5
*setvalue mats id=5
*setvalue mats id=5
*setvalue mats id=5
*setvalue mats id=5
*setvalue mats id=5
*createmark materials 1 "CODEX_MCP_TEMP_FIELDS_47882"
*deletemark materials 1
*createmark materials 1
*deletemark materials 1
*createentity mats name="MAT_ELASTIC_47882001" cardimage=MATL1
*setvalue mats id=5 Rho=7.85e-09
*setvalue mats id=5 E=210000
*setvalue mats id=5 Nu=0.3
*createmark materials 1 "MAT_ELASTIC_47882001"
*deletemark materials 1
*createmark properties 1
*deletemark properties 1
*createentity props name=CODEX_MCP_TEMP_SECTSLD_47882 cardimage=SectSld
*setvalue props id=1
*setvalue props id=1
*setvalue props id=1
*setvalue props id=1
*setvalue props id=1
*setvalue props id=1
*setvalue props id=1
*createmark properties 1 "CODEX_MCP_TEMP_SECTSLD_47882"
*deletemark properties 1
*createmark properties 1
*deletemark properties 1
*createentity props name="SECTION_SOLID_47882002" cardimage=SectSld
*createmark properties 1 "SECTION_SOLID_47882002"
*deletemark properties 1
*createmark components 1
*deletemark components 1
*createmark materials 1
*deletemark materials 1
*createmark properties 1
*deletemark properties 1
*createentity mats name="MAT_ELASTIC_47882011" cardimage=MATL1
*setvalue mats id=5 Rho=7.85e-09
*setvalue mats id=5 E=210000
*setvalue mats id=5 Nu=0.3
*createentity props name="SECTION_SOLID_47882012" cardimage=SectSld
*createentity comps name="PART_BIND_TEST_47882"
*setvalue comps id=10000184 propertyid=1
*setvalue comps id=10000184 materialid=5
*setvalue comps id=10000184
*setvalue comps id=10000184
*setvalue comps id=10000184 property=1
*setvalue comps id=10000184 material=5
*createmark components 1 "PART_BIND_TEST_47882"
*deletemark components 1
*createmark properties 1 "SECTION_SOLID_47882012"
*deletemark properties 1
*createmark materials 1 "MAT_ELASTIC_47882011"
*deletemark materials 1
*createmark components 1
*deletemark components 1
*createmark properties 1
*deletemark properties 1
*createmark materials 1
*deletemark materials 1
*createentity mats name="MAT_ELASTIC_47882101" cardimage=MATL1
*setvalue mats id=5 Rho=7.85e-09
*setvalue mats id=5 E=210000
*setvalue mats id=5 Nu=0.3
*createentity props name="SECTION_SOLID_47882102" cardimage=SectSld
*createentity comps name="PART_CHAIN_47882"
*setvalue comps id=10000184 propertyid=1
*setvalue comps id=10000184 materialid=5
*createmark components 1 "PART_CHAIN_47882"
*deletemark components 1
*createmark properties 1 "SECTION_SOLID_47882102"
*deletemark properties 1
*createmark materials 1 "MAT_ELASTIC_47882101"
*deletemark materials 1
*createentity mats name=TEST_LSDYNA cardimage=MAT_ELASTIC
*setvalue mats id=1 cardimage=MAT_ELASTIC
*templatefileset "E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key"
*createmark cards 1
*deletemark cards 1
*createentity cards name=CODEX_TEMP_TERMIN_47882 cardimage=Termin
*setvalue cards id=29
*setvalue cards id=29
*setvalue cards id=29
*setvalue cards id=29
*setvalue cards id=29
*createmark cards 1 29
*deletemark cards 1
*templatefileset "E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key"
*createmark cards 1
*deletemark cards 1
*createentity cards name=CODEX_TEMP_TERMIN_47882 cardimage=Termin
*setvalue cards id=29 LSD_ENDTIM=0.012
*setvalue cards id=29 LSD_ENDCYCLE=100
*setvalue cards id=29 LSD_TSMIN=1e-8
*setvalue cards id=29 LSD_TERMRAT=0.0
*setvalue cards id=29 LSD_PERMASS=0.0
*setvalue cards id=29 LSD_NOSOL=0
*createmark cards 1 29
*deletemark cards 1
*createmark cards 1
*deletemark cards 1
*createentity cards name=CODEX_TEMP_DBPLOT_47882 cardimage=DBplot
*setvalue cards id=29 LSD_DT=1e-4
*setvalue cards id=29 LSD_LCID=0
*setvalue cards id=29 LSD_NOBEAM=0
*setvalue cards id=29 LSD_NPLTC=10
*setvalue cards id=29 LSD_PSID=0
*setvalue cards id=29 LSD_IOOPT=1
*createmark cards 1 29
*deletemark cards 1
*createentity cards name="CONTROL_TERMINATION" cardimage=Termin
*setvalue cards id=29 LSD_ENDTIM=0.012
*setvalue cards id=29 LSD_ENDCYCLE=100
*setvalue cards id=29 LSD_TSMIN=1e-08
*setvalue cards id=29 LSD_TERMRAT=0.0
*setvalue cards id=29 LSD_PERMASS=0.0
*setvalue cards id=29 LSD_NOSOL=0
*createmark cards 1 29
*deletemark cards 1
*createentity cards name="DATABASE_BINARY_D3PLOT" cardimage=DBplot
*setvalue cards id=29 LSD_DT=0.0001
*setvalue cards id=29 LSD_LCID=0
*setvalue cards id=29 LSD_NOBEAM=0
*setvalue cards id=29 LSD_NPLTC=10
*setvalue cards id=29 LSD_PSID=0
*setvalue cards id=29 LSD_IOOPT=1
*createmark cards 1 29
*deletemark cards 1
*setvalue mats id=1 cardimage=MAT_ELASTIC
*createentity mats name=TEST_MAT cardimage=MAT_ELASTIC
*setvalue mats name=TEST_MAT STATUS=2
*setvalue mats name=TEST_MAT
*setvalue mats id=1 cardimage=MAT_ELASTIC
*setvalue mats id=1 cardimage=MAT_ELASTIC
*setvalue mats id=1 STATUS=2
*setvalue mats id=1
*setvalue mats id=1 cardimage=MAT_ELASTIC
*setvalue mats id=1 cardimage=MAT_ELASTIC
*createentity mats name=TEST_MAT cardimage=MAT_ELASTIC
*templatefileset "E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key"
*setvalue mats id=1 cardimage=MAT_ELASTIC
*setvalue groups cardimage=CONTROL_TERMINATION
*setvalue groups cardimage=DATABASE_BINARY_D3PLOT
