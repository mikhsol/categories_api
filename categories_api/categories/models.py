from django.db import models


class Category(models.Model):
    name = models.CharField(verbose_name='Category name', max_length=1024,
                            unique=True)
