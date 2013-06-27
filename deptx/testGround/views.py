from django.shortcuts import render

from testGround.models import Car

def index(request):
    car_list = Car.objects.all()
    context = {'car_list': car_list}
    return render(request, 'testGround/index.html', context)