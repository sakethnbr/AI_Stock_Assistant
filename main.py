import json
import openai
import matplotlib.pyplot as plt
import streamlit as st
#import pandas as pd
import yfinance as yf 


###1. Authenticate with the Open AI API key 
openai.api_key = open('Key', 'r').read()



###2. Defining  and creating all of the functions that we want to use
def get_stock_price(ticker):
#Used for getting stock price 
#This function takes in the ticker parameter that the OpenAI API passes 
#in and then passess it through the yfinance information and returns the stock data
#From the past year in string form
    return str(yf.Ticker(ticker).history(period = '1y').iloc[-1].Close)

def calculate_SMA(ticker, window):
#Used to calculate SMA (Simple Moving Average)
#Done by taking the ticket history data from yf and
#Using it to find the mean of the live data 
    data = yf.Ticker(ticker).history(period = '1y').Close
    return str(data.rolling(window = window).mean().iloc[-1])

def calculate_EMA(ticker, window):
#Used to calculate EMA (Exponential Moving Average)
#Done by taking the ticket history data from yf and
#Using it to find the mean of the live data 
    data = yf.Ticker(ticker).history(period = '1y').Close
    return str(data.ewm(span = window, adjust=False).mean().iloc[-1])

def calculate_RSI(ticker):
#Used to calculate RSI (Relative Strength Index)
#FINISH DOCUMENTATION FOR THIS
    data = yf.Ticker(ticker).history(period = '1y').Close
    delta = data.diff()
    up = delta.clip(lower = 0)
    down = -1 * delta.clip(upper =0)
    ema_up = up.ewm(com = 14 -1, adjust = False).mean()
    ema_down = down.ewm(com = 14 - 1, adjust =False).mean()
    rs= ema_up / ema_down
    return str(100 - (100 / (1 + rs)).iloc[-1])

def calculate_MACD(ticker):
#Used to calculate MACD (Moving average convergence/divergence)
#to indicate to invesors when to buy or sell stocks
    data = yf.Ticker(ticker).history(period = '1y').Close
    short_EMA = data.ewm(span = 12, adjust =False).mean()
    long_EMA = data.ewm(span = 26, adjust =False).mean()
    MACD = short_EMA - long_EMA
    signal = MACD.ewm(span = 9, adjust = False).mean()
    MACD_histogram = MACD - signal
    return f'{MACD[-1]}, {signal[-1]}, {MACD_histogram[-1]}'

def plot_stock_price(ticker):
    # Function used to plot the stock price
    # Sends ticker information into a plot using matplotlib
    data = yf.Ticker(ticker).history(period='1y').Close
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data.Close) 
    plt.title(f'{ticker} Stock Price Over Last Year')
    plt.xlabel('Date')
    plt.ylabel('Stock Price ($)')
    plt.grid(True)
    plt.savefig('stock.png')
    plt.close()




###3. Defining these functions that exist for chatGPT by creating a list of dictionaries

functions = [ 
    {
        'name': 'get_stock_price',
        'description': "Gets the latest stock price given the ticker symbol of a company.",
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (for example AAPL for Apple)'
                }
            },
            'required': ['ticker'],
        }
    },
    {
        'name': 'calculate_SMA',
        'description': 'Calculate the sample moving average for a given stock ticker and a window.',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (for example AAPL for Apple)'
                },
                'window': {
                    'type': 'integer',
                    'description': 'The timeframe to consider when calculating the SMA'
                }
            },
            'required': ['ticker', 'window'],
        },
    },
    {
        'name': 'calculate_EMA',
        'description': "Calculate the exponential moving average for a given stock ticker and a window",
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (for example AAPL for Apple)'
                },
                'window': {
                    'type': 'integer',
                    'description': 'The timeframe to consider when calculating the EMA'
                }
            },
            'required': ['ticker', 'window'],
        },
    },
     {
        'name': 'calculate_RSI',
        'description': "Calculate the RSI for a given stock ticker",
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (for example AAPL for Apple)'
                },
            },
            'required': ['ticker'],
        },
    },
    {
        'name': 'calculate_MACD',
        'description': "Calculate the MACD for a given stock ticker",
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (for example AAPL for Apple)'
                },
            },
            'required': ['ticker'],
        },
    },
    {
        'name': 'plot_stock_price',
        'description': "Plot the stock price for the last year given the ticker symbol of a company.",
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type': 'string',
                    'description': 'The stock ticker symbol for a company (for example AAPL for Apple)'
                },
            },
            'required': ['ticker'],
        },
    },
]

