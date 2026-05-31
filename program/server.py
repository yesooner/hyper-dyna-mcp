"""Dyna-mcp MCP server. Registers tools for CAE workflow automation."""

from __future__ import annotations

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from program.tools.env_check import check_environment
from program.tools.k_parser import parse_k_file
from program.tools.k_writer import KModel, Material, Part, Section, write_k_file, generate_k_content
from program.tools.lsdyna_runner import generate_solver_command, run_lsdyna
from program.tools.obsidian_logger import write_execution_log
from program.tools.path_tools import load_yaml, validate_path

# Phase 2 modules — import guarded for missing dependencies
try:
    from program.tools.lsdyna_log_parser import parse_messag
except ImportError:
    parse_messag = None  # type: ignore[assignment]

try:
    from program.tools.hm_runner import (
        generate_hmbatch_command,
        run_hmbatch,
        check_hypermesh_connection,
    )
    from program.tools.hm_tcl_generator import (
        generate_surface_automesh_tcl,
        generate_solid_mesh_tcl,
        generate_info_tcl,
        generate_save_tcl,
        validate_tcl_script,
    )
    from program.tools.hm_policy import check_meshing_rules
except ImportError:
    generate_hmbatch_command = None  # type: ignore[assignment]
    run_hmbatch = None  # type: ignore[assignment]
    check_hypermesh_connection = None  # type: ignore[assignment]
    generate_surface_automesh_tcl = None  # type: ignore[assignment]
    generate_solid_mesh_tcl = None  # type: ignore[assignment]
    generate_info_tcl = None  # type: ignore[assignment]
    generate_save_tcl = None  # type: ignore[assignment]
    validate_tcl_script = None  # type: ignore[assignment]
    check_meshing_rules = None  # type: ignore[assignment]

try:
    from program.tools.lsprepost_runner import generate_lsprepost_command, run_lsprepost
    from program.tools.cfile_generator import (
        generate_cfile,
        generate_post_processing,
        generate_export_png,
    )
except ImportError:
    generate_lsprepost_command = None  # type: ignore[assignment]
    run_lsprepost = None  # type: ignore[assignment]
    generate_cfile = None  # type: ignore[assignment]
    generate_post_processing = None  # type: ignore[assignment]
    generate_export_png = None  # type: ignore[assignment]

try:
    from program.tools.hm_gui import (
        execute_tcl_gui,
        save_listener_tcl,
        generate_listener_tcl,
    )
except ImportError:
    execute_tcl_gui = None  # type: ignore[assignment]
    save_listener_tcl = None  # type: ignore[assignment]
    generate_listener_tcl = None  # type: ignore[assignment]

try:
    from program.tools.lsprepost_ipc import generate_cfile_commands, write_cfile
except ImportError:
    generate_cfile_commands = None  # type: ignore[assignment]
    write_cfile = None  # type: ignore[assignment]

