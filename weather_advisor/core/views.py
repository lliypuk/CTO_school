from django.shortcuts import render
from django.conf import settings
from .forms import WeatherAdvisorForm
import requests, json


def weather_recommendation(code_weather):
    if 200 <= code_weather <= 232:
        return "Сегодня гроза, не забудь зонт и не лазь по деревьям!"
    elif 300 <= code_weather <= 321:
        return "Сегодня моросит, надевай свитер потеплее и еще лучше, оставайся дома!"
    elif 500 <= code_weather <= 531:
        return "Дождь! Зонт и сапоги - набор победителя!"
    elif 600 <= code_weather <= 622:
        return "Надевай теплые ботинки и крутку, сегодня снег и " \
               "лучше не пользоваться машиной, если он все еще на летней резине"
    elif 700 <= code_weather <= 781:
        return "Сегодня атмосферные явления, может быть плохая видимость, очкие не помешают!"
    elif code_weather == 800:
        return "Чистое небо над головой! Что может быть прекраснее? Но одевайся по температуре!"
    elif 800 < code_weather <= 804:
        return "Сегодня облачно, не забудь зонт"


def get_coordinate_by_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    parameters = {
        'address': address,
        'key': settings.GOOGLE_API_KEY,
        'language': 'ru'
    }
    try:
        response = requests.get(url, parameters)
        if response.status_code == 200:
            answer = json.loads(response.text)
            if answer['status'] == 'ZERO_RESULTS':
                return {'error': f'Адрес {address} не найдет!'}

            coordinates = []
            for result in answer['results']:
                formatted_address = result['formatted_address']
                lat = result['geometry']['location']['lat']
                lon = result['geometry']['location']['lng']
                coordinates.append({'lat': lat, 'lon': lon, 'formatted_address': formatted_address})
            return coordinates
        return {'error': 'Ошибка превращения адреса в координаты'}
    except requests.ConnectionError:
        return {'error': 'Ошибка соединения с интернет, не могу адрес превратить в координаты'}


def get_weather_by_coordinates(coordinate):
    url = 'https://api.openweathermap.org/data/2.5/weather'

    parameters = {
        'lat': coordinate['lat'],
        'lon': coordinate['lon'],
        'appid': settings.OPENWEATHERMAP_API_KEY,
        'lang': 'ru',
        'units': 'metric'
    }

    try:
        response = requests.get(url, parameters)
        answer = json.loads(response.text)

        if response.status_code == 200:
            weather = answer['weather'][0]['description']
            id_weather = answer['weather'][0]['id']
            icon_code = answer['weather'][0]['icon']
            recommendation = weather_recommendation(id_weather)
            temp = answer['main']['temp']
            feels_like = answer['main']['feels_like']
            temp_min = answer['main']['temp_min']
            temp_max = answer['main']['temp_max']
            humidity = answer['main']['humidity']
            wind_speed = answer['wind']['speed']

            return {
                'weather': weather,
                'icon_code': icon_code,
                'temp': temp,
                'feels_like': feels_like,
                'temp_min': temp_min,
                'temp_max': temp_max,
                'humidity': humidity,
                'recommendation': recommendation,
                'wind_speed': wind_speed,
                'formatted_address': coordinate['formatted_address']
            }
    except requests.ConnectionError:
        return {"error": 'Ошибка сети, '
                         'проверьте подключение '
                         'к интернет'}
    return {"error": 'Ошибка получения погоды с сервера'}


def main_view(request):
    if request.method == 'POST':
        form = WeatherAdvisorForm(request.POST)
        if form.is_valid():
            address = ','.join(filter(lambda x: x, (form.cleaned_data['country'],
                                                    form.cleaned_data['region'],
                                                    form.cleaned_data['city'])))

            coordinates = get_coordinate_by_address(address)

            if 'error' in coordinates:
                return render(request, 'index.html', {'form': form, 'error': {
                    'message': coordinates['error']}})

            weather_data = []
            for coordinate in coordinates:
                weather = get_weather_by_coordinates(coordinate)
                if 'error' in weather:
                    return render(request, 'index.html', {'form': form, 'error': {
                        'message': weather_data['error']}})
                weather_data.append(weather)
            return render(request, 'index.html', {'form': form, 'weather_data': weather_data})
        return render(request, 'index.html', {'form': form, 'error': 'Ошибка валидации формы'})
    form = WeatherAdvisorForm()
    return render(request, 'index.html', {'form': form})
