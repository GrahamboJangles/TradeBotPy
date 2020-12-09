#@title Trade Bot { form-width: "25%" }

# %tb

# import Alpaca trade API, and install in Colab
try:
  import alpaca_trade_api as tradeapi
except:
  print("Installing alpaca_trade_api")
  #!pip install alpaca_trade_api --quiet
  import alpaca_trade_api as tradeapi

import pandas as pd

from datetime import datetime
import time

from tqdm import tqdm
from tqdm import trange

# authentication and connection details
api_key = "" #@param{type:"string"}
api_secret = "" #@param{type:"string"}
base_url = 'https://paper-api.alpaca.markets'

# instantiate REST API
api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

# Debugging

debug = False #@param{type:"boolean"}
verbose = True #@param{type:"boolean"}
# Debugging - set a custom test time
if debug:
  current_time = "09:30:00"

# Convert utc time to local?
# Try this if the current time is wrong
convert_time = False

backtesting = False #@param{type:"boolean"}
  
ticker = "SPY"
investment = 20000
keep_as_cash = 70000 - investment
margin_times = 4
shorting = True #@param{type:"boolean"}

global trade_ext_hours
trade_ext_hours = False #@param{type:"boolean"}

start_date = "automatic"
end_date = "automatic"

start_time = "9:30"
end_time = "16:00" # 4 p.m.

# Initialize
e = ""
portfolio_value = None

def get_current_datetime():
  global convert_time
  if not convert_time:
    now = datetime.now()
  else: now = utc_to_local(datetime.now())

  #24-hour format
  # print(now.strftime('%Y/%m/%d %H:%M:%S'))
  current_time = now.strftime('%H:%M:%S')
  #12-hour format
  curr_datetime = now.strftime('%Y/%m/%d %I:%M:%S %p')
  # current_time = now.strftime('%I:%M:%S %p')
  print(curr_datetime)
  #print(current_time)
  return current_time, curr_datetime

def check_if_open(api=api):
  # Check when the market opens/closes
  from datetime import datetime
  todays_date = datetime.today().strftime('%Y-%m-%d')
  date = todays_date
  calendar = api.get_calendar(start=date, end=date)[0]
  print('The market opened at {} and closed at {} on {}.'.format(
        calendar.open,
        calendar.close,
        date
        ))

  # Check if the market is open now.
  clock = api.get_clock()
  open = clock.is_open
  print('The market is {}'.format('open.' if open else 'closed.'))

  if debug:
    open = True

  current_time, curr_datetime = get_current_datetime()

  global trade_ext_hours

  if (current_time >= "16") and (current_time < "18"):
    ext_hours = True
    if trade_ext_hours:
      open = True
  elif (current_time >= "18") and (current_time < "9"):
    ext_hours = False
    open = False
  if (current_time > "15:58") and not trade_ext_hours:
    open = False
  if current_time > "9:30" and current_time < "16":
    open = True
    ext_hours = True

  ext_hours = True

  return open, calendar.open, calendar.close, date, ext_hours

# https://discuss.codecademy.com/t/how-to-convert-to-12-hour-clock/3920/3

import pytz

local_tz = pytz.timezone('US/Eastern')

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary

if not convert_time:
  now = datetime.now()
else: now = utc_to_local(datetime.now())

def wait_for_open():
  #global open 
  open = False
  if not open:
    print("Getting current time...")
    if debug:
      global current_time
    else:
      current_time, curr_datetime = get_current_datetime()

    split_time = str(current_time).split(":")
    hours = int(split_time[0])
    minutes = int(split_time[1])
    seconds = int(split_time[2])
    #print(hours, minutes, seconds)
    hours_till_open = (23 - hours) + 9
    if hours_till_open >= 23:
      hours_till_open = hours_till_open - 24
    minutes_till_open = (60 - minutes) + 30
    seconds_till_open = (0 - seconds)
    #print(hours_till_open, minutes_till_open, seconds_till_open)
    time_till_open = ((hours_till_open*60)*60) + (minutes_till_open*60) + seconds_till_open 
    print(f"Waiting {hours_till_open} hours, {minutes_till_open} minutes, and {seconds_till_open} seconds until open.")
    print(f"Or {time_till_open} seconds until open.")
   
    for i in trange(time_till_open):
      time.sleep(1-.01)

    open, open_time, close_time, todays_date, ext_hours = check_if_open()

    print("Getting current time")
    current_time, curr_datetime = get_current_datetime()

    if not open and current_time >= "9" and current_time < "16":
      print("Must be weekend or holiday, waiting till tommorow...")
      open = False
  return open, ext_hours

