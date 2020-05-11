from django.urls import path,include

from .views import init_game, new_ball, update_ball_values

urlpatterns = [
    path('initgame',init_game, name='init-game'),
    path('newball',new_ball, name='new-ball'),
    path('updatevalues',update_ball_values, name='update-ball-values')
]
