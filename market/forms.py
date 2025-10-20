from django import forms
from .models import ContactForm, Car

class ContactFormClass(forms.ModelForm):
    class Meta:
        model = ContactForm
        fields = ['name', 'phone', 'model', 'message']
    
    # Custom field for selecting a car model
    model = forms.CharField(widget=forms.Select)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate the 'model' field with available cars
        self.fields['model'].widget.choices = [
            (car.slug, car.name_en) for car in Car.objects.all()
        ]
