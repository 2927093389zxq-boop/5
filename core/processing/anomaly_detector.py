"""
Anomaly detection for data analysis.
"""

from typing import List, Dict, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)


def detect_anomalies(data: List[float], threshold: float = 2.5) -> List[int]:
    """
    Detect anomalies in a time series using z-score method.
    
    Args:
        data: List of numeric values
        threshold: Z-score threshold for anomaly detection (default: 2.5)
        
    Returns:
        List of indices where anomalies were detected
    """
    if not data or len(data) < 3:
        return []
    
    try:
        # Convert to numpy array
        arr = np.array(data, dtype=float)
        
        # Calculate mean and standard deviation
        mean = np.mean(arr)
        std = np.std(arr)
        
        # Avoid division by zero
        if std == 0:
            return []
        
        # Calculate z-scores
        z_scores = np.abs((arr - mean) / std)
        
        # Find anomalies
        anomaly_indices = np.where(z_scores > threshold)[0].tolist()
        
        logger.info(f"Detected {len(anomaly_indices)} anomalies in {len(data)} data points")
        return anomaly_indices
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        return []


def detect_anomalies_iqr(data: List[float], k: float = 1.5) -> List[int]:
    """
    Detect anomalies using Interquartile Range (IQR) method.
    
    Args:
        data: List of numeric values
        k: IQR multiplier (default: 1.5)
        
    Returns:
        List of indices where anomalies were detected
    """
    if not data or len(data) < 4:
        return []
    
    try:
        arr = np.array(data, dtype=float)
        
        # Calculate quartiles
        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)
        iqr = q3 - q1
        
        # Calculate bounds
        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr
        
        # Find anomalies
        anomaly_indices = np.where((arr < lower_bound) | (arr > upper_bound))[0].tolist()
        
        logger.info(f"IQR method: Detected {len(anomaly_indices)} anomalies")
        return anomaly_indices
        
    except Exception as e:
        logger.error(f"Error detecting anomalies with IQR: {e}")
        return []


def detect_anomalies_moving_average(data: List[float], window_size: int = 5, threshold: float = 2.0) -> List[int]:
    """
    Detect anomalies using moving average method.
    
    Args:
        data: List of numeric values
        window_size: Size of the moving average window (default: 5)
        threshold: Threshold multiplier for standard deviation (default: 2.0)
        
    Returns:
        List of indices where anomalies were detected
    """
    if not data or len(data) < window_size:
        return []
    
    try:
        arr = np.array(data, dtype=float)
        anomaly_indices = []
        
        for i in range(window_size, len(arr)):
            # Calculate moving average and std
            window = arr[i-window_size:i]
            ma = np.mean(window)
            std = np.std(window)
            
            # Check if current value is anomalous
            if std > 0 and abs(arr[i] - ma) > threshold * std:
                anomaly_indices.append(i)
        
        logger.info(f"Moving average method: Detected {len(anomaly_indices)} anomalies")
        return anomaly_indices
        
    except Exception as e:
        logger.error(f"Error detecting anomalies with moving average: {e}")
        return []


def analyze_system_metrics(metrics_data: Dict[str, List[float]]) -> Dict[str, any]:
    """
    Analyze system metrics for anomalies.
    
    Args:
        metrics_data: Dictionary of metric names to their time series data
        
    Returns:
        Dictionary containing anomaly detection results for each metric
    """
    results = {}
    
    for metric_name, data in metrics_data.items():
        if not data:
            continue
            
        try:
            # Apply multiple detection methods
            z_score_anomalies = detect_anomalies(data, threshold=2.5)
            iqr_anomalies = detect_anomalies_iqr(data, k=1.5)
            ma_anomalies = detect_anomalies_moving_average(data, window_size=5, threshold=2.0)
            
            # Combine results
            all_anomalies = set(z_score_anomalies + iqr_anomalies + ma_anomalies)
            
            # Calculate statistics
            arr = np.array(data, dtype=float)
            mean = np.mean(arr)
            std = np.std(arr)
            median = np.median(arr)
            
            results[metric_name] = {
                'anomaly_indices': sorted(list(all_anomalies)),
                'anomaly_count': len(all_anomalies),
                'anomaly_percentage': (len(all_anomalies) / len(data) * 100) if data else 0,
                'statistics': {
                    'mean': float(mean),
                    'std': float(std),
                    'median': float(median),
                    'min': float(np.min(arr)),
                    'max': float(np.max(arr))
                },
                'methods_used': {
                    'z_score': len(z_score_anomalies),
                    'iqr': len(iqr_anomalies),
                    'moving_average': len(ma_anomalies)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing metric {metric_name}: {e}")
            results[metric_name] = {'error': str(e)}
    
    return results


def calculate_health_score(metrics_data: Dict[str, List[float]]) -> Tuple[float, str]:
    """
    Calculate overall system health score based on anomaly detection.
    
    Args:
        metrics_data: Dictionary of metric names to their time series data
        
    Returns:
        Tuple of (health_score, status_message)
    """
    try:
        analysis_results = analyze_system_metrics(metrics_data)
        
        if not analysis_results:
            return 0.0, "无数据"
        
        # Calculate weighted anomaly percentage
        total_anomaly_pct = 0
        valid_metrics = 0
        
        for metric_name, result in analysis_results.items():
            if 'error' not in result:
                total_anomaly_pct += result['anomaly_percentage']
                valid_metrics += 1
        
        if valid_metrics == 0:
            return 0.0, "无有效数据"
        
        avg_anomaly_pct = total_anomaly_pct / valid_metrics
        
        # Convert to health score (100 = healthy, 0 = unhealthy)
        health_score = max(0.0, 100.0 - avg_anomaly_pct * 10)
        
        # Determine status
        if health_score >= 90:
            status = "优秀 - 系统运行正常"
        elif health_score >= 70:
            status = "良好 - 存在少量异常"
        elif health_score >= 50:
            status = "警告 - 存在明显异常"
        else:
            status = "严重 - 需要立即处理"
        
        return health_score, status
        
    except Exception as e:
        logger.error(f"Error calculating health score: {e}")
        return 0.0, f"计算错误: {e}"

