# HyperMesh Tcl: Tetrahedral mesh generation
# Template for generating tetra mesh on selected components
# TODO: Verify mesh commands against your HM version

*createmark components 1 "{{component_name}}"
*mesh10_components 1 {{element_size}}

# Quality check
*checkelems_quality 1 1 0 0 1 0 0 0 0 0 0 0 0 0 0 0
