#@title Trade Bot { form-width: "25%" }

from tqdm import tqdm
from tqdm import trange

try:
  import alpaca_trade_api as tradeapi
except:
  print("Installing alpaca_trade_api")
  #!pip install alpaca_trade_api --quiet
  import alpaca_trade_api as tradeapi

# authentication and connection details
api_key = "" #@param{type:"string"}
api_secret = "" #@param{type:"string"}
base_url = 'https://paper-api.alpaca.markets'
# base_url = 'https://data.alpaca.markets'

# instantiate REST API
api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

def api_open_check(api=api):
   # Check when the market opens/closes
   from datetime import datetime
   todays_date = datetime.today().strftime('%Y-%m-%d')F
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
   return open, calendar.open, calendar.close, date

open, open_time, close_time, todays_date = api_open_check()
#print(f"open time: {open_time}, close_time: {close_time}, todays_date: {todays_date}")
#from datetime import timedelta
#test = (close_time - timedelta(hours=0, minutes=15)).time()
close_time = str(close_time).split(":")
close_time[1] = int(close_time[1]) - 15
close_time = str(close_time[0]) + ":" + str(close_time[1]) + ":" + str(close_time[2])
print(close_time)
#close_time = close_time.strftime('%H:%M:%S')
#open_time = open_time.strftime('%H:%M:%S')

from datetime import datetime
import pytz

# https://discuss.codecademy.com/t/how-to-convert-to-12-hour-clock/3920/3

local_tz = pytz.timezone('US/Eastern')

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary

now = datetime.now()
#now = utc_to_local(datetime.now())

def get_current_datetime():
    now = datetime.now()
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
    current_time, curr_datetime = get_current_datetime()
    #current_time = "09:25:21"
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

    open = api_open_check()
    print("Getting current time")
    current_time, curr_datetime = get_current_datetime()

    if not open and current_time >= "9" and current_time < "16":
      print("Must be weekend or holiday, waiting till tommorow...")
      open = False
  return open

investment = 0.0
portfolio_value = 0.0
e = ""
def sendEmail(e=e, portfolio_value=portfolio_value, investment=investment):
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
  #message_text += str(portfolio_value)
  message_text += '\n'
  try: 
    message_text += positions
  except Exception as e:
    print(e)
  #message_text += str(print_position())
  message_text += f"Current value is: ${portfolio_value}"
  message_text += '\n'
  message_text += f"Total profit: ${portfolio_value - investment:.2f}"
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
  # https://stackoverflow.com/a/54295274/8142044
  # Play an audio beep. Any audio URL will do.
  #from google.colab import output
  #if sound=="filled":
    #output.eval_js('new Audio("https://proxy.notificationsounds.com/notification-sounds/eventually-590/download/file-sounds-1137-eventually.ogg").play()')
  #if sound=="error":
    #output.eval_js('new Audio("https://proxy.notificationsounds.com/notification-sounds/point-blank-589/download/file-sounds-1136-point-blank.ogg").play()')
 
#%tb

import time
import sys
# current_time = int(time.time())
nine = 1604932895 - (41-30)
four = 1604696400
six = 1604962802
 
current_time, curr_datetime = get_current_datetime()

extended_hours = False
backtesting = False #@param {type:"boolean"}

# You can test any time here by changing this string, has to be in this exact format though.
# If this doesnt work, try changing it within the wait_for_open function
#current_time = "09:25:23"

print(f"Current time: {current_time}, open_time: {open_time}")

if open:
  if not backtesting:
    if (current_time >= str(open_time)) and (current_time < str(close_time)):
      print("During market hours")
      open = True
    else:
      print("Outside of market hours")
      open = False
      wait_for_open()
else:
  wait_for_open()
#if current_time > "16":
  #print("Market not open")
  #open = False
  #wait_for_open() 
#if current_time < "18" and current_time > "16": # 18 is 6
  #print("During aftermarket hours")
  #extended_hours = True
  #open = True
  #open = False
  #wait_for_open()
#elif (current_time < "16") and (current_time > "09:30 AM") and open: # 16 is 4
  #print(f"Open = {open}")
  #print("During market hours")
  #extended_hours = False
  #open = True
#elif (current_time > "09 AM") and (current_time < "09:30 AM"):
  #print("During beforemarket hours")
  #extended_hours = True
  #open = True
  #open = False
  #wait_for_open()
#else:
  #open = False
  #if not open:
    #wait_for_open()
  #if not backtesting:
    #pass
    # waitTillMarketclose()
    # raise Exception("Market is closed") 
    # sys.exit("Market is closed")
    # time.sleep(60)
    # now = utc_to_local(datetime.now())
    # current_time = now.strftime('%H:%M:%S')
    # if current_time > "09":
    #   open = True
 
 
# if current_time < six:
#   open = True
#   print("During aftermarket hours")
#   if current_time < four:
#     open = True
#     print("During market hours")
# else:
#   # open = False
#   # sys.exit("Market is closed")
#   open = True
 
