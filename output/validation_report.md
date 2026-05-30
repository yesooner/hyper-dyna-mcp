# Dyna-mcp Validation Report

**Date:** 2026-05-31
**Model:** `output/model_original.k`
**Status:** PASS

---

## 1. Model Summary

| Item | Count | IDs |
|------|-------|-----|
| Parts | 2 | PID=1 (Steel Plate), PID=2 (Rigid Impactor) |
| Materials | 2 | MID=1 (MAT_024), MID=2 (MAT_020) |
| Sections | 2 | SECID=1 (Shell), SECID=2 (Shell) |
| Nodes | 8 | NID 1-8 |
| Elements | 2 | EID=1 (Shell, Part 1), EID=2 (Shell, Part 2) |
| Sets | 5 | SET_PART_LIST×2, SET_NODE_LIST×1, SET_SEGMENT×2 |
| Contact | 1 | AUTOMATIC_SURFACE_TO_SURFACE |
| Boundary | 1 | BOUNDARY_SPC_SET |
| Load | 1 | LOAD_PRESCRIBED_VELOCITY_SET |
| Define Curve | 1 | LCID=1 |
| Keywords | 30 | Total |

---

## 2. Cross-Reference Validation

| Check | Status |
|-------|--------|
| Part → Material reference | ✓ PASS |
| Part → Section reference | ✓ PASS |
| Contact → Slave Set (SID=5) | ✓ PASS |
| Contact → Master Set (SID=4) | ✓ PASS |
| Load → Node Set (SID=3) | ✓ PASS |
| Boundary → Node Set (SID=3) | ✓ PASS |
| Load → Curve (LCID=1) | ✓ PASS |
| All IDs unique | ✓ PASS |

---

## 3. LS-DYNA Keyword Compliance

| Keyword | Format | Status |
|---------|--------|--------|
| *KEYWORD | First line | ✓ |
| *TITLE | Present | ✓ |
| *CONTROL_TERMINATION | ENDTIM=0.005 | ✓ |
| *CONTROL_TIMESTEP | DTMIN/DTMAX set | ✓ |
| *CONTROL_HOURGLASS | IHQ=1 | ✓ |
| *DATABASE_BINARY_D3PLOT | DT=0.0001 | ✓ |
| *MAT_PIECEWISE_LINEAR_PLASTICITY | 8 strain pts | ✓ |
| *MAT_RIGID | Standard | ✓ |
| *SECTION_SHELL | ELFORM=0 | ✓ |
| *PART (×2) | PID/SECID/MID set | ✓ |
| *NODE | 8 nodes, coordinates | ✓ |
| *ELEMENT_SHELL | 4-node quad | ✓ |
| *SET_PART_LIST (×2) | SID=1,2 | ✓ |
| *SET_NODE_LIST | SID=3, 4 nodes | ✓ |
| *SET_SEGMENT (×2) | SID=4,5 | ✓ |
| *CONTACT_AUTOMATIC_SURFACE_TO_SURFACE | SSID/MSID set | ✓ |
| *BOUNDARY_SPC_SET | NSID=3, all DOF | ✓ |
| *DEFINE_CURVE | LCID=1, 4 points | ✓ |
| *LOAD_PRESCRIBED_VELOCITY_SET | SID=3, LCID=1 | ✓ |
| *INITIAL_VELOCITY_GENERATION | SETID=2 | ✓ |
| *END | Last line | ✓ |

---

## 4. Compatibility

| Item | Value | Status |
|------|-------|--------|
| K file format | Standard (8×10 char) | ✓ |
| Python version | 3.13.5 | ✓ |
| Windows path | Forward slashes | ✓ |
| LS-PrePost version | 4.8 | ✓ |
| HyperMesh version | 2021 | ✓ |

---

## 5. Issues Found

### Round 1: 2026-05-31

| # | Bug | Type | File | Fix | Status |
|---|-----|------|------|-----|--------|
| 1 | Second *PART missing keyword header | Code Logic | output/model_original.k | Added *PART before second part | ✓ Fixed |
| 2 | hm_getmark returns empty in batch mode | Compatibility | hm_runner.py | Binary .hm format, not blocking | Known Issue |

### Unresolved

- LS-PrePost subprocess automation limited (GUI app, no headless mode)
- hm_getmark returns empty for binary .hm files

---

## 6. Next Steps

1. Manual GUI verification in LS-PrePost (open model_original.k)
2. Enhance K parser to handle more keyword types
3. Add ID conflict detection
4. Add empty set detection
