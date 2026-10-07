import streamlit as st
from typing import Dict, Tuple, List, Any, Optional
import heapq


# ---------- UCS core algorithm ----------
def uniform_cost_search(
    graph: Dict[str, Dict[str, float]],
    start: str,
    goal: Optional[str] = None,
) -> Tuple[List[str], float, List[str], Dict[str, float], Dict[str, Optional[str]], List[Dict[str, Any]]]:
    """
    Run Uniform Cost Search (Dijkstra) on a weighted directed graph.

    Returns
    - path: list of nodes from start to goal (empty if no goal or not found)
    - total_cost: total path cost (float('inf') if not found)
    - expanded_order: nodes expanded in order
    - best_cost: mapping node -> best known cost from start
    - parent: mapping node -> predecessor used to reconstruct path
    - trace: list of step-by-step snapshots (for UI/debug)
    """

    pq: List[Tuple[float, str]] = []  # (cost, node)
    heapq.heappush(pq, (0.0, start))
    best_cost: Dict[str, float] = {start: 0.0}
    parent: Dict[str, Optional[str]] = {start: None}
    visited: set[str] = set()
    expanded_order: List[str] = []
    trace: List[Dict[str, Any]] = []

    goal_found = goal is None  # if no goal specified, compute SPT

    while pq:
        cost, node = heapq.heappop(pq)

        # Skip stale entries
        if cost != best_cost.get(node, float("inf")):
            continue

        if node in visited:
            continue
        visited.add(node)
        expanded_order.append(node)

        # Snapshot for UI
        trace.append({
            "expanded": node,
            "cost": cost,
            "frontier": list(pq),
            "best_cost": dict(best_cost),
        })

        if goal is not None and node == goal:
            goal_found = True
            break

        for nbr, w in graph.get(node, {}).items():
            if w < 0:
                # UCS/Dijkstra assumes non-negative weights
                raise ValueError(f"Negative edge weight detected on {node}->{nbr}: {w}")

            new_cost = cost + float(w)
            if new_cost < best_cost.get(nbr, float("inf")):
                best_cost[nbr] = new_cost
                parent[nbr] = node
                heapq.heappush(pq, (new_cost, nbr))

    # Reconstruct path (only if a specific goal was requested and found)
    path: List[str] = []
    total = float("inf")
    if goal is not None and goal_found:
        total = best_cost.get(goal, float("inf"))
        if total != float("inf"):
            cur = goal
            while cur is not None:
                path.append(cur)
                cur = parent.get(cur)
            path.reverse()

    return path, total, expanded_order, best_cost, parent, trace


# ---------- Helpers ----------
def parse_edges(text: str, undirected: bool) -> Dict[str, Dict[str, float]]:
    """
    Parse edges from user input.
    Format per line: source,target,cost  (comma or whitespace separated)
    Ignores blank lines and lines starting with '#'.
    """
    graph: Dict[str, Dict[str, float]] = {}

    def ensure_node(node: str):
        if node not in graph:
            graph[node] = {}

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue

        # Allow either comma-separated or whitespace-separated
        parts = [p for p in line.replace(',', ' ').split() if p]
        if len(parts) != 3:
            raise ValueError(f"Invalid edge line: '{line}'. Expected: src dst cost")
        u, v, w = parts[0], parts[1], parts[2]
        try:
            w_val = float(w)
        except ValueError:
            raise ValueError(f"Invalid weight in line: '{line}'. Got '{w}'")

        ensure_node(u)
        ensure_node(v)
        graph[u][v] = w_val
        if undirected:
            graph[v][u] = w_val

    # Ensure isolated nodes captured if user listed them as 'X' alone (optional)
    return graph


def all_nodes(graph: Dict[str, Dict[str, float]]) -> List[str]:
    nodes = set(graph.keys())
    for u, nbrs in graph.items():
        nodes.update(nbrs.keys())
    return sorted(nodes)


