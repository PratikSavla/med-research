from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from .forms import NewUserForm
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


#AI CODE HERE
import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
# model = tensorflow.keras.models.load_model("keras_model.h5")

# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1.

def get_predictions():
    np.set_printoptions(suppress=True)

# Load the model
    model = tensorflow.keras.models.load_model('mobilenet.h5')
    path = default_storage.open('static/tmp/'+"img.jpg")
    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # Replace this with the path to your image
    image = Image.open(path)

    #resize the image to a 224x224 with the same strategy as in TM2:
    #resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    #turn the image into a numpy array
    image_array = np.asarray(image)

    # display the resized image
    #image.show()

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    prediction = model.predict(data)
    return prediction


# Create your views here.
def homepage(request):
    if request.method == 'POST':
        try:
            img = request.FILES['file']

            with default_storage.open('static/tmp/'+"img.jpg", 'wb+') as dest:
                for chunk in img.chunks():
                    dest.write(chunk)

            output = get_predictions()
            acc = str(output[0][output[0].argmax()]*100)
            output = str(['Optetrak','Maxx Freedom Knee','Smith and Nephew - Legion',
                          'Stryker - NRG','Zimmer - LPS','Zimmer_Persona_(SIIMS)'][output[0].argmax()])
            # output = "Test Name"
            return render(request = request,
                      template_name='Main/home.html',
                      context = {"tutorials":"Testing","output":True, "result":output, "acc":acc})
        except:
            return render(request = request,
                template_name='Main/home.html',
                     context = {"tutorials":"Testing","output":False})

    return render(request = request,
                  template_name='Main/home.html',
                  context = {"tutorials":"Testing","output":False})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New account created: {username}")
            login(request, user)
            return redirect("Main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            return render(request = request,
                          template_name = "Main/register.html",
                          context={"form":form})

    form = UserCreationForm
    return render(request = request,
                  template_name = "Main/register.html",
                  context={"form":form})

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request = request,
                    template_name = "main/login.html",
                    context={"form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("Main:homepage")