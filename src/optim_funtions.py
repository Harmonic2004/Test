import numpy as np
from scipy.optimize import minimize
import scipy.optimize as sco
import random


# Tính toán các chỉ số
def calculate_returns_risk(predictions, scaler=None):

    if scaler is not None:
      original_predictions = scaler.inverse_transform(predictions.reshape(-1, 1))
    else:
      original_predictions = predictions

    # Lợi nhuận hàng ngày
    returns = np.diff(original_predictions, axis=0) / original_predictions[:-1]

    # Lợi nhuận kỳ vọng và rủi ro
    expected_return = np.mean(returns)
    risk = np.std(returns)

    risk_free_rate = 0.02 / 52
    sharpe_ratio = (expected_return - risk_free_rate) / risk if risk != 0 else 0

    # Tỷ lệ Sortino (chỉ tính downside risk)
    downside_returns = returns[returns < 0]
    downside_risk = np.std(downside_returns) if len(downside_returns) > 0 else 0
    sortino_ratio = (expected_return - risk_free_rate) / downside_risk if downside_risk > 0 else 0

    # Maximum Drawdown
    cumulative = np.cumprod(1 + returns.flatten())
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative / running_max) - 1
    max_drawdown = np.min(drawdown)

    return {
        'expected_return': expected_return,
        'risk': risk,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown': max_drawdown
    }

#-----------------------------------------------------------------------------------------------------------------------------------------
# MVO
def mvo_optimization(expected_returns, cov_matrix, 
                     risk_free_rate=0.02/52,
                     max_weight=0.4,    # Giới hạn trọng số tối đa
                     alpha=0.1):       # Mức phạt danh mục tập trung
    """
    Tối ưu hóa danh mục đầu tư theo phương pháp Mean-Variance Optimization (MVO)
    với các ràng buộc nâng cao:
      - Tổng trọng số = 1
      - 0 <= w_i <= max_weight (để tránh dồn hết vào 1 mã)
      - Thêm penalty alpha * sum(w_i^2) nếu alpha > 0 (để tránh danh mục tập trung)
    """
    n = len(expected_returns)

    # Hàm mục tiêu: Tối đa hóa Sharpe Ratio (hoặc tối thiểu hóa -Sharpe)
    def negative_sharpe_ratio(weights):
        portfolio_return = np.sum(weights * expected_returns)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = (portfolio_return - risk_free_rate) / (portfolio_risk + 1e-8)
        # Thêm penalty để "phạt" danh mục quá tập trung
        penalty = alpha * np.sum(weights**2)
        return -sharpe + penalty

    # Ràng buộc: Tổng trọng số = 1
    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

    # Biên: 0 <= w_i <= max_weight
    bounds = tuple((0, max_weight) for _ in range(n))

    # Giá trị ban đầu cho thuật toán tối ưu
    initial_weights = np.array([1/n] * n)

    try:
        result = minimize(
            negative_sharpe_ratio, 
            initial_weights, 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints, 
            options={'maxiter': 1000}
        )

        if result['success']:
            weights = result['x']
            # Làm tròn các trọng số nhỏ
            weights[weights < 1e-4] = 0
            # Chuẩn hóa lại để tổng = 1 (tránh sai số số học)
            if np.sum(weights) > 0:
                weights = weights / np.sum(weights)
            else:
                weights = initial_weights
            return weights
        else:
            print("Tối ưu hóa không thành công:", result['message'])
            return initial_weights
    except Exception as e:
        print(f"Lỗi trong quá trình tối ưu hóa: {e}")
        return initial_weights



# Định nghĩa các hàm tính toán hiệu suất danh mục đầu tư
def portfolio_return(weights, expected_returns):
    """Tính lợi nhuận kỳ vọng của danh mục đầu tư"""
    return np.sum(weights * expected_returns)

def portfolio_volatility(weights, cov_matrix):
    """Tính rủi ro (độ biến động) của danh mục đầu tư"""
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

def portfolio_sharpe_ratio(weights, expected_returns, cov_matrix, risk_free_rate=0.02/52):
    """Tính Sharpe ratio của danh mục đầu tư"""
    portfolio_ret = portfolio_return(weights, expected_returns)
    portfolio_vol = portfolio_volatility(weights, cov_matrix)
    return (portfolio_ret - risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0


#----------------------------------------------------------------------------------------------------------------------------
# Phương pháp Monte Carlo
def monte_carlo_simulation(expected_returns, cov_matrix, risk_free_rate=0.02/52, 
                                   num_simulations=50000, max_weight=0.4):
    num_assets = len(expected_returns)
    results = np.zeros((num_simulations, num_assets + 3))  # +3 for return, volatility, sharpe
    
    for i in range(num_simulations):
        # Tạo trọng số ngẫu nhiên với ràng buộc max_weight
        weights = np.random.uniform(0, max_weight, num_assets)
        # Chuẩn hóa tổng = 1
        weights = weights / np.sum(weights)
        
        # Tính toán lợi nhuận và rủi ro của danh mục
        portfolio_ret = portfolio_return(weights, expected_returns)
        portfolio_vol = portfolio_volatility(weights, cov_matrix)
        sharpe = (portfolio_ret - risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
        
        # Lưu kết quả
        results[i, :num_assets] = weights
        results[i, num_assets] = portfolio_ret
        results[i, num_assets + 1] = portfolio_vol
        results[i, num_assets + 2] = sharpe
    
    # Tìm danh mục có tỷ lệ Sharpe cao nhất
    max_sharpe_idx = np.argmax(results[:, num_assets + 2])
    
    optimal_weights = results[max_sharpe_idx, :num_assets]
    optimal_return = results[max_sharpe_idx, num_assets]
    optimal_vol = results[max_sharpe_idx, num_assets + 1]
    optimal_sharpe = results[max_sharpe_idx, num_assets + 2]
    
    # Tìm danh mục có rủi ro thấp nhất
    min_vol_idx = np.argmin(results[:, num_assets + 1])
    min_vol_weights = results[min_vol_idx, :num_assets]
    
    return {
        'max_sharpe': {
            'weights': optimal_weights,
            'return': optimal_return,
            'risk': optimal_vol,
            'sharpe': optimal_sharpe
        },
        'min_volatility': {
            'weights': min_vol_weights,
            'return': results[min_vol_idx, num_assets],
            'risk': results[min_vol_idx, num_assets + 1],
            'sharpe': results[min_vol_idx, num_assets + 2]
        },
        'efficient_frontier': results[:, [num_assets + 1, num_assets]]  # risk, return pairs
    }

