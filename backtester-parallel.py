import sys
from pandas import read_csv, DataFrame
import plotly.graph_objects as go
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import time
import plotly.io as pio
import gc

def run_simulation(df, window_size, start_coin, start_cash, debug, stop_percentage, max_window_size, buy_window, sell_window, go_percentage, bad_percentage, cleanup):
    if max_window_size < min(buy_window, sell_window):
        return 0, 0, 0, 0, 0, 0, [], [], [], [], [], []

    #data = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    data = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    fee = 0.000
    trades = 0
    sell_good = 0
    sell_bad = 0
    buy_good = 0
    buy_bad = 0
    wins = []
    losses = []
    data_len = len(data)
    close_price = 0.0
    highest_price = 0.0

    coin = start_coin
    cash = start_cash

    # Lists to store values for visualization
    balance_history = []
    close_price_history = []
    volume_history = []
    buy_signals = []
    sell_signals = []

    # Lists to store min_range and max_range for visualization
    min_range_history = []
    max_range_history = []

    # List to store stop prices for visualization
    stop_price_history = []
    go_price_history = []
    bad_price_history = []

    last_buy_price = 0.0
    last_sell_price = 0.0
    
    go_price = 0
    bad_price = 0

    for i in range(max_window_size, data_len):
        high_price = data['High'].iloc[i]
        low_price = data['Low'].iloc[i]
        close_price = data['Close'].iloc[i]
        Volume = data['Volume'].iloc[i]
        curr_profit = 0
        decision = 0

        close_price_history.append((i, close_price))
        volume_history.append((i, Volume))
        balance_history.append((i, cash + coin * close_price))

        if i == min(buy_window, sell_window) and debug:
            print(i, close_price, close_price, close_price, close_price, coin, cash, coin + cash / close_price,
                  coin * close_price + cash, trades)

        min_range = min(data['Close'].iloc[i - sell_window + 1:i + 1])
        max_range = max(data['Close'].iloc[i - buy_window + 1:i + 1])
        min_range_history.append((i, min_range))
        max_range_history.append((i, max_range))

        if coin > 0:
            # Trailing stop logic
            if close_price > highest_price:
                highest_price = close_price

            stop_price = highest_price * (1 - stop_percentage)
            stop_price_history.append((i, stop_price))
            
                
            go_price_history.append((i, go_price))

            # Sell if the price falls below the stop price, min range, or if the profit exceeds go_percentage
            if close_price <= min_range or close_price <= stop_price or (last_buy_price > 0 and close_price >= go_price):
                
                bad_price = close_price * (1 + bad_percentage)
                bad_price_history.append((i, bad_price))
                
                
                
                
                cash = coin * close_price * (1 - fee)
                trades += 1
                if debug:
                    print("***trade #", trades, "sell", coin, "BTC for $", cash)
                coin = 0.0
                decision = -1
                sell_signals.append((i, close_price))
                if last_buy_price > 0:
                    curr_profit = close_price - last_buy_price
                    if curr_profit >= 0:
                        sell_good += 1
                        wins.append(curr_profit)
                    else:
                        sell_bad += 1
                        losses.append(curr_profit)
                last_sell_price = close_price

        elif cash > 0:
            # Looking to buy with additional Volume-based conditions
            
            bad_price_history.append((i, bad_price))
            
            if close_price >= max_range  or (last_sell_price > 0 and close_price <= bad_price):
               
                
                go_price = close_price * (1 + go_percentage)
                go_price_history.append((i, go_price))
                
                
                
                coin = cash / close_price * (1 - fee)
                highest_price = close_price  # Reset highest price after buying
                stop_price = highest_price * (1 - stop_percentage)
                stop_price_history.append((i, stop_price))  # Add stop price after buying
                if debug:
                    print("***trade #", trades, "buy", coin, "BTC for $", cash)
                cash = 0.0
                trades += 1
                decision = 1
                buy_signals.append((i, close_price))
                if last_sell_price > 0:
                    curr_profit = close_price - last_sell_price
                    if curr_profit >= 0:
                        buy_good += 1
                    else:
                        buy_bad += 1
                last_buy_price = close_price

        if debug:
            print(i, close_price, min_range, max_range, coin, cash, coin + cash / close_price, coin * close_price + cash, trades, decision)

    if debug:
        print(data_len, close_price, min_range, max_range, coin, cash, coin + cash / close_price,
              coin * close_price + cash, trades, decision)

    if len(wins) == 0:
        aver_wins = 0.0
    else:
        aver_wins = sum(wins) / len(wins)

    if len(losses) == 0:
        aver_losses = 0.0
    else:
        aver_losses = sum(losses) / len(losses)
    
    if cleanup:
    	balance_history = []
    	close_price_history = []
    	volume_history = []
    	buy_signals = []
    	sell_signals = []
    	min_range_history = []
    	max_range_history = []
    	stop_price_history = []
    	go_price_history = []
    	bad_price_history = []
    	balance_history = []
    	#del close_price_history
    	#del volume_history
    	#del buy_signals
    	#del sell_signals
    	#del min_range_history
    	#del max_range_history
    	#del stop_price_history
    	#del go_price_history
    	#del bad_price_history
    	# Force garbage collection
    	gc.collect()
    
    return data_len, coin, cash, coin + cash / close_price, coin * close_price + cash, trades, balance_history, close_price_history, volume_history, buy_signals, sell_signals, buy_good, buy_bad, sell_good, sell_bad, aver_wins, aver_losses, window_size, stop_percentage, min_range_history, max_range_history, stop_price_history, go_price_history, bad_price_history, buy_window, sell_window, go_percentage, bad_percentage