def get_market_data():
  if not backtesting:
    #try:
      # Getting time of first order
      #list_orders = api.list_orders(status="closed", direction="asc", limit=1)
      #first_order_fill_time = str(list_orders).split("'filled_at': '")
      #first_order_fill_time = str(first_order_fill_time[1]).split("',")
      #first_order_fill_time = first_order_fill_time[0]

      #ticker_data = api.get_barset(ticker, timeframe="1Min", start=first_order_fill_time)
      #ticker_data = ticker_data.df
      #ticker_data = ticker_data.between_time(time_range_start, time_range_end) 
    #except:
    ticker_data = api.get_barset(ticker, timeframe="1Min", limit=100)
    ticker_data = ticker_data.df
    ticker_data = ticker_data.between_time(start_time, end_time) 
  else:
    start = "2016-01-01" #@param {type:"date"}
    # start = "2014-01-01T09:30:00-04:00"
    start += "T09:30:00-04:00"
    end = "2016-01-01" #@param {type:"date"}
    end_today = True
    
    if not end_today:
      end += "T09:30:00-04:00"
      ticker_data = api.get_barset(ticker, timeframe="1Min", start=start, end=end)
    else: 
      ticker_data = api.get_barset(ticker, timeframe="1Min", start=start)
    ticker_data = ticker_data.df
    ticker_data = ticker_data.between_time(start_time, end_time) 
  
  ticker_data.columns = ticker_data.columns.droplevel(0)
  ticker_data.columns

  return ticker_data


