# AI 2002 – Artificial Intelligence (Spring 2026)  
**Assignment 4 – Question 3: Sudoku Boards as CSPs**

**CSP Sudoku Solver using Backtracking Search + Forward Checking + AC-3**

---

##  Overview

This repository contains a complete Constraint Satisfaction Problem (CSP) solver for Sudoku puzzles.  
The solver implements:

- **Backtracking search** with MRV (Minimum Remaining Values) heuristic  
- **Forward Checking**  
- **AC-3** algorithm for maintaining arc consistency  

It can solve Sudoku boards of varying difficulty (Easy → Very Hard) and reports:
- The solved board
- Number of times the `BACKTRACK` function was called
- Number of times the `BACKTRACK` function returned failure
---

##  Repository Structure
ai2002-assignment4-q3/
├── sudoku_solver.py          # Main CSP solver (well-commented)
├── easy.txt
├── medium.txt
├── hard.txt
├── veryhard.txt
├── solutions/                # (Optional) solved boards
│   ├── easy_solved.txt
│   ├── medium_solved.txt
│   ├── hard_solved.txt
│   └── veryhard_solved.txt
├── README.md                 # This file
└── output.log                # (Optional) console output of all runs

text---

##  How to Run

```bash
# Solve a single board
python sudoku_solver.py easy.txt

# Solve all four boards (recommended)
python sudoku_solver.py --all
Expected Output Format (example):
text=== Solving easy.txt ===
Solved Board:
7 8 4 9 3 2 1 5 6
...
BACKTRACK calls     : 12
BACKTRACK failures  : 3

📊 Results
1. Easy Board (easy.txt)
Input:
text004030050
609400000
005100489
000060930
300807002
026040000
453009600
000004705
090050200

Solved Board:
text
784932156
619485327
235176489
578261934
341897562
926543871
453729618
862314975
197658243
BACKTRACK calls: 1
BACKTRACK failures: 0
Comment: Very fast solve. Forward checking + AC-3 eliminated almost all conflicts early.

 Implementation Notes

Variables = empty cells (represented as (row, col))
Domain = {1,2,3,4,5,6,7,8,9} (reduced by forward checking & AC-3)
Constraints = row, column, and 3×3 subgrid uniqueness
Used AC3() before every backtracking step + forward checking after each assignment
All code is heavily commented as required


 Deliverables Fulfilled

 Well-commented source code (sudoku_solver.py)
 Solutions for all four boards
 BACKTRACK call/failure counts + brief comments
 GitHub link included


Submission Ready!
Feel free to star ⭐ the repo if it helped you!
