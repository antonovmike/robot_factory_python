from django.db import models


class Customer(models.Model):
    name = models.TextField(blank=False, null=False)
    email = models.EmailField(blank=False, null=False, unique=True)
    login = models.TextField(blank=False, null=False, unique=True)
    password = models.TextField(blank=False, null=False)

    class Meta:
        db_table = 'customers'
