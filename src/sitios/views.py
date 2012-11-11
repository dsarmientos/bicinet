from django.shortcuts import render_to_response

def buscador(request):
    return render_to_response('sitios/mapa.html')
