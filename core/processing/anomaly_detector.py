"""
Anomaly detection for data analysis.
"""

from typing import List
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
