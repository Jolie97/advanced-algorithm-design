# Advanced Algorithm Design

This repository contains two algorithmic problem-solving projects implemented in Python.

---

# 1. Student Transport Optimizer

A graph and flow-network based solution for assigning students to buses under:
- distance constraints,
- bus capacity constraints,
- exact student allocation requirements.

The algorithm determines whether a valid allocation exists and returns one possible assignment of students to buses.

## Algorithms Used

- Dijkstra’s Algorithm
- Ford-Fulkerson Maximum Flow
- Residual Graphs
- Lower-Bound Flow Constraints

## Complexity

- Time Complexity: O(S*T + L + R log L)
- Space Complexity: O(S + L + R)

---

# 2. Music Pattern Analyser

A transposition-invariant music pattern detection system using trie-based pattern matching.

## Features

- Detects recurring musical motifs
- Supports transposed pattern matching
- Efficient frequent-pattern retrieval

## Algorithms & Data Structures

- Trie Data Structure
- Breadth-First Search (BFS)
- Interval-based Pattern Encoding

## Complexity

- Preprocessing: O(N*M²)
- Query: O(K)

---

# Repository Structure

```text
├── README.md
├── transport_optimizer.py
├── transport_test_cases.py
├── music_analyser.py
├── music_test_case.py
└── .gitignore
```

---

# How to Run

## Student Transport Optimizer

```bash
python transport_test_cases.py
```

## Music Pattern Analyser

```bash
python music_test_cases.py
```

---

# Technologies

- Python
- Graph Algorithms
- Network Flow
- Trie Structures
- Complexity Analysis
