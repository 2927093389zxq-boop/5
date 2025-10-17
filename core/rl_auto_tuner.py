"""
强化学习自动调参框架
Reinforcement Learning Auto-tuning Framework
"""
import numpy as np
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from collections import deque
import pickle


class RLAutoTuner:
    """
    基于Q-Learning的参数自动调优器
    Q-Learning based parameter auto-tuner
    """
    
    def __init__(
        self,
        param_space: Dict[str, List[Any]],
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.2,
        model_path: str = "data/models/rl_tuner.pkl"
    ):
        """
        初始化RL调优器
        
        Args:
            param_space: 参数空间，如 {'delay': [0.5, 1.0, 2.0], 'timeout': [10, 20, 30]}
            learning_rate: 学习率
            discount_factor: 折扣因子
            epsilon: 探索率
            model_path: 模型保存路径
        """
        self.param_space = param_space
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.model_path = model_path
        
        # Q表：(状态, 动作) -> Q值
        # Q-table: (state, action) -> Q-value
        self.q_table: Dict[Tuple, float] = {}
        
        # 历史记录 / History
        self.history = deque(maxlen=1000)
        
        # 尝试加载已保存的模型 / Try to load saved model
        self._load_model()
    
    def _state_to_tuple(self, state: Dict[str, float]) -> Tuple:
        """将状态字典转换为元组 / Convert state dict to tuple"""
        return tuple(sorted(state.items()))
    
    def _action_to_params(self, action_idx: int) -> Dict[str, Any]:
        """将动作索引转换为参数组合 / Convert action index to parameter combination"""
        # 计算所有可能的参数组合 / Calculate all possible parameter combinations
        param_names = list(self.param_space.keys())
        param_values = [self.param_space[name] for name in param_names]
        
        # 使用索引选择组合 / Use index to select combination
        total_combinations = 1
        for values in param_values:
            total_combinations *= len(values)
        
        if action_idx >= total_combinations:
            action_idx = action_idx % total_combinations
        
        selected_params = {}
        for i, name in enumerate(param_names):
            values = param_values[i]
            idx = action_idx % len(values)
            selected_params[name] = values[idx]
            action_idx //= len(values)
        
        return selected_params
    
    def _get_action_count(self) -> int:
        """获取动作空间大小 / Get action space size"""
        count = 1
        for values in self.param_space.values():
            count *= len(values)
        return count
    
    def _get_q_value(self, state: Tuple, action: int) -> float:
        """获取Q值 / Get Q-value"""
        key = (state, action)
        return self.q_table.get(key, 0.0)
    
    def _set_q_value(self, state: Tuple, action: int, value: float):
        """设置Q值 / Set Q-value"""
        key = (state, action)
        self.q_table[key] = value
    
    def select_action(self, state: Dict[str, float]) -> Tuple[int, Dict[str, Any]]:
        """
        选择动作（参数组合）
        Select action (parameter combination)
        
        Returns:
            (动作索引, 参数字典) / (action index, parameter dict)
        """
        state_tuple = self._state_to_tuple(state)
        
        # ε-贪心策略 / ε-greedy policy
        if np.random.random() < self.epsilon:
            # 探索：随机选择 / Explore: random selection
            action = np.random.randint(0, self._get_action_count())
        else:
            # 利用：选择最优动作 / Exploit: select best action
            action_count = self._get_action_count()
            q_values = [self._get_q_value(state_tuple, a) for a in range(action_count)]
            action = int(np.argmax(q_values))
        
        params = self._action_to_params(action)
        return action, params
    
    def update(
        self,
        state: Dict[str, float],
        action: int,
        reward: float,
        next_state: Dict[str, float]
    ):
        """
        更新Q值
        Update Q-value
        
        Args:
            state: 当前状态 / Current state
            action: 执行的动作 / Action taken
            reward: 获得的奖励 / Reward received
            next_state: 下一个状态 / Next state
        """
        state_tuple = self._state_to_tuple(state)
        next_state_tuple = self._state_to_tuple(next_state)
        
        # 当前Q值 / Current Q-value
        current_q = self._get_q_value(state_tuple, action)
        
        # 下一个状态的最大Q值 / Max Q-value of next state
        action_count = self._get_action_count()
        next_max_q = max([
            self._get_q_value(next_state_tuple, a)
            for a in range(action_count)
        ])
        
        # Q-learning更新公式 / Q-learning update formula
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * next_max_q - current_q
        )
        
        self._set_q_value(state_tuple, action, new_q)
        
        # 记录历史 / Record history
        self.history.append({
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state,
            'q_value': new_q
        })
    
    def calculate_reward(
        self,
        base_metrics: Dict[str, float],
        new_metrics: Dict[str, float],
        weights: Dict[str, float] = None
    ) -> float:
        """
        计算奖励
        Calculate reward
        
        Args:
            base_metrics: 基准指标 / Baseline metrics
            new_metrics: 新指标 / New metrics
            weights: 权重 / Weights
        
        Returns:
            奖励值 / Reward value
        """
        if weights is None:
            weights = {
                'items_total': 0.55,
                'pages_zero': -0.30,
                'avg_list_time': -0.10,
                'errors_total': -0.40,
                'captcha_hits': -0.15
            }
        
        reward = 0.0
        for metric, weight in weights.items():
            base_val = base_metrics.get(metric, 0)
            new_val = new_metrics.get(metric, 0)
            
            if weight > 0:
                # 正向指标：越大越好 / Positive metric: bigger is better
                reward += weight * (new_val - base_val)
            else:
                # 负向指标：越小越好 / Negative metric: smaller is better
                reward += weight * (new_val - base_val)
        
        return reward
    
    def _save_model(self):
        """保存模型 / Save model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'history': list(self.history)
            }, f)
    
    def _load_model(self):
        """加载模型 / Load model"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.q_table = data.get('q_table', {})
                    self.history = deque(data.get('history', []), maxlen=1000)
            except Exception as e:
                print(f"模型加载失败 / Model loading failed: {e}")
    
    def save(self):
        """保存模型（公共方法） / Save model (public method)"""
        self._save_model()
    
    def get_best_params(self, state: Dict[str, float]) -> Dict[str, Any]:
        """
        获取当前状态下的最优参数
        Get best parameters for current state
        """
        state_tuple = self._state_to_tuple(state)
        action_count = self._get_action_count()
        
        q_values = [self._get_q_value(state_tuple, a) for a in range(action_count)]
        best_action = int(np.argmax(q_values))
        
        return self._action_to_params(best_action)