def add_calculations(data, advice, margin_times=margin_times):
  count = 0

  stock = data

  # stock = stock.between_time('9:00', '18:00')
  # stock = stock.between_time(time_range_start, time_range_end)

  # first_close = stock['close'][0]
  # stock['close'] = stock['close'][0] * int(investment / stock['close'][0])
  stock['balance'] = stock['close']
  # stock['balance'][0] = investment
  balance = stock['balance']
  # balance[0] = investment
  # advice = stock['advice']
  # print(last_minute_data)
  # input()
  # stock = 
  stock['price change'] = stock['close'].diff(periods=1)
  price_change = stock['price change']# * (int(investment / stock['close'][0]))

  #last = stock['Last']
  close = stock['close']

  print(count)

  own_shares = 0

  index = stock.index

  # in tqdm(range(1, len(advice...
  time_start = time.time()
  for i in tqdm(range(1, len(advice)), disable=not backtesting, desc="Calculating backtest balances... [1/3]"):
    if advice[i] == "SELL": 
      own_shares = 0

    if advice[i] == "BUY":
      own_shares = int(balance[i] / close[i])

    # Simulate closing positions before end of day
    try:
      subtract = index[i+1] - index[i]
      subtract = subtract.to_pytimedelta()
      subtract = str(subtract).split(":")
      subtract = int(subtract[1])
      # If the next row is more than 30 mins away, close out of positions
      if subtract > 30:
        own_shares = 0
    except:
      own_shares = 0

    if own_shares >= 1:
      balance[i] = balance[i-1] + (price_change[i])#*own_shares
    else:
      if shorting:
        balance[i] = balance[i-1] - (price_change[i])#*own_shares
      else:
        balance[i] = balance[i-1]
  time_end = time.time()
  print(f"advice took {time_end - time_start} seconds")

  stock['real choice'] = advice
  real_choice = stock['real choice']

  time_start = time.time()
  for i in tqdm(range(1, len(price_change)-1), disable=not backtesting, desc="Calculating buy and sell signals... [2/3]"):
    if price_change[i+1] > 0:
      real_choice[i] = "BUY" 
    if price_change[i+1] < 0:
      real_choice[i] = "SELL" 
  time_end = time.time()
  print(f"Price_change took {time_end - time_start} seconds")

  stock['correct'] = advice
  correct = stock['correct']

  def count_correct(advice, real_choice):
    time_start = time.time()

    # debugging
    print("Printing real choice")
    print(real_choice)

    # for i in range(1, len(real_choice)):
    #   if advice.iloc[i] == "HOLD":
    #     advice.iloc[i] = advice.iloc[i-1]
    #   if real_choice.iloc[i] == "HOLD": 
    #     real_choice.iloc[i] = real_choice.iloc[i-1]

    '''These two above and below are seemingly interchangable, but .iloc proves to be actually slower.'''

    for i in trange(1, len(real_choice), disable=not backtesting, desc="Converting HOLDs and calculating backtest correct/incorrect... [3/3]"):
      if (advice[i] == "HOLD"):
        advice[i] = advice[i-1]
      if (real_choice[i] == "HOLD"):
        real_choice[i] = real_choice[i-1]

      if advice[i] == real_choice[i]:
        correct[i] = "CORRECT"
      else:
        correct[i] =  "INCORRECT"
    time_end = time.time()
    print(f"count_correct took {time_end - time_start} seconds")

  def percent_right():
    # did this cuz counting the number of 'correct' includes the incorrect
    num_incorrect = correct.str.count("INCORRECT").sum() 
    total_choices = len(correct)
    num_correct = total_choices - num_incorrect
    print(f"""
    num correct: {num_correct}
    total_choices: {total_choices}
    """)
    return (num_correct / total_choices) * 100

  count_correct(advice, real_choice)
  print("Percent right: {}%".format(round(percent_right(), 3)))

  initial = balance.iloc[1]
  end_price = balance.iloc[-1]

  def calc_percent_return(initial, end_price):
    calc = (end_price-initial)/initial
    calc = calc*100
    return calc

  percent_return = calc_percent_return(initial, end_price)
  percent_return = round(percent_return, 3)

  print(f"Percent return: {percent_return}%")

  # stock.index.values[-1] <-- tried this, but gave a really big number idk if its seconds or what
  start_date = stock.index[1]
  end_date = stock.index[-1]

  def calculate_days(start_date, end_date):
    return end_date - start_date

  days = calculate_days(start_date, end_date)
  days = str(days).split()
  days = days[0]
  days = int(days)

  print(f"Time for return: {days} days")

  def extrapolate_returns(percent_return, days):
    # seconds = days.total_seconds()
    # hours = seconds / 60
    # days = hours / 24
    # print(days)
    return_per_day = percent_return / days #6? 
    return_per_year = return_per_day * 365 #252 trading days
    return_per_year = round(return_per_year, 3)
    return return_per_year

  print("Return per year: {}%".format(extrapolate_returns(percent_return, days)))

  print()

  def baseline_return():
    initial_baseline = close.iloc[1]
    end_price_baseline = close.iloc[-1]
    baseline_return = calc_percent_return(initial_baseline, end_price_baseline)
    baseline_return = round(baseline_return, 3)
    return baseline_return

  baseline_return = baseline_return()
  print(f"Baseline return: {baseline_return}%")

  baseline_advantage = percent_return - baseline_return
  baseline_advantage = round(baseline_advantage, 3)
  print(f"Percent better than baseline: {baseline_advantage}%")
  print()

  def plot(data, type="pyplot"):
    if type == "pyplot":
      import matplotlib.pyplot as plt
      balance.plot()
      close.plot()
      plt.ylabel('price')
      plt.show()
      
      list_orders = api.list_orders(status="closed", direction="asc", limit=1)
      first_order_fill_time = str(list_orders).split("'filled_at': '")
      first_order_fill_time = str(first_order_fill_time[1]).split("',")
      first_order_fill_time = first_order_fill_time[0]
      first_order_fill_time = first_order_fill_time[:10]
      # portfolio_history = api.get_portfolio_history(timeframe="1Min", date_start=first_order_fill_time)
      current_time, curr_datetime = get_current_datetime()
      # global curr_datetime
      print(curr_datetime[:10])
      import numpy as np
      portfolio_history = api.get_portfolio_history(timeframe="1Min", date_start=str(curr_datetime[:10]).replace("/", "-"), date_end=str(curr_datetime[:10]).replace("/", "-"))
      profit_loss = portfolio_history.profit_loss
      profit_loss = pd.DataFrame(np.array(profit_loss).reshape(len(profit_loss),1), columns = list("p"))
      # print(profit_loss)
      profit_loss.plot()
      plt.ylabel('profit')
      plt.xlabel('arbitrary time')
      plt.show()
    if type == "interactive":
      import plotly.offline as pyo
      import plotly.graph_objs as go
      from plotly.offline import iplot

      import cufflinks as cf
      from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot 

      cf.go_offline()

      #%matplotlib inline
      init_notebook_mode(connected=False)
      def configure_plotly_browser_state():
        import IPython
        display(IPython.core.display.HTML('''
              <script src="/static/components/requirejs/require.js"></script>
              <script>
                requirejs.config({
                  paths: {
                    base: '/static/base',
                    plotly: 'https://cdn.plot.ly/plotly-1.5.1.min.js?noext',
                  },
                });
              </script>
              '''))

      configure_plotly_browser_state()
      stock.iplot(kind='line',x='',y=['close', 'balance'], color=['orange', 'blue'], 
      theme='solar', mode='markers+lines',title='Trading bot')

  if backtesting:
    plot_type = "pyplot" #@param ["interactive", "pyplot"]
  else:
    plot_type = "pyplot"
  plot(data, type=plot_type)

