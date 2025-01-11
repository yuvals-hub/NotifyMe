from django.shortcuts import render
from .forms import CreateNewList
from django.conf import settings
import googlemaps, json, re, pyowm
from datetime import datetime
from geopy.geocoders import Nominatim 

from django.http import StreamingHttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from demoApp.models import CameraSet
from demoApp.models import YoutubeSet
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
import requests

# Create your views here.

def index(request):
    template = "main/index.html"
    
    if request.method == "POST":
        form = CreateNewList(request.POST)
    else:
        form = CreateNewList()
    return render(request, template, {"form":form, 'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY})


def homepage(request):
    template = "main/homepage.html"

    #OpenWeatherMap
    #Connecting to API and initializing weather manager
    owm = pyowm.OWM(settings.OWM_API_KEY)
    weatherManager = owm.weather_manager()

    #Pulling weather data for given location
    # owmLocation = s_city + ", " + s_country
    owmLocation = "Toronto, Canada";
    weatherData = weatherManager.weather_at_place(owmLocation).weather

    #Obtaining desired datapoints
    locationWeather = weatherData.detailed_status
    locationTemp = weatherData.temperature('celsius')['temp']
    locationWind = round(weatherData.wind()['speed']*3.6)
    locationVis = weatherData.visibility(unit='kilometers')

    #Get travel time modifier weight and apply it to base duration
    weatherWeight = calculateWeight(locationWeather)
    # modifiedDuration = round(durationMin*weatherWeight)
    
    #CATSA Wait Times
    #Process terminal wait times if destination is YYZ or YTZ
    termWaitTimes = 0 #Unused flag
    # if d_add == "Toronto Pearson International Airport (YYZ), 6301 Silver Dart Dr, Mississauga, ON L5P 1B2, Canada":
    #     termWaitTimes = getAirportWait("https://www.catsa-acsta.gc.ca/en/airport/toronto-pearson-international-airport")
    # elif d_add == "Billy Bishop Toronto City Airport, 2 Eireann Quay, Toronto, ON M5V 1A1, Canada":
    #     termWaitTimes = getAirportWait("https://www.catsa-acsta.gc.ca/en/airport/billy-bishop-toronto-city-airport")

    youtube_set = list(YoutubeSet.objects.all().values())
    youtube_set_json = json.dumps(youtube_set)

    context = {
        'api_key':settings.GOOGLE_MAPS_API_KEY,
        'locationWeather': locationWeather,
        'locationTemp': locationTemp,
        'locationWind': locationWind,
        'locationVis': locationVis,
        'weatherWeight':weatherWeight,
        # 'modifiedDuration':modifiedDuration,
        'termWaitTimes':termWaitTimes,
        'youtube_set': youtube_set,
        'youtube_set_json': youtube_set_json,
        }

    return render(request, template, context)


def credits(request):
    template = "main/credits.html"
    return render(request, template)
    
def traffic(request):
    template = "main/traffic.html"
    cam_list = list(CameraSet.objects\
        .exclude(latitude__isnull=True)\
        .exclude(longitude__isnull=True)\
        .values('latitude',
                'longitude',
                'cam_url'))

    all_cams_json = json.dumps(cam_list)

    all_cams_json = json.dumps(cam_list)

    youtube_set = list(YoutubeSet.objects.all().values())

    countries = set([point['country'] for point in youtube_set if 'country' in point])

    youtube_set_json = json.dumps(youtube_set)

    show_feed = True
    feed_url = 'https://511on.ca/map/Cctv/600001-0-1--1'

    context = {
        'traffic_feed_url':feed_url,
        'width': "720",
        'height': '428',
        'show_traffic_feed': show_feed,
        'api_key':settings.GOOGLE_MAPS_API_KEY,
        'cam_set': all_cams_json,
        'youtube_set': youtube_set,
        'youtube_set_json': youtube_set_json,
        'countries': countries
    }
    return render(request, template, context)
    

def airport(request):
    template = "main/airport.html"    
    return render(request, template, {'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY})

def weather(request):
    template = "main/weather.html"
    return render(request, template)

def results(request):
    template = "main/results.html"
    #Obtaining user input from form
    s_add = request.POST.get("source")
    d_add = request.POST.get("destination")
    mode = str(request.POST.get("transport"))

    #Google Maps
    #Connecting to API and pulling raw trip data from Google
    gmaps_cl = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    time_now = datetime.now()
    query = json.dumps(gmaps_cl.distance_matrix(str(s_add), str(d_add), mode.lower(), departure_time=time_now, traffic_model="best_guess"))
    result = json.loads(query)
   
    #Obtaining desired datapoints as basic datatypes
    distance = result['rows'][0]['elements'][0]['distance']['text']
    s_add = result['origin_addresses'][0]
    d_add = result['destination_addresses'][0]
    s_city = result['origin_addresses'][0].split(',')[1].strip()
    s_country = result['origin_addresses'][0].split(',')[3].strip()
    #Account for traffic in base duration
    if mode == "Driving":
        duration = result['rows'][0]['elements'][0]['duration_in_traffic']['text']
        durationMin = round(result['rows'][0]['elements'][0]['duration_in_traffic']['value']/60)
    else:
        duration = result['rows'][0]['elements'][0]['duration']['text']
        durationMin = round(result['rows'][0]['elements'][0]['duration']['value']/60)
    
    #OpenWeatherMap
    #Connecting to API and initializing weather manager
    owm = pyowm.OWM(settings.OWM_API_KEY)
    weatherManager = owm.weather_manager()

    #Pulling weather data for given location
    owmLocation = s_city + ", " + s_country
    weatherData = weatherManager.weather_at_place(owmLocation).weather

    #Obtaining desired datapoints
    locationWeather = weatherData.detailed_status
    locationTemp = weatherData.temperature('celsius')['temp']
    locationWind = round(weatherData.wind()['speed']*3.6)
    locationVis = weatherData.visibility(unit='kilometers')

    #Get travel time modifier weight and apply it to base duration
    weatherWeight = calculateWeight(locationWeather)
    modifiedDuration = round(durationMin*weatherWeight)
    
    #CATSA Wait Times
    #Process terminal wait times if destination is YYZ or YTZ
    termWaitTimes = 0 #Unused flag
    if d_add == "Toronto Pearson International Airport (YYZ), 6301 Silver Dart Dr, Mississauga, ON L5P 1B2, Canada":
        termWaitTimes = getAirportWait("https://www.catsa-acsta.gc.ca/en/airport/toronto-pearson-international-airport")
    elif d_add == "Billy Bishop Toronto City Airport, 2 Eireann Quay, Toronto, ON M5V 1A1, Canada":
        termWaitTimes = getAirportWait("https://www.catsa-acsta.gc.ca/en/airport/billy-bishop-toronto-city-airport")

    context = {
        'result':result,
        'distance':distance,
        'duration':duration,
        'mode':mode.lower(),
        's_add':s_add,
        'd_add':d_add,
        'locationWeather': locationWeather,
        'locationTemp': locationTemp,
        'locationWind': locationWind,
        'locationVis': locationVis,
        'weatherWeight':weatherWeight,
        'modifiedDuration':modifiedDuration,
        'termWaitTimes':termWaitTimes,
        'api_key':settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, template, context)

def results2(request):
    template = "main/results2.html"
    location = request.POST.get("reference")
    gmaps_cl = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    g_location = gmaps_cl.geocode(location)
    latlng = (g_location[0]["geometry"]["location"]["lat"], g_location[0]["geometry"]["location"]["lng"])
    radius = request.POST.get("radius")
    airport_list = []
    
    
    query = gmaps_cl.places_nearby(location=latlng,
                                   keyword = 'airport',
                                   type = airport,
                                   name = 'airport',
                                   radius = radius)
    airport_list.extend(query.get('results'))
    
    df = pd.DataFrame(airport_list)
    result = df.iloc[0]['name']
    df.to_excel('test.xlsx', index=False)
    df2 = pd.read_excel('airports.xlsx')
    
    base = r'^{}'
    expr = '(?=.*{})'
    words = result.split()  
    
    result2 = df2.loc[df2['name'].str.contains(base.format(''.join(expr.format(w) for w in words)), regex=True), ['iata_code']].values[0]
    
    context = {
        'result':result,
        'result2':result2[0]
    }
    return render(request, template, context)

#Function to scrape and parse CATSA site for airport wait times
def getAirportWait(url):
	#Connect to CATSA URL and pull source
    page = requests.get(url)
    source = BeautifulSoup(page.text, "html.parser")

    #Find all instances of terminals and corresponding wait time
    terminals = source.findAll("td", attrs={"class":"views-field views-field-field-wt-checkpoint-name"})
    waitTimes = source.findAll("td", attrs={"class":"views-field views-field-php"})

    #Parse data and convert to usuable standard lists
    terminalList = []
    waitTimesList = []
    for terminal, waitTime in zip(terminals, waitTimes):
        terminalList.append(terminal.text)
        waitTimesList.append(waitTime.text)
    return zip(terminalList, waitTimesList)

#Function for calculating weather travel time multiplier
def calculateWeight(weatherDesc):
    #Create switch-case LUT of weights for all possible conditions
    timeOvernight = {
        "thunderstorm with light rain":1.041,
        "thunderstorm with rain":1.041,
        "thunderstorm with heavy rain":1.105,
        "thunderstorm with light drizzle":1.041,
        "thunderstorm with drizzle":1.041,
        "thunderstorm with heavy drizzle":1.105,
        "heavy intensity drizzle":1.041,
        "drizzle rain":1.041,
        "heavy intensity drizzle rain":1.041,
        "shower rain and drizzle":1.041,
        "heavy shower rain and drizzle":1.105,
        "shower drizzle":1.041,
        "light rain":1.041,
        "moderate rain":1.041,
        "heavy intensity rain":1.105,
        "very heavy rain":1.105,
        "extreme rain":1.105,
        "freezing rain":1.105,
        "light intensity shower rain":1.041,
        "shower rain":1.041,
        "heavy intensity shower rain":1.105,
        "ragged shower rain":1.041,
        "light snow":1.195,
        "snow":1.195,
        "heavy snow":1.986,
        "sleet":1.195,
        "light shower sleet":1.195,
        "shower sleet":1.195,
        "light rain and snow":1.195,
        "rain and snow":1.195,
        "light shower snow":1.195,
        "shower snow":1.195,
        "heavy shower snow":1.986
    }
    timeAMRush = {
        "thunderstorm with light rain":1.288,
        "thunderstorm with rain":1.288,
        "thunderstorm with heavy rain":1.655,
        "thunderstorm with light drizzle":1.288,
        "thunderstorm with drizzle":1.288,
        "thunderstorm with heavy drizzle":1.655,
        "heavy intensity drizzle":1.288,
        "drizzle rain":1.288,
        "heavy intensity drizzle rain":1.288,
        "shower rain and drizzle":1.288,
        "heavy shower rain and drizzle":1.655,
        "shower drizzle":1.288,
        "light rain":1.288,
        "moderate rain":1.288,
        "heavy intensity rain":1.655,
        "very heavy rain":1.655,
        "extreme rain":1.655,
        "freezing rain":1.655,
        "light intensity shower rain":1.288,
        "shower rain":1.288,
        "heavy intensity shower rain":1.655,
        "ragged shower rain":1.288,
        "light snow":1.4355,
        "snow":1.4355,
        "heavy snow":2.5075,
        "sleet":1.4355,
        "light shower sleet":1.4355,
        "shower sleet":1.4355,
        "light rain and snow":1.4355,
        "rain and snow":1.4355,
        "light shower snow":1.4355,
        "shower snow":1.4355,
        "heavy shower snow":2.5075
    }
    timeMidday = {
        "thunderstorm with light rain":1.07,
        "thunderstorm with rain":1.07,
        "thunderstorm with heavy rain":1.255,
        "thunderstorm with light drizzle":1.07,
        "thunderstorm with drizzle":1.07,
        "thunderstorm with heavy drizzle":1.255,
        "heavy intensity drizzle":1.07,
        "drizzle rain":1.07,
        "heavy intensity drizzle rain":1.07,
        "shower rain and drizzle":1.07,
        "heavy shower rain and drizzle":1.255,
        "shower drizzle":1.07,
        "light rain":1.07,
        "moderate rain":1.07,
        "heavy intensity rain":1.255,
        "very heavy rain":1.255,
        "extreme rain":1.255,
        "freezing rain":1.255,
        "light intensity shower rain":1.07,
        "shower rain":1.07,
        "heavy intensity shower rain":1.255,
        "ragged shower rain":1.07,
        "light snow":1.136,
        "snow":1.136,
        "heavy snow":1.59,
        "sleet":1.136,
        "light shower sleet":1.136,
        "shower sleet":1.136,
        "light rain and snow":1.136,
        "rain and snow":1.136,
        "light shower snow":1.136,
        "shower snow":1.136,
        "heavy shower snow":1.59
    }
    timePMRush = {
        "thunderstorm with light rain":1.1445,
        "thunderstorm with rain":1.1445,
        "thunderstorm with heavy rain":1.3255,
        "thunderstorm with light drizzle":1.1445,
        "thunderstorm with drizzle":1.1445,
        "thunderstorm with heavy drizzle":1.3255,
        "heavy intensity drizzle":1.1445,
        "drizzle rain":1.1445,
        "heavy intensity drizzle rain":1.1445,
        "shower rain and drizzle":1.1445,
        "heavy shower rain and drizzle":1.3255,
        "shower drizzle":1.1445,
        "light rain":1.1445,
        "moderate rain":1.1445,
        "heavy intensity rain":1.3255,
        "very heavy rain":1.3255,
        "extreme rain":1.3255,
        "freezing rain":1.3255,
        "light intensity shower rain":1.1445,
        "shower rain":1.1445,
        "heavy intensity shower rain":1.3255,
        "ragged shower rain":1.1445,
        "light snow":1.2025,
        "snow":1.2025,
        "heavy snow":2.024,
        "sleet":1.2025,
        "light shower sleet":1.2025,
        "shower sleet":1.2025,
        "light rain and snow":1.2025,
        "rain and snow":1.2025,
        "light shower snow":1.2025,
        "shower snow":1.2025,
        "heavy shower snow":2.024
    }

    #Return correct weight based on current time
    time_now_min = (datetime.now().hour*60)+datetime.now().minute
    if time_now_min < 385: #12:00AM-6:24AM
        return timeOvernight.get(weatherDesc, 1)
    elif time_now_min >=385 and time_now_min < 545: #6:25AM-9:04AM
        return timeAMRush.get(weatherDesc, 1)
    elif time_now_min >=545 and time_now_min < 890: #9:05AM-2:49PM
        return timeMidday.get(weatherDesc, 1)
    elif time_now_min >=890 and time_now_min < 1120: #2:50PM-6:39PM
        return timePMRush.get(weatherDesc, 1)
    else: #6:40PM-11:59PM
        return timeOvernight.get(weatherDesc, 1)

# AJAX call to return the closest traffic camera
# Input some coordinates, return the closest camera to display
def get_closest_camera(request):
    long = float(request.GET.get('long'))
    lat = float(request.GET.get('lat'))

    # QuerySet to pandas df
    df_cams = pd.DataFrame(list(CameraSet.objects.all().values('latitude', 'longitude', 'cam_url')))

    # Get distances 
    df_cams['distance'] = np.sqrt((long - df_cams['longitude'])**2 + (lat - df_cams['latitude'])**2)

    # Get minimum distance camera
    url = df_cams[df_cams.distance == df_cams.distance.min()]['cam_url']
    print("\n\nURL: " + url.iloc[0])

    data = {'url' : url.iloc[0]}

    return JsonResponse(data)


# ___________________________________________________________________________

# TRAVEL ADVISOR FUNCTIONS

keys = ["10b5713f47msh8e356e02c8122cap171f1ajsn29df68c2ef56", "51f7bea90emsh79dc283e2320d96p136222jsn5a652cb43d5b"]

def get_city(lat, lng):

    api_key = "AIzaSyCxcxARvS-64ciU9FmsanvB5h3WASLQxVE"
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}"
    response = requests.get(endpoint)
    data = response.json()
    city = data["results"][0]["address_components"][2]["long_name"]
    return city

def get_location_id(request):

    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)

    city_name = get_city(lat,lng)

    success = False

    for key in keys:

        # API request options
        options = {
            "method": "GET",
            "url": "https://travel-advisor.p.rapidapi.com/locations/search",
            "params": {
                "query": city_name,
                "limit": "50",
                "offset": "0",
                "units": "km",
                "currency": "USD",
                "sort": "relevance",
                "lang": "en_US"
            },
            "headers": {
                "X-RapidAPI-Key": key,
                "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
            }
        }

        try: 

            # Send the API request
            response = requests.request(**options)

            # Parse the API response
            data = response.json()
            for result in data["data"]:
                if result["result_type"] == "geos":
                    success = True
                    print(result["result_object"]["location_id"])
                    return result["result_object"]["location_id"]
        
        except:
            continue
    
    # if none of the keys work, return none 
    
    if not success:
        return None

# Functions to get hotels, attractions, and restaurants based on a given lat/long

def get_hotels(request):
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)

    if lat is None or lng is None:
        return JsonResponse({"error": "Latitude and longitude are required."})

    # Get location_id
    location_id = get_location_id(request)

    hotels = []

    for key in keys:
        options = {
            "method": "GET",
            "url": "https://travel-advisor.p.rapidapi.com/hotels/list",
            "params": {
                "location_id": location_id,
                "adults": "1",
                "rooms": "1",
                "nights": "2",
                "offset": "0",
                "currency": "USD",
                "order": "asc",
                "limit": "10",
                "sort": "recommended",
                "lang": "en_US"
            },
            "headers": {
                "X-RapidAPI-Key": key,
                "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
            }
        }

        try:
            response = requests.request(**options)
            data = response.json()
            hotels = data.get("data", [])

            if hotels:
                break

        except:
            continue

    # Extract the relevant information from the response
    hotel_info = []
    for hotel in hotels:
        hotel_info.append({
            "name": hotel.get("name", ""),
            "latitude": hotel.get("latitude", ""),
            "longitude": hotel.get("longitude", ""),
            "rating": hotel.get("rating", ""),
            "price": hotel.get("price", ""),
            "url": hotel.get("desktop_contacts", [{"value": ""}])[0]["value"]
        })

    return JsonResponse({"hotels": hotel_info})


def get_attractions(request):
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)

    if lat is None or lng is None:
        return JsonResponse({"error": "Latitude and longitude are required."})

    # Get location_id
    location_id = get_location_id(request)

    attractions = []

    for key in keys:
        options = {
            "method": "GET",
            "url": "https://travel-advisor.p.rapidapi.com/attractions/list",
            "params": {
                "location_id": location_id,
                "currency": "USD",
                "limit": "10",
                "lang": "en_US",
                "lunit": "km",
                "sort": "recommended",
            },
            "headers": {
                "X-RapidAPI-Key": key,
                "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
            }
        }

        try:
            response = requests.request(**options)
            data = response.json()
            attractions = data.get("data", [])

            if attractions:
                break

        except:
            continue

    if not attractions:
        return JsonResponse({"error": "No attractions are available at this time."})

    # Extract the relevant information from the response
    attraction_info = []
    for attraction in attractions:
        attraction_info.append({
            "name": attraction.get("name", ""),
            "address": attraction.get("address", ""),
            "rating": attraction.get("rating", ""),
            "latitude": attraction.get("latitude", ""),
            "longitude": attraction.get("longitude", ""),
            "web_url": attraction.get("web_url", "")
        })

    return JsonResponse({"attractions": attraction_info})


