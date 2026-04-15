"""
=============================================================
  CSP-Based Sudoku Solver
  AI 2002 – Artificial Intelligence (Spring 2026)
  Assignment 4 – Question 3

  Techniques Used:
    1. Backtracking Search
    2. Forward Checking
    3. AC-3 (Arc Consistency)
    4. MRV (Minimum Remaining Values) heuristic for variable selection
=============================================================
"""

import sys
from copy import deepcopy
from collections import deque

# ──────────────────────────────────────────────────────────
# Global Counters
# ──────────────────────────────────────────────────────────
backtrack_calls   = 0   # total times BACKTRACK was entered
backtrack_failures = 0  # times BACKTRACK returned FAILURE


# ──────────────────────────────────────────────────────────
# Helper: peer cells (all cells sharing a constraint)
# ──────────────────────────────────────────────────────────
# Pre-compute peers for every cell once to save repeated work
PEERS = {}
for _r in range(9):
    for _c in range(9):
        p = set()
        # same row
        for cc in range(9):
            if cc != _c:
                p.add((_r, cc))
        # same column
        for rr in range(9):
            if rr != _r:
                p.add((rr, _c))
        # same 3×3 box
        br, bc = 3 * (_r // 3), 3 * (_c // 3)
        for rr in range(br, br + 3):
            for cc in range(bc, bc + 3):
                if (rr, cc) != (_r, _c):
                    p.add((rr, cc))
        PEERS[(_r, _c)] = p


# ──────────────────────────────────────────────────────────
# Board I/O
# ──────────────────────────────────────────────────────────
def parse_board(filename: str) -> list[list[int]]:
    """Read a 9×9 board from a text file (0 = empty cell)."""
    board = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                board.append([int(ch) for ch in line])
    if len(board) != 9 or any(len(r) != 9 for r in board):
        raise ValueError(f"Board in {filename} must be 9 lines of 9 digits.")
    return board


def print_board(solution: dict, board: list[list[int]] = None) -> None:
    """Pretty-print a 9×9 board with box separators."""
    grid = [[0] * 9 for _ in range(9)]
    if board:
        for r in range(9):
            for c in range(9):
                grid[r][c] = board[r][c]
    if solution:
        for (r, c), v in solution.items():
            grid[r][c] = v

    print("+-------+-------+-------+")
    for r in range(9):
        row_str = "| "
        for c in range(9):
            row_str += str(grid[r][c]) + " "
            if c % 3 == 2:
                row_str += "| "
        print(row_str)
        if r % 3 == 2:
            print("+-------+-------+-------+")


# ──────────────────────────────────────────────────────────
# Domain Initialisation
# ──────────────────────────────────────────────────────────
def initialize_domains(board: list[list[int]]) -> dict:
    """
    Build initial domains:
      • Filled cell  → singleton {v}
      • Empty cell   → {1..9}
    """
    domains = {}
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                domains[(r, c)] = {board[r][c]}
            else:
                domains[(r, c)] = set(range(1, 10))
    return domains


# ──────────────────────────────────────────────────────────
# AC-3 (Arc Consistency Algorithm 3)
# ──────────────────────────────────────────────────────────
def revise(domains: dict, xi: tuple, xj: tuple) -> bool:
    """
    REVISE: Remove values from domain(xi) that have no support in domain(xj).
    For Sudoku the constraint is xi ≠ xj, so a value v in domain(xi) is
    inconsistent only when domain(xj) = {v} (xj is already forced to v).

    Returns True if domain(xi) was reduced.
    """
    revised = False
    if len(domains[xj]) == 1:
        (forced,) = domains[xj]          # the single value xj must take
        if forced in domains[xi]:
            domains[xi].discard(forced)
            revised = True
    return revised


def ac3(domains: dict) -> bool:
    """
    AC-3: Enforce arc consistency over all variable pairs.
    Returns False if any domain becomes empty (inconsistency detected).
    """
    # Initialise queue with every directed arc (xi → xj) for peer pairs
    queue = deque()
    for cell in domains:
        for peer in PEERS[cell]:
            queue.append((cell, peer))

    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False          # domain wipeout → no solution this path
            # xi's domain shrank → re-check all arcs pointing TO xi
            for xk in PEERS[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True


# ──────────────────────────────────────────────────────────
# Variable Selection: MRV Heuristic
# ──────────────────────────────────────────────────────────
def select_unassigned_variable(domains: dict, assignment: dict) -> tuple:
    """
    MRV (Minimum Remaining Values): pick the unassigned cell whose domain
    is smallest (most constrained), to fail early and prune more of the tree.
    """
    unassigned = [cell for cell in domains if cell not in assignment]
    return min(unassigned, key=lambda cell: len(domains[cell]))


# ──────────────────────────────────────────────────────────
# Forward Checking
# ──────────────────────────────────────────────────────────
def forward_check(domains: dict, cell: tuple, value: int):
    """
    After assigning `value` to `cell`, remove `value` from all peer domains.
    Returns updated (deep-copied) domains, or None if any domain becomes empty.
    """
    new_domains = deepcopy(domains)
    new_domains[cell] = {value}        # fix this cell's domain to singleton

    for peer in PEERS[cell]:
        if value in new_domains[peer]:
            new_domains[peer].discard(value)
            if len(new_domains[peer]) == 0:
                return None            # domain wipeout
    return new_domains


# ──────────────────────────────────────────────────────────
# Backtracking Search
# ──────────────────────────────────────────────────────────
def backtrack(assignment: dict, domains: dict):
    """
    Recursive BACKTRACK function.
    Combines:
      • Forward Checking  – prune peers after each assignment
      • AC-3              – additional propagation after forward check
      • MRV               – pick most-constrained unassigned variable

    Returns a complete assignment or None (failure).
    """
    global backtrack_calls, backtrack_failures
    backtrack_calls += 1

    # ── Base case: all 81 cells assigned ──
    if len(assignment) == 81:
        return assignment

    # ── Choose variable ──
    cell = select_unassigned_variable(domains, assignment)

    # ── Try each value in the domain (sorted for determinism) ──
    for value in sorted(domains[cell]):

        # Consistency check (quick – before deep-copy overhead)
        if all(assignment.get(peer) != value for peer in PEERS[cell]):

            assignment[cell] = value

            # Forward checking
            new_domains = forward_check(domains, cell, value)

            if new_domains is not None:
                # AC-3 propagation on the pruned domains
                if ac3(new_domains):
                    result = backtrack(assignment, new_domains)
                    if result is not None:
                        return result          # ← solution found

            # Undo assignment and try next value
            del assignment[cell]

    # No value worked → return FAILURE
    backtrack_failures += 1
    return None


# ──────────────────────────────────────────────────────────
# Main Solve Entry Point
# ──────────────────────────────────────────────────────────
def solve(board: list[list[int]]) -> dict | None:
    """
    Solve a Sudoku board.
    Steps:
      1. Initialise domains from the given board.
      2. Run AC-3 to prune domains before search begins.
      3. Pre-assign all cells whose domain collapsed to a singleton.
      4. Run backtracking search.

    Returns the solution assignment dict {(row, col): value} or None.
    """
    global backtrack_calls, backtrack_failures
    backtrack_calls   = 0
    backtrack_failures = 0

    domains = initialize_domains(board)

    # Initial AC-3 pass (propagates givens through the whole grid)
    if not ac3(domains):
        print("  ✗ Initial AC-3 detected unsolvable board.")
        return None

    # Seed assignment from singletons (many easy boards solve here alone!)
    assignment = {}
    for cell, domain in domains.items():
        if len(domain) == 1:
            assignment[cell] = next(iter(domain))

    # Full backtracking search
    return backtrack(assignment, domains)


# ──────────────────────────────────────────────────────────
# Run on all four boards
# ──────────────────────────────────────────────────────────
def run_board(name: str, filename: str) -> None:
    sep = "=" * 55
    print(f"\n{sep}")
    print(f"  Board: {name.upper()}  ({filename})")
    print(sep)

    try:
        board = parse_board(filename)
    except FileNotFoundError:
        print(f"  ✗ File not found: {filename}")
        return
    except ValueError as e:
        print(f"  ✗ Parse error: {e}")
        return

    print("  Input puzzle:")
    print_board(None, board)

    solution = solve(board)

    if solution:
        print("\n  ✓ Solution:")
        print_board(solution, board)
    else:
        print("\n  ✗ No solution found.")

    print(f"\n  BACKTRACK calls   : {backtrack_calls:>6}")
    print(f"  BACKTRACK failures: {backtrack_failures:>6}")

    # Brief commentary
    if backtrack_calls < 200:
        note = "Very few backtracks — AC-3 + forward checking resolved most/all cells before search."
    elif backtrack_calls < 2000:
        note = "Moderate backtracks — some trial-and-error needed despite strong propagation."
    else:
        note = "Many backtracks — high ambiguity; MRV keeps it tractable but search is deep."
    print(f"  Commentary        : {note}")


if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__))

    boards = [
        ("Easy",      os.path.join(base, "easy.txt")),
        #commented these bcz, I only created the easy board 
        # ("Medium",    os.path.join(base, "medium.txt")),
        # ("Hard",      os.path.join(base, "hard.txt")),
        # ("Very Hard", os.path.join(base, "veryhard.txt")), 
    ]

    for name, path in boards:
        run_board(name, path)

    print("\nDone.")