from django.db import models
import ppygis

class arco(models.Model):
    osmId = models.CharField(max_length=30)
    origen = models.IntegerField()
    destino = models.IntegerField()
    # geomet = ppygis.Geometry()
    

class Ruta(models.Model):
    nombre = models.CharField(max_length=30)
    categoria = models.ForeignKey('Categoria')

    def __unicode__(self):
        return self.nombre 


class Categoria(models.Model):
    nombre = models.CharField(max_length=30)

    def __unicode__(self):
        return self.nombre 

