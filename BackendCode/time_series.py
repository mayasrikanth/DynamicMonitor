'''Script for applying time series models to hashtag frequency data.
Currently supports ARIMA (we will continue to add code for more complex nonlinear
deep learning models). '''
import warnings
warnings.filterwarnings("ignore")
from statsmodels.tsa.arima_model import ARIMA   # running ARIMA
from sklearn.metrics import mean_squared_error  # evaluating ARIMA
from statsmodels.tsa.stattools import adfuller # import for check stationarity
from datetime import date, time, datetime
import pandas as pd

def process_data(): # specific to BB experiment
    # get correct number of day observations & output... (track issue until 5/1/2013)
    threshold =  datetime(year=2013, month=5, day=1, hour=0, minute=0, second=0)

    dynamic_keywords = ['hash_bostonbombings', 'hash_bostonmarathon', 'hash_boston', \
    'hash_cambridge']
    for keyword in dynamic_keywords:
        fname = keyword + '_daycounts.csv'
        df = pd.read_csv(fname)
        df['Date (GMT)'] = pd.to_datetime(df['Date (GMT)'])
        df = df[df['Date (GMT)'] <= threshold]
        fname = keyword + 'counts_arima.csv'
        df.to_csv(fname)


# Function to check a given series for stationarity
def check_stationary(X):
    '''Return true if series is stationary, return false otherwise.'''
    res = adfuller(X)
    p_val = res[1]
    if p_val > 0.05:
        print("Non-stationary: ", p_val)
        return False
    else:
        print("Stationary: ", p_val)
        return True

# Function to try different combinations of parameters (p,d,q) to construct optimal arima model
# for now, simply prints the best configuration, but in future, we'll need to actually return the model.
def evaluate_models(train, test, p_values, d_values, q_values):
    best_score, best_cfg = float("inf"), None
    for p in p_values:
        for d in d_values:
            for q in q_values:
                order = (p,d,q)
                try:
                    mse = evaluate_arima_model(train, test, order)
                    if mse < best_score:
                        best_score, best_cfg = mse, order
                        print('ARIMA%s MSE=%.3f' % (order,mse))
                except:
                    continue
    print('Optimal ARIMA%s MSE=%.3f' % (best_cfg, best_score))


def run_arima(test, train, arima_order):
    ''' Function to run ARIMA for plotting forecasts vs. actuals'''
    history = [x for x in train]
    # make predictions
    predictions = list()
    for t in range(len(test)):
        model = ARIMA(history, order=arima_order)
        model_fit = model.fit(disp=0)
        yhat = model_fit.forecast()[0]
        predictions.append(yhat)
        history.append(test[t])
    # calculate out of sample error
    error = mean_squared_error(test, predictions)
    print(error)
    return (test, predictions)


def forecast_arima(test, train, arima_order):
    ''' Function to run ARIMA and plot the forecasts vs. actuals'''
    history = [x for x in train]

    # make predictions
    model = ARIMA(history, order=arima_order)
    model_fit = model.fit()
    forecast, stderr, conf = model_fit.forecast(steps=len(test), alpha=0.05) #[0]
    print("CONFIDENCE: ", conf)

    print(forecast)
    ## forecast for length of test set
    n_steps = len(test)
    #forecast = model_fit.forecast(steps=n_steps)[0]

    # calculate out of sample error
    error = mean_squared_error(test, forecast)
    print(error)
    return (conf, history,forecast)


def forecast_arima_plot(series):
    # running multistep_arima on a given series for weekly/daily forecast 15 steps into future.
    t = 15
    future_start = len(series) - t
    conf, history, forecast = forecast_arima(series[future_start:], series[:future_start], (4,1,3))
    # Plotting forecast with confidence intervals....
    x = list(range(future_start, len(series)))
    y1 = conf[:, 0]
    y2 = conf[:, 1]



    plt.fill_between(x, y1, y2, color='red', alpha=0.2, label='95% Confidence')
    plt.plot(series, color='turquoise', lw=2, label='True')
    plt.plot(list(range(future_start, len(series))), forecast, color='magenta', lw=2, label='Forecast')
    plt.title("#Insurrection")
    plt.xlabel("Hour")
    plt.ylabel("Log Raw Counts")
    plt.box(on=None)
    plt.axis('on')
    plt.legend()

if __name__ == '__main__':
    print("Simulation round ...")
    #infile = input('Name of input Tweets file?: ')
    #outfile = input('Name of output file?: ')
    print('\n\n START....')
    #compile_data(infile, outfile)
    process_data()