server = Server("dyna-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="check_environment",
            description="Check Python version, conda env, and required packages",
            inputSchema={
                "type": "object",
                "properties": {
                    "required_packages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Package names to check (default: mcp, pydantic, yaml, loguru)",
                    },
                },
            },
        ),
        Tool(
            name="load_path_config",
            description="Load a YAML path configuration file from path/ directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Config name without .yaml extension (e.g., local_paths, lsdyna_paths)",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="validate_path",
            description="Check if a filesystem path exists",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Filesystem path to check"},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="parse_k_file",
            description="Parse an LS-DYNA .k keyword file and return structured data with validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to .k file"},
                },
                "required": ["filepath"],
            },
        ),
        Tool(
            name="write_k_file",
            description="Generate an LS-DYNA .k keyword file from parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Output .k file path"},
                    "title": {"type": "string", "default": "Generated Model"},
                    "termination_time": {"type": "number", "default": 0.001},
                    "material": {
                        "type": "object",
                        "properties": {
                            "mid": {"type": "integer"},
                            "rho": {"type": "number"},
                            "e": {"type": "number"},
                            "pr": {"type": "number"},
                        },
                    },
                },
                "required": ["filepath"],
            },
        ),
        Tool(
            name="generate_lsdyna_command",
            description="Generate LS-DYNA solver command (dry_run by default — does not execute)",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Path to .k input file"},
                    "ncpus": {"type": "integer", "description": "Number of CPU cores"},
                    "memory": {"type": "string", "description": "Memory allocation (e.g., 200m)"},
                    "dry_run": {"type": "boolean", "default": True, "description": "If true, only generate command"},
                },
                "required": ["input_file"],
            },
        ),
        Tool(
            name="write_obsidian_log",
            description="Write execution log entry to Obsidian vault",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Task description"},
                    "modified_files": {"type": "array", "items": {"type": "string"}},
                    "commands": {"type": "array", "items": {"type": "string"}},
                    "test_results": {"type": "string"},
                    "next_steps": {"type": "string"},
                    "log_type": {"type": "string", "enum": ["execution", "workflow", "validation"], "default": "execution"},
                },
                "required": ["task"],
            },
        ),
        Tool(
            name="generate_solver_command",
            description="Generate LS-DYNA solver command line (dry_run by default)",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Path to .k input file"},
                    "ncpus": {"type": "integer", "description": "Number of CPU cores"},
                    "memory": {"type": "string", "description": "Memory allocation (e.g., 200m)"},
                },
                "required": ["input_file"],
            },
        ),
        Tool(
            name="parse_solver_log",
            description="Parse LS-DYNA output log (messag file) for termination status and errors",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to messag file"},
                },
                "required": ["filepath"],
            },
        ),
        Tool(
            name="generate_hmbatch_command",
            description="Generate HyperMesh hmbatch command from Tcl script (dry_run only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "tcl_script": {"type": "string", "description": "Path to .tcl script or Tcl script content"},
                    "model_file": {"type": "string", "description": "Path to .hm model file (optional)"},
                },
                "required": ["tcl_script"],
            },
        ),
        Tool(
            name="execute_hmbatch",
            description="Execute a Tcl script via hmbatch.exe (dry_run by default)",
            inputSchema={
                "type": "object",
                "properties": {
                    "tcl_script": {"type": "string", "description": "Path to .tcl file or inline Tcl content"},
                    "model_file": {"type": "string", "description": "Path to .hm model file (optional)"},
                    "dry_run": {"type": "boolean", "default": True},
                    "timeout": {"type": "integer", "default": 300, "description": "Timeout in seconds"},
                },
                "required": ["tcl_script"],
            },
        ),
        Tool(
            name="generate_tcl_script",
            description="Generate a HyperMesh Tcl script (surface automesh, solid mesh, info, save)",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_type": {
                        "type": "string",
                        "enum": ["surface_automesh", "solid_mesh", "info", "save"],
                        "description": "Type of Tcl script to generate",
                    },
                    "element_size": {"type": "number", "description": "Element size (for automesh/solid_mesh)"},
                    "output_hm_path": {"type": "string", "description": "Path to save .hm file (optional)"},
                },
                "required": ["script_type"],
            },
        ),
        Tool(
            name="check_hypermesh_connection",
            description="Verify hmbatch.exe is accessible and configured",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="execute_lsprepost",
            description="Execute an LS-PrePost cfile (dry_run by default)",
            inputSchema={
                "type": "object",
                "properties": {
                    "cfile": {"type": "string", "description": "Path to .cfile command file"},
                    "dry_run": {"type": "boolean", "default": True},
                    "timeout": {"type": "integer", "default": 600},
                },
                "required": ["cfile"],
            },
        ),
        Tool(
            name="generate_cfile",
            description="Generate an LS-PrePost cfile script from commands",
            inputSchema={
                "type": "object",
                "properties": {
                    "commands": {"type": "array", "items": {"type": "string"}, "description": "LS-PrePost commands"},
                    "output_path": {"type": "string", "description": "Path to save the cfile"},
                },
                "required": ["commands"],
            },
        ),
        Tool(
            name="generate_post_processing_cfile",
            description="Generate a post-processing cfile (open d3plot, stress contour, export PNG)",
            inputSchema={
                "type": "object",
                "properties": {
                    "d3plot_path": {"type": "string", "description": "Path to d3plot file"},
                    "output_dir": {"type": "string", "description": "Directory for output images"},
                    "views": {"type": "array", "items": {"type": "string"}, "description": "Views to capture (front, top, iso, right)"},
                },
                "required": ["d3plot_path", "output_dir"],
            },
        ),
        # --- GUI interaction tools ---
        Tool(
            name="start_hypermesh_gui_listener",
            description="Generate and save the HyperMesh GUI listener Tcl script",
            inputSchema={
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "default": 47881, "description": "Listener port"},
                },
            },
        ),
        Tool(
            name="execute_tcl_gui",
            description="Execute Tcl in HyperMesh GUI via socket listener (requires listener running)",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "Tcl script to execute"},
                    "model_path": {"type": "string", "description": "Path to .hm file to load first"},
                    "output_hm_path": {"type": "string", "description": "Path to save .hm file after"},
                    "timeout": {"type": "integer", "default": 120},
                },
                "required": ["script"],
            },
        ),
        # (LS-PrePost IPC removed — LS-PrePost 4.8 does not support Tcl via cfile)
                },
                "required": ["action"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "check_environment":
        pkgs = arguments.get("required_packages")
        report = check_environment(pkgs)
        import json
        return [TextContent(type="text", text=json.dumps(report.to_dict(), indent=2))]

    elif name == "load_path_config":
        data = load_yaml(arguments["name"])
        import json
        return [TextContent(type="text", text=json.dumps(data, indent=2))]

    elif name == "validate_path":
        ok = validate_path(arguments["path"])
        return [TextContent(type="text", text=f"Path exists: {ok}" if ok else f"Path NOT found: {arguments['path']}")]

    elif name == "parse_k_file":
        kfile = parse_k_file(arguments["filepath"])
        errors = kfile.validate()
        parts = kfile.get_parts()
        mats = kfile.get_materials()
        lines = [
            f"Title: {kfile.title}",
            f"Keywords: {len(kfile.keywords)}",
            f"Parts: {len(parts)}",
            f"Materials: {len(mats)}",
            f"Validation errors: {len(errors)}",
        ]
        for e in errors:
            lines.append(f"  ERROR: {e}")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "write_k_file":
        mat_data = arguments.get("material", {})
        model = KModel(
            title=arguments.get("title", "Generated Model"),
            termination_time=arguments.get("termination_time", 0.001),
        )
        if mat_data:
            model.materials.append(Material(
                mid=mat_data.get("mid", 1),
                rho=mat_data.get("rho", 7.85e-9),
                e=mat_data.get("e", 210000.0),
                pr=mat_data.get("pr", 0.3),
            ))
        content = write_k_file(model, arguments["filepath"])
        return [TextContent(type="text", text=f"Wrote K file: {arguments['filepath']}\n{len(content)} bytes")]

    elif name == "generate_lsdyna_command":
        dry_run = arguments.get("dry_run", True)
        result = run_lsdyna(
            input_file=arguments["input_file"],
            dry_run=dry_run,
            ncpus=arguments.get("ncpus"),
            memory=arguments.get("memory"),
        )
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "write_obsidian_log":
        entry = write_execution_log(
            task=arguments["task"],
            modified_files=arguments.get("modified_files"),
            commands=arguments.get("commands"),
            test_results=arguments.get("test_results"),
            next_steps=arguments.get("next_steps"),
            log_type=arguments.get("log_type", "execution"),
        )
        return [TextContent(type="text", text=f"Log written.\n{entry[:200]}...")]

    elif name == "generate_solver_command":
        result = generate_solver_command(
            input_file=arguments["input_file"],
            ncpus=arguments.get("ncpus"),
            memory=arguments.get("memory"),
        )
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "parse_solver_log":
        if parse_messag is None:
            return [TextContent(type="text", text="Error: lsdyna_log_parser not available (missing loguru)")]
        log = parse_messag(arguments["filepath"])
        lines = [
            f"File: {log.filepath}",
            f"Termination: {log.termination_status or 'unknown'}",
            f"Warnings: {len(log.warnings)}",
            f"Errors: {len(log.errors)}",
        ]
        for w in log.warnings[:5]:
            lines.append(f"  WARN: {w}")
        for e in log.errors[:5]:
            lines.append(f"  ERROR: {e}")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "generate_hmbatch_command":
        if generate_hmbatch_command is None:
            return [TextContent(type="text", text="Error: hm_runner not available")]
        cmd = generate_hmbatch_command(
            tcl_script=arguments["tcl_script"],
            model_file=arguments.get("model_file"),
        )
        return [TextContent(type="text", text=f"Command: {' '.join(cmd)}")]

    elif name == "execute_hmbatch":
        if run_hmbatch is None:
            return [TextContent(type="text", text="Error: hm_runner not available")]
        result = run_hmbatch(
            tcl_script=arguments["tcl_script"],
            model_file=arguments.get("model_file"),
            dry_run=arguments.get("dry_run", True),
            timeout=arguments.get("timeout", 300),
        )
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    elif name == "generate_tcl_script":
        script_type = arguments["script_type"]
        if script_type == "surface_automesh":
            if generate_surface_automesh_tcl is None:
                return [TextContent(type="text", text="Error: hm_tcl_generator not available")]
            script = generate_surface_automesh_tcl(
                element_size=arguments.get("element_size", 2.0),
                output_hm_path=arguments.get("output_hm_path"),
            )
        elif script_type == "solid_mesh":
            if generate_solid_mesh_tcl is None:
                return [TextContent(type="text", text="Error: hm_tcl_generator not available")]
            script = generate_solid_mesh_tcl(
                element_size=arguments.get("element_size", 3.0),
                output_hm_path=arguments.get("output_hm_path"),
            )
        elif script_type == "info":
            if generate_info_tcl is None:
                return [TextContent(type="text", text="Error: hm_tcl_generator not available")]
            script = generate_info_tcl()
        elif script_type == "save":
            if generate_save_tcl is None:
                return [TextContent(type="text", text="Error: hm_tcl_generator not available")]
            output = arguments.get("output_hm_path", "model.hm")
            script = generate_save_tcl(output)
        else:
            return [TextContent(type="text", text=f"Unknown script_type: {script_type}")]
        return [TextContent(type="text", text=script)]

    elif name == "check_hypermesh_connection":
        if check_hypermesh_connection is None:
            return [TextContent(type="text", text="Error: hm_runner not available")]
        result = check_hypermesh_connection()
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "execute_lsprepost":
        if run_lsprepost is None:
            return [TextContent(type="text", text="Error: lsprepost_runner not available")]
        result = run_lsprepost(
            cfile=arguments["cfile"],
            dry_run=arguments.get("dry_run", True),
            timeout=arguments.get("timeout", 600),
        )
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    elif name == "generate_cfile":
        if generate_cfile is None:
            return [TextContent(type="text", text="Error: cfile_generator not available")]
        content = generate_cfile(
            commands=arguments["commands"],
            output_path=arguments.get("output_path"),
        )
        return [TextContent(type="text", text=content)]

    elif name == "generate_post_processing_cfile":
        if generate_post_processing is None:
            return [TextContent(type="text", text="Error: cfile_generator not available")]
        content = generate_post_processing(
            d3plot_path=arguments["d3plot_path"],
            output_dir=arguments["output_dir"],
            views=arguments.get("views"),
        )
        return [TextContent(type="text", text=content)]

    # --- GUI interaction handlers ---

    elif name == "start_hypermesh_gui_listener":
        if save_listener_tcl is None:
            return [TextContent(type="text", text="Error: hm_gui not available")]
        path = save_listener_tcl(port=arguments.get("port", 47881))
        return [TextContent(type="text", text=(
            f"Listener Tcl saved to: {path}\n\n"
            "To activate:\n"
            "1. Open HyperMesh GUI\n"
            "2. In HyperMesh Tcl console, run:\n"
            f"   source \"{path}\"\n"
            "3. You should see: 'Dyna-mcp GUI listener ready on 127.0.0.1:47881'\n"
            "4. Then use execute_tcl_gui to send commands"
        ))]

    elif name == "execute_tcl_gui":
        if execute_tcl_gui is None:
            return [TextContent(type="text", text="Error: hm_gui not available")]
        result = execute_tcl_gui(
            script=arguments["script"],
            model_path=arguments.get("model_path"),
            output_hm_path=arguments.get("output_hm_path"),
            timeout=arguments.get("timeout", 120),
        )
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
