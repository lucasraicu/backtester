# backtester
Slow Turtle BackTesting with CRYPTEX

To plot the data in the CSV files, you can run the following python program.

python3 plot-data.py -h
usage: plot-data.py [-h] [--show-figure] input_csv [output_file]

Plot OHLC data, mark bull/bear segments, and optionally show/save the figure.

positional arguments:
  input_csv      Path to the input CSV file.
  output_file    Optional output filename (HTML or image).

options:
  -h, --help     show this help message and exit
  --show-figure  If set, display the Plotly figure on screen.

To plot and display figure in a browser:
python3 plot-data.py data/btc_cycle4_1D.csv --show-figure

To plot and save output file to an image:
python3 plot-data.py data/btc_cycle4_1D.csv btc_cycle4_1D.jpg

To plot and save output file to an HTML file:
python3 plot-data.py data/btc_cycle4_1D.csv btc_cycle4_1D.html

There are a number of CSV files for historical BTCUSD pricing data, which can be used for this backtester. 
Additional datasets can be downloaded from the CRYPTEX: fine-grained CRYPTocurrency datasets EXploration
http://crypto.cs.iit.edu/datasets/download.html.  

To run the backtester, here is the command line usage:
python3 backtester-parallel.py -h
Usage: python backtester-parallel.py <parallelism> <data_file> <start_coin> <start_cash> <min_window_size> <max_window_size> <debug> <figure>

One particular example is:
python3 backtester-parallel.py 16 data/btc_cycle2_5D.csv 0 1000 2 7 False False

Sample output is:
1.0s: 255/2700 completed...
2.005s: 724/2700 completed...
3.005s: 1199/2700 completed...
4.007s: 1673/2700 completed...
5.017s: 2152/2700 completed...
6.020s: 2700/2700 completed...
...
Best Parameters: Window Size: 0, Stop Percentage: 0.1, Buy Window: 4, Sell Window: 4, Go Percentage: 5.0, Bad Percentage: 0.1 
Final Balance (in cash): 630656.99
Total Trades: 95
buy_good: 27, buy_bad: 20, sell_good: 20, sell_bad: 27
Win Average: 116.49934967041017, Loss Average: -41.75677998860677
Elapsed Time: 6.366 seconds
