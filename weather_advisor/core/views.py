from django.shortcuts import render
from django.conf import settings
from .forms import WeatherAdvisorForm
import requests, json


def weather_recommendation(code_weather):
    if 200 <= code_weather <= 232:
        return "Сегодня гроза, не забудь зонт и не лазь по деревьям!"
    elif 300 <= code_weather <= 321:
        return "Сегодня моросит, надевай свитер потеплее и еще лучше, оставайяся дома!"
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


def main_view(request):
    if request.method == 'POST':
        form = WeatherAdvisorForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            region = form.cleaned_data['region']
            city = form.cleaned_data['city']

            url = 'https://api.openweathermap.org/data/2.5/weather'

            parameters = {
                'q': city,
                'appid': settings.OPENWEATHERMAP_API_KEY,
                'lang': 'ru',
                'units': 'metric'
            }

            try:
                response = requests.get(url, parameters)
            except requests.ConnectionError:
                return render(request, 'index.html', {'form': form, 'error': {'code': 0,
                                                                              'message': 'Ошибка сети, '
                                                                                         'проверьте подключение '
                                                                                         'к интернет'}})
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

            return render(request, 'index.html', {'form': form,
                                                  'weather': weather,
                                                  'icon_code': icon_code,
                                                  'temp': temp,
                                                  'feels_like': feels_like,
                                                  'temp_min': temp_min,
                                                  'temp_max': temp_max,
                                                  'humidity': humidity,
                                                  'recommendation': recommendation
                                                  })
        return render(request, 'index.html',
                      {'form': form, 'error': {'code': answer['cod'], 'message': answer['message']}})

    form = WeatherAdvisorForm()
    return render(request, 'index.html', {'form': form})
