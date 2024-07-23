from django import forms
from .models import Movie,Screening
from dataclasses import field

class CreateMovie(forms.ModelForm):
    movie_startTime = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M'],  # Adjust this format to match the input format you expect
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'  # Add any additional classes here
        })
    )
    released_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Movie
        fields= '__all__'

class CreateScreening(forms.ModelForm):
    start_time = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M'],  # Adjust this format to match the input format you expect
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'  # Add any additional classes here
        })
    )
    class Meta:
        model = Screening
        fields= '__all__'