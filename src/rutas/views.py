from django.shortcuts import render_to_response
from rutas.models import Ruta

def home(request):
    rutas = Ruta.objects.all()
    return render_to_response('rutas/home.html', {'rutas': rutas})

