from django.db import models

# Create your models here.

class Product(models.Model):
    id    = models.AutoField(primary_key=True)
    name  = models.CharField(max_length = 1) 
    info  = models.CharField(max_length = 1, default = '')
    price = models.IntegerField(blank=True, null=False)

    def __str__(self):
        return self.name
   