def get_restaurants(request):
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)

    if lat is None or lng is None:
        return JsonResponse({"error": "Latitude and longitude are required."})

    # Get location_id
    location_id = get_location_id(request)

    restaurants = []

    for key in keys:
        options = {
            "method": "GET",
            "url": "https://travel-advisor.p.rapidapi.com/restaurants/list",
            "params": {
                "location_id": location_id,
                "restaurant_tagcategory": "10591",
                "restaurant_tagcategory_standalone": "10591",
                "currency": "USD",
                "lunit": "km",
                "limit": "10",
                "open_now": "false",
                "lang": "en_US"
            },
            "headers": {
                "X-RapidAPI-Key": key,
                "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
            }
        }

        try:
            response = requests.request(**options)
            data = response.json()
            restaurants = data.get("data", [])

            if restaurants:
                break

        except:
            continue

    if not restaurants:
        return JsonResponse({"error": "No restaurants are available at this time."})

    # Extract the relevant information from the response
    restaurant_info = []
    for restaurant in restaurants:
        restaurant_info.append({
            "name": restaurant.get("name", ""),
            "address": restaurant.get("address", ""),
            "rating": restaurant.get("rating", ""),
            "price": restaurant.get("price", ""),
                "latitude": restaurant.get("latitude", ""),
                "longitude": restaurant.get("longitude", ""),
                "web_url": restaurant.get("web_url", "")
            })

    return JsonResponse({"restaurants": restaurant_info})

