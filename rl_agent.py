# rl_agent.py
# Simple tabular Q-learning agent used by the game.
# State: (x,y) tuple
# Actions: 0=up,1=right,2=down,3=left
# Q-table maps (state,action) -> float

import random
import pickle
import os

QFILE = "qtable.pkl"

class RLAgent:
    def __init__(self, actions=4, load=True, alpha=0.1, gamma=0.9,
                 eps=0.3, eps_min=0.02, eps_decay=0.9995, qfile=QFILE):
        self.actions = list(range(actions))
        self.alpha = alpha
        self.gamma = gamma
        self.eps = eps
        self.eps_min = eps_min
        self.eps_decay = eps_decay
        self.qfile = qfile
        self.q = {}
        if load:
            self.load(self.qfile)

    def _key(self, state, action):
        return (state, action)

    def qvalue(self, state, action):
        return self.q.get(self._key(state, action), 0.0)

    def best_action(self, state, legal_actions=None):
        """
        Return the best action for `state`. If legal_actions provided,
        only consider those actions (avoids illegal choices).
        """
        if legal_actions is None or len(legal_actions) == 0:
            legal_actions = self.actions

        vals = [self.qvalue(state, a) for a in legal_actions]
        maxv = max(vals) if vals else 0.0
        best = [a for a, v in zip(legal_actions, vals) if v == maxv]
        return random.choice(best) if best else random.choice(self.actions)

    def choose(self, state, legal_actions=None):
        """
        Epsilon-greedy selection. If legal_actions supplied, pick from them.
        """
        if legal_actions is None or len(legal_actions) == 0:
            legal_actions = self.actions

        if random.random() < self.eps:
            return random.choice(legal_actions)
        return self.best_action(state, legal_actions)

    def update(self, s, a, r, s_next, legal_actions=None):
        """
        Q-learning update:
          Q(s,a) <- Q(s,a) + alpha * (r + gamma * max_a' Q(s',a') - Q(s,a))
        If legal_actions provided, max over those; otherwise consider all actions.
        """
        if legal_actions is None or len(legal_actions) == 0:
            legal_actions = self.actions

        qsa = self.qvalue(s, a)
        max_next = max([self.qvalue(s_next, aa) for aa in legal_actions], default=0.0)
        new_q = qsa + self.alpha * (r + self.gamma * max_next - qsa)
        self.q[self._key(s, a)] = new_q

        # decay epsilon
        if self.eps > self.eps_min:
            self.eps *= self.eps_decay
            if self.eps < self.eps_min:
                self.eps = self.eps_min

    # Persistence
    def save(self, path=None):
        path = path or self.qfile
        try:
            with open(path, "wb") as f:
                pickle.dump(self.q, f)
        except Exception as e:
            print("Failed to save Q-table:", e)

    def load(self, path=None):
        path = path or self.qfile
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    self.q = pickle.load(f)
                print(f"[RLAgent] Loaded Q-table from {path} (entries={len(self.q)})")
            except Exception as e:
                print("Failed to load qtable:", e)
                self.q = {}
        else:
            self.q = {}
            print(f"[RLAgent] No Q-table file found at {path}, starting fresh.")    
            