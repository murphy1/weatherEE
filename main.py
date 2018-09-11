# this program will get the weather from open weather map. With 3 hour forecasts
import requests
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import logging

logging.basicConfig(filename="weatherEE_Log.txt", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("NEW ----- Start of program")

owm_api_key = ""
dark_sky_api_key = ""
acc_api_key = ""


# Accuweather API
def accuweather_api():
    try:
        acc_dublin = requests.get("http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/207931?apikey=%s" % acc_api_key)
        acc_dublin.raise_for_status()
        acc_json = json.loads(acc_dublin.text)
        return acc_json
    except Exception as err:
        logging.warning("Problem with loading the Accuweather API")
        logging.warning(str(err))


# DateTime
# IconPhrase
# Temperature (dict with value 'Value')

def accuweather_api_hourly():
    acc_weather = []

    # 50 calls per day !!!!!!!!!!
    try:
        for hour in accuweather_api()[:50:3]:
            acc_weather_hourly = list()
            time_stamp = hour["DateTime"]
            # get rid of the letters in the date time to match the other API's
            letterbegone = time_stamp.replace("T", " ")
            letterbegone1 = letterbegone.replace("+01:00", "")
            acc_weather_hourly.append("Time: "+letterbegone1)
            acc_weather_hourly.append("Description: "+hour["IconPhrase"])
            # convert from Fahrenheit to Celcius
            celcius = round(((hour["Temperature"]["Value"]) - 32) * 0.5556)
            acc_weather_hourly.append("Temp: "+str(celcius))
            acc_weather.append(acc_weather_hourly)
    except Exception as err:
        logging.warning("Error with the accuweather hourly for loop")
        logging.warning("Exception: "+str(err))

    return acc_weather
    

# 1000 calls per day

def dark_sky_api():
    try:
        dsky_dublin = requests.get("https://api.darksky.net/forecast/%s/53.3498,6.2603" % dark_sky_api_key)
        dsky_dublin.raise_for_status()
        dsky_json = json.loads(dsky_dublin.text)
        return dsky_json
    except Exception as err:
        logging.warning("Problem with the Dark Sky API")
        logging.warning(str(err))

def dark_sky_api_hourly():
    dsky_weather = []

    # time
    # description
    # temp
    # humidity
    try:
        for k, v in dark_sky_api().items():
            if k == "hourly":
                # Dark sky API provides its data hourly. So we need to skip hours to get the 3 hour forecast
                for time in (v["data"])[1:26:3]:
                    dsky_weather_hourly = list()
                    # convert the UNIX timestamp in a human readable time
                    unix_time_stamp = (time["time"])
                    real_time = (datetime.fromtimestamp(unix_time_stamp).strftime("%Y-%m-%d %H:%M:%S"))
                    dsky_weather_hourly.append("Time: "+str(real_time))
                    dsky_weather_hourly.append("Description: "+time["summary"])
                    # convert from fahrenheit to celcius
                    celcius = round((((time["temperature"]) - 32) * 0.5556))
                    dsky_weather_hourly.append("Temp: "+str(celcius))
                    # remove the decimal point from the humidity
                    humidity = (str(time["humidity"])).split(".")
                    dsky_weather_hourly.append("Humidity: "+humidity[1])
                    dsky_weather.append(dsky_weather_hourly)
    except Exception as err:
        logging.warning("Error with the Dark Sky API hourly for loop")
        logging.warn("Exception: "+str(err))

    return dsky_weather

def open_weather_api():
    # 60 calls per min
    try:
        owm_dublin = requests.get("http://api.openweathermap.org/data/2.5/forecast?id=2964574&APPID=%s" % owm_api_key)
        owm_dublin.raise_for_status()
        owm_json = json.loads(owm_dublin.text)
        return owm_json
    except Exception as err:
        logging.warning("Error with the Open Weather Map API")
        logging.warning(str(err))

def open_weather_api_hourly():
    owm_weather = []
    # key["dt_txt"] = gets the time
    # key["main"] = includes temp
    # key["weather"] = gets the description
    try:

        for k, v in open_weather_api().items():
            if k == "list":
                for key in v[:9]:
                    owm_weather_hour = list()
                    owm_weather_hour.append("Time: "+key["dt_txt"])
                    for desc in key["weather"]:
                        owm_weather_hour.append("Description: "+desc["description"])
                    # -273 to convert from Kelvin to Celcius
                    owm_weather_hour.append("Temp: "+str(round((key["main"]["temp"])-273)))
                    owm_weather_hour.append("Humidity: "+str(key["main"]["humidity"]))
                    owm_weather.append(owm_weather_hour)
    except Exception as err:
        logging.warning("Error with the Open Weather API hourly for loop")
        logging.warning(str(err))

    return owm_weather


def y_axis_asc_temp():
    # this method will set the y axis numbers for the temp
    try:
        plot_data_for_temp = []
        for i in range(-5, 30, 2):
            plot_data_for_temp.append(i)
        return plot_data_for_temp
    except Exception as err:
        logging.debug("Problem with the y axis temp numbers")
        logging.debug(str(err))

def y_axis_asc_humidity():
    # this method will set the y axis numbers for Humidity
    try:
        plot_data_for_humidity = []
        for i in range(0, 101, 5):
            plot_data_for_humidity.append(float(i))
        return plot_data_for_humidity
    except Exception as err:
        logging.debug("Problem with the humidity ascending number method")
        logging.debug(str(err))


# plotting Open Weather Map results with Matplotlib


# get the Time, Temp and Humidity for the Axes
time_list = []
temp_list = []
humidity_list = []
for lst in open_weather_api_hourly():
    time = lst[0].split(" ")
    time_list.append(time[2])
    temp = lst[2].split(" ")
    temp_list.append(temp[1])
    humidity = lst[3].split(" ")
    humidity_list.append(humidity[1])

del time_list[-1]
del temp_list[-1]
# change the list to floats for an ordered list
float_temp_list_for_graph = [float(i) for i in temp_list]
del humidity_list[-1]
float_humidity_list_for_graph = [float(i) for i in humidity_list]

# OWM Time and Temp
def open_weather_map_temp():
    try:
        plt.plot(time_list, float_temp_list_for_graph, color="red")
        plt.title("Open Weather Map Temperature")
        plt.xlabel("Time")
        plt.gcf().autofmt_xdate()
        plt.ylabel("Temperature")
        plt.yticks(y_axis_asc_temp())
        plt.grid(True)
        plt.show()
    except Exception as err:
        logging.info("Problem with the OWM temp graph")
        logging.info(str(err))

# OWN Time and Humidity
def open_weather_map_humidity():
    try:
        plt.plot(time_list, float_humidity_list_for_graph, color="red")
        plt.title("Open Weather Map Humidity")
        plt.xlabel("Time")
        plt.gcf().autofmt_xdate()
        plt.ylabel("Humidity")
        plt.yticks(y_axis_asc_humidity())
        plt.grid(True)
        plt.show()
    except Exception as err:
        logging.info("Problem with the OWM humidity graph")
        logging.info(str(err))


# Plotting Accuweather with Matplotlib
acc_time_for_graph = []
acc_temp_for_graph = []
for key in accuweather_api_hourly():
    acc_time = key[0].split(" ")
    acc_time_for_graph.append(acc_time[2])
    acc_temp = key[2].split(" ")
    acc_temp_for_graph.append(acc_temp[1])

# convert stings to floats for ascending correct y axis
float_temp_for_graph = [float(i) for i in acc_temp_for_graph]

def accuweather_temp():
    try:
        plt.plot(acc_time_for_graph, float_temp_for_graph, color="red")
        plt.title("Accuweather Temperature")
        plt.yticks(y_axis_asc_temp())
        plt.xlabel("Time")
        plt.ylabel("Temperature:")
        plt.grid(True)
        plt.show()
    except Exception as err:
        logging.info("Problem with the Accuweather Temp Graph")
        logging.info(str(err))

# plotting Dark Sky API with Matplotlib

# get the Time, Temp and Humidity for the axes
dsky_time_for_graph = []
dsky_temp_for_graph = []
dsky_humidity_for_graph = []
for key in dark_sky_api_hourly():
    dsky_time = key[0].split(" ")
    dsky_time_for_graph.append(dsky_time[2])
    dsky_temp = key[2].split(" ")
    dsky_temp_for_graph .append(dsky_temp[1])
    dsky_humidity = key[3].split(" ")
    dsky_humidity_for_graph.append(dsky_humidity[1])

# convert temp from string to floats for an ascending y-axis
float_dsky_temp_for_graph = [float(i) for i in dsky_temp_for_graph]

# convert humidity from string to floats for an ascending y-axis
float_dsky_humidity_for_graph = [float(i) for i in dsky_humidity_for_graph]

# remove a variable off the end of each list for a nicer graph
del dsky_time_for_graph[-1]
del float_dsky_temp_for_graph[-1]
del float_dsky_humidity_for_graph[-1]


# plot the graph for temp
def dark_sky_temp():
    try:
        plt.plot(dsky_time_for_graph, float_dsky_temp_for_graph, color="red")
        plt.title("Dark Sky Temperature")
        plt.xlabel("Time")
        plt.gcf().autofmt_xdate()
        plt.ylabel("Temperature")
        plt.yticks(y_axis_asc_temp())
        plt.grid(True)
        plt.show()
    except Exception as err:
        logging.info("Problem with the Dark Sky temp graph")
        logging.info(str(err))

# plot the graph for humidity
def dark_sky_humidity():
    try:
        plt.plot(dsky_time_for_graph, float_dsky_humidity_for_graph, color="red")
        plt.title("Dark Sky Humidity")
        plt.xlabel("Time")
        plt.gcf().autofmt_xdate()
        plt.ylabel("Humidity")
        plt.yticks(y_axis_asc_humidity())
        plt.grid(True)
        plt.show()
    except Exception as err:
        logging.info("Problem with the Dark Sky humidity graph")
        logging.info(str(err))

# get average temp per hour and plot (d sky and owm)
def average_temp():
    try:
        avg_temps = []
        count_avg_temp = 0
        for owm_num in float_temp_list_for_graph:
            avg_temps.append((owm_num + float_dsky_temp_for_graph[count_avg_temp]) / 2)
            count_avg_temp += 1

        plt.plot(dsky_time_for_graph, avg_temps, color="red")
        plt.title("Average Temperature (Dark Sky and OWM)")
        plt.xlabel("Time")
        plt.gcf().autofmt_xdate()
        plt.ylabel("Temperature")
        plt.yticks(y_axis_asc_temp())
        plt.grid(True)
        plt.show()
    except Exception as err:
        logging.info("Problem with the average temp graph")
        logging.info(str(err))

# get average humidity per hour and plot (d sky and owm)
def average_humidity():
    try:
        avg_humidity = []
        count_avg_humidity = 0
        for owm_num in float_humidity_list_for_graph:
            avg_humidity.append((owm_num + float_dsky_humidity_for_graph[count_avg_humidity]) / 2)
            count_avg_humidity += 1

        plt.plot(dsky_time_for_graph, avg_humidity, color="red")
        plt.title("Average Humidity (Dark Sky and OWM)")
        plt.xlabel("Time")
        plt.gcf().autofmt_xdate()
        plt.ylabel("Humidity")
        plt.yticks(y_axis_asc_humidity())
        plt.grid(True)
        plt.show()
    except Exception as err:
        logging.info("Problem with the average humidity graph")
        logging.info(str(err))

average_temp()
logging.debug("END ----- End of program")