def test_get_hotels(request):

    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)

    if lat is None or lng is None:
        return JsonResponse({"error": "Latitude and longitude are required."})

    # Get location ID
    location_id = get_location_id(request)
    if location_id is None:
        return {"error": "Could not find location ID."}

    # API request options
    options = {
        "method": "GET",
        "url": "https://travel-advisor.p.rapidapi.com/hotels/list",
        "params": {
            "location_id": location_id,
            "adults": "1",
            "rooms": "1",
            "nights": "2",
            "offset": "0",
            "currency": "USD",
            "order": "asc",
            "limit": "30",
            "sort": "recommended",
            "lang": "en_US"
        },
        "headers": {
            "X-RapidAPI-Key": "b94d8c478fmsh085e055daa551fap1d1c6djsn3b6ee8bf2657",
            "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
        }
    }

    # Send the API request
    response = requests.request(**options)

    # Parse the API response
    data = response.json()
    hotels = data.get("data", [])

    # Extract the relevant information from the response
    hotel_info = []
    for hotel in hotels:
        hotel_info.append({
            "name": hotel.get("name", ""),
            "address": hotel.get("address", ""),
            "rating": hotel.get("rating", ""),
            "price": hotel.get("price", "")
        })

    return JsonResponse({"hotels": hotel_info})