def get_advice(data, strategy="default"):
  if strategy == "default":
    #your strat here

    return advice, last_advice

def cancel_all_orders():
  print("Cancelling all orders...")
  api.cancel_all_orders()

def get_positions():
  #wait(1)
  cancel_all_orders()
  try:
    positions = api.get_position(ticker)
    qty = int(positions.qty)
    market_value = float(positions.market_value)
    side = positions.side
    if side == "short":
      side = "sell"
    else:
      side = "buy"
  except Exception as e:
    positions = None
    qty = 0
    market_value = 0
    side = None
    print(e)
  return positions, qty, market_value, side
account = api.get_account()

def truncate(n, decimals=0):
  multiplier = 10 ** decimals
  return int(n * multiplier) / multiplier


def order(last_advice, e=""):
  current_time, curr_datetime = get_current_datetime()
  if (current_time > "15:58") and not trade_ext_hours:
    close_margin(last_advice)
    open = False
  filled = False
  while not filled:
    current_positions, current_qty, current_market_value, current_side = get_positions()
    print(f"Current quantity: {current_qty}")
    print(f"Current side: {current_side}")
    print(f"Current market value: {current_market_value}")

    def define_order(e=""):
      if verbose:
        print("Defining order")
      close_prices = market_data['close']
      last_close = close_prices[-1]
      limit_price = last_close
      global account
      last_equity = float(account.last_equity)
      if e == "insufficient buying power":
        buying_power = float(account.regt_buying_power)
      else:
        buying_power = float(account.buying_power)
      buying_power = buying_power / 4
      if margin_times > 1:
        buying_power = buying_power * margin_times
      buying_power = truncate((buying_power - current_market_value), 2)
      portfolio_value = float(account.portfolio_value)
      total_profit = truncate(((portfolio_value - keep_as_cash) - investment), 2)
      todays_profit = truncate((portfolio_value - last_equity), 2)
      useable_cash = truncate(((last_equity - keep_as_cash)*margin_times), 2) # Using last_equity instead of portfolio_value because funds aren't settled until the end of day
      target_qty = int(useable_cash / limit_price)

      if verbose:
        print(f"Last equity: ${last_equity}")
        print(f"Buying power: ${buying_power}")
        print(f"Keep as cash: ${keep_as_cash}")
        print(f"Portfolio value: ${portfolio_value}")
        print(f"Total profit: ${total_profit}")
        print(f"Today's profit: ${todays_profit}")
        print(f"Useable cash: ${useable_cash}")
        print(f"Limit price: ${limit_price}")
        print(f"Target Qty: {target_qty}")

      return limit_price, target_qty, buying_power, useable_cash

    limit_price, target_qty, buying_power, useable_cash = define_order(e)
    quantity = target_qty
    if last_advice == None:
      to_close = True
      if current_side == "sell":
        side = "buy"
        last_advice = "buy"
      else: 
        side = "sell"
        last_advice = "sell"
      target_qty = 0
    else: to_close = False
    future_buying_power = useable_cash - (limit_price * quantity)

    if future_buying_power < 0:
      print(f"Skipping because future buying power == {future_buying_power}")
      return

    if buying_power == 0:
      print(f"Skipping because buying power is {buying_power}")
      return
    
    if quantity < 1 and last_advice == "buy":
      print(f"Setting quantity = current_qty because quantity {quantity} < 1 and last_advice is {last_advice}")
      quantity = current_qty

    i = 1
    while last_advice == "hold":
      i += 1
      last_advice = advice[-i]
      last_advice = last_advice.lower()

    try:
      if (current_side == last_advice) and (abs(target_qty) == abs(current_qty)):
        print(f"Skipping order because we are holding positions")
        return
    except Exception as e: print(e)

    # input(f"quantity = {quantity}, last advice = {last_advice}")
    # if (quantity < 1) and (last_advice == current_side):
    #   print(f"Skipping order because quantity {quantity} < 1 and we're on same side")
    #   return

    try:
      print(f"Current side: {current_side}, last advice: {last_advice}")
      print(f"current qty: {current_qty}, Quantity: {quantity}")
      if current_side != None:

        if (current_side != last_advice) and (quantity > current_qty):
          print("Setting quantity == current_qty because we're trying to switch sides")
          quantity = current_qty
          print(f"Quantity: {quantity}")
    except Exception as e:
      print(e)
    global ext_hours
    
    # input("5")
    if trade_ext_hours == False:
      if debug:
        print("Setting ext_hours to false")
      ext_hours = False

    # Debugging
    # last_advice = "sell"
    # quantity = 56
    # send_order(limit_price, quantity, last_advice)
    
    def send_order(limit_price, quantity, side, ext_hours, type="limit"):
      cancel_all_orders()
      current_positions, current_qty, current_market_value, current_side = get_positions()
      if current_side == side:
        if (quantity + current_qty) > target_qty:
          print(f"Trade quantity {quantity} + current_qty: {current_qty} would exceed target_qty: {target_qty}")
          send_email("Trade quantity {quantity} + current_qty: {current_qty} would exceed target_qty: {target_qty}")
          if target_qty - current_qty > current_qty:
            quantity = target_qty - current_qty
      quantity = abs(quantity)
      print(f"Quantity: {quantity}")
      print(f"Side: {side}, Last advice: {last_advice}")
 
      if quantity < 1:
        filled = True
        return filled
      if debug:
        print("Sending order")
      try:
        if ext_hours:
          print(f"Extended limit order: {side} {quantity} shares of {ticker} for ~${limit_price}. Total: ~${limit_price*quantity:.2f}")
          api.submit_order(symbol=ticker,
              qty=abs(quantity),
              side=side,
              time_in_force='day',
              extended_hours= ext_hours,
              type='limit',
              limit_price=limit_price)
              # client_order_id=order_id)
        else:
          print(f"{type} order: {side} {quantity} shares of {ticker} for ~${limit_price}. Total: ~${(limit_price*quantity):.2f}")
          api.submit_order(symbol=ticker,
              qty=abs(quantity),
              side=side,
              time_in_force='day',
              type='limit',
              limit_price=limit_price)
              # limit_price=400.00,
              # client_order_id=order_id)
      except Exception as e:
        print(e)
        e = str(e)
        if "insufficient buying power" in e:
          order(last_advice, e="insufficient buying power")
    current_positions, current_qty, current_market_value, current_side = get_positions()
    def qty_delta(current_qty, quantity, current_side, last_advice, limit_price, side, ext_hours):
      print("In qty_delta")
      #elif current_qty != quantity:
        ## input("3")
        #print("Getting quantity delta")
        ## if (current_side == "sell" and current_qty < 0) and
        #quantity_delta = current_qty - quantity
        #print(f"Quantity detla: {quantity_delta}")
        #if quantity_delta
        #send_order(limit_price, quantity=quantity_delta, last_advice)
      #if abs(current_qty) != abs(quantity):
        #if (current_qty > quantity) or (current_qty < quantity):
          #print("Getting quantity delta")
          #quantity_delta = current_qty - (quantity)
          #if quantity_delta > 0:
            #side = "sell"
          #if quantity_delta < 0:
            #side = "buy"
          #send_order(limit_price, quantity=quantity_delta, side=side)

      current_positions, current_qty, current_market_value, current_side = get_positions()
      if current_qty == 0:
        if quantity != 0:
          quantity_delta = quantity
        else: quantity_delta = target_qty
        side = last_advice
        return side, quantity_delta
        
      quantity = target_qty
      if abs(current_qty) != abs(quantity):
          if (abs(current_qty) > abs(quantity)) or (abs(current_qty) < abs(quantity)):
            if current_side == last_advice:
              quantity_delta = abs(quantity) - abs(current_qty)
              if quantity_delta > 0:
                side = current_side
              elif quantity_delta < 0:
                if current_side == "sell":
                  side = "buy"
                else: side = "sell" 

            else:
              side = last_advice
              print(f"I think we want to switch sides here, setting qty_delta to current_qty")
              quantity_delta = current_qty
              #quantity_delta = abs(quantity) - abs(current_qty)
              #if quantity_delta > 0:
                #side = "buy"
              #elif quantity_delta < 0:
                #side = "sell"
            print("Sending order to fix quantity delta")
            if current_qty == 0:
              side = last_advice

              #if current_side == last_advice:
                #side = last_advice
              #else:
                #side = current_side
            
            if quantity_delta == 0 or (quantity_delta == quantity):
              print(f"Quantity delta is {quantity_delta}, so setting quantity delta to quantity {quantity}")
              quantity_delta = quantity
            if (quantity_delta > current_qty) and (current_side != last_advice):
              print(f"Setting quantity delta to quantity because we're trying to switch sides")
              quantity_delta = current_qty
            print(f"Quantity delta: {quantity_delta}")
            print(f"Last advice: {last_advice}")
            print(f"Side: {side}")
           
            send_order(limit_price, quantity=quantity_delta, side=side, ext_hours=ext_hours)
      else: 
        side = last_advice
        quantity_delta = quantity
      return side, quantity_delta

    try:
      # input("1")
      if (current_side == last_advice) and (current_qty == quantity):
        # input("2")
        print(f"Skipping order because current_positions.side and current_qty are the same")
        return
    except Exception as e:
      print(e)
      pass

    try: side
    except: side = last_advice
    
    try: quantity_delta
    except:
      print(f"Setting quantity = quantity_delta")
      quantity_delta = quantity
    print(f"Quantity: {quantity}, qty delta: {quantity_delta}")
    
    if current_qty != target_qty:
      side, quantity = qty_delta(current_qty, quantity, current_side, last_advice, limit_price, side, ext_hours)

    #if abs(current_qty) != abs(quantity):
      #print("Sending regular order")
      #send_order(limit_price, quantity, side=last_advice)

    def check_fill(current_positions, current_qty, current_side, side, quantity, target_qty, to_close=to_close):
      print("In check_fill")
      #open_orders_list = api.list_orders(status='open')
      # Check if there are no open orders
      #if not open_orders_list:
        #print("No open orders")
        #filled = True
        #return filled
      try:
        old_positions = current_positions
        old_qty = current_qty
        #old_market_value = current_market_value
        old_side = current_side
        #wait(5)
        current_positions, current_qty, current_market_value, current_side = get_positions()
        print(f"Current qty: {current_qty}, quantity: {quantity}")
        print(f"Current side: {current_side}, last advice: {last_advice}")

        if old_qty == current_qty and old_side == current_side:
          filled = False
        if abs(target_qty) == abs(current_qty) and last_advice == current_side:
          filled = True
        else:
          filled = False
        if to_close:
          if current_qty == 0 and current_side != "sell" and current_side != "buy" and current_side != "hold":
            filled = True

        try: side
        except: side = last_advice
        
        if current_qty != target_qty:
          side, quantity = qty_delta(current_qty, quantity, current_side, last_advice, limit_price, side, ext_hours)
      except Exception as e:
        print(e)
        filled = False

      return filled

    print(f"Target qty: {target_qty}")
    filled = check_fill(current_positions, current_qty, current_side, side, quantity, target_qty)
    if filled:
      play_sound("filled")
    print(f"Filled: {filled}")
    # input("6")
    def get_filled(filled, limit_price, quantity, side):
      i = 0
      while not filled:
        if current_qty != target_qty:
          side, quantity = qty_delta(current_qty, quantity, current_side, last_advice, limit_price, side, ext_hours)
        if side == "sell":
          limit_price = limit_price - 0.01
        else:
          limit_price = limit_price + 0.01
        print(f"Iterations: {i}")
        if i >= 4:
          if side == "sell":
            limit_price = limit_price - 1
          else: limit_price = limit_price + 1
        print(f"Limit price: {limit_price}")
        print("Sending order to get filled")
        filled = check_fill(current_positions, current_qty, current_side, side, quantity, target_qty)
        send_order(limit_price, quantity, side, ext_hours)
        i += 1
        #wait(5)
        filled = check_fill(current_positions, current_qty, current_side, side, quantity, target_qty)
        print(f"Filled: {filled}")
      else:
        print(f"Filled: {filled}")
        play_sound("filled")
    # input("7")
    if not filled:
      # input("8")
      print(f"Quantity: {quantity}")
      get_filled(filled, limit_price, quantity, side)
    
