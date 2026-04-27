import networkx as nx
from .pypi import fetch_pypi_info

def build_graph(
    root_packages: list[str],
    depth: int | None,
    root_label: str = "project",
) -> tuple[nx.DiGraph, dict[str, str], dict[str, int]]:
    """
    Return (graph, {package: license}, {package: depth}).
    Graph: 'project' → level-1 deps → level-2 deps, etc.
    """
    G = nx.DiGraph()
    licenses: dict[str, str] = {}
    depths: dict[str, int] = {}
    G.add_node(root_label)
    licenses[root_label] = "Root"

    queue: list[tuple[str, int]] = [(pkg, 1) for pkg in root_packages]
    visited: set[str] = set(root_packages)

    for pkg in root_packages:
        G.add_edge(root_label, pkg)

    while queue:
        pkg, level = queue.pop(0)
        depths[pkg] = level

        print(f"  {'  ' * level}↳ {pkg} (depth {level})")
        info = fetch_pypi_info(pkg)
        licenses[pkg] = info["license"]

        if depth is None or level < depth:
            for dep in info["deps"]:
                G.add_edge(pkg, dep)
                if dep not in visited:
                    visited.add(dep)
                    queue.append((dep, level + 1))

        # Ensure every node in the graph has a license entry
        for node in list(G.nodes):
            if node != root_label and node not in licenses:
                info = fetch_pypi_info(node)
                licenses[node] = info["license"]
                if node not in depths:
                    depths[node] = level + 1

    return G, licenses, depths
