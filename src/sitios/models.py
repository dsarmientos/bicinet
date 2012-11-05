from django.db import models

# Create your models here.

class Punto(models.Model):
    osmId = models.IntegerField()
    nombre = models.CharField(max_length=30)

    def __unicode__(self):
        return self.nombre 


class CategoriaSitio(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=254)

    def __unicode__(self):
        return self.nombre 

class Sitio(models.Model):
    nombre = models.CharField(max_length=30)
    confirmado = models.BooleanField()
    fechaConfirmado = models.DateField(auto_now = False)
    categoria = models.ForeignKey('CategoriaSitio')
    punto = models.ForeignKey('Punto')

    def __unicode__(self):
        return self.nombre 

class TipoIncidente(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=254)

    def __unicode__(self):
        return self.nombre 


class incidente(models.Model):
    tipoIncidente = models.ForeignKey('TipoIncidente')
    fechaHoraReporte = models.DateTimeField(auto_now_add = True)
    reportadoPor = models.CharField(max_length=30)
    comentarios = models.CharField(max_length=254)