def close_margin(last_advice):
  global trade_ext_hours
  trade_ext_hours = True
  current_positions, current_qty, current_market_value, current_side = get_positions()
  if current_qty == 0 and current_side != "sell" and current_side != "buy" and current_side != "hold":
    print("No current positions")
  else:
    print("Closing out of margin...")
    global margin_times
    margin_times = 1

    if current_qty == 0 and current_side != "sell" and current_side != "buy":
      print("No current positions")

    order(last_advice, e=e)
    #send_order(limit_price, quantity=current_qty, side=side, ext_hours=ext_hours)

def close_all_positions():
      global trade_ext_hours
      trade_ext_hours = True
      current_positions, current_qty, current_market_value, current_side = get_positions()
      if current_qty == 0 and current_side != "sell" and current_side != "buy" and current_side != "hold":
        print("No current positions")
      else:
        print("Closing all positions...")
        #api.close_all_positions()

        if current_qty == 0 and current_side != "sell" and current_side != "buy":
          print("No current positions")
        if current_side == "sell":
          side = "buy"
        else: side = "sell"
        side = None
        order(side, e=e)
        #send_order(limit_price, quantity=current_qty, side=side, ext_hours=ext_hours)

def send_email(error, e=e):
  print("Sending email...")
  import traceback
  traceback = traceback.format_exc()
  import smtplib, ssl

  email = "" #@param {type:"string"}
  password = '' #@param {type:"string"}

  port = 587  # For starttls
  smtp_server = "smtp.gmail.com"
  sender_email = email
  receiver_email = email
  subject_text = """\
  TRADE BOT"""
  global message_text
  message_text = str(e)
  message_text = '\n'
  message_text += str(traceback)
  
  def newline(n=1):
    while n > 0:
      global message_text
      message_text += '\n'
      n = n - 1
  
  try:
    message_text += str(error)
  except:
    pass
  newline()
  try: 
    message_text += positions
  except Exception as e:
    print(e)
  account = api.get_account()
  message_text += str(account)
  positions, qty, market_value, side = get_positions()
  message_text += str(positions)
  portfolio_value = float(account.portfolio_value)
  newline()
  message_text += f"Current value is: ${portfolio_value}"
  newline()
  total_profit = (portfolio_value - keep_as_cash) - investment
  message_text += f"Total profit: ${total_profit:.2f}"
  last_equity = float(account.last_equity)
  newline()
  todays_profit = portfolio_value - last_equity
  message_text += f"Today's profit: ${todays_profit:.2f}"
  newline()
  message_text += f"Useable cash: {last_equity - keep_as_cash}:.2f"
  message = 'Subject: %s\n%s' % (subject_text, message_text)
  context = ssl.create_default_context()
  with smtplib.SMTP(smtp_server, port) as server:
      server.ehlo()  # Can be omitted
      server.starttls(context=context)
      server.ehlo()  # Can be omitted
      server.login(sender_email, password)
      server.sendmail(sender_email, receiver_email, message)

