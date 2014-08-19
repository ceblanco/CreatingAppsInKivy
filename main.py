import json
from kivy.app import App
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
from kivy.uix.listview import ListItemButton
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty

def locations_args_converter(index, data_item):
    city, country = data_item
    return {'location': (city, country)}

class LocationButton(ListItemButton):
    location = ListProperty()

class WeatherRoot(BoxLayout):
    current_weather = ObjectProperty()
    locations = ObjectProperty()

    def show_current_weather(self, location=None):
        self.clear_widgets()

        if self.current_weather is None:
            self.current_weather = CurrentWeather()
        if self.locations is None:
            self.locations = Factory.Locations()

        if location is not None:
            self.current_weather.location = location
            if location not in self.locations.locations_list.adapter.data:
                self.locations.locations_list.adapter.data.append(location)
                self.locations.locations_list._trigger_reset_populate()

        self.current_weather.update_weather()
        self.add_widget(self.current_weather)

    def show_add_location_form(self):
        self.clear_widgets()
        self.add_widget(AddLocationForm())

    def show_locations(self):
        self.clear_widgets()
        self.add_widget(self.locations)

class LocationButton(ListItemButton):
    location = ListProperty()

class AddLocationForm(BoxLayout):
    search_input = ObjectProperty()
    search_results = ObjectProperty()

    def search_location(self):
        search_template = "http://api.openweathermap.org/data/2.5/find?q={}&type=like"
        search_url = search_template.format(self.search_input.text)
        request = UrlRequest(search_url, self.found_location)

    def found_location(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        #cities = ["{} ({})".format(d['name'], d['sys']['country']) for d in data['list']]
        cities = [(d['name'], d['sys']['country']) for d in data['list']]
        self.search_results.item_strings = cities

        del self.search_results.adapter.data[:]
        self.search_results.adapter.data.extend(cities)
        self.search_results._trigger_reset_populate()

class CurrentWeather(BoxLayout):
    location = ListProperty(['Long Beach', 'US'])
    conditions = StringProperty()
    conditions_image = ObjectProperty()
    temp = NumericProperty()
    temp_min = NumericProperty()
    temp_max = NumericProperty()

    def update_weather(self):
        weather_template = "http://api.openweathermap.org/data/2.5/weather?q={},{}&units=imperial"
        weather_url = weather_template.format(*self.location)
        request = UrlRequest(weather_url, self.weather_retrieved)

    def weather_retrieved(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        self.conditions = data['weather'][0]['description']
        self.conditions_image = "http://openweathermap.org/img/w/{}.png".format(data['weather'][0]['icon'])
        self.temp = data['main']['temp']
        self.temp_min = data['main']['temp_min']
        self.temp_max = data['main']['temp_max']

class WeatherApp(App):
    def on_pause(self):
        return True

if __name__ == "__main__":
    WeatherApp().run()
