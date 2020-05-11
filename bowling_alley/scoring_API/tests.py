from django.test import TestCase

# Create your tests here.

from rest_framework.test import APITestCase
from rest_framework import status

from .views import calculate_score


BASE_URL = "http://127.0.0.1:8000/api/"
BASE_PAYLOAD = {"lane":1,"name":"Luke"}

valid_scoring_permutations = [
                            # (scoring string, expected score)
                            ("1/x",20),  # spare followed by strike
                            ("1/25", 19), # spare followed by numbers
                            ("x34", 24), # strike followed by two numbers
                            ("x6/", 20), # strike followed by spare
                            ("xx7/", 47), # double strike followed by spare
                            ("xx81", 56), # double strike followed by two numbers
                            ("xxx12", 67), #triple strike followed by numbers
                            ("xxx3/", 73),# triple strike followed by spare
                            ("xxxxxxxxxx12", 274), # tenth frame strike followed by two numbers
                            ("xxxxxxxxxx1/", 281), # tenth frame strike followed by spare
                            ("xxxxxxxxxxxx", 300), # tenth frame strike followed by two strikes
                            ("11111111111111111111", 20)# no closed frames
]
invalid_scoring_permutations = [
                                    "1/2/34/", #invalid spare on first ball of frame
                                    "2x", #invalid strike on second ball of frame
                                    "87", # invalid numeric combo
                                    "xxxxxxxxxxxxx",# adding ball after game end
                                    "1111111111111111111111",
                                    "xxxxxxxxxx2/2"

]



class API_UnitTests(APITestCase):
    # create
    def test_create_single_player_game(self):
        response = self.init_single_game()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_multiplayer_game(self):
        payload ={
                    "lane": 1,
                    "names":["Luke","Duke"]
                 }
        response = self.client.post(BASE_URL + "initgame", payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # score calculation
    def test_valid_direct_score_calculations(self):
        for parameters in valid_scoring_permutations:
            scoring_string = parameters[0]
            expected_val = parameters[1]
            self.assertEqual(calculate_score(scoring_string)[-1],expected_val )

    def test_valid_score_calculations_through_updatevalues(self):
        self.init_single_game()
        for parameters in valid_scoring_permutations:
            BASE_PAYLOAD["ball_values"] = parameters[0]
            response = self.client.post(BASE_URL + "updatevalues", BASE_PAYLOAD, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_newballs(self):
        for parameters in valid_scoring_permutations:
            self.init_single_game()
            ball_values = parameters[0]
            for ball in ball_values:
                BASE_PAYLOAD["ball_value"] = ball
                response = self.client.post(BASE_URL + "newball", BASE_PAYLOAD, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    # invalid updates
    def test_invalid_scores_updatevalues(self):
        self.init_single_game()
        for scoring_string in invalid_scoring_permutations:
            BASE_PAYLOAD["ball_values"] = scoring_string
            response = self.client.post(BASE_URL + "updatevalues", BASE_PAYLOAD, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_invalid_newball(self):
        for scoring_string in invalid_scoring_permutations:
            self.init_single_game()
            for ball in scoring_string:
                BASE_PAYLOAD["ball_value"] = ball
                response = self.client.post(BASE_URL + "newball", BASE_PAYLOAD, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    def init_single_game(self):
        payload ={
                "lane": 1,
                "names":["Luke"]
                }
        return self.client.post(BASE_URL + "initgame", payload, format='json')