from django.db import models
from django.core.validators import int_list_validator
from .validators import ball_validator


    
# Create your models here.
class Game(models.Model):
    name = models.CharField(max_length=15)
    # 21 is max possible with 2 balls per frame and 3 balls in frame 10
    ball_values = models.CharField(max_length=21, blank=True, default="", validators=[ball_validator])
    frame_scores = models.CharField(max_length=60, blank=True, default="", validators=[int_list_validator])
    lane = models.PositiveIntegerField()

    def __str__(self):
        return (f'{self.name} on lane {self.lane}')