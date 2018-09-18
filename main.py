import requests
import json
import logging
from datetime import datetime
import matplotlib.pyplot as plt

logging.basicConfig(filename="weatherEE_Log.txt", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("NEW ----- Start of program")

owm_api_key = ""
dark_sky_api_key = ""
acc_api_key = ""

geocoder_id = ""
geocoder_code = ""


class Weather(object):

    def __init__(self, forecast_location):
        try:

            location = forecast_location
            api_res = requests.get(
                "https://geocoder.api.here.com/6.2/geocode.json?app_id=%s&app_code=%s&searchtext=%s" % (
                geocoder_id, geocoder_code, location))
            api_res.raise_for_status()
            api_json = json.loads(api_res.text)

            lst = api_json["Response"]["View"]
            latitude = (lst[0]["Result"][0]["Location"]["DisplayPosition"]["Latitude"])
            longitude = (lst[0]["Result"][0]["Location"]["DisplayPosition"]["Longitude"])

            self.latlng = str(latitude) + " " + str(longitude)

            # get API request for Dark Sky

            location = self.latlng.split(" ")
            dsky_dublin = requests.get(
                "https://api.darksky.net/forecast/%s/%s,%s" % (dark_sky_api_key, location[0], location[1]))
            dsky_dublin.raise_for_status()
            self.dsky_json = json.loads(dsky_dublin.text)
            dsky_dublin.close()

            # get API request for Open Weather Map

            location = self.latlng.split(" ")
            owm_dublin = requests.get("http://api.openweathermap.org/data/2.5/forecast?lat=%s&lon=%s&APPID=%s" % (
            location[0], location[1], owm_api_key))
            owm_dublin.raise_for_status()
            self.owm_json = json.loads(owm_dublin.text)
            owm_dublin.close()

            # get API request for Accuweather

            acc_dublin = requests.get(
                "http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/207931?apikey=%s" % acc_api_key)
            acc_dublin.raise_for_status()
            self.acc_json = json.loads(acc_dublin.text)
            acc_dublin.close()


        except Exception as err:
            logging.info("Problem with the init method")
            logging.info(str(err))


# Accuweather API -----

    def accuweather_api_hourly(self):
        acc_weather = []
        try:
            for hour in self.acc_json[:50:3]:
                acc_weather_hourly = list()
                time_stamp = hour["DateTime"]
                # get rid of the letters in the date time to match the other API's
                letterbegone = time_stamp.replace("T", " ")
                letterbegone1 = letterbegone.replace("+01:00", "")
                acc_weather_hourly.append("Time: " + letterbegone1)
                acc_weather_hourly.append("Description: " + hour["IconPhrase"])
                # convert from Fahrenheit to Celcius
                celcius = round(((hour["Temperature"]["Value"]) - 32) * 0.5556)
                acc_weather_hourly.append("Temp: " + str(celcius))
                acc_weather.append(acc_weather_hourly)
        except Exception as err:
            logging.warning("Error with the accuweather hourly for loop")
            logging.warning("Exception: " + str(err))

        return acc_weather


# Dark Sky API ----

    def dark_sky_api_hourly(self):
        dsky_weather = []
        try:
            for k, v in self.dsky_json.items():
                if k == "hourly":
                    # Dark sky API provides its data hourly for 48 hours. So we need to skip hours to get the 3 hour forecast
                    for time in (v["data"])[1:27:3]:
                        dsky_weather_hourly = list()
                        # convert the UNIX timestamp in a human readable time
                        unix_time_stamp = (time["time"])
                        real_time = (datetime.fromtimestamp(unix_time_stamp).strftime("%Y-%m-%d %H:%M:%S"))
                        dsky_weather_hourly.append("Time: " + str(real_time))
                        # convert from fahrenheit to celcius
                        celcius = round((((time["temperature"]) - 32) * 0.5556))
                        dsky_weather_hourly.append("Temp: " + str(celcius))
                        # remove the decimal point from the humidity
                        humidity = (str(time["humidity"])).split(".")
                        dsky_weather_hourly.append("Humidity: " + humidity[1])
                        precipitation = (str(time["precipProbability"]))
                        precipitation_split = (str(time["precipProbability"])).split(".")
                        if precipitation.startswith("0.0") or precipitation == "0":
                            dsky_weather_hourly.append("Precipitation Percent: 0")
                        else:
                            dsky_weather_hourly.append("Precipitation Percent: " + precipitation_split[1])
                        dsky_weather.append(dsky_weather_hourly)
        except Exception as err:
            logging.warning("Error with the Dark Sky API hourly for loop")
            logging.warning("Exception: " + str(err))

        return dsky_weather


# Open Weather Map API -----

    def open_weather_api_hourly(self):
        owm_weather = []
        try:
            for k, v in self.owm_json.items():
                if k == "list":
                    for key in v[:9]:
                        owm_weather_hour = list()
                        owm_weather_hour.append("Time: " + key["dt_txt"])
                        # -273 to convert from Kelvin to Celcius
                        owm_weather_hour.append("Temp: " + str(round((key["main"]["temp"]) - 273)))
                        owm_weather_hour.append("Humidity: " + str(key["main"]["humidity"]))
                        if key.get("rain") is None:
                            owm_weather_hour.append("Precipitation: 0")
                        elif (str(key["rain"])) == "{}":
                            owm_weather_hour.append("Precipitation: 0")
                        else:
                            owm_weather_hour.append(str("Precipitation: " + str(key["rain"]["3h"])))
                        owm_weather.append(owm_weather_hour)
        except Exception as err:
            logging.warning("Error with the Open Weather API hourly for loop")
            logging.warning(str(err))

        return owm_weather


# Set the y axis numbers (ticks)


    def y_axis_asc_temp(self):
        # this method will set the y axis numbers for the temp
        try:
            plot_data_for_temp = []
            for i in range(-5, 36, 2):
                plot_data_for_temp.append(i)
            return plot_data_for_temp
        except Exception as err:
            logging.debug("Problem with the y axis temp numbers")
            logging.debug(str(err))

    def y_axis_asc_humidity(self):
        # this method will set the y axis numbers for Humidity
        try:
            plot_data_for_humidity = []
            for i in range(0, 101, 5):
                plot_data_for_humidity.append(float(i))
            return plot_data_for_humidity
        except Exception as err:
            logging.debug("Problem with the humidity ascending number method")
            logging.debug(str(err))

    def y_axis_asc_precipitation(self):
        # this method will set the y axis numbers for the precipitation
        try:
            plot_data_for_precipitation = []
            for i in range(0, 101, 5):
                plot_data_for_precipitation.append(float(i))
            return plot_data_for_precipitation
        except Exception as err:
            logging.debug("Problem with the precipitation ascending number method")
            logging.debug(str(err))


# Plotting Open Weather Map with Matplotlib

    def plot_open_weather_map(self):
        time_list = []
        temp_list = []
        humidity_list = []
        precipitation_list = []

    # add the time, temp and humidity to lists which can be plotted
        for lst in Weather.open_weather_api_hourly(self):
            time = lst[0].split(" ")
            time_list.append(time[2])
            temp = lst[1].split(" ")
            temp_list.append(temp[1])
            humidity = lst[2].split(" ")
            humidity_list.append(humidity[1])
            precipitation = lst[3].split(" ")
            precipitation_list.append(precipitation[1])

        del time_list[-1]
        del temp_list[-1]
        del precipitation_list[-1]
        # change the list to floats for an ordered list
        float_temp_list_for_graph = [float(i) for i in temp_list]
        del humidity_list[-1]
        float_humidity_list_for_graph = [float(i) for i in humidity_list]
        float_precipitation_list_for_graph = [float(i) for i in precipitation_list]

        return time_list, temp_list, humidity_list, precipitation_list, float_temp_list_for_graph, float_humidity_list_for_graph, float_precipitation_list_for_graph

    def open_weather_map_temp(self):
        try:
            plt.plot(Weather.plot_open_weather_map(self)[0], Weather.plot_open_weather_map(self)[4], color="red")
            plt.title("Open Weather Map Temperature")
            plt.xlabel("Time")
            plt.gcf().autofmt_xdate()
            plt.ylabel("Temperature")
            plt.yticks(Weather.y_axis_asc_temp(self))
            plt.grid(True)
            plt.show()
        except Exception as err:
            logging.info("Problem with the OWM temp graph")
            logging.info(str(err))

    def open_weather_map_humidity(self):
        try:
            plt.plot(Weather.plot_open_weather_map(self)[0], Weather.plot_open_weather_map(self)[5], color="red")
            plt.title("Open Weather Map Humidity")
            plt.xlabel("Time")
            plt.gcf().autofmt_xdate()
            plt.ylabel("Humidity")
            plt.yticks(Weather.y_axis_asc_humidity(self))
            plt.grid(True)
            plt.show()
        except Exception as err:
            logging.info("Problem with the OWM humidity graph")
            logging.info(str(err))

    def open_weather_map_precip(self):
        try:
            plt.plot(Weather.plot_open_weather_map(self)[0], Weather.plot_open_weather_map(self)[6], color="red")
            plt.title("Open Weather Map Precipitation")
            plt.xlabel("Time")
            plt.gcf().autofmt_xdate()
            plt.ylabel("Precipitation %")
            plt.yticks(Weather.y_axis_asc_precipitation(self))
            plt.grid(True)
            plt.show()
        except Exception as err:
            logging.info("Problem with the OWM Precipitation graph")
            logging.info(str(err))


# Plotting Accuweather with Matplotlin


    def plot_accuweather(self):
        acc_time_for_graph = []
        acc_temp_for_graph = []
        # add the time and temp to lists so they can be plotted
        for key in Weather.accuweather_api_hourly(self):
            acc_time = key[0].split(" ")
            acc_time_for_graph.append(acc_time[2])
            acc_temp = key[2].split(" ")
            acc_temp_for_graph.append(acc_temp[1])

        # convert stings to floats for ascending correct y axis
        float_temp_for_graph = [float(i) for i in acc_temp_for_graph]

        return acc_time_for_graph, acc_temp_for_graph, float_temp_for_graph

    def accuweather_temp(self):
        try:
            plt.plot(Weather.plot_accuweather(self)[0], Weather.plot_accuweather(self)[2], color="red")
            plt.title("Accuweather Temperature")
            plt.yticks(Weather.y_axis_asc_temp(self))
            plt.xlabel("Time")
            plt.ylabel("Temperature:")
            plt.grid(True)
            plt.show()
        except Exception as err:
            logging.info("Problem with the Accuweather Temp Graph")
            logging.info(str(err))


# Plotting Dark Sky API with matplotlib

    def plot_dark_sky(self):
        dsky_time_for_graph = []
        dsky_temp_for_graph = []
        dsky_humidity_for_graph = []
        dsky_precipitation_for_graph = []
        for key in Weather.dark_sky_api_hourly(self):
            # add the time, temp and humidity to lists so they can be plotted
            dsky_time = key[0].split(" ")
            dsky_time_for_graph.append(dsky_time[2])
            dsky_temp = key[1].split(" ")
            dsky_temp_for_graph.append(dsky_temp[1])
            dsky_humidity = key[2].split(" ")
            dsky_humidity_for_graph.append(dsky_humidity[1])
            dsky_precipitation = key[3].split(" ")
            dsky_precipitation_for_graph.append(dsky_precipitation[2])

        # convert temp from string to floats for an ascending y-axis
        float_dsky_temp_for_graph = [float(i) for i in dsky_temp_for_graph]

        # convert humidity from string to floats for an ascending y-axis
        float_dsky_humidity_for_graph = [float(i) for i in dsky_humidity_for_graph]

        # convert precipitation from string to floats for an ascending y-axis
        float_dsky_precipitation_for_graph = [float(i) for i in dsky_precipitation_for_graph]

        # remove a variable off the end of each list (prevents the plot from going backwards)
        del dsky_time_for_graph[-1]
        del float_dsky_temp_for_graph[-1]
        del float_dsky_humidity_for_graph[-1]
        del float_dsky_precipitation_for_graph[-1]

        return dsky_time_for_graph, float_dsky_temp_for_graph, float_dsky_humidity_for_graph, float_dsky_precipitation_for_graph

    def dark_sky_temp(self):
        try:
            plt.plot(Weather.plot_dark_sky(self)[0], Weather.plot_dark_sky(self)[1], color="red")
            plt.title("Dark Sky Temperature")
            plt.xlabel("Time")
            plt.gcf().autofmt_xdate()
            plt.ylabel("Temperature")
            plt.yticks(Weather.y_axis_asc_temp(self))
            plt.grid(True)
            plt.show()
        except Exception as err:
            logging.info("Problem with the Dark Sky temp graph")
            logging.info(str(err))

    def dark_sky_humidity(self):
        try:
            plt.plot(Weather.plot_dark_sky(self)[0], Weather.plot_dark_sky(self)[2], color="red")
            plt.title("Dark Sky Humidity")
            plt.xlabel("Time")
            plt.gcf().autofmt_xdate()
            plt.ylabel("Humidity")
            plt.yticks(Weather.y_axis_asc_humidity(self))
            plt.grid(True)
            plt.show()
        except Exception as err:
            logging.info("Problem with the Dark Sky humidity graph")
            logging.info(str(err))

    def dark_sky_precip(self):
        try:
            plt.plot(Weather.plot_dark_sky(self)[0], Weather.plot_dark_sky(self)[3], color="red")
            plt.title("Dark Sky Precipitation")
            plt.xlabel("Time")
            plt.gcf().autofmt_xdate()
            plt.ylabel("Precipitation %")
            plt.yticks(Weather.y_axis_asc_precipitation(self))
            plt.grid(True)
            plt.show()
        except Exception as err:
            logging.info("Problem with the Dark Sky Precipitation graph")
            logging.info(str(err))

# Get the averages per hour

    def average_temp(self):
        try:
            avg_temps = []
            count_avg_temp = 0
            for owm_num in Weather.plot_open_weather_map(self)[4]:
                avg_temps.append((owm_num + Weather.plot_dark_sky(self)[1][count_avg_temp]) / 2)
                count_avg_temp += 1

            plt.plot(Weather.plot_dark_sky(self)[0], avg_temps, color="red")
            plt.title("Average Temperature (Dark Sky and OWM)")
            plt.xlabel("Time")
            plt.gcf().autofmt_xdate()
            plt.ylabel("Temperature")
            plt.yticks(Weather.y_axis_asc_temp(self))
            plt.grid(True)
            plt.show()
        except Exception as err:
            logging.info("Problem with the average temp graph")
            logging.info(str(err))

    def average_humidity(self):
        try:
            avg_humidity = []
            count_avg_humidity = 0
            for owm_num in Weather.plot_open_weather_map(self)[5]:
                avg_humidity.append((owm_num + Weather.plot_dark_sky(self)[2][count_avg_humidity]) / 2)
                count_avg_humidity += 1

            plt.plot(Weather.plot_dark_sky(self)[0], avg_humidity, color="red")
            plt.title("Average Humidity (Dark Sky and OWM)")
            plt.xlabel("Time")
            plt.gcf().autofmt_xdate()
            plt.ylabel("Humidity")
            plt.yticks(Weather.y_axis_asc_humidity(self))
            plt.grid(True)
            plt.show()
        except Exception as err:
            logging.info("Problem with the average humidity graph")
            logging.info(str(err))

    def average_precipitation(self):
        try:
            avg_precip = []
            num_count = 0

            for owm_num in Weather.plot_open_weather_map(self)[6]:
                avg_precip.append((owm_num + Weather.plot_dark_sky(self)[3][num_count]) / 2)
                num_count += 1

            plt.plot(Weather.plot_dark_sky(self)[0], avg_precip, color="red")
            plt.title("Average Precipitation (Dark Sky and OWM)")
            plt.xlabel("Time")
            plt.gcf().autofmt_xdate()
            plt.ylabel("Precipitation")
            plt.yticks(Weather.y_axis_asc_precipitation(self))
            plt.grid(True)
            plt.show()

        except Exception as err:
            logging.info("Problem with the average precipitation")
            logging.info(str(err))


logging.debug("END ----- End of program")
