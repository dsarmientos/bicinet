from django.db import models

# Create your models here.

class CategoriaSitio(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=254)

class Sitio(models.Model):
    nombre = models.CharField(max_length=30)
    confirmado = models.BooleanField()
    fechaConfirmado = models.DateField(auto_now=false)
    categoria = models.ForeignKey('CategoriaSitio')

    def __unicode__(self):
        return self.nombre 
