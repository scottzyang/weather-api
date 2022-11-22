import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
# from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'
# https://api.openweathermap.org/data/2.5/weather?q={city name}&appid={API key}

################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    # TODO: Use 'request.args' to retrieve the city & units from the query
    # parameters.
    city = request.args.get('city')
    units = request.args.get('units')

    params = {
        # TODO: Enter query parameters here for the 'appid' (your api key),
        # the city, and the units (metric or imperial).
        # See the documentation here: https://openweathermap.org/current
        'q': city,
        'units': units,
        'appid': API_KEY,
    }

    result_json = requests.get(API_URL, params=params).json()

    # Uncomment the line below to see the results of the API call!
    # pp.pprint(result_json)

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the result_json object above.

    # For the sunrise & sunset variables, I would recommend to turn them into
    # datetime objects. You can do so using the `datetime.fromtimestamp()` 
    # function.
    context = {
        'date': datetime.now(),
        'city': result_json['name'],
        'description': result_json['weather'][0]['description'],
        'temp': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    # TODO: Make 2 API calls, one for each city. HINT: You may want to write a 
    # helper function for this.
    def city_result(city):
        params = {
            'q': city,
            'units': units,
            'appid': API_KEY,
        }
        city_response = requests.get(API_URL, params=params).json()
        return city_response

    city1_response = city_result(city1)
    city2_response = city_result(city2)
    
    # function to determine 
    def greater_or_less(city1_stats, city2_stats):
        if city1_stats > city2_stats:
            return True
        return
    
    # function to determine differences
    def weather_difference(city1_stats, city2_stats):
        weather_diff = round(abs(city1_stats - city2_stats))
        return weather_diff

    # initialize values to False
    is_warmer = False
    is_humid = False
    is_windy = False

    # call function to determine if values should be true based on city weather info
    is_warmer = greater_or_less(city1_response['main']['temp'], city2_response['main']['temp'])
    is_humid = greater_or_less(city1_response['main']['humidity'], city2_response['main']['humidity'])
    is_windy = greater_or_less(city1_response['wind']['speed'], city2_response['wind']['speed'])

    # call function to determine the weather differences
    temp_diff = weather_difference(city1_response['main']['temp'], city2_response['main']['temp'])
    humid_diff = weather_difference(city1_response['main']['humidity'], city2_response['main']['humidity'])
    wind_diff = weather_difference(city1_response['wind']['speed'], city2_response['wind']['speed'])

    # TODO: Pass the information for both cities in the context. Make sure to
    # pass info for the temperature, humidity, wind speed, and sunset time!
    # HINT: It may be useful to create 2 new dictionaries, `city1_info` and 
    # `city2_info`, to organize the data.
    context = {
        'temp_diff': {
            'delta': temp_diff,
            'is_warmer': is_warmer
            },
        'humid_diff': {
            'delta': humid_diff,
            'is_humid': is_humid
        },
        'wind_diff': {
            'delta': wind_diff,
            'is_windy': is_windy
        },
        'units': get_letter_for_units(units),
        'date': datetime.now(),
        'city1': {
            'city': city1_response['name'],
            'description': city1_response['weather'][0]['description'],
            'temp': city1_response['main']['temp'],
            'humidity': city1_response['main']['humidity'],
            'wind_speed': city1_response['wind']['speed'],
            'sunrise': datetime.fromtimestamp(city1_response['sys']['sunrise']),
            'sunset': datetime.fromtimestamp(city1_response['sys']['sunset']),
        },
        'city2': {
            'city': city2_response['name'],
            'description': city2_response['weather'][0]['description'],
            'temp': city2_response['main']['temp'],
            'humidity': city2_response['main']['humidity'],
            'wind_speed': city2_response['wind']['speed'],
            'sunrise': datetime.fromtimestamp(city2_response['sys']['sunrise']),
            'sunset': datetime.fromtimestamp(city2_response['sys']['sunset']),
        }
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