def main(argv):
    if len(argv) != 8:
        print('Usage: python trader-simple-parallel.py <parallelism> <data_file> <start_coin> <start_cash> <min_window_size> <max_window_size> <debug> <figure>')
        sys.exit(2)

    workers = int(argv[0])
    data_file = argv[1]
    start_coin = float(argv[2])
    start_cash = float(argv[3])
    min_window_size = int(argv[4])
    max_window_size = int(argv[5])
    debug = argv[6].lower() == 'true'
    figure = argv[7].lower() == 'true'

    # Start time
    start_time = time.time()
    cur_time = time.time()

    # Load the data
    df = read_csv(data_file, skiprows=0, sep=",")

    window_size = 0
    #stop_percentages = [0.01, 0.02,0.04,0.06,0.08,0.1,0.12,0.14,0.16,0.18,0.2,0.22,0.24,0.26,0.28,0.3,0.32,0.34,0.36,0.38,0.4,0.42,0.44,0.46,0.48,0.5]
    #stop_percentages = [0.1,0.12,0.14,0.16,0.18,0.2,0.22,0.24,0.26,0.28,0.3,0.32,0.34,0.36,0.38,0.4,0.42,0.44,0.46,0.48,0.5]
    #buy_windows = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84, 91, 98]
    #sell_windows = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84, 91, 98]
    
    sell_windows = []
    sell_window_min = min_window_size
    sell_window_max = max_window_size
    sell_window_increment = 1    
    for i in range(sell_window_min,sell_window_max,sell_window_increment):
    	sell_windows.append(i)
    
    #sell_windows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    stop_percentages = [0.1,0.2,0.3]
    
    buy_windows = []
    buy_window_min = min_window_size
    buy_window_max = max_window_size
    buy_window_increment = 1    
    for i in range(buy_window_min,buy_window_max,buy_window_increment):
    	buy_windows.append(i)
    
    #buy_windows = [1, 7, 14]
    #sell_windows = [14]
    #go_percentages = [2.0]
    #bad_percentages = [2.0]
    #go_percentages = [1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3]
    #bad_percentages = [1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3]
    go_percentages = [0.1, 1.0, 2.0, 3.0, 4.0, 5.0]
    bad_percentages = [0.1, 1.0, 2.0, 3.0, 4.0, 5.0]
    #go_percentages = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    #bad_percentages = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    #go_percentages = [0.01, 0.02,0.04,0.06,0.08,0.1,0.12,0.14,0.16,0.18,0.2,0.22,0.24,0.26,0.28,0.3,0.32,0.34,0.36,0.38,0.4,0.42,0.44,0.46,0.48,0.5]
    #bad_percentages = [0.01,0.02,0.04,0.06,0.08,0.1,0.12,0.14,0.16,0.18,0.2,0.22,0.24,0.26,0.28,0.3,0.32,0.34,0.36,0.38,0.4,0.42,0.44,0.46,0.48,0.5]
    
    #stop_percentages = [0.01, 0.02,0.04,0.06,0.08,0.1]
    #buy_windows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    #sell_windows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    #go_percentages = [0.01, 0.02,0.04,0.06,0.08,0.1]
    #bad_percentages = [0.01,0.02,0.04,0.06,0.08,0.1]

    best_params = None
    best_profit = float('-inf')
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(run_simulation, df, window_size, start_coin, start_cash, debug, stop_percentage, max_window_size, buy_window, sell_window, go_percentage, bad_percentage, True)
            #for window_size in window_sizes
            for stop_percentage in stop_percentages
            for buy_window in buy_windows
            for sell_window in sell_windows
            for go_percentage in go_percentages
            for bad_percentage in bad_percentages
        ]
        
        # Collect results
        results = []
        for i, future in enumerate(futures):
            result = future.result()  # Waits for the future to complete
            results.append(result)
            cur_elapsed_time = time.time() - cur_time
            elapsed_time = round(time.time() - start_time, 3)
            if cur_elapsed_time >= 1.0:
                print(f"{elapsed_time}s: {i+1}/{len(futures)} completed...")
                cur_time = time.time()

    for result in results:
    	_, end_coin, end_cash, final_balance, final_cash, trades, _, _, _, _, _, buy_good, buy_bad, sell_good, sell_bad, win_average, loss_average, window_size, stop_percentage, _, _, _, _, _, buy_window, sell_window, go_percentage, bad_percentage = result
    
    	print(f"Window Size: {window_size}, Stop Percentage: {stop_percentage}, Buy Window: {buy_window}, Sell Window: {sell_window}, Go Percentage: {go_percentage}, Bad Percentage: {bad_percentage}, "
          f"Start Coins: {start_coin}, Start Cash: {start_cash}, "
          f"End Coins: {end_coin}, End Cash: {end_cash}, Final Balance: {final_balance}, Balance (in cash): {final_cash}, "
          f"Trades: {trades}, buy_good: {buy_good}, buy_bad: {buy_bad}, sell_good: {sell_good}, sell_bad: {sell_bad}, win_average: {win_average}, loss_average: {loss_average}")

    	if final_cash > best_profit:
    		print('****found a better configuration:',window_size, stop_percentage, buy_window, sell_window, go_percentage, bad_percentage, start_coin, start_cash, final_cash)
    		best_profit = final_cash
    		best_params = (window_size, stop_percentage, buy_window, sell_window, go_percentage, bad_percentage, start_coin, start_cash, final_cash)

    #if best_params:
    #    print(f"Best parameters: Window Size: {best_params[0]}, Stop Percentage: {best_params[1]}, Buy Window: {best_params[2]}, Sell Window: {best_params[3]}, Final Balance: {best_params[6]}")
    window_size, stop_percentage, buy_window, sell_window, go_percentage, bad_percentage, start_coin, start_cash, final_cash = best_params
    print('****found the best configuration:',window_size, stop_percentage, buy_window, sell_window, go_percentage, bad_percentage, start_coin, start_cash, final_cash)
    #window_size, stop_percentage, buy_window, sell_window, start_coin, start_cash, final_cash = best_params
    result = run_simulation(df, window_size, start_coin, start_cash, debug, stop_percentage, max_window_size, buy_window, sell_window, go_percentage, bad_percentage, False)
    _, end_coin, end_cash, final_balance, final_cash, trades, balance_history, close_price_history, volume_history, buy_signals, sell_signals, buy_good, buy_bad, sell_good, sell_bad, win_average, loss_average, window_size, stop_percentage, min_range_history, max_range_history, stop_price_history, go_price_history, bad_price_history, buy_window, sell_window , go_percentage, bad_percentage = result

    print("****************************************")
    print(f"\nBest Parameters: Window Size: {window_size}, Stop Percentage: {stop_percentage}, Buy Window: {buy_window}, Sell Window: {sell_window}, Go Percentage: {go_percentage}, Bad Percentage: {bad_percentage} ")
    print(f"Final Balance (in cash): {round(final_cash,2)}")
    print(f"Total Trades: {trades}")
    print(f"buy_good: {buy_good}, buy_bad: {buy_bad}, sell_good: {sell_good}, sell_bad: {sell_bad}")
    print(f"Win Average: {win_average}, Loss Average: {loss_average}")
    print(f"Elapsed Time: {elapsed_time} seconds")



    if figure:
        
        balance_x, balance_y = zip(*balance_history)
        price_x, price_y = zip(*close_price_history)
        #volume_x, volume_y = zip(*volume_history)
        buy_x, buy_y = zip(*buy_signals)
        sell_x, sell_y = zip(*sell_signals)
        min_range_x, min_range_y = zip(*min_range_history)
        max_range_x, max_range_y = zip(*max_range_history)
        stop_price_x, stop_price_y = zip(*stop_price_history)
        go_price_x, go_price_y = zip(*go_price_history)
        bad_price_x, bad_price_y = zip(*bad_price_history)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=balance_x, y=balance_y, mode='lines', name='Balance'))
        fig.add_trace(go.Scatter(x=price_x, y=price_y, mode='lines', name='Close Price'))
        #fig.add_trace(go.Bar(x=volume_x, y=volume_y, name='Volume', marker=dict(color='rgba(0, 255, 0, 0.5)'), opacity=0.5))
        fig.add_trace(go.Scatter(x=buy_x, y=buy_y, mode='markers', marker=dict(color='green', size=9), name='Buy Signal'))
        fig.add_trace(go.Scatter(x=sell_x, y=sell_y, mode='markers', marker=dict(color='red', size=9), name='Sell Signal'))
        fig.add_trace(go.Scatter(x=min_range_x, y=min_range_y, mode='lines', line=dict(color='gray'), name='Min Range'))
        fig.add_trace(go.Scatter(x=max_range_x, y=max_range_y, mode='lines', line=dict(color='black'), name='Max Range'))
        fig.add_trace(go.Scatter(x=stop_price_x, y=stop_price_y, mode='lines', line=dict(color='purple'), name='Stop Price'))
        fig.add_trace(go.Scatter(x=go_price_x, y=go_price_y, mode='lines', line=dict(color='orange'), name='Go Price'))
        fig.add_trace(go.Scatter(x=bad_price_x, y=bad_price_y, mode='lines', line=dict(color='pink'), name='Bad Price'))
    
        
        graphTitle = 'Simulation Results: buy_window='+str(buy_window)+' sell_window='+str(sell_window)+' stop='+str(stop_percentage)+' go='+str(go_percentage)+ ' bad='+str(bad_percentage)+' trades='+str(trades)+' balance=$'+str(round(final_cash,2))
        output_filename = 'results-trader-simple-parallel-v3-Close-bw'+str(buy_window)+'-sw'+str(sell_window)+'-s'+str(stop_percentage)+'-g'+str(go_percentage)+'-b'+str(bad_percentage)+'.html'
        
        fig.update_layout(title=graphTitle, xaxis_title='Time', yaxis_title='$')
        fig.show()
        fig.write_html(output_filename)

if __name__ == "__main__":
    main(sys.argv[1:])