def play_sound(sound):
  print("placeholder function for sound")
  #send_email(error="Order filled")
  # https://stackoverflow.com/a/54295274/8142044
  # Play an audio beep. Any audio URL will do.
  #from google.colab import output
  #if sound=="filled":
    #output.eval_js('new Audio("https://proxy.notificationsounds.com/notification-sounds/eventually-590/download/file-sounds-1137-eventually.ogg").play()')
  #if sound=="error":
    #output.eval_js('new Audio("https://proxy.notificationsounds.com/notification-sounds/point-blank-589/download/file-sounds-1136-point-blank.ogg").play()')

def wait(seconds):
  if seconds <= 0:
    return
  print(f"Waiting {seconds} seconds.")
  time.sleep(seconds)

def wait_for_new_data():
  print("Waiting for new data...")
  ticker_data = api.get_barset(ticker, timeframe="1Min", limit=1)
  ticker_data = str(ticker_data).split("'t': ")
  ticker_time = ticker_data[1]
  ticker_time = ticker_time.split(",")
  ticker_time = ticker_time[0]
  last_ticker_time = ticker_time
  while ticker_time == last_ticker_time:
    ticker_data = api.get_barset(ticker, timeframe="1Min", limit=1)
    ticker_data = str(ticker_data).split("'t': ")
    ticker_time = ticker_data[1]
    ticker_time = ticker_time.split(",")
    ticker_time = ticker_time[0]
    time.sleep(1)
  print(f"ticker data: {ticker_time}")
  print(f"last_ticker_data: {last_ticker_time}")
  print(f"{ticker_time == last_ticker_time}")
  
