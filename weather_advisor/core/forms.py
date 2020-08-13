from django import forms


class WeatherAdvisorForm(forms.Form):
    country = forms.CharField(max_length=100, label='Страна', required=False)
    region = forms.CharField(max_length=100, label='Регион, Край', required=False)
    city = forms.CharField(max_length=100, label='Город')
