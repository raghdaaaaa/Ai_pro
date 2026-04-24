# Ai_pro
# Ludo AI Project – Minimax vs Greedy

## Project Overview
This project is an AI-based simulation of a modified Ludo game designed to study and compare different artificial intelligence decision-making algorithms. The game implements three agents: a Minimax-based AI, a Greedy-based AI, and a human player. The main objective is to analyze how each algorithm performs in a competitive multi-agent environment.

Unlike traditional Ludo, this version removes randomness (dice rolls) and replaces it with deterministic movement choices (1–10 steps). This modification allows the environment to be suitable for applying search-based AI algorithms such as Minimax.

---

## Environment Description
- Turn-based game with 3 players
- Fully observable state space
- Deterministic transitions (no randomness)
- Static environment during decision-making

---

## Key Features
- Minimax AI agent with Alpha-Beta pruning
- Greedy AI agent for baseline comparison
- Human player interaction
- Graphical user interface using Tkinter
- Real-time visualization of moves and AI decisions
- AI thinking process display

---

## Game Modifications
The original Ludo game depends on dice rolling, which introduces randomness.  
In this project:
- Dice mechanism is removed
- Movement is replaced by selectable steps (1 to 10)
- The goal is to convert the game into a deterministic search problem suitable for AI algorithms

---

## AI Algorithms

### Minimax Algorithm
- Explores future game states up to a defined depth
- Uses Alpha-Beta pruning to optimize performance
- Evaluates board states using a heuristic function

### Greedy Algorithm
- Selects moves based on immediate benefit only
- Prioritizes:
  1. Capturing opponent pieces
  2. Winning moves
  3. Maximum forward progress
- Does not consider future consequences

---

## Heuristic Function
The evaluation function considers:
- Piece progress toward the goal
- Reaching the home area
- Safe positions on the board
- Risk of being captured
- Opportunities to capture opponent pieces

---

## How to Run
```bash
python main.py
