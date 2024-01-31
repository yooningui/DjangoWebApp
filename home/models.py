from django.db import models

# Create your models here.

class Product(models.Model):
    id    = models.AutoField(primary_key=True)
    name  = models.CharField(max_length = 2) 
    info  = models.CharField(max_length = 2, default = '')
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if Product.objects.count() >= 2:
            Product.objects.create()  
        else:
            super().save(*args, **kwargs)