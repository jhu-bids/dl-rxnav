import os
import requests
import pandas as pd
import json

BASE_URL = "https://rxnav.nlm.nih.gov"

rxcuis = [ 8640, 6902, 3264, 10759, 5492, 8638, 1514, 4452, 22396,
            21660, 2878, 55681, 4463, 1312358, 21285, 38668, 3256,
            7910, 29523, 12473, 978038, 2286252, 665792, 495088, 669988,]

for c in rxcuis:
    data = requests.get(f"{BASE_URL}/REST/rxcui/{c}/allrelated.json").json()
    #data = requests.get(f"{BASE_URL}/REST/rxcui/{c}/allrelated.json?tty=SCDC+DFG+IN+MIN").json()
    #dfg =
    print(data)


#ttys = data['allRelatedGroup']['conceptGroup']
#dfgs = [tty['conceptProperties'] for tty in ttys if tty['tty'] == 'DFG'][0]
#print(dfgs)

