"""LS-PrePost cfile (command file) generation.

cfiles are simple text scripts that LS-PrePost executes line by line.
Common commands: open, close, view, export, query.
"""

from __future__ import annotations

from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def generate_cfile(commands: list[str], output_path: str | None = None) -> str:
    """Generate a cfile script from a list of commands.

    Args:
        commands: List of LS-PrePost commands (one per line).
        output_path: Optional path to save the cfile.

    Returns:
        The cfile content string.
    """
    lines = [cmd for cmd in commands]
    content = "\n".join(lines) + "\n"

    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info(f"Wrote cfile: {path}")

    return content


def generate_open_d3plot(d3plot_path: str) -> list[str]:
    """Generate commands to open a d3plot file."""
    return [f"open d3plot {d3plot_path}"]


def generate_open_key(key_path: str) -> list[str]:
    """Generate commands to open a keyword file."""
    return [f"open key {key_path}"]


def generate_undeformed() -> list[str]:
    """Generate commands to show undeformed shape."""
    return ["plot undeform all 1"]


def generate_deformed(scale: float = 1.0) -> list[str]:
    """Generate commands to show deformed shape.

    Args:
        scale: Deformation scale factor.
    """
    return [f"plot deform all 1 {scale}"]


def generate_stress_contour(component: str = "von_mises") -> list[str]:
    """Generate commands to display stress contour.

    Args:
        component: Stress component (von_mises, sig_xx, sig_yy, sig_zz, sig_xy, sig_yz, sig_zx).
    """
    component_map = {
        "von_mises": "1",
        "sig_xx": "2",
        "sig_yy": "3",
        "sig_zz": "4",
        "sig_xy": "5",
        "sig_yz": "6",
        "sig_zx": "7",
    }
    cid = component_map.get(component, "1")
    return [
        f"result {cid}",
        "fringe stress",
        "plot fringe all 1",
    ]


def generate_strain_contour() -> list[str]:
    """Generate commands to display effective plastic strain contour."""
    return [
        "result 1",
        "fringe塑性应变",
        "plot fringe all 1",
    ]


def generate_energy_plot() -> list[str]:
    """Generate commands to display energy time history."""
    return [
        "xypLOT energy",
    ]


def generate_export_png(output_path: str, width: int = 1920, height: int = 1080) -> list[str]:
    """Generate commands to export viewport as PNG.

    Args:
        output_path: Path for the output PNG file.
        width: Image width in pixels.
        height: Image height in pixels.
    """
    return [
        f"set screen width {width}",
        f"set screen height {height}",
        f"capture viewport {output_path}",
    ]


def generate_screenshot_set(output_dir: str, prefix: str = "frame") -> list[str]:
    """Generate commands to export multiple views.

    Args:
        output_dir: Directory for output images.
        prefix: Filename prefix.
    """
    return [
        f"set screen width 1920",
        f"set screen height 1080",
        f"capture viewport {output_dir}/{prefix}_front.png",
        "view front",
        f"capture viewport {output_dir}/{prefix}_top.png",
        "view top",
        f"capture viewport {output_dir}/{prefix}_iso.png",
        "view iso",
    ]


def generate_post_processing(
    d3plot_path: str,
    output_dir: str,
    views: list[str] | None = None,
) -> str:
    """Generate a complete post-processing cfile.

    Args:
        d3plot_path: Path to d3plot file.
        output_dir: Directory for output images.
        views: List of views to capture (front, top, iso, right). Default: all.

    Returns:
        Complete cfile content.
    """
    if views is None:
        views = ["front", "top", "iso"]

    commands: list[str] = []
    commands.extend(generate_open_d3plot(d3plot_path))
    commands.extend(generate_undeformed())
    commands.extend(generate_export_png(f"{output_dir}/undeformed.png"))

    commands.extend(generate_deformed())
    commands.extend(generate_stress_contour())
    commands.extend(generate_export_png(f"{output_dir}/stress_contour.png"))

    for view in views:
        commands.append(f"view {view}")
        commands.extend(generate_export_png(f"{output_dir}/deformed_{view}.png"))

    return generate_cfile(commands)