def test_get_attractions(request):

    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)

    if lat is None or lng is None:
        return JsonResponse({"error": "Latitude and longitude are required."})

    # Get location ID
    location_id = get_location_id(request)
    if location_id is None:
        return JsonResponse({"error": "Could not find location ID."})

    # API request options
    options = {
        "method": "GET",
        "url": "https://travel-advisor.p.rapidapi.com/attractions/list",
        "params": {
            "location_id": location_id,
            "currency": "USD",
            "lang": "en_US",
            "lunit": "km",
            "sort": "recommended"
        },
        "headers": {
            "X-RapidAPI-Key": "b94d8c478fmsh085e055daa551fap1d1c6djsn3b6ee8bf2657",
            "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
        }
    }

    # Send the API request
    response = requests.request(**options)

    # Parse the API response
    data = response.json()
    attractions = data.get("data", [])

    # Extract the relevant information from the response
    attraction_info = []
    for attraction in attractions:
        attraction_info.append({
            "name": attraction.get("name", ""),
            "address": attraction.get("address", ""),
            "rating": attraction.get("rating", ""),
            "description": attraction.get("description", "")
        })

    return JsonResponse({"attractions": attraction_info})


def test_get_restaurants(request):

    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)

    if lat is None or lng is None:
        return JsonResponse({"error": "Latitude and longitude are required."})

    # Get location ID
    location_id = get_location_id(request)
    if location_id is None:
        return JsonResponse({"error": "Could not find location ID."})

    # API request options
    options = {
        "method": "GET",
        "url": "https://travel-advisor.p.rapidapi.com/restaurants/list",
        "params": {
            "location_id": location_id,
            "restaurant_tagcategory": "10591",
            "restaurant_tagcategory_standalone": "10591",
            "currency": "USD",
            "lunit": "km",
            "limit": "30",
            "open_now": "false",
            "lang": "en_US"
        },
        "headers": {
            "X-RapidAPI-Key": "b94d8c478fmsh085e055daa551fap1d1c6djsn3b6ee8bf2657",
            "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
        }
    }

    # Send the API request
    response = requests.request(**options)

    # Parse the API response
    data = response.json()
    restaurants = data.get("data", [])

    # Extract the relevant information from the response
    restaurant_info = []
    for restaurant in restaurants:
        restaurant_info.append({
            "name": restaurant.get("name", ""),
            "address": restaurant.get("address", ""),
            "rating": restaurant.get("rating", ""),
            "cuisine": restaurant.get("cuisine", ""),
            "price_range": restaurant.get("price_range", "")
        })

    return JsonResponse({"restaurants": restaurant_info})

def test_get_location_id(request):
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)

    if lat is None or lng is None:
        return JsonResponse({"error": "Latitude and longitude are required."})

    location_id = get_location_id(request)
    return JsonResponse({"location_id": location_id})

