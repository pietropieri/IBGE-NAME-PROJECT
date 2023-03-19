import plotly.express as px
import plotly as plt
import pandas as pd
import json
from requestsIbge.ibgerequests import Ibge 

ibge = Ibge()

ibge.setName("pietro")

brasil = json.load(open("brasilgeojson.json", "r"))


fig = px.choropleth(data_frame=ibge.data_frame, locations='estado', geojson=brasil, hover_data=['estado'], color='pessoa', scope='south america', range_color=(0,ibge.max_frequency))

fig.update_layout(height=800)

plt.offline.plot(fig, filename = 'map.html')

