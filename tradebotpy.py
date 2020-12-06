#@title Trade Bot { form-width: "25%" }

# %tb

# import Alpaca trade API, and install in Colab
try:
  import alpaca_trade_api as tradeapi
except:
  print("Installing alpaca_trade_api")
  !pip install alpaca_trade_api --quiet
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

debug = True #@param{type:"boolean"}
verbose = True #@param{type:"boolean"}
# Debugging - set a custom test time
if debug:
  current_time = "09:30:00"

backtesting = False #@param{type:"boolean"}
  
ticker = "SPY"
investment = 21000
margin_times = 1
shorting = True #@param{type:"boolean"}

trade_ext_hours = False #@param{type:"boolean"}

start_date = "automatic"
end_date = "automatic"

start_time = "9:30"
end_time = "16:00" # 4 p.m.

# Initialize
e = ""
portfolio_value = None

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
  return open, calendar.open, calendar.close, date

# https://discuss.codecademy.com/t/how-to-convert-to-12-hour-clock/3920/3

import pytz

local_tz = pytz.timezone('US/Eastern')

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary

# now = datetime.now()
now = utc_to_local(datetime.now())

def get_current_datetime():
  global now

  #24-hour format
  # print(now.strftime('%Y/%m/%d %H:%M:%S'))
  current_time = now.strftime('%H:%M:%S')
  #12-hour format
  curr_datetime = now.strftime('%Y/%m/%d %I:%M:%S %p')
  # current_time = now.strftime('%I:%M:%S %p')
  print(curr_datetime)
  #print(current_time)
  return current_time, curr_datetime

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

    open, open_time, close_time, todays_date = check_if_open()
    print("Getting current time")
    current_time, curr_datetime = get_current_datetime()

    if not open and current_time >= "9" and current_time < "16":
      print("Must be weekend or holiday, waiting till tommorow...")
      open = False
  return open

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
    df = data

    #your strat here

    return advice, last_advice

