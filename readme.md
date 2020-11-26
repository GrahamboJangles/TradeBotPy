Yes, there are some lines that could be written better. But I just made this to work. And it does... For the most part.

- Is lite enough to run on a Raspberry Pi Zero.

- Backtesting and live trading in the same script, just change the backtesting variable.

- Just add your own strategy and have it return an advice column.

- Enter your own email credentials for error reporting.

- Enter your own API keys.

- Pull requests welcome.


# TO DO:
- if first order was too long ago, it will slow down pi because of live backtesting
- if past market hours and holding positions, close them
- going from short to long makes the bot buy too much, but is corrected shortly. not a huge problem but should fix

## Low priority:
- correlation graph of bot performance backtest & profit
- add some additional statistical analysis to the backtesting (STD, # of days up/# of days down)
- maybe add a debugging mode to print stuff
- backtest AMZN with no shorting
- maybe for ext market limit order, gradually increase limit_order difference if not filled
 
# KIND OF DONE:
- might need to add something to check if this has already been run because it appends over and over if i run it multiple times
 
# DONE:
- get rid of HOLD, and just replace with previous action
- if we can't buy QUANTITY, then trade CASH / limit_price
- MAKE SURE THAT WE'RE NOT GOING SHORT EVER ok maybe not
- backtest on AMZN cuz of its high price - DONE, it performed awful
- make it so the loading bar is only called if it will take a certain amount of time
- replace orders with order function
- add margin options
- check if need to trade during extended hours
- maybe I shouldn't do extended hours, it doesn't really seem to be worth it
- additonally, backtest closing positions before market close
- backtest with 2-4x margin during market hours
- maybe stop using market orders, seem to be losing quite a bit to slippage depending on volitility
- add a test to see if we actually get filled, and if not, try again
- add a graph using Alpaca order data and put it underneath the backtesting graph to compare
- change the wait time until next day to wait for a specific time delta instead of checking every minute


[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]()
Colab link doesn't work yet
