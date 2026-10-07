"""Simple Streamlit BFS app. Run: python -m streamlit run bfs_simple.py"""
import json
from collections import deque

import streamlit as st
from graphviz import Digraph, escape


def bfs(graph, start):
    visited, order = {start}, []
    queue = deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return order


st.set_page_config(page_title="BFS Explorer", page_icon="🔵", layout="wide")
st.markdown("<style>h1 {color: #0891b2;} .stButton button {border-radius: 10px;}</style>",
            unsafe_allow_html=True)
st.title("Breadth-First Search")
st.caption("Explore all neighbours before moving to the next level. No API key required.")

default_graph = {
    "A": ["B", "C"], "B": ["D", "E"], "C": ["F"],
    "D": [], "E": ["F"], "F": [],
}
text = st.sidebar.text_area("Edit graph (JSON)", json.dumps(default_graph, indent=2), height=300)
try:
    graph = json.loads(text)
    if not isinstance(graph, dict) or not graph:
        raise ValueError("Use a non-empty JSON object.")
    for neighbours in list(graph.values()):
        if not isinstance(neighbours, list) or not all(isinstance(n, str) and n.strip() for n in neighbours):
            raise ValueError("Each neighbour list must contain non-empty strings.")
        for node in neighbours:
            graph.setdefault(node, [])  # Add referenced nodes with no outgoing edges.
    if len(graph) > 100 or not all(node.strip() for node in graph):
        raise ValueError("Use 1–100 nodes with non-empty names.")
except ValueError as error:
    st.error(f"Invalid graph: {error}")
    st.stop()

start = st.sidebar.selectbox("Start node", list(graph))
order = bfs(graph, start) if st.sidebar.button("Run BFS", type="primary") else []

canvas, result = st.columns([2, 1])
with canvas:
    st.subheader("Graph")
    dot = Digraph()
    dot.attr(bgcolor="transparent", rankdir="TB")
    dot.attr("node", shape="circle", style="filled", fontname="Arial", fontcolor="#111827")
    ids = {node: f"n{i}" for i, node in enumerate(graph)}
    for node in graph:
        color = "#fde68a" if node == start else "#67e8f9" if node in order else "#e2e8f0"
        label = node + (f"\n#{order.index(node) + 1}" if node in order else "")
        dot.node(ids[node], escape(label), fillcolor=color, color="#0891b2")
        for neighbour in graph[node]:
            dot.edge(ids[node], ids[neighbour], color="#94a3b8")
    st.graphviz_chart(dot, width="stretch")

with result:
    st.subheader("Traversal order")
    if order:
        st.code(" → ".join(order), language="text")
        st.metric("Visited nodes", f"{len(order)} / {len(graph)}")
        missed = [node for node in graph if node not in order]
        if missed:
            st.caption("Unreachable from the start: " + ", ".join(missed))
    else:
        st.info("Choose a start node and click Run BFS.")
    st.caption("Yellow: start · Cyan: visited · Grey: unvisited")
st.caption("Dr. Ku Muhammad Naim Ku Khalif · Algorithm Explorer")
