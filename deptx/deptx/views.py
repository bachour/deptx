from django.shortcuts import render

def index(request):
    return render(request, 'players/deptx_index.html')