def get_positions():
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
def order(last_advice, e=""):
  # input("-2")
  filled = False
  while not filled:
    # input("-1")
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
      buying_power = buying_power - current_market_value
      keep_as_cash = last_equity - investment
      useable_cash = last_equity - keep_as_cash
      quantity = int(useable_cash / limit_price)

      if verbose:
        print(f"Last equity: ${last_equity}")
        print(f"Buying power: ${buying_power}")
        print(f"Keep as cash: ${keep_as_cash}")
        print(f"Useable cash: ${useable_cash}")
        print(f"Limit price: ${limit_price}")
        print(f"Quantity: {quantity}")

      return limit_price, quantity, buying_power, useable_cash
    # input("0")
    limit_price, quantity, buying_power, useable_cash = define_order(e)

    future_buying_power = useable_cash - (limit_price * quantity)

    if future_buying_power < 0:
      print(f"Skipping because future buying power == {future_buying_power}")
      return

    if buying_power == 0:
      print(f"Skipping because buying power is {buying_power}")
      return

    try:
      # input("1")
      if (current_side == last_advice) and (current_qty == quantity):
        # input("2")
        print(f"Skipping order because current_positions.side and current_qty are the same")
        return
      elif current_qty != quantity:
        # input("3")
        print("Getting quantity delta")
        # if (current_side == "sell" and current_qty < 0) and 
        quantity = abs(quantity) - abs(current_qty)
        print(f"Quantity: {quantity}")
    except Exception as e:
      print(e)
      pass
    # input("4")

    # if quantity < 1:
    #   print(f"Skipping order because quantity {quantity} < 1")
    #   return

    if quantity < 1 and last_advice == "buy":
      quantity = current_qty

    try:
      if (last_advice == "hold") and (current_side == last_advice):
          print(f"Skipping order because last_advice == {last_advice} and is == {current_positions.side}")
          return
    except: pass

    i = 1
    while last_advice == "hold":
      i += 1
      last_advice = advice[-i]
      last_advice = last_advice.lower()

    # input(f"quantity = {quantity}, last advice = {last_advice}")
    # if (quantity < 1) and (last_advice == current_side):
    #   print(f"Skipping order because quantity {quantity} < 1 and we're on same side")
    #   return

    try:
      print(f"Current side: {current_side}, last advice: {last_advice}")
      print(f"Quantity: {quantity}, current qty: {current_qty}")
      if current_side != None:

        if (current_side != last_advice) and (quantity > current_qty):
          print("Setting quantity == current_qty because we're trying to switch sides")
          quantity = current_qty
          print(f"Quantity: {quantity}")
    except Exception as e:
      print(e)

    # input("5")
    if trade_ext_hours == False:
      if debug:
        print("Setting extended_hours to false")
      extended_hours = False

    # Debugging
    # last_advice = "sell"
    # quantity = 56
    # send_order(limit_price, quantity, last_advice)

    def send_order(limit_price, quantity, last_advice, type="limit"):
      api.cancel_all_orders()
      quantity = abs(quantity)
      if debug:
        print("Sending order")
      try:
        if extended_hours:
          print(f"Extended limit order: {last_advice} {quantity} shares of {ticker} for ~${limit_price}. Total: ~${limit_price*quantity:.2f}")
          api.submit_order(symbol=ticker,
              qty=abs(quantity),
              side=last_advice,
              time_in_force='day',
              extended_hours= extended_hours,
              type='limit',
              limit_price=limit_price)
              # client_order_id=order_id)
        else:
          print(f"{type} order: {last_advice} {quantity} shares of {ticker} for ~${limit_price}. Total: ~${(limit_price*quantity):.2f}")
          api.submit_order(symbol=ticker,
              qty=abs(quantity),
              side=last_advice,
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
    fuck
    send_order(limit_price, quantity, last_advice)

    def check_fill():
      try:
        old_positions = current_positions
        old_qty = current_qty
        old_market_value = current_market_value
        old_side = current_side
        current_positions, current_qty, current_market_value, current_side = get_positions()
        print(f"Current qty: {current_qty}, qty {quantity}")
        print(f"Current side: {current_side}, last advice: {last_advice}")
        if old_qty == current_qty and old_side == current_side:
          filled = False
        else: filled = True
        # if (abs(current_qty) == abs(quantity)) and (current_side == last_advice):
        #   filled = True
        # else: 
        #   filled = False
      except Exception as e:
        print(e)
        filled = False

      return filled
    
    filled = check_fill()
    if filled:
      play_sound("filled")
    print(f"Filled: {filled}")
    # input("6")
    def get_filled(filled=filled, limit_price=limit_price):
      while not filled:
        if last_advice == "sell":
          limit_price = limit_price - 0.01
        else:
          limit_price = limit_price + 0.01
        print(f"Limit price: {limit_price}")
        send_order(limit_price, quantity, last_advice)
        wait(5)
        filled = check_fill()
        print(f"Filled: {filled}")
      else:
        print(f"Filled: {filled}")
        play_sound("filled")
    # input("7")
    if not filled:
      # input("8")
      get_filled()

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
  message_text = str(e)
  message_text = '\n'
  message_text += str(traceback)
  try:
    message_text += str(error)
  except:
    pass
  message_text += '\n'
  try: 
    message_text += positions
  except Exception as e:
    print(e)
  positions, qty, market_value, side = get_positions()
  message_text += str(positions)
  portfolio_value = float(account.portfolio_value)
  message_text += f"Current value is: ${portfolio_value}"
  message_text += '\n'
  message_text += f"Total profit: ${portfolio_value - investment:.2f}"
  last_equity = float(account.last_equity)
  message_text += '\n'
  message_text += f"Today's profit: ${last_equity - portfolio_value}"
  message = 'Subject: %s\n%s' % (subject_text, message_text)
  context = ssl.create_default_context()
  with smtplib.SMTP(smtp_server, port) as server:
      server.ehlo()  # Can be omitted
      server.starttls(context=context)
      server.ehlo()  # Can be omitted
      server.login(sender_email, password)
      server.sendmail(sender_email, receiver_email, message)

def play_sound(sound):
  # print("placeholder function for sound")
  # https://stackoverflow.com/a/54295274/8142044
  # Play an audio beep. Any audio URL will do.
  from google.colab import output
  if sound=="filled":
    output.eval_js('new Audio("https://proxy.notificationsounds.com/notification-sounds/eventually-590/download/file-sounds-1137-eventually.ogg").play()')
  if sound=="error":
    output.eval_js('new Audio("https://proxy.notificationsounds.com/notification-sounds/point-blank-589/download/file-sounds-1136-point-blank.ogg").play()')

def wait(seconds):
  print(f"Waiting for {seconds} seconds")
  time.sleep(seconds)




try:

  open, open_time, close_time, todays_date = check_if_open()

  while open:
    stopwatch_start = time.time()
    #ticker, start_date, end_date, start_time, end_time
    market_data = get_market_data()

    advice, last_advice = get_advice(market_data)

    if backtesting:
      add_calculations(market_data, advice)
      input("Backtesting done")

    order(last_advice)

    open, open_time, close_time, todays_date = check_if_open()

    stopwatch_end = time.time()
    time_delta = stopwatch_end - stopwatch_start
    print(f"Time took: {time_delta}")

    wait(59 - time_delta)
  else:
    open = wait_for_open()
except Exception as e:
  send_email(error=e)
  raise(e)