def to_graphviz(graph: Dict[str, Dict[str, float]], path: List[str], directed: bool = True) -> str:
    """Build DOT source highlighting the found path."""
    is_on_path = set()
    for i in range(len(path) - 1):
        is_on_path.add((path[i], path[i + 1]))
        if not directed:
            is_on_path.add((path[i + 1], path[i]))

    rankdir = "LR"
    gtype = "digraph" if directed else "graph"
    arrow = "->" if directed else "--"

    lines = [
        f"{gtype} G {{",
        f"  rankdir={rankdir};",
        "  node [shape=circle, fontsize=12, fontname=Helvetica];",
    ]

    # Ensure nodes exist even if isolated
    nodes = all_nodes(graph)
    for n in nodes:
        lines.append(f'  "{n}";')

    for u, nbrs in graph.items():
        for v, w in nbrs.items():
            on_path = (u, v) in is_on_path
            color = "#d32f2f" if on_path else "#4285f4"
            penwidth = "3" if on_path else "1"
            lines.append(f'  "{u}" {arrow} "{v}" [label="{w}", color="{color}", penwidth={penwidth}];')

    lines.append("}")
    return "\n".join(lines)


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Uniform Cost Search (UCS)", page_icon="🧭", layout="wide")

st.title("Uniform Cost Search (UCS)")
st.caption("Explore weighted graphs with UCS (Dijkstra). Non-negative edge weights only.")

with st.sidebar:
    st.header("Graph Input")
    input_mode = st.radio("Definition mode", ["Sample", "Custom"], index=0)
    undirected = st.checkbox("Treat edges as undirected", value=False)

    sample_edges = """
    # source,target,cost
    A,B,1
    A,C,4
    B,C,2
    B,D,5
    C,D,3
    """.strip()

    if input_mode == "Sample":
        edge_text = sample_edges
        st.image("UCS_img1.jpg", caption="Sample graph (if available)", use_container_width=True)
    else:
        edge_text = st.text_area(
            "Edges (one per line: src,dst,cost)",
            value=sample_edges,
            height=160,
            help="Use commas or spaces. Comments start with '#'.",
        )

    parse_ok = True
    graph: Dict[str, Dict[str, float]] = {}
    try:
        graph = parse_edges(edge_text, undirected=undirected)
    except Exception as e:
        parse_ok = False
        st.error(str(e))

if not parse_ok or not graph:
    st.stop()

nodes = all_nodes(graph)
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    start_node = st.selectbox("Start", nodes, index=0 if nodes else None)
with col2:
    goal_node = st.selectbox("Goal (optional)", ["<none>"] + nodes, index=(nodes.index("D") + 1) if "D" in nodes else 0)
with col3:
    run_btn = st.button("Run UCS", type="primary")

st.divider()

if run_btn and start_node:
    goal_value = None if goal_node == "<none>" else goal_node
    try:
        path, total, expanded, best_cost, parent, trace = uniform_cost_search(graph, start_node, goal_value)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Result")
        if goal_value is None:
            st.write("Computed shortest-path tree (no specific goal).")
        elif path:
            st.success(f"Path: {' → '.join(path)}  |  Total cost: {total}")
        else:
            st.warning("No path found to the specified goal.")

        st.write("Expanded order:", ", ".join(expanded) if expanded else "None")

        # Best costs table
        rows = [
            {"Node": n, "Cost from start": (best_cost[n] if n in best_cost else float('inf')), "Parent": parent.get(n)}
            for n in nodes
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)

        # Step-by-step trace (collapsed)
        with st.expander("Step-by-step frontier (trace)"):
            for i, snap in enumerate(trace, start=1):
                frontier_str = ", ".join(f"{n}@{c}" for c, n in sorted(list(snap["frontier"]))[:10])
                st.write(f"{i}. expanded={snap['expanded']}  cost={snap['cost']}  frontier=[{frontier_str}]  ")

    with right:
        st.subheader("Graph")
        gv = to_graphviz(graph, path if path else [], directed=not undirected)
        st.graphviz_chart(gv, use_container_width=True)

else:
    st.info("Set start/goal and click Run UCS to execute.")