###4. Map the function names to the actual functions 
available_functions = {
    'get_stock_price': get_stock_price,
    'calculate_EMA': calculate_EMA,
    'calculate_SMA': calculate_SMA,
    'calculate_RSI': calculate_RSI,
    'calculate_MACD': calculate_MACD,
    'plot_stock_price': plot_stock_price
}


###5. Create streamlit web application calls process to pass information in to and from the Open AI API

#Initializing a message list which is initially empty
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

#Title for chatbot
st.title('Stock Analysis Chatbot Assistant')

#This is where user input is collected
user_input = st.text_input('Your input:')

###6. Take in the inputs and identify what functions to call and pass in the arguments
if user_input: 
    try:
        #This is where the user asks the question and the contexts are applied to the question
        #Which is then referenced by the list of dictionaries in order to make a function call if necessary
        st.session_state['messages'].append({'role': 'user', 'content': f'{user_input}'})
        #This is where the conversation between chatGPT and the user is occuring
        #The user response is fed to chatGPT where it will run through
        #OpenAI servers to then be filled with contexts and send calls to functions if necessary
        response = openai.ChatCompletion.create(
            model = 'gpt-3.5-turbo-0613',
            messages = st.session_state['messages'],
            functions=functions,
            function_call='auto'
        )
        response_message = response['choices'][0]['message']

        #This is for the scenario if chatGPT brings in a function call
        #This clause is for if the user passes in a reference or call to
        #one of our created functions, then the called function will be referenced
        if response_message.get('function_call'):
            #Where function name and function arguments are passed in
            function_name = response_message['function_call']['name']
            function_args = json.loads(response_message['function_call']['arguments'])
            #For if passed in arguments only give a ticker:
            if function_name in ['get_stock_price', 'calculate_RSI', 'calculate_MACD', 'plot_stock_price']:
                #This is for if we only get a stock ticker passed in as input from chatGPT
                args_dict = {'ticker': function_args.get('ticker')}
            #For if passed in arguments give both a ticker and a window:
            elif function_name in ['calculate_SMA', 'calculate_EMA', ]:
                args_dict = {'ticker': function_args.get('ticker'), 'window':function_args.get('window')}
                
            #Here is where the function is called and the response is recieved    
            function_to_call = available_functions[function_name]
            function_response = function_to_call(**args_dict)

            #This clause is for if someone wants to call the stock plotting function
            if function_name == 'plot_stock_price':
                st.image('stock.png')
            #For any other function, append the role function, the name of function, and response to the session
            else:
                st.session_state['messages'].append(response_message)
                st.session_state['messages'].append(
                    {
                        'role': 'function',
                        'name':function_name,
                        'content':function_response
                    }
                )
                ###7.Take outputs produced by functions and run them through OpenAI API and bring back responses
                #here is where we add a second completion where we run it through openAI servers and get a normal human
                #response generated
                second_response = openai.ChatCompletion.create(
                    model = 'gpt-3.5-turbo-0613',
                    messages = st.session_state['messages']
                )
                #Displaying response
                st.text(second_response['choices'][0]['message']['content'])
                #Adding the response to the context
                st.session_state['messages'].append({'role': 'assistant', 'content': second_response['choices'][0]['message']['content']})

        else:
            #This is for if the response does not result in a function call, it will just display the result of whatever you ask for
            st.text(response_message['content'])
            st.session_state['messages'].append({'role': 'assistnant', 'content': response_message['content']})

                    

    except Exception as e:
        st.text('Error occurred, ',str(e))
