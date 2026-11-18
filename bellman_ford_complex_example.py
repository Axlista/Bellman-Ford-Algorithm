#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bellman-Ford 同步更新（7 個頂點、12 條邊）。

用法：
  python bellman_ford_complex_example.py
  python bellman_ford_complex_example.py --show-edges
  python bellman_ford_complex_example.py --output-dir ./results
"""
import argparse
import csv
from math import inf
from pathlib import Path

VERTICES = ["S", "A", "B", "C", "D", "E", "F"]
# 邊順序與 PPT 的 Edge Relaxation Table 相同
EDGES = [
    ("S", "A", 7), ("S", "B", 4), ("S", "C", 12),
    ("A", "C", 2), ("A", "D", 5), ("B", "A", -3),
    ("B", "D", 7), ("C", "E", -4), ("D", "E", 2),
    ("D", "F", 6), ("E", "D", 3), ("E", "F", 2),
]

def show_distance(x):
    return "∞" if x == inf else str(x)

def show_path(p):
    return "—" if p is None else " → ".join(p)

def bellman_ford(vertices, edges, source):
    # 初始化最短距離與路徑
    dist = {v: inf for v in vertices}
    dist[source] = 0
    paths = {v: None for v in vertices}
    paths[source] = (source,)
    dist_history = [dist.copy()]
    path_history = [paths.copy()]
    edge_records = []
    stopped_early = False

    # 每一輪只讀取上一輪 dist，將候選結果寫入 next_dist
    for k in range(1, len(vertices)):
        next_dist = dist.copy()
        next_paths = paths.copy()
        updated = False
        for edge_no, (u, v, w) in enumerate(edges, start=1):
            before = next_dist[v]
            candidate = dist[u] + w if dist[u] != inf else inf
            changed = candidate < before
            if changed:
                next_dist[v] = candidate
                next_paths[v] = paths[u] + (v,)
                updated = True
            edge_records.append([
                k, edge_no, u, v, w, show_distance(dist[u]),
                show_distance(candidate), show_distance(before),
                "Yes" if changed else "No",
            ])
        # 一輪完整結束後才提交結果
        dist, paths = next_dist, next_paths
        dist_history.append(dist.copy())
        path_history.append(paths.copy())
        if not updated:
            stopped_early = True
            break

    # 從起點可到達的負權重環檢查
    negative_cycle_edges = [
        (u, v, w) for u, v, w in edges
        if dist[u] != inf and dist[u] + w < dist[v]
    ]
    return dist_history, path_history, edge_records, negative_cycle_edges, stopped_early

def write_csv(path, headers, rows):
    # utf-8-sig 可讓 Windows Excel 正確顯示中文及 ∞ 符號
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def print_table(headers, rows):
    widths = [max(len(str(r[i])) for r in [headers, *rows])
              for i in range(len(headers))]
    for j, row in enumerate([headers, *rows]):
        print(" | ".join(str(item).ljust(widths[i]) for i, item in enumerate(row)))
        if j == 0:
            print("-+-".join("-" * w for w in widths))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show-edges", action="store_true",
                        help="顯示所有 Edge 的逐輪計算")
    parser.add_argument("--output-dir", default=".", type=Path,
                        help="CSV 輸出資料夾（預設目前資料夾）")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    dh, ph, er, neg, early = bellman_ford(VERTICES, EDGES, "S")
    headers = ["Vertex", "Init"] + [f"Round {k}" for k in range(1, len(dh))]
    distance_rows = [[v] + [show_distance(h[v]) for h in dh] for v in VERTICES]
    path_rows = [[v] + [show_path(h[v]) for h in ph] for v in VERTICES]
    edge_headers = ["Round", "Edge", "u", "v", "w(u,v)",
                    "d_(k-1)(u)", "Candidate", "next[v] before", "Updated"]

    print("Bellman-Ford (Synchronous Relaxation)")
    print(f"V={len(VERTICES)}, E={len(EDGES)}")
    print_table(headers, distance_rows)
    print("\nFinal shortest paths:")
    for v in VERTICES:
        print(f"  {v}: {show_distance(dh[-1][v]):>2} | {show_path(ph[-1][v])}")
    print("\nNegative Cycle:", "Detected" if neg else "Not detected")
    if early:
        print(f"Early termination: no updates in round {len(dh)-1}")
    if args.show_edges:
        print("\nEdge Relaxation Table:")
        print_table(edge_headers, er)

    write_csv(args.output_dir / "bellman_ford_distance_table.csv", headers, distance_rows)
    write_csv(args.output_dir / "bellman_ford_path_table.csv", headers, path_rows)
    write_csv(args.output_dir / "bellman_ford_edge_relaxation_table.csv", edge_headers, er)
    print(f"\n3 CSV files saved to {args.output_dir.resolve()}")

if __name__ == "__main__":
    main()