''' These two functions are two different ways of doing the same thing, but wait_for_next_minute requires less API requests. '''

def wait_for_next_minute():
  current_time, curr_datetime = get_current_datetime()
  split_time = str(current_time).split(":")
  seconds = int(split_time[2]) 
  seconds = 60 - seconds
  seconds += 5.5 # Alpaca data updates every minute + 5ish seconds
  print(f"Waiting {seconds} seconds for new data.")

  #for i in trange(seconds):
    #time.sleep(1-.01)

  time.sleep(seconds)

  if seconds <= 0:
    return




try:

  open, open_time, close_time, todays_date, ext_hours = check_if_open()

  while open:
    stopwatch_start = time.time()
    #ticker, start_date, end_date, start_time, end_time
    market_data = get_market_data()

    advice, last_advice = get_advice(market_data)

    if backtesting:
      add_calculations(market_data, advice)
      input("Backtesting done")

    order(last_advice)

    open, open_time, close_time, todays_date, ext_hours = check_if_open()

    stopwatch_end = time.time()
    time_delta = stopwatch_end - stopwatch_start
    print(f"Time took: {time_delta}")
    
    #wait_for_new_data()
    wait_for_next_minute()
    #wait(59 - time_delta)
  else:
    close_all_positions()
    open, ext_hours = wait_for_open()
except Exception as e:
  close_all_positions()
  send_email(error=e)
  raise(e)
