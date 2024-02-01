from django.db import models

# Create your models here.
var_flag = False

class Product(models.Model):
    id    = models.AutoField(primary_key=True)
    name  = models.CharField(max_length = 2) 
    info  = models.CharField(max_length = 2, default = '')
    price = models.IntegerField(blank=True, null=True)
    

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        global var_flag
        if self.price == (2**32)-1:
            return False

        if self.price == -((2**32)-1):
            var_flag = True          

        if var_flag is True:
            return False
       
        super().save(*args, **kwargs)