# ticker = "SPY" # SHV, SPY, BIL
ticker = "SPY" #@param {type:"string"}
# backtest_start_date = "2020-01-01"
 
#investment = 25000 #@param {type:"integer"}
margin = False #@param {type:"boolean"}
margin_times = 1 #@param {type:"number"}
 
# obtain account information
account = api.get_account()
investment = float(account.last_equity)
print(account)
#starting_portfolio_value = account.portfolio_value
 
# try:
# position = api.get_position(ticker)
 
shorting = True #@param{type:"boolean"}
if shorting:
  api.update_account_configurations(no_shorting=False)
else:  
  api.update_account_configurations(no_shorting=True)

while True:
  while not open:
    open = wait_for_open()
  else:
    # while True:
    try:
      CONSTANT = 15 # 15 minutes before close
      CONSTANT_SECONDS = CONSTANT * 60 # time  in seconds (900 seconds = 15 min)
      # print(CONSTANT_SECONDS)
  
  
      # fifteen minute before: 1604695536
      
  
      # try:
      #   from alpha_vantage.timeseries import TimeSeries
      #   from alpha_vantage.techindicators import TechIndicators
      # except Exception as e:
      #   print(e)
      #   !pip install alpha_vantage --quiet
      #   from alpha_vantage.timeseries import TimeSeries
      #   from alpha_vantage.techindicators import TechIndicators
  
      from matplotlib.pyplot import figure
      import matplotlib.pyplot as plt
      import pandas as pd
  
      initialize = True
  
      # Your key here
  
        
      # Chose your output format, or default to JSON (python dict)
      # ts = TimeSeries(key, output_format='pandas')
      # ti = TechIndicators(key)
  
      time_range_start = "9:30" #@param {type:"string"}
      time_range_end = "16:00" #@param {type:"string"}
  
      def add_calculations(data, margin_times=margin_times):
  
        #stock = ticker_data
  
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
        advice = stock['advice']
        # print(last_minute_data)
        # input()
        # stock = 
        price_change = stock['price change']# * (int(investment / stock['close'][0]))
  
        #last = stock['Last']
        close = stock['close']
  
        # for i in range(1, len(close)):
        #   #last[i] = stock.loc[stock.index[i], 'close']
        #   last[i] = close[i - 1]
  
        # if (stock.loc[stock.index[count], 'advice'] == "SELL"):
        #   balance = stock.loc[stock.index[count], 'Balance']
        #   count += 1
        # elif (stock.loc[stock.index[count], 'advice'] == "BUY"):
        #   balance += stock.loc[stock.index[count], 'price change']
        #   count += 1
  
        # if (advice[count] == "SELL"):
        #   balance = balance[count]
        #   count += 1

        # if (advice[count] == "SELL"):
        #   balance -= price_change[count]
        #   count += 1
        # elif (advice[count] == "BUY"):
        #   balance += price_change[count]
        #   count += 1
  
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
  
        # for b in price_change.loc[1, len(price_change)-1]:
        #   if price_change[i+1] > 0:
        #     real_choice[i] = "BUY" #
        #   if price_change[i+1] < 0:
        #     real_choice[i] = "SELL" #
        
  
      # current contents of your for loop
  
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
              advice[i] = advice[i-1] # ========================================================================================================================
            if (real_choice[i] == "HOLD"):
              real_choice[i] = real_choice[i-1]
  
              # correct[i] = correct[i-1]
              # while (advice[i] != "BUY") or (advice[i] != "SELL"):
              #   correct[i-1]
  
            if advice[i] == real_choice[i]:
              correct[i] = "CORRECT"
            else:
              correct[i] =  "INCORRECT"
          time_end = time.time()
          print(f"count_correct took {time_end - time_start} seconds")
  
        def percent_right():
          num_incorrect = correct.str.count("INCORRECT").sum() # did this cuz counting the number of 'correct' includes the incorrect
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
  
        #            stock.index.values[-1] <-- tried this, but gave a really big number idk if its seconds or what
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
            # current_time, curr_datetime = get_current_datetime()
            global curr_datetime
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
        
        # for i in range(1, len(advice)):
        #   if advice[i]
  
  
      def vwap(df):
          # q = df['volume'].values
          q = df.iloc[:,4]
          # p = df['close'].values
          p = df.iloc[:,3]
          return df.assign(vwap=(p * q).cumsum() / q.cumsum())
  
      def get_advice(data, strategy="default"):
        if strategy == "default":
          df = data
  
          #your strat
          return stock['advice']
  
      def do_new_data(margin_times=margin_times):  
        api.cancel_all_orders()
        try:
          ticker_data
        except NameError:
          print("Getting data...")
          # ticker_data, ticker_meta_data = ts.get_intraday(symbol='SPY', interval='1min', outputsize='full')
  
          # Maybe use after instead of start?
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
            ticker_data = ticker_data.between_time(time_range_start, time_range_end) 
          else:
            start = "2014-07-01" #@param {type:"date"}
            # start = "2014-01-01T09:30:00-04:00"
            start += "T09:30:00-04:00"
            ticker_data = api.get_barset(ticker, timeframe="1Min", start=start)
            ticker_data = ticker_data.df
            ticker_data = ticker_data.between_time(time_range_start, time_range_end) 
  
          # Backtesting this year
          # SPY = api.get_barset('SPY', timeframe="1Min", start="2020-01-01T09:30:00-04:00", end="2020-11-6T09:30:00-04:00")
          # Goes back as far as 2015
          # SPY = api.get_barset('SPY', timeframe="1Min", start="2010-01-01T09:30:00-04:00", end="2020-11-6T09:30:00-04:00")
          # data = SPY.df
          # data
          # try:
          #   ticker_data = ticker_data.df
          # except:
          #   pass
          # print(SPY.columns)
          # SPY = SPY.reset_index(level=0, drop=False, inplace=False, col_level=0)
  
          # print(SPY.columns)
  
          # SPY
          # SPY.columns = SPY.columns.map(''.join)
          ticker_data.columns = ticker_data.columns.droplevel(0)
          ticker_data.columns
          # data = SPY
  
          # ticker_data = data
          print(ticker_data)
          # input()
        
  
        #last_minute_data = ticker_data.iloc[1]
        #last_minute_close = last_minute_data[3]
  
        ticker_data = pd.DataFrame(ticker_data)
        ticker_data = ticker_data.sort_index()
        try:
          df
        except NameError:
          try:
            print("df not defined")
            last_minute_data = ticker_data.iloc[[-3, -2, -1]]
          except:
            ticker_data = api.get_barset(ticker, timeframe="1Min", limit=100)
            print("df not defined")
            ticker_data = ticker_data.df
            ticker_data.columns = ticker_data.columns.droplevel(0)
            ticker_data.columns
            last_minute_data = ticker_data.iloc[[-3, -2, -1]]
        else:
          last_minute_data = df.iloc[[-3, -2, -1]]
          
        #last_minute_data = pd.DataFrame(last_minute_data)
  
        # global last_minute_data
        # last_minute_data['close'] = last_minute_data['4. close']
  
        print("vwap")
        vwap(ticker_data)
  
        print("get_advice")
        get_advice(ticker_data)
  
        ticker_data['close'] = ticker_data['close']# * (int(investment / ticker_data['close'][0]))
        ticker_data['price change'] = ticker_data['close'].diff(periods=1)
        # print(last_minute_data)
        print("get_advice")
        get_advice(ticker_data)
        print("ticker_data")
        print(ticker_data)
        print("add_calculations to ticker data")
        add_calculations(ticker_data)
        print("ticker_data")
        # print(ticker_data)
        # print(ticker_data.iloc[:,-3:])
        print(ticker_data[['close', 'balance', 'advice', 'real choice', 'correct']])
        action = ticker_data["advice"]
        action = action[-1]
        action = action.lower()
        print("action is: {}".format(action))
        print("ticker_data['advice']")
        print(ticker_data['advice'].tail(15))
  
        if action == "sell" and not shorting:
          print("Closing all positions")
          api.close_all_positions()
  
        # global order_id
  
        # try:
        #   order_id
        # except NameError:
        #   print("defining order_id")
        #   order_id = "000"
  
        # print("order ID: {}".format(order_id))
  
        account = api.get_account()
        print()
        portfolio_value = account.portfolio_value
        portfolio_value = float(portfolio_value.replace("'", ''))
        print(f"Current value is: ${portfolio_value}")
        print(f"Today's profit: ${portfolio_value - float(account.last_equity):.2f}")
        #print(f"Total profit: ${portfolio_value - investment:.2f}")
  
        if backtesting:
          # Was gonna add standard deviation, but it'd be higher if the trade bot makes more money
          # print(ticker_data.std(axis=0)['balance'])
          close_std = ticker_data.std(axis=0)['close']
          print(f"Close standard deviation: {close_std}")
  
        buy_and_hold = ticker_data['close'][-1] - ticker_data['close'][0]
        print(f"first close - last close: {buy_and_hold:.2f}")
        # input()
        try:
          # print("Getting position close")
          # position = api.get_position(ticker)
          position = print_position()
          current_qty = int(position.qty)
          # print(f"qty: {qty}, price change: {buy_and_hold}")
          buy_and_hold = buy_and_hold * abs(current_qty)
        except:
          print("No current positions")
          pass
        
        # print(f"{buy_and_hold} * {quantity}")
        print(f"{ticker} performance since first trade: ${buy_and_hold:.2f}")
        try:
          print(f" with {abs(current_qty)} shares")
        except:
          try:
            print(f" with {abs(quantity)} shares")
          except Exception as e:
            print(e)
            print(" with 1 share")

        # https://stackoverflow.com/a/29370182/8142044
        #greater than the start date and smaller than the end date
        global now
        mask = (ticker_data.index >= now.strftime('%Y/%m/%d')) & (ticker_data.index <= now.strftime('%Y/%m/%d'))
        today_data = ticker_data.loc[mask]
        #print("Today Data ===============================================")
        #print(today_data)
        avg_vol = ticker_data['volume'].mean()
        today_avg_vol = today_data['volume'].mean()
        print(f"Average volume: {int(avg_vol)}")
        print(f"Today's average volume: {today_avg_vol}")
  
        bot_performance = ticker_data['balance'][-1] - ticker_data['balance'][0]
        print(f"first balance - last balance: {bot_performance:.2f}")
        # input()
        try:
          # print("Getting position bot")
          # position = api.get_position(ticker)
          position = print_position()
          current_qty = int(position.qty)
          # print(f"qty: {qty}, price change: {buy_and_hold}")
          bot_performance = bot_performance * abs(current_qty)
        except:
          print("No current positions")
          pass
        
        # print(f"{buy_and_hold} * {quantity}")
        print(f"Bot performance since first trade: ${bot_performance:.2f}")
        try:
          print(f" with {abs(current_qty)} shares")
        except:
          try:
            print(f" with {abs(quantity)} shares")
          except Exception as e:
            print(e)
            print(" with 1 share")
  
        print(f"Bot advantage: ${bot_performance - buy_and_hold:.2f}")
  
        print_position()
  
        # Protect from over-doing it
        short_market = account.short_market_value
        short_market = short_market.replace("'", '')
        short_market = float(short_market)
  
        cash = account.cash
        cash = cash.replace("'", '')
        cash = float(cash)
  
        # if (short_market < -24000):
        #   if action == "sell":
        #     print("Skipping to get_new_data")
        #     print("sleeping")
        #     time.sleep(time_to_wait)
        #     get_new_data()
        
        limit_price = ticker_data['close']
        limit_price = limit_price[-1]
  
        from datetime import datetime
        
        now = datetime.now()
        #now = utc_to_local(datetime.now())
        #24-hour format
        # print(now.strftime('%Y/%m/%d %H:%M:%S'))
        current_time = now.strftime('%H:%M:%S')
        #12-hour format
        curr_datetime = now.strftime('%Y/%m/%d %I:%M:%S %p')
        # current_time = now.strftime('%I:%M:%S %p')
        print(curr_datetime)
        #print(current_time)
        
        if current_time == "15:57":
          api.close_all_positions()
          print("Sleeping until next day...")
          time.sleep(63000)
          open = False
          if not open:
            wait_for_open()
        if current_time > "15:57":
          api.close_all_positions()
          print("15 min ======================================")
          open = False
          wait_for_open()
        if current_time < "18" and current_time > "16": # 18 is 6
          print("During aftermarket hours")
          extended_hours = True
          #open = True
          open = False
          if not open:
            wait_for_open()
        elif (current_time < "16") and (current_time > "09:30 AM"): # 16 is 4
          print("During market hours")
          open = True
          extended_hours = False
          if not open:
            wait_for_open()
        elif (current_time > "09 AM") and (current_time < "09:30 AM"):
          print("During beforemarket hours")
          extended_hours = True
          open = True
          if not open:
            wait_for_open()
        else:
          open = False
          if not backtesting:
            pass
            # raise Exception("Market is closed") 
            # sys.exit("Market is closed")
          # if not open:
          #   wait_for_open()
 
        global margin

        if margin and (not current_time > "15:57"):
          pass
          #portfolio_value = portfolio_value * margin_times
        else:
          margin = False
          margin_times = 1

        #margin_times = 4  
        #global margin_times
        # quantity = 60 #20
        keep_as_cash = investment - (380*3)
        print(f"quantity = {account.last_equity} - {keep_as_cash} * {margin_times} / {limit_price}")
        quantity = ((float(account.last_equity) - keep_as_cash) * margin_times) / limit_price
        print(f"Quantity = {quantity}")
        #keep_as_cash = 600
        #quantity = quantity - keep_as_cash
        #bp_quantity = float(account.regt_buying_power) / limit_price
        bp_quantity = (float(account.buying_power) - (keep_as_cash)) / limit_price
        #bp_quantity = bp_quantity - keep_as_cash
        print(f"bp qty: {int(bp_quantity)} qty: {int(quantity)}")
        if (bp_quantity < quantity) and (bp_quantity >= 1):
            quantity = bp_quantity
        print(f"Buying power: ${account.buying_power}")
        #quantity = portfolio_value / limit_price
        quantity = int(quantity)
        if action == "sell":
          quantity = -quantity
  
        long_market = account.long_market_value
        long_market = float(long_market.replace("'", ''))
  
        last_action = ticker_data["advice"]
        last_action = last_action[-1]
        # if action != last_action:
        #   # quantity = quantity * 2
        #   if (long_market + (limit_price * quantity)) > (short_market - (limit_price * quantity)):
        #     portfolio_value = (long_market + (limit_price * quantity))
        #     quantity = portfolio_value / limit_price
        #     quantity = int(quantity)
        #   else: 
        #     portfolio_value = (short_market - (limit_price * quantity))
        #     quantity = portfolio_value / limit_price
        #     quantity = int(quantity)
  
  
        if open:
          trade = True
        time_to_wait = 47 #@param {type:"slider", min:1, max:60, step:1}
        
        # if (short_market - (limit_price * quantity)) < -investment:
        #   print((short_market - (limit_price * quantity)))
      
        #   if action == "sell":
        #       print("setting trade to false: sell")
        #       trade = False
        #       print("Skipping to get_new_data")
        #       print("sleeping")
        #       time.sleep(time_to_wait)
        #       get_new_data()
  
  
  
        limit_price = ticker_data['close']
        limit_price = limit_price[-1]
        # if (long_market + (limit_price * quantity)) > investment:
          
        #   print((long_market + (limit_price * quantity)))
        #   if action == "buy":
        #     print("setting trade to false")
        #     trade = False
        #     print("Skipping to get_new_data")
        #     print("sleeping")
        #     time.sleep(time_to_wait)
        #     get_new_data()
  
        
  
        # if (cash / (limit_price * quantity)) < 1:
        #     print("Skipping to get_new_data")
        #     print("sleeping")
        #     time.sleep(time_to_wait)
            # get_new_data()
  
        # if (long_market > 24000):
        #   if action == "buy":
        #     print("Skipping to get_new_data")
        #     print("sleeping")
        #     time.sleep(time_to_wait)
        #     get_new_data()
        try:
          print("Getting positions")
          position = print_position()
          current_qty = int(position.qty)
        except Exception as e:
          print(e)
          current_qty = 0
     
        #print(f"{current_qty}, {quantity}")
        #if current_qty > 0:
          #quantity = quantity - current_qty
        #else:
          #quantity = quantity + current_qty

        print(f"{abs(((current_qty+quantity) * limit_price))} > {abs(float(account.buying_power))}")
        print(abs(((current_qty+quantity) * limit_price)) > abs(float(account.last_equity)))
        print(f"current: {current_qty} trade qty: {quantity}")
        if abs(((current_qty+quantity) * limit_price)) > (abs(float(account.last_equity) - keep_as_cash) * margin_times):
          print("Setting trade to false because trade > account.last_equity (bp)")
          trade = False
        else: trade = True
  
        def order(type="limit", extended_hours=extended_hours, action=action, quantity=quantity, ticker=ticker, limit_price=limit_price):
            if extended_hours:
              print(f"Extended limit order: {action} {quantity} shares of {ticker} for ~${limit_price}. Total: ~${limit_price*quantity:.2f}")
              api.submit_order(symbol=ticker,
                  qty=abs(quantity),
                  side=action,
                  time_in_force='day',
                  extended_hours= extended_hours,
                  type='limit',
                  limit_price=limit_price)
                  # client_order_id=order_id)
            else:
              print(f"{type} order: {action} {quantity} shares of {ticker} for ~${limit_price}. Total: ~${(limit_price*quantity):.2f}")
              api.submit_order(symbol=ticker,
                  qty=abs(quantity),
                  side=action,
                  time_in_force='day',
                  type='limit',
                  limit_price=limit_price)
                  # limit_price=400.00,
                  # client_order_id=order_id)
                  
        def check_fill(to_close=False, limit_price=limit_price, ticker=ticker, action=action, quantity=quantity):
            print("In check fill")
            filled = 0
            if not to_close:
              #while not filled:
              while filled == 0:
                if limit_price <= limit_price/2:
                  raise Exception(f"limit price == {limit_price}")
                try:
                  print("Getting positions")
                  api.get_position(ticker)
                except:
                  print("No current positions")
                  print("Check fill cancelling orders...")
                  api.cancel_all_orders() 
                  #filled = False
                  print(f"Filled = {filled}")
                  print("Not filled, so changing limit...")
                  if action=="buy":
                    print("Raising limit price to buy...")
                    limit_price = limit_price + 0.01
                    try:
                      print("Ordering after raising limit price to buy")
                      #filled = check_fill(limit_price=limit_price)
                      order(limit_price=limit_price, quantity=quantity, action=action)
                      print("and then checking fill of buy")
                      filled = check_fill(limit_price=limit_price, quantity=quantity, action=action)
                    except Exception as e:
                      print(e)
             
                  else:
                    print("Lowering limit price to sell...")
                    limit_price = limit_price - 0.01
                    try:
                      print("Ordering after lowering limit price to sell")
                      #filled = check_fill(limit_price=limit_price)
                      order(limit_price=limit_price, quantity=quantity, action=action)
                      print("and then checking fill")
                      filled = check_fill(limit_price=limit_price, quantity=quantity, action=action)
                    except Exception as e:
                      print(e)

                  #if not extended_hours:
                    #order()
                else:
                  print("Filled")
                  filled += 1
                  return filled
              return filled
            else:
              print("Check fill to_close")
              try:
                print("Getting positions")
                api.get_position(ticker)
              except:
                print("No positions")
                filled += 1
                return filled
              else: 
                #filled = False
                api.cancel_all_orders()
                if action=="buy":
                  print("Raising limit price to buy...")
                  limit_price = limit_price + 0.01
                  print("Order after raising limit price to buy to close")
                  order(limit_price=limit_price, quantity=quantity, action=action)
                  filled = check_fill(to_close=True, limit_price=limit_price, quantity=quantity, action=action)
                  print(f"Filled: {filled}")
                else:
                  print("Lowering limit price to sell")
                  limit_price = limit_price - 0.01
                  print("Order after lowering limit price to sell to close")
                  order(limit_price=limit_price, quantity=quantity, action=action)
                  filled = check_fill(to_close=True, limit_price=limit_price, quantity=quantity, action=action)
                  print(f"Filled: {filled}")
        e = ""
        def bp_error(e=e):
          i = quantity - 1
          filled = 0
          #while not filled:
          while filled == 0:
            while i > 0:
              try:
                print(f"======================i = {i}")
                order(quantity=i)
                filled = check_fill()
                print(f"Filled: {filled}")
              except Exception as e:
                print(e)
                #filled = False
                i -= 1
              else:
                print("Filled")
                filled += 0
                return filled
                break
            else:
              if not filled: 
                raise Exception(f"filled: {filled} i: {i}")
          else:
            filled += 1
        def qty_error(e=e):
          print("Not filled")
          filled = 0
          i = quantity
          #while not filled:
          while filled == 0:
            while i > 0:
              i -= 1
              print(f"=-=-=-=-==-=-=- i = {i}")
              try:
                order(quantity=i)
                print("CHECKING FILL ==============")
                filled = check_fill()
                print(f"Filled: {filled}")
              except Exception as e:
                #filled = False
                e = str(e)
                print(e)
                print(e[:36])
                if e[:25] == "insufficient buying power":
                  print("Calling bp_error from qty_error")
                  bp_error(e)
              else:
                print("filled")
                filled += 1
                play_sound("filled")
                return filled
                break
            else: 
              raise Exception(f"i = {i}")
                  
        # if abs(((qty+quantity) * limit_price)) > investment:
        #   print("Closing all positions because ")
        #   api.close_all_positions()
        # portfolio_value = account.portfolio_value # already called this, prob dont need to call here
        # portfolio_value = float(portfolio_value.replace("'", '')) #################################
        try:
          market_value = position.market_value
          market_value = float(market_value.replace("'", ''))
          print(f"position market value: {abs(market_value)} > portfolio value: ${(portfolio_value - keep_as_cash) * margin_times:.2f}")
        except:
          print("No current positions")
        try:
          position = api.get_position(ticker)
          print(f"Market value > usable cash: {abs(market_value)} > ({account.last_equity} - {keep_as_cash}) * {margin_times}")
        except Exception as e:
          print(e)
        try:
          if (abs(market_value) > ((float(account.last_equity) - keep_as_cash) * margin_times)) and not backtesting:
            print("Correcting position size because position market value > useable cash")
            #api.close_all_positions()
            correction = ((abs(market_value) - ((float(account.last_equity) - keep_as_cash) * margin_times))) / limit_price
            import math
            correction = math.ceil(correction)
            if position.side == "long":
              correct_side = "sell"
            if position.side == "short":
              correct_side = "buy"
            try:
              order(quantity=correction, action=correct_side)
              filled = check_fill(limit_price=limit_price, action=correct_side, quantity=correction)
              sendEmail()
            except Exception as e:
              #filled = False
              e = str(e)
              print(e)
              print(e[:36])
              if e[:36] == "insufficient qty available for order":
                qty_error(e)
              elif e[:25] == "insufficient buying power":
                bp_error(e)
        except Exception as e:
          print(e)
    
        try:
          market_value
        except:
          market_value = 0

        try:
          position = api.get_position(ticker)
          side = position.side
        except Exception as e:
          print(e)
          side = ""

        if (abs(market_value) < (quantity * limit_price)) and not backtesting and (position.side == action):
          print("Not utilizing available cash, correcting positions...")
          quantity = abs(market_value) - (quantity * limit_price)
          try:
            order()
            filled = check_fill()
          except Exception as e:
            #filled = False
            e = str(e)
            print(e)
            print(e[:36])
            if e[:36] == "insufficient qty available for order":
              qty_error(e)
            elif e[:25] == "insufficient buying power":
              bp_error(e)

        # Check if the market is open now.
        clock = api.get_clock()
        open = clock.is_open
        print('The market is {}'.format('open.' if open else 'closed.'))
  
        # if margin and (current_time > "15:45"): # 3:45, or maybe 17:45
        #   print("Closing margin")
        #   # quantity / 2
        #   margin_times = 1
        #   margin = False
  
        # print(f"ext hours: {extended_hours}")
        print(f"trade: {trade}")
      
        # Check when the market was open on Dec. 1, 2018
        from datetime import datetime
        todays_date = datetime.today().strftime('%Y-%m-%d')
        date = todays_date
        calendar = api.get_calendar(start=date, end=date)[0]
        print('The market opened at {} and closed at {} on {}.'.format(
            calendar.open,
            calendar.close,
            date
        ))
  
        # current_time = int(time.time())
        # fifteen_min = six - CONSTANT_SECONDS
        # print(f"Current time: {current_time}")
        # print(f"time before 15: {fifteen_min}")
    
        # minutes_to_six = (six - current_time)/60
        # print(f"Minutes to six: {minutes_to_six}")
  
        # if (current_time > fifteen_min) and (current_time < six):
        #   print("15 minute mark, closing positions...")
        #   api.close_all_positions()
        #   open = False
        #   sys.exit("15 minute mark")
  
        # if current_time == six:
        #   open = False
  
        # if open:
        #   extended_hours = False
        # else:
        #   extended_hours = True
        extended_hours = False
        if backtesting:
          trade = False
          play_sound("error")
          # To pause to not trade, only for backtesting
          input()
        if trade == True:
          print(f"ext: {extended_hours}")
          print("Cancelling all orders")
          api.cancel_all_orders()
          
          quantity = abs(quantity)
          print(f"trade: {trade}")
          print("Cancelling all orders")
          api.cancel_all_orders()
                  
          if extended_hours == False:
            try:
              api.get_position(ticker)
              print(f"============Position side: {position.side}")
              if position.side == "short" and action == "buy":
                print("Closing all positions to buy")
                #api.close_all_positions()
                try:
                  print("Ordering")
                  order()
                  print("Checking fill")
                  filled = check_fill(to_close=True)
                  print(f"Filled: {filled}")
                except Exception as e:
                  e = str(e)
                  print(e)
                # time.sleep(8) # sleep because it won't let us trade too fast
                # quantity = quantity * 2
              if position.side == "long" and action == "sell":
                print("Closing all positions to sell")
                #api.close_all_positions()
                try:
                  print("Ordering")
                  order()
                  filled = check_fill(to_close=True)
                  print(f"Filled: {filled}")
                except Exception as e:
                  e = str(e)
                  print(e)
            except Exception as e:
              print(e)

            # https://algotrading101.com/learn/alpaca-trading-api-guide/
            try:
              api.get_position(ticker)
            except:
              try:
                order()
                filled = check_fill()
                print(f"Filled: {filled}")
              except Exception as e:
                print(f"Buying power: {account.buying_power}")
                #filled = False
                e = str(e)
                print(e)
                print(e[:36])
                if e[:36] == "insufficient qty available for order":
                  qty_error(e)
                elif e[:25] == "insufficient buying power":
                  bp_error(e)
              else:
                print("Order sent")
                play_sound("filled")
          else:
            print("ext hours")
            # quantity = 50
            # Get the last close price for the limit price
            limit_price = ticker_data['close']
            limit_price = limit_price[-2]
            if action == "sell":
              limit_price -=1
            else:
              limit_price +=1
  
            try:
              api.get_position(ticker)
              print(f"Positions side: {position.side}")
              if position.side == "short" and action == "buy":
                print("Closing all positions to buy")
                time.sleep(10) # sleep because it won't let us trade too fast
                # quantity = quantity * 2
              if position.side == "long" and action == "sell":
                print("Closing all positions to sell")
                time.sleep(10) # sleep because it won't let us trade too fast
                # quantity = quantity * 2
            except:
              print("No current positions")
  
            try:
              order()
              filled = check_fill()
              print(f"Filled: {filled}")
            except Exception as e: 
              # check if we get filled, if not try again
              def check_fill(limit_price=limit_price, quantity=quantity, filled=filled):
                #while not filled:
                while filled == 0:
                  try:
                    api.get_position(ticker)
                  except:
                    api.cancel_all_orders() 
                    #filled = False
                    if action=="buy":
                      limit_price = limit_price + 0.01
                      order(limit_price=limit_price, quantity=quantity)
                    else:
                      limit_price = limit_price - 0.01
                      order(limit_price=limit_price, quantity=quantity)
                    
                    #if not extended_hours:
                      #order()
                  else:
                    filled += 1
                    print(f"Filled = {filled}")
  
              check_fill()
              play_sound("error")
              print(e)
  
  
        # initialize = False
  
        # current_position = 
        
        # print("incrementing order_id")
        # order_id = int(order_id)
        # order_id += 1
        # print("order ID: {}".format(order_id))
  
        #stock = stock.append({'close': last_minute_close}, ignore_index=True)
        try:
          stock = stock.append(last_minute_data)
        except:
          stock = last_minute_data
          stock = stock.append(last_minute_data)
  
        stock
  
        return ticker_data
  
      def print_position():
        try:
          # Doesn't work for some reason, get do position.side
          # position = api.list_positions()
          print("Getting positions function")
          #global position
          position = api.get_position(ticker)
          # print(position)
          print(f"Currently {position.side} {position.qty} shares of {position.symbol} for ${position.market_value}")
          return position
        except Exception as e: 
          print(e)
          # pass
          # print("No current positions")
  
      import sys
  
      import time
  
      def get_new_data():
        # return open
        oldtime = time.time()
        time_to_wait = 47 #@param {type:"slider", min:1, max:60, step:1}
  
        # print(oldtime)
        print("It's been a minute, getting new data...")
        # ticker_data, ticker_meta_data = ts.get_intraday(symbol='SPY', interval='1min', outputsize='full')
  
        ticker_data = api.get_barset(ticker, timeframe="1Min")
        # data = SPY.df
        # data
        try:
          ticker_data = ticker_data.df
        except:
          pass
        # print(SPY.columns)
        # SPY = SPY.reset_index(level=0, drop=False, inplace=False, col_level=0)
  
        # print(SPY.columns)
  
        # SPY
        # SPY.columns = SPY.columns.map(''.join)
        ticker_data.columns = ticker_data.columns.droplevel(0)
        ticker_data.columns
        # data = SPY
  
        # ticker_data = data
        oldtime = time.time()
        print(f"Oldtime: {oldtime}")
  
        ticker_data = do_new_data()
        ran_this_already = True
        #return open
        if (time.time() - oldtime) < time_to_wait:
          print("It has not been a minute")
          first_time = False
          print("sleeping")
          time.sleep(time_to_wait)
  
  
      while True:
        try:
          if (time.time() - oldtime) > time_to_wait or first_time == True:
            get_new_data()
        except NameError:
          get_new_data()
  
      # try:
      #     ran_this_already
      # except NameError:
      #     print("Not defined")
      #     ticker_data = do_new_data()
      #     ran_this_already = True
      # else:
      #     #sys.exit("Already ran")
      #     print(ran_this_already)
      #     print("Already ran")
  
      #     # Get the last three minutes
      #     last_minute_data = df.iloc[[-1, -2, -1]]
      #     print(last_minute_data)
      #     get_advice(ticker_data)
      #     add_calculations(ticker_data)
      #     #stock
  
    # on exit 
    # https://stackoverflow.com/a/3850293/8142044
    # except KeyboardInterrupt:
    except ConnectionResetError:
      pass
    except Exception as e:
      print(e)
      e = str(e)
      if e[:31] == "failed to validate Bearer token":
        pass 
      if e[:51] == "alpaca_trade_api.rest.APIError: service unavailable":
        pass
      # clean up
      print("Closing positions...")
      api.close_all_positions()
      initialize = True
      account = api.get_account()
      print()
      portfolio_value = account.portfolio_value
      portfolio_value = float(portfolio_value.replace("'", ''))
      print(f"Current value is: ${portfolio_value}")
      today_profit = portfolio_value - investment
      print(f"Today's profit: ${today_profit:.2f}")

      if today_profit < -500:
        raise Exception(f"Fail safe triggered. Today's profit: {today_profit}")
        api.close_all_positions()
        sys.exit("Fail safe triggered")
  
      # print(f"{ticker} performance since first trade: ${buy_and_hold:.2f}")
      try:
        print(f" with {quantity} shares")
      except:
        try:
          print(f" with {qty} shares")
        except:
          print(" with 1 share")
  
      if margin and (not current_time > "15:45"):
        portfolio_value = portfolio_value * margin_times
        do_new_data()
      else:
        margin = False
        margin_times = 1
  
      #print_position()

      sendEmail()
      play_sound("error")
      sys.exit(e)
        # try:
        #   # Doesn't work for some reason, get do position.side
        #   # position = api.list_positions()
        #   position = api.get_position(ticker)
        #   print(f"Currently {position.side} {position.qty} shares of {position.symbol} for ${position.market_value}")
        # except Exception as e: 
        #   print(e)
        #   print("No current positions")
        # raise
  
# TODO:
# - if current_time == "market open" and api_open == false, wait a day
# - if first order was too long ago, it will slow down pi
# - correlation graph of bot performance backtest & profit

# - check if need to trade during extended hours
# - might need to add something to check if this has already been run because it appends over and over if i run it multiple times
# - maybe I shouldn't do extended hours, it doesn't really seem to be worth it
# - add some additional statistical analysis to the backtesting (STD, # of days up/# of days down)
# - additonally, backtest closing positions before market close
# - maybe add a debugging mode to print stuff
# - backtest AMZN with no shorting
# - backtest with 2-4x margin during market hours
# - add a test to see if we actually get filled, and if not, try again
# - maybe for ext market limit order, gradually increase limit_order difference if not filled
 
# DONE:
# - get rid of HOLD, and just replace with previous action
# - if we can't buy QUANTITY, then trade CASH / limit_price
# - MAKE SURE THAT WE'RE NOT GOING SHORT EVER ok maybe not
# - backtest on AMZN cuz of its high price - DONE, it performed awful
# - make it so the loading bar is only called if it will take a certain amount of time
# - replace orders with order function
# - add margin options
