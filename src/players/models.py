from django.db import models


# Create your models here.
class Player(models.Model):
    player_id = models.CharField(max_length=255, unique=True)
    user_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_name
