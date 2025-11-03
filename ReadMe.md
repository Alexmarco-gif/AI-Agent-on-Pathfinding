## 🧠 AI Maze Agent: From Foundational Search to Reinforcement Learning

This project began as an academic exercise following Harvard University's CS50 for Artificial Intelligence (CS50AI) course on search problems. It evolved from a simple solver for static mazes using classical search algorithms into a dynamic, interactive game environment where an agent learns optimal movement policies using Q-Learning (Reinforcement Learning).

The project demonstrates two key pillars of AI: Classical Search (A*, BFS, DFS) and Model-Free Reinforcement Learning.

## 🚀 Project Evolution and Core Features

* Phase 1: Foundational Search Algorithms (CS50AI Focus)
The initial phase focused on building solvers for finding the shortest path in a generated maze.

| File | Algorithms & Role |
| maze_gen.py / maze_generator.py | Generates a random, solvable maze using a Recursive Backtracker (DFS) algorithm. |
| search_algorithm.py / search_algorithms.py | Implements three core uninformed and informed search strategies: Breadth-First Search (BFS), Depth-First Search (DFS), and A* Search (using Manhattan distance as the heuristic). |
| main.py | Command-line interface to generate a maze, solve it using a user-selected algorithm, and print the resulting path. |

* Phase 2: Game Environment and Reinforcement Learning (RL)

The project was advanced into a small Stealth Game where a controlled agent (the "bot") must collect "loot" while avoiding patrolling "guards." The original search code is repurposed, specifically A Search*, to manage the movement of the patrolling 'guards', while the main player bot uses Q-Learning to navigate.

| File | Role |
| game_lr.py | The main game loop (implemented with pygame). It handles rendering, physics, guard movement (using A*), and agent-environment interaction. |
| rl_agent.py | Implements a Tabular Q-Learning Agent. It stores and updates the Q-table using the Bellman Equation to learn the optimal action-selection policy. |
| qtable.pkl / q_table.pkl | Persistent storage for the agent's learned Q-Table, allowing the agent to retain its knowledge across game sessions. |

## ⚙️ Technical Deep Dive: The RL Agent

The central AI challenge is to train the bot to survive in the dynamic maze environment.

State Representation

The bot's state is simplified to be manageable for tabular Q-Learning. The state includes:

The bot's current (x, y) cell coordinates.

The presence and encoded relative position of nearby environmental elements (e.g., walls, nearest loot, guard visibility).

Actions

The agent has four possible actions in the game grid:

0: Up

1: Right

2: Down

3: Left

### Reward Structure

The agent learns through trial-and-error based on the following reward structure:

| Event | Reward | Rationale |
| Collect Loot | +10 | Primary objective; strong positive reinforcement. |
| Take a Step | -0.1 | Encourages the agent to find the goal quickly (minimizing moves). |
| Get Caught by a Guard | -10 | Critical failure; strong negative penalty to discourage dangerous paths. |
| Stuck/Idle | Large Negative | Penalty applied if the agent fails to move for a prolonged period, forcing regeneration. |

### Learning Mechanism

The agent uses the following hyperparameters for Q-Learning:

Learning Rate ($\alpha$): Controls how quickly the agent adopts new information.

Discount Factor ($\gamma$): Controls the importance of future rewards.

Epsilon ($\epsilon$): Controls the trade-off between exploration (trying random actions) and exploitation (choosing the best known action). Crucially, Epsilon decays over time, starting high for initial exploration and decreasing to cause the agent to exploit known optimal paths as it becomes more confident in its policy.

## 📦 File Breakdown

| File | Description |
| main.py | (Legacy CLI) Solves static mazes using classic algorithms. |
| maze_gen.py | Generates the maze structure. |
| search_algorithm.py | Implements BFS, DFS, and A* search (used by guards in the game). |
| game_lr.py | The main game application and RL training loop. |
| rl_agent.py | The class defining the Q-Learning algorithm and agent behavior. |
| qtable.pkl | Saved model weights (the Q-Table). |
| requirements.txt | (Assumed) List of necessary Python packages (e.g., pygame, numpy). |