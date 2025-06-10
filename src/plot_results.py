import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_portfolio_allocation(mvo_weights, selected_symbols):
    """
    1. Biểu đồ phân bổ trọng số danh mục đầu tư (Pie chart)
    """
    plt.figure(figsize=(6, 6))
    plt.pie(mvo_weights, labels=selected_symbols, autopct='%1.1f%%', startangle=90, shadow=True)
    plt.title('Phân bổ danh mục đầu tư theo mô hình MVO', fontsize=14)
    plt.axis('equal')  # Đảm bảo pie chart là hình tròn
    plt.tight_layout()
    plt.show()

def plot_return_risk_comparison(expected_returns, risks, selected_symbols):
    """
    2. Biểu đồ so sánh tỷ suất lợi nhuận và rủi ro
    """
    plt.figure(figsize=(8, 6))
    x = np.arange(len(selected_symbols))
    width = 0.35

    plt.bar(x - width/2, [r*100 for r in expected_returns], width, 
            label='Lợi nhuận kỳ vọng (%)', color='green', alpha=0.7)
    plt.bar(x + width/2, [r*100 for r in risks], width, 
            label='Rủi ro (%)', color='red', alpha=0.7)

    plt.xlabel('Mã cổ phiếu')
    plt.ylabel('Phần trăm (%)')
    plt.title('Lợi nhuận kỳ vọng và rủi ro của từng cổ phiếu', fontsize=14)
    plt.xticks(x, selected_symbols)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_portfolio_performance(all_data, selected_symbols, mvo_weights):
    """
    3. Biểu đồ hiệu suất của danh mục đầu tư theo thời gian
       - Giả sử all_data[symbol] có cột 'closing_price'.
       - Vẽ giá trị danh mục + tỷ suất lợi nhuận theo thời gian.
    """
    plt.figure(figsize=(14, 7))
    closing_prices = {}
    portfolio_value = None
    dates = None

    # Lấy 252 ngày (1 năm) gần nhất, tùy chỉnh nếu cần
    for symbol in selected_symbols:
        stock_data = all_data[symbol].reset_index()
        if dates is None:
            dates = stock_data.index[-252:]  # Lấy 1 năm gần nhất

        # Lấy giá đóng cửa 1 năm gần nhất
        closing_prices[symbol] = stock_data['closing_price'].iloc[-252:].values

        # Tính giá trị danh mục đầu tư
        weight = mvo_weights[selected_symbols.index(symbol)]
        if portfolio_value is None:
            portfolio_value = closing_prices[symbol] * weight
        else:
            portfolio_value += closing_prices[symbol] * weight

    # Vẽ biểu đồ giá trị danh mục đầu tư
    plt.subplot(2, 1, 1)
    plt.plot(dates, portfolio_value, 'b-', linewidth=2)
    plt.title('Giá trị danh mục đầu tư theo thời gian', fontsize=14)
    plt.xlabel('Ngày')
    plt.ylabel('Giá trị')
    plt.grid(True, linestyle='--', alpha=0.7)

    # Vẽ biểu đồ tỷ suất lợi nhuận danh mục
    plt.subplot(2, 1, 2)
    portfolio_returns = np.diff(portfolio_value) / portfolio_value[:-1]
    plt.plot(dates[1:], portfolio_returns, 'g-', linewidth=1)
    plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
    plt.fill_between(dates[1:], portfolio_returns, 0, 
                     where=(portfolio_returns > 0), color='green', alpha=0.3)
    plt.fill_between(dates[1:], portfolio_returns, 0, 
                     where=(portfolio_returns < 0), color='red', alpha=0.3)
    plt.title('Tỷ suất lợi nhuận danh mục đầu tư theo thời gian', fontsize=14)
    plt.xlabel('Ngày')
    plt.ylabel('Tỷ suất lợi nhuận')
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()

def plot_sharpe_ratios(selected_symbols, sharpe_ratios, port_sharpe):
    """
    4. Biểu đồ so sánh Sharpe ratio
    """
    plt.figure(figsize=(8, 6))
    plt.bar(selected_symbols, sharpe_ratios, color='purple', alpha=0.7)
    plt.axhline(y=port_sharpe, color='r', linestyle='--', 
                label=f'Sharpe ratio của danh mục: {port_sharpe:.4f}')
    plt.title('Sharpe ratio của các cổ phiếu trong danh mục', fontsize=14)
    plt.xlabel('Mã cổ phiếu')
    plt.ylabel('Sharpe ratio')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

def plot_correlation_matrix(market_data, selected_symbols):
    """
    5. Biểu đồ ma trận tương quan giữa các cổ phiếu
       - market_data là dữ liệu (DataFrame hoặc array) chứa các cột là các mã cổ phiếu
    """
    plt.figure(figsize=(8, 6))
    # Giả sử market_data là numpy array. Nếu là DataFrame, dùng .corr() sẽ tiện hơn
    correlation_matrix = np.corrcoef(market_data, rowvar=False)
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', 
                xticklabels=selected_symbols, yticklabels=selected_symbols)
    plt.title('Ma trận tương quan giữa các cổ phiếu', fontsize=14)
    plt.tight_layout()
    plt.show()

def plot_prediction_comparison(all_predictions, selected_symbols):
    """
    6. Biểu đồ so sánh dự báo và giá thực tế (LSTM vs Actual)
       - all_predictions[symbol] = {'y_test':..., 'lstm_pred':...}
    """
    plt.figure(figsize=(12, 10))
    for i, symbol in enumerate(selected_symbols):
        plt.subplot(2, 2, i+1)
        y_test = all_predictions[symbol]['y_test']
        lstm_pred = all_predictions[symbol]['y_pred']
        
        plt.plot(y_test, label='Giá thực tế', color='blue')
        plt.plot(lstm_pred, label='Dự báo', color='red', linestyle='--')
        
        plt.title(f'So sánh dự báo và giá thực tế - {symbol}', fontsize=12)
        plt.xlabel('Thời gian')
        plt.ylabel('Giá cổ phiếu (đã chuẩn hóa)')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

def plot_efficient_frontier(selected_symbols, expected_returns, cov_matrix, 
                            port_risk, port_return, num_portfolios=10000, 
                            risk_free_rate=0.02/52, label_mvo='Danh mục MVO'):
    """
    7. Biểu đồ đường hiệu quả (Efficient Frontier)
       - Sinh num_portfolios danh mục ngẫu nhiên để tạo scatter.
       - Đánh dấu danh mục tối ưu MVO trên biểu đồ.
    """
    results = np.zeros((3, num_portfolios))
    weights_record = []
    n = len(selected_symbols)

    for i in range(num_portfolios):
        weights = np.random.random(n)
        weights /= np.sum(weights)
        weights_record.append(weights)
        
        p_return = np.sum(weights * expected_returns)
        p_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        p_sharpe = (p_return - risk_free_rate) / p_risk if p_risk > 0 else 0
        
        results[0, i] = p_return
        results[1, i] = p_risk
        results[2, i] = p_sharpe

    # Tìm danh mục Sharpe tối đa
    max_sharpe_idx = np.argmax(results[2])
    max_sharpe_return = results[0, max_sharpe_idx]
    max_sharpe_risk = results[1, max_sharpe_idx]

    # Tìm danh mục rủi ro tối thiểu
    min_risk_idx = np.argmin(results[1])
    min_risk_return = results[0, min_risk_idx]
    min_risk_risk = results[1, min_risk_idx]

    plt.figure(figsize=(10, 7))
    sc = plt.scatter(results[1, :], results[0, :], c=results[2, :], cmap='viridis', 
                     marker='o', alpha=0.5)
    plt.colorbar(sc, label='Sharpe ratio')

    # Đánh dấu các danh mục đặc biệt
    plt.scatter(max_sharpe_risk, max_sharpe_return, marker='*', color='r', s=300, label='Sharpe tối đa')
    plt.scatter(min_risk_risk, min_risk_return, marker='*', color='g', s=300, label='Rủi ro tối thiểu')
    plt.scatter(port_risk, port_return, marker='*', color='black', s=300, label=label_mvo)

    plt.title('Đường hiệu quả (Efficient Frontier)', fontsize=14)
    plt.xlabel('Rủi ro (Volatility)')
    plt.ylabel('Lợi nhuận kỳ vọng')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

def print_summary_table(selected_symbols, mvo_weights, expected_returns, 
                        risks, sharpe_ratios, port_return, port_risk, port_sharpe):
    """
    8. Tạo bảng thống kê tổng hợp danh mục đầu tư
    """
    summary_data = {
        'Cổ phiếu': selected_symbols,
        'Trọng số (%)': [w*100 for w in mvo_weights],
        'Lợi nhuận kỳ vọng (%)': [r*100 for r in expected_returns],
        'Rủi ro (%)': [r*100 for r in risks],
        'Sharpe ratio': sharpe_ratios
    }

    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('Trọng số (%)', ascending=False).round(2)

    print("\nBảng thống kê tổng hợp danh mục đầu tư:")
    print(summary_df.to_string(index=False))

    # Thêm hàng tổng
    total_row = pd.DataFrame({
        'Cổ phiếu': ['TỔNG'],
        'Trọng số (%)': [sum(mvo_weights)*100],  # hoặc sum(w*100 for w in mvo_weights)
        'Lợi nhuận kỳ vọng (%)': [port_return*100],
        'Rủi ro (%)': [port_risk*100],
        'Sharpe ratio': [port_sharpe]
    }).round(2)

    summary_df = pd.concat([summary_df, total_row], ignore_index=True)
    print("\nKết quả tổng hợp:")
    print(summary_df.to_string(index=False))