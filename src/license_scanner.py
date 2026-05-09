"""
Dependency license scanner with recursive graph visualization.

Usage:
    python src/license_scanner.py [--depth 2] [--output wyniki/licenses.png]
"""

import sys
from pathlib import Path

import click

from scanner import find_dependencies, build_graph, print_table, write_jsonl, draw_graph, draw_interactive
from scanner.explain import explain_warnings
from scanner.visualization import LAYOUTS


class DepthType(click.ParamType):
    name = "depth"

    def convert(self, value, param, ctx):
        if isinstance(value, int):
            return value
        if str(value).lower() == "max":
            return None
        try:
            v = int(value)
            if v < 1:
                self.fail(f"{value!r} must be >= 1 or 'max'", param, ctx)
            return v
        except ValueError:
            self.fail(f"{value!r} is not an integer or 'max'", param, ctx)


@click.command()
@click.option(
    "--depth", default="2", show_default=True,
    type=DepthType(),
    help="Recursion depth, or 'max' for full BFS.",
)
@click.argument(
    "directory",
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--output",
    default=None,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output PNG path (e.g. wyniki/licenses.png).",
)
@click.option("--display", is_flag=True, default=False, help="Show matplotlib graph visualization.")
@click.option(
    "--browser",
    default=None,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Export interactive HTML graph (e.g. wyniki/graph.html).",
)
@click.option(
    "--layout", default="shell", show_default=True,
    type=click.Choice(LAYOUTS, case_sensitive=False),
    help="Graph layout algorithm.",
)
@click.option(
    "--out",
    default=None,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Save table to a file.",
)
@click.option(
    "--out-type", "out_type",
    default="pretty", show_default=True,
    type=click.Choice(["pretty", "jsonl"], case_sensitive=False),
    help="Output format for --out.",
)
@click.option(
    "--ai-explain", "ai_explain",
    is_flag=True, default=False,
    help="Use Gemini to explain license warnings (requires GOOGLE_API_KEY).",
)
def main(depth: int | None, directory: Path, output: Path | None, display: bool, browser: Path | None, layout: str, out: Path | None, out_type: str, ai_explain: bool) -> None:
    """Dependency license scanner with recursive graph visualization."""
    directory = directory.resolve()
    depth_label = "max" if depth is None else depth
    click.echo("\nDependency License Scanner")
    click.echo(f"  Directory : {directory}")
    click.echo(f"  Depth     : {depth_label}")
    click.echo()

    click.echo("Searching for dependency files...")
    packages = find_dependencies(directory)

    if not packages:
        click.echo("No dependencies found. Check pyproject.toml / requirements.txt.")
        sys.exit(1)

    click.echo(f"\nFound {len(packages)} direct dependencies:")
    for p in packages:
        click.echo(f"  • {p}")

    click.echo(f"\nBuilding graph (depth {depth_label})...")
    G, licenses, depths = build_graph(packages, depth=depth)

    print_table(licenses, depths=depths)

    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="") as f:
            if out_type == "jsonl":
                write_jsonl(licenses, depths=depths, file=f)
            else:
                print_table(licenses, depths=depths, file=f)
        click.echo(f"  Table saved → {out} ({out_type})")

    if ai_explain:
        click.echo("\nQuerying Gemini for license warning explanations...")
        explanation = explain_warnings(licenses)
        if explanation:
            click.echo("\n" + "─" * 78)
            click.echo("  AI EXPLANATION (Gemini)")
            click.echo("─" * 78)
            click.echo(explanation)
            click.echo("─" * 78 + "\n")
        else:
            click.echo("  No warnings to explain — all licenses are permissive.\n")

    if display:
        draw_graph(G, licenses, output=output, depths=depths, layout=layout)

    if browser:
        draw_interactive(G, licenses, output=browser, depths=depths)


if __name__ == "__main__":
    main()
