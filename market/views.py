from __future__ import annotations

from django.shortcuts import render, redirect

from .content import build_copy
from .models import Car, ContactForm
from .forms import ContactFormClass


from django.shortcuts import render, redirect
from .models import Car, ContactForm
from .forms import ContactFormClass

def home(request):
    # Get all cars (this part is for the home page)
    cars = Car.objects.all()

    # Handle the contact form submission
    if request.method == 'POST':
        form = ContactFormClass(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Redirect to the success page if form is valid
        else:
            print(form.errors)  # Print form validation errors to the console

    else:
        form = ContactFormClass()  # Initialize an empty form if it's not a POST request

    # Build the context for rendering both the form and the cars
    context = {
        "cars": cars,
        "form": form,
        "copy": build_copy(),  # Assuming you have a function to generate the copy
    }

    return render(request, 'market/index.html', context)



def contact_view(request):
    if request.method == 'POST':
        form = ContactFormClass(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Redirect to a success page
        else:
            print(form.errors)  # This will print form validation errors
    else:
        form = ContactFormClass()

    return render(request, 'market/index.html', {'form': form})


def success(request):
    return render(request, 'market/success.html')
