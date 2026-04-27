from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from pyvis.network import Network

from .constants import LICENSE_COLOR, LicenseCategory, LICENSE_TO_CATEGORY
from .classifier import classify_license

def _shell_layout_by_depth(
    G: nx.DiGraph,
    depths: dict[str, int],
    root_label: str,
) -> dict:
    """Concentric-ring layout: root at centre, one ring per depth level."""
    from collections import defaultdict
    rings: dict[int, list] = defaultdict(list)
    rings[0].append(root_label)
    for node, d in depths.items():
        rings[d].append(node)
    nlist = [rings[k] for k in sorted(rings)]
    return nx.shell_layout(G, nlist=nlist)


LAYOUTS = ("shell", "spring", "kamada_kawai", "spectral", "circular")


def _build_pos(
    G: nx.DiGraph,
    layout: str,
    depths: Optional[dict[str, int]],
    root_label: str,
) -> dict:
    if layout == "shell":
        if depths:
            return _shell_layout_by_depth(G, depths, root_label)
        return nx.shell_layout(G)
    if layout == "spring":
        return nx.spring_layout(G, seed=42, k=2.5)
    if layout == "kamada_kawai":
        return nx.kamada_kawai_layout(G)
    if layout == "spectral":
        return nx.spectral_layout(G)
    if layout == "circular":
        return nx.circular_layout(G)
    raise ValueError(f"Unknown layout: {layout!r}")


def draw_graph(
    G: nx.DiGraph,
    licenses: dict[str, str],
    output: Optional[Path],
    root_label: str = "project",
    depths: Optional[dict[str, int]] = None,
    layout: str = "shell",
) -> None:
    fig, ax = plt.subplots(figsize=(22, 14))
    ax.set_facecolor("#1e1e2e")
    fig.patch.set_facecolor("#1e1e2e")

    pos = _build_pos(G, layout, depths, root_label)

    # Node colors by license category
    node_colors = []
    for node in G.nodes():
        if node == root_label:
            node_colors.append("#2196f3")
        else:
            lic_str = licenses.get(node, "Unknown")
            lic_enum = classify_license(lic_str)
            cat = LICENSE_TO_CATEGORY.get(lic_enum, LicenseCategory.UNKNOWN)
            node_colors.append(LICENSE_COLOR.get(cat, LICENSE_COLOR[LicenseCategory.UNKNOWN]))

    # Node sizes
    node_sizes = [
        2800 if node == root_label else
        900 if G.in_degree(node) == 1 else 600
        for node in G.nodes()
    ]

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#555577", arrows=True, arrowsize=12, width=0.8)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes, alpha=0.92)

    # Labels
    labels = {}
    for node in G.nodes():
        if node == root_label:
            labels[node] = root_label
        else:
            lic = licenses.get(node, "?")
            lic_short = lic[:18] + "…" if len(lic) > 18 else lic
            labels[node] = f"{node}\n[{lic_short}]"

    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=6.5, font_color="white", font_weight="bold")

    # Legend
    legend_handles = [
        mpatches.Patch(color="#2196f3", label="Project (root)"),
        mpatches.Patch(color=LICENSE_COLOR[LicenseCategory.PERMISSIVE], label="Permissive (MIT, BSD, Apache…)"),
        mpatches.Patch(color=LICENSE_COLOR[LicenseCategory.WEAK_COPYLEFT], label="Weak Copyleft (LGPL, MPL…)"),
        mpatches.Patch(color=LICENSE_COLOR[LicenseCategory.COPYLEFT], label="Copyleft (GPL, AGPL)"),
        mpatches.Patch(color=LICENSE_COLOR[LicenseCategory.PROPRIETARY], label="Proprietary"),
        mpatches.Patch(color=LICENSE_COLOR[LicenseCategory.UNKNOWN], label="Unknown"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", framealpha=0.3, facecolor="#2a2a3e", labelcolor="white", fontsize=9)

    ax.set_title(f"Dependency license graph (nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()})", color="white", fontsize=13, pad=14)
    ax.axis("off")
    plt.tight_layout()

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, dpi=150, bbox_inches="tight")
        print(f"\n  Graph saved → {output}")
    plt.show()


def draw_interactive(
    G: nx.DiGraph,
    licenses: dict[str, str],
    output: Path,
    root_label: str = "project",
    depths: Optional[dict[str, int]] = None,
) -> None:
    net = Network(height="100vh", width="100%", directed=True, bgcolor="#1e1e2e", font_color="white")
    net.barnes_hut(spring_length=120, spring_strength=0.04, damping=0.09)

    for node in G.nodes():
        if node == root_label:
            color, size, label = "#2196f3", 35, root_label
            title = "Project root"
        else:
            lic_str = licenses.get(node, "Unknown")
            lic_enum = classify_license(lic_str)
            cat = LICENSE_TO_CATEGORY.get(lic_enum, LicenseCategory.UNKNOWN)
            color = LICENSE_COLOR.get(cat, LICENSE_COLOR[LicenseCategory.UNKNOWN])
            depth_val = depths[node] if depths and node in depths else "?"
            size = max(10, 28 - int(depth_val) * 5) if isinstance(depth_val, int) else 12
            label = node
            title = f"{node}\nLicense: {lic_str}\nCategory: {cat.value}\nDepth: {depth_val}"

        net.add_node(node, label=label, color=color, size=size, title=title, font={"size": 11})

    for src, dst in G.edges():
        net.add_edge(src, dst, color={"color": "#555577", "highlight": "#ffffff"}, arrows="to")

    output.parent.mkdir(parents=True, exist_ok=True)
    net.save_graph(str(output))
    print(f"\n  Interactive graph saved → {output}")
