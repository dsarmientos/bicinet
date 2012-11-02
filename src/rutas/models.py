from django.db import models
import ppygis

class arco(models.Model):
    osmId = models.CharField(max_length=30)
    origen = models.IntegerField()
    destino = models.IntegerField()

class CampoCosto(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion =  models.CharField(max_length=254)

    def __unicode__(self):
        return self.nombre 

class valoresCampo(models.Model):
    nombreCampo = models.ForeignKey('CampoCosto')
    valor = models.CharField(max_length=30)

    def __unicode__(self):
        return self.valor 


class TipoPreferencia(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=254)

    def __unicode__(self):
        return self.nombre 


class CostPreferencia(models.Model):
    usuario = models.CharField(max_length=30)
    tipoPreferencia = models.ForeignKey('TipoPreferencia')
    valorCampo = models.ForeignKey('valoresCampo')
    costo = models.IntegerField()

class CategoriaRuta(models.Model):
    nombre = models.CharField(max_length=30)

    def __unicode__(self):
        return self.nombre 

class Ruta(models.Model):
    nombre = models.CharField(max_length=30)
    categoria = models.ForeignKey('CategoriaRuta')

    def __unicode__(self):
        return self.nombre 

class RutaUsuario(Ruta):
     evaluacion = models.IntegerField()
     descrEval = models.CharField(max_length=1000)



