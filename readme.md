[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/gist/GrahamboJangles/8cbe716adeb7f091a1832dac9a86a4c9/forms-snippets.ipynb)

Yes, there are some lines that could be written better. But I just made this to work.
- Uses Alpaca

- Is lite enough to run on a Raspberry Pi Zero.

- Backtesting and live trading in the same script, just change the backtesting variable.

- Just add your own strategy and have it return an advice column.

- Enter your own email credentials for error reporting.

- Enter your own API keys.

- Pull requests welcome.


# TO DO:
- limit the amount of data downloaded during live trading, right now it downloads all data since first trade but that will slow down the script over time
   - i just limited it to 100 minutes as of right now

##kind of done: 
- if past market hours and holding positions, close them

## Low priority:
- correlation graph of bot performance backtest & profit
- add some additional statistical analysis to the backtesting (STD, # of days up/# of days down)
- backtest AMZN ext market limit order, gradually increase limit_order difference if not filled with no shorting
 
# DONE:
- might need to add something to check if this has already been run because it appends over and over if i run it multiple times
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
- maybe add a debugging mode to print stuff
- add a graph using Alpaca order data and put it underneath the backtesting graph to compare
- change the wait time until next day to wait for a specific time delta instead of checking every minute
- change the closing all positions because of using too much cash to correct to the amount of shares that we want instead of closing out
- add loading bar for waiting until open
- sometimes the market closes early on holiday's, should change the close early to a variable using API close times
- check the amount of usable cash before each trade to prevent overbuying or selling
- make strategy volatility adjustable
- going from short to long makes the bot buy too much, but is corrected shortly
