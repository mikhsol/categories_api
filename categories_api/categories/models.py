from django.db import models


class Category(models.Model):
    name = models.CharField(verbose_name='Category name', max_length=1024,
                            unique=True)
    kids = models.ManyToManyField('self', symmetrical=False,
                                  related_name='child_of')
    siblings = models.ManyToManyField('self', symmetrical=True,
                                    related_name='sibling_of')

