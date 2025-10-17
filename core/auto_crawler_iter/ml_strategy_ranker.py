"""
ML策略排序器 - 基于历史数据的策略效果评估
ML Strategy Ranker - Strategy effectiveness evaluation based on historical data
"""
import json
import os
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle


class MLStrategyRanker:
    """
    使用机器学习对策略组合进行排序
    Uses machine learning to rank strategy combinations
    """
    
    def __init__(self, history_path: str = "logs/iter_history.jsonl"):
        self.history_path = history_path
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = "data/models/strategy_ranker.pkl"
        self.scaler_path = "data/models/strategy_scaler.pkl"
        
        # 尝试加载已训练的模型 / Try to load pre-trained model
        self._load_model()
    
    def _load_model(self):
        """加载已保存的模型 / Load saved model"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.is_trained = True
            except Exception as e:
                print(f"模型加载失败 / Model loading failed: {e}")
                self.is_trained = False
    
    def _save_model(self):
        """保存模型 / Save model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
    
    def _extract_features(self, strategies: List[str], metrics: Dict[str, float]) -> np.ndarray:
        """
        从策略和指标中提取特征
        Extract features from strategies and metrics
        """
        # 策略特征 - one-hot编码 / Strategy features - one-hot encoding
        strategy_features = self._encode_strategies(strategies)
        
        # 指标特征 / Metric features
        metric_features = [
            metrics.get('items_total', 0),
            metrics.get('pages_zero', 0),
            metrics.get('errors_total', 0),
            metrics.get('captcha_hits', 0),
            metrics.get('avg_list_time', 0.0)
        ]
        
        # 合并特征 / Combine features
        return np.concatenate([strategy_features, metric_features])
    
    def _encode_strategies(self, strategies: List[str]) -> np.ndarray:
        """
        策略列表转换为特征向量
        Convert strategy list to feature vector
        """
        # 所有可能的策略 / All possible strategies
        all_strategies = [
            'reduce_delay', 'increase_delay', 'change_user_agent',
            'rotate_proxy', 'adjust_timeout', 'modify_headers',
            'change_parser', 'enable_cache', 'retry_logic'
        ]
        
        # One-hot编码 / One-hot encoding
        features = np.zeros(len(all_strategies))
        for i, strategy in enumerate(all_strategies):
            if strategy in strategies:
                features[i] = 1
        
        return features
    
    def train_from_history(self) -> bool:
        """
        从历史记录训练模型
        Train model from history
        """
        if not os.path.exists(self.history_path):
            print(f"历史文件不存在 / History file not found: {self.history_path}")
            return False
        
        # 加载历史数据 / Load history data
        X_list = []
        y_list = []
        
        with open(self.history_path, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                
                # 只使用候选或应用的补丁 / Only use candidate or applied patches
                if entry.get('status') in ['candidate', 'applied']:
                    strategies = entry.get('strategies', [])
                    metrics_before = entry.get('metrics_before', {})
                    evaluation = entry.get('evaluation', {})
                    
                    # 提取特征 / Extract features
                    features = self._extract_features(strategies, metrics_before)
                    
                    # 目标值：评分 / Target: score
                    score = evaluation.get('raw_score', 0)
                    
                    X_list.append(features)
                    y_list.append(score)
        
        if len(X_list) < 5:
            print(f"历史数据不足 / Insufficient history data: {len(X_list)} entries")
            return False
        
        # 训练模型 / Train model
        X = np.array(X_list)
        y = np.array(y_list)
        
        # 标准化特征 / Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练随机森林 / Train random forest
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # 保存模型 / Save model
        self._save_model()
        
        print(f"模型训练完成 / Model training completed: {len(X_list)} samples")
        return True
    
    def rank_strategies(
        self,
        strategy_options: List[List[str]],
        current_metrics: Dict[str, float]
    ) -> List[Tuple[List[str], float]]:
        """
        对多个策略组合进行排序
        Rank multiple strategy combinations
        
        Args:
            strategy_options: 策略组合列表 / List of strategy combinations
            current_metrics: 当前指标 / Current metrics
        
        Returns:
            排序后的 (策略组合, 预测分数) 列表 / Sorted list of (strategies, predicted score)
        """
        if not self.is_trained:
            # 如果模型未训练，尝试训练 / If model not trained, try to train
            self.train_from_history()
        
        if not self.is_trained:
            # 如果仍未训练成功，返回原始顺序 / If still not trained, return original order
            return [(strategies, 0.0) for strategies in strategy_options]
        
        # 预测每个策略组合的分数 / Predict score for each strategy combination
        predictions = []
        for strategies in strategy_options:
            features = self._extract_features(strategies, current_metrics)
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            predicted_score = self.model.predict(features_scaled)[0]
            predictions.append((strategies, predicted_score))
        
        # 按预测分数降序排序 / Sort by predicted score descending
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions
    
    def get_best_strategy(
        self,
        strategy_options: List[List[str]],
        current_metrics: Dict[str, float]
    ) -> List[str]:
        """
        获取最佳策略组合
        Get best strategy combination
        """
        ranked = self.rank_strategies(strategy_options, current_metrics)
        if ranked:
            return ranked[0][0]  # 返回得分最高的策略 / Return highest scoring strategy
        return strategy_options[0] if strategy_options else []
