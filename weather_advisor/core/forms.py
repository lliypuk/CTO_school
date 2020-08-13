from django import forms


class WeatherAdvisorForm(forms.Form):
    country = forms.CharField(max_length=100, label='Страна')
    region = forms.CharField(max_length=100, label='Регион, Край')
    city = forms.CharField(max_length=100, label='Город')

