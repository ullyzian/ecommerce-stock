from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField()

    def __str__(self):
        return 