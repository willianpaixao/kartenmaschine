from django import forms

class ExportForm(forms.Form):
    grid_front = forms.BooleanField()
    grid_rear = forms.BooleanField()
    flip = forms.BooleanField()

