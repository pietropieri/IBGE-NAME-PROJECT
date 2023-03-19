import json
import unicodedata

with open("/home/pietro/Projetos/nameMap/requestsIbge/brasilgeojson.json") as json_file:
    brasil = json.load(json_file)

for feature in brasil['features']:
    feature['id'] = feature['properties']['UF_05']

with open("/home/pietro/Projetos/nameMap/requestsIbge/brasilgeojson.json", "w") as json_file:
    json.dump(brasil, json_file)

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
