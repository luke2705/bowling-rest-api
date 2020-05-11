from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.core.exceptions import ValidationError

from .models import Game
from .serializers import ScoreSerializer


# Create your views here.
def calculate_score(ball_values):
    final_frame_scores = []
    if ball_values:
        open_frame_scores = [0 for _ in range(10)]
        frame_balls_remaining = [2 for _ in range(10)]
        remaining_frames = [i for i in range(10)]
        current_frame=0
        previous_ball=0
        increment_current_frame = False

        for ball in ball_values:
            # handle multiple counting for strikes and spares
            if ball in "Xx/":
                # don't add extra balls if the strike/spare is already a 10th frame bonus ball
                if current_frame < 10:
                    frame_balls_remaining[remaining_frames.index(current_frame)]+=1
                increment_current_frame = True

            # update ball to be int
            if ball in "Xx":
                ball = 10
            if ball =='/':
                ball = 10 - previous_ball
            else:
                ball = int(ball)
            previous_ball=ball

            # The loop below will update the current frame score and any previous frame scores that are still open
            
            # set iterator to number of currently pending frames
            if current_frame < 10:
                open_frames = range(remaining_frames.index(current_frame)+1)
            # catch tenth frame with extra remaining frames
            else:
                open_frames = range(len(frame_balls_remaining))
            # since we are using indices to access data, we dont want to pop elements till the end
            pop_count=0
            
            for frame in open_frames:
                open_frame_scores[frame] += (ball)
                frame_balls_remaining[frame] -= 1

                if frame_balls_remaining[frame] == 0:
                    # if there is a previous frame, add the current frame to the previous frame for the total
                    if len(final_frame_scores) == 0:
                        final_frame_scores.append(open_frame_scores[frame])
                    else:
                        final_frame_scores.append(open_frame_scores[frame]+final_frame_scores[-1])
                    pop_count += 1

            for _ in range(pop_count):
                remaining_frames.pop(0) 
                open_frame_scores.pop(0)
                frame_balls_remaining.pop(0)

            if increment_current_frame or current_frame not in remaining_frames:
                current_frame += 1
                increment_current_frame = False
              
    return final_frame_scores

@csrf_exempt
def init_game(request):
    if request.method == 'GET':
        games = Game.objects.all()
        serializer = ScoreSerializer(games, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        
        # delete any existing games on the lane
        if data.get('add_player')!=True:            
            old_games = Game.objects.filter(lane=data['lane']).delete()

        # ...and create new ones
        for name in data['names']:
            game = {'name':name,'lane':data['lane']}
            serializer = ScoreSerializer(data=game)
            if serializer.is_valid():
                serializer.save()
            else:
                return JsonResponse(serializer.errors, status=400)
        games = Game.objects.filter(lane=data['lane'])
        serializer = ScoreSerializer(games, many=True)
        return JsonResponse(serializer.data, status=201, safe=False)

@csrf_exempt
def new_ball(request):
    if request.method == 'GET':
        games = Game.objects.all()
        serializer = ScoreSerializer(games, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        current_game = Game.objects.filter(lane=data['lane'], name=data['name'])[0]
        current_game.ball_values += data['ball_value']
        current_game.frame_scores = calculate_score(current_game.ball_values)

        try:
            current_game.clean_fields()
            current_game.save()
        except ValidationError as e:
            return JsonResponse(e.message_dict, status=400)
        
        games = Game.objects.filter(lane=data['lane'])
        serializer = ScoreSerializer(games, many=True)
        return JsonResponse(serializer.data, status=200, safe=False)

@csrf_exempt
def update_ball_values(request):
    if request.method == 'GET':
        games = Game.objects.all()
        serializer = ScoreSerializer(games, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        current_game = Game.objects.filter(lane=data['lane'], name=data['name'])[0]
        current_game.ball_values = data['ball_values']
        
        try:
            current_game.frame_scores = calculate_score(current_game.ball_values)
            current_game.clean_fields()
            current_game.save()
        except ValidationError as e:
            return JsonResponse(e.message_dict, status=400)
        
        games = Game.objects.filter(lane=data['lane'])
        serializer = ScoreSerializer(games, many=True)
        return JsonResponse(serializer.data, status=200, safe=False)

def GUI(request):
    return render(request, 'GUI.html', context={})