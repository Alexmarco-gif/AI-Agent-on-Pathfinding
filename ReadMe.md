# 🧠 AI Maze Agent: From Foundational Search to Reinforcement Learning 
This project showcases a complete transition in AI methodology: starting with foundational Classical Search algorithms and evolving into a dynamic, interactive environment solved by a Model-Free Reinforcement Learning (Q-Learning) agent. It demonstrates proficiency in core AI concepts, algorithmic implementation, and the development of a functional game environment using Python/Pygame.

💡 Why This Project? (My Fascination)
This project originated from Harvard's CS50 for Artificial Intelligence (CS50AI), focusing on pathfinding problems. My goal was to move beyond static, solved problems and address the complexity of dynamic, adversarial environments.I found the transition from telling an algorithm the right path (A* Search) to allowing an agent to discover the optimal path through trial-and-error (Q-Learning) to be incredibly fascinating. The primary technical goal was to engineer a minimal yet informative State Representation that would make Tabular Q-Learning feasible in a visually complex stealth game scenario. The result is a hybrid AI system where two different algorithms solve two distinct problems: efficient movement for the predictable guards, and adaptive survival for the learning agent.

🚀 Project Evolution and Core Features
The project is split into two distinct phases:
Phase 1: Foundational Search Algorithms (Core Competency)The initial phase focused on building efficient solvers for finding the shortest path in a static, generated maze structure. AlgorithmTypeUse CaseBreadth-First Search (BFS) Uninformed Guarantees the shortest path in terms of steps. Depth-First Search (DFS) Uninformed Used in the Recursive Backtracker for maze generation. A* Search Informed Finds the shortest path efficiently using the Manhattan distance heuristic.

Phase 2: Stealth Game Environment and Reinforcement Learning
The project advanced into a small Stealth Game where the main player ("the bot") must collect "loot" while avoiding patrolling "guards."Component AI Methodology Role in GameGuardsA* Search Their patrol movement is managed by A*, ensuring the shortest path to their designated checkpoints.The BotTabular Q-LearningLearns an optimal policy for survival and resource collection, managing the Exploration-Exploitation trade-off. Persistenceqtable.pkl The agent's knowledge (Q-Table) is saved across sessions, enabling transfer learning.⚙️ Technical Deep Dive: The Q-Learning AgentThe RL Agent is defined in rl_agent.py. It uses the core Q-Learning update rule:$$Q(s,a) \leftarrow Q(s,a) + \alpha \cdot \left(r + \gamma \cdot \max_{a'} Q(s',a') - Q(s,a)\right) $$

### State Representation
To manage the large state space of a $25 \times 17$ grid, the state was simplified to be manageable for tabular learning:

1.  **Current (x, y) Cell:** The agent's physical location.
2.  **Local Context:** Encoded relative position of nearby elements (walls, closest loot).
3.  **Adversarial Context:** A critical element indicating **guard visibility** (line-of-sight), which dramatically changes the optimal action.

### Reward Structure

The agent learns through a balanced reward function designed to prioritize the primary objective while penalizing inefficient or risky behavior.

| Event | Reward | Rationale |
| :--- | :--- | :--- |
| **Collect Loot** | $+10$ | Primary objective; strong positive reinforcement. |
| **Get Caught** | $-10$ | Critical failure; strong negative penalty to discourage dangerous paths. |
| **Take a Step** | $-0.1$ | Small penalty to encourage efficiency and **minimize total moves**. |

### Hyperparameters

| Hyperparameter | Symbol | Technique |
| :--- | :--- | :--- |
| **Epsilon ($\epsilon$)** | Epsilon Decay | Controls the Exploration-Exploitation balance. Crucially, $\epsilon$ **decays over time** to transition the agent from random exploration to exploiting the learned policy. |
| **Learning Rate ($\alpha$)** | N/A | Controls the weight given to new information during the Q-Table update. |
| **Discount Factor ($\gamma$)** | N/A | Controls the importance of future rewards over immediate rewards. |

-----

## 📦 How to Run the Project

### Prerequisites

Ensure you have Python 3.8+ installed.

```bash
# Install Pygame and other required packages
pip install pygame numpy
```

### Execution

1.  **Start the Game:** Run the main game file.

<!-- end list -->

```bash
python game_lr.py
```

2.  **Training:** The agent will start in **training mode**, where its Epsilon ($\epsilon$) is high. Watch it fail and eventually learn an optimal policy.
3.  **Policy Retention:** The learned Q-Table will be automatically saved to `qtable.pkl` (or `q_table.pkl`) and loaded on subsequent runs, allowing the agent to continue learning or demonstrate its learned policy immediately.

-----

## 📂 File Breakdown

| File | Description |
| :--- | :--- |
| `game_lr.py` | The main **Pygame application** and the Reinforcement Learning **training loop**. |
| `rl_agent.py` | The class defining the **Tabular Q-Learning algorithm** and the agent's behavior. |
| `search_algorithms.py` | Implements **A\* Search** (used by the patrolling guards). |
| `maze_generator.py` | Utility to generate the random, solvable maze structure using **Recursive Backtracker (DFS)**. |
| `qtable.pkl` | **Saved model weights** (the learned Q-Table) for policy persistence. |

-----

## 🤝 Next Steps & Collaboration

This project is a continuous exploration of AI methodologies, and there are many avenues for future development:

* **Move to Deep Q-Learning (DQN):** Replace the current tabular state representation with a Neural Network to handle larger, more complex state spaces (e.g., raw pixel input or full map visibility).
* **Adversarial Learning:** Introduce a more sophisticated guard policy (e.g., guards also use Q-Learning) or allow guards to dynamically hunt the player based on last known location.
* **Hyperparameter Tuning:** Implement automated hyperparameter tuning (e.g., Grid Search or Bayesian Optimization) to find the optimal $\alpha$ and $\epsilon$ decay schedule for faster convergence.

Feel free to fork the repository, open an issue, or submit a pull request\!$$
