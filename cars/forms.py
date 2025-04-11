from django import forms
from .models import Car, CarImage

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'price', 'year', 'condition', 'mileage', 'location', 'description']

class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ['image']
