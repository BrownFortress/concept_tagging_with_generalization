import re
import pprint
import numpy as np
from collections import Counter
from dataset.data_manager import DataManager
import plotly.graph_objects as go

class_cluster = {}
dm = DataManager()
class_cluster["actor.name"] = "actor.name"
class_cluster["producer.name"] = "producer.name"
class_cluster["director.name"] = "director.name"
class_cluster["person.name"] = "person.name"
class_cluster["actor.nationality"] = "person.nationality"
class_cluster["director.nationality"] = "person.nationality"
class_cluster["movie.language"] = "person.nationality"
class_cluster["movie.release_region"] = "country.name"
class_cluster["country.name"] = "country.name"
class_cluster["movie.location"] = "country.name"
entities = dm.extract_entities(class_cluster.keys(), "train_features.txt")
print("Overlapping:")
for ent1, set1 in entities.items():
    for ent2 in entities.keys():
        value = len(set(set1).intersection(set(entities[ent2])))
        if value != 0 and ent1 != ent2:
            print(ent1 + " & " + ent2 + " = " + str(value))

print("Sparsity")
concepts = []
presence = []
unique_elements = []
for ent1, set1 in entities.items():
    value = len(set1)
    value2 = len(set(set1))
    concepts.append(ent1)
    presence.append(value)
    unique_elements.append(value2)

fig = go.Figure(data=[
    go.Bar(name="Number of tokens", x=concepts, y=presence, marker_color="royalblue"),
    go.Bar(name="Number of unique tokens", x=concepts, y=unique_elements, marker_color="indianred")
])
# Change the bar mode
fig.update_layout(
    title="Concepts frequencies",
    xaxis_title="Concepts",
    yaxis_title="Frequency",
    font=dict(
        family="Droid Sans",
        size=36,
        color="#7f7f7f"
    )
    )
fig.update_layout(barmode='group')
fig.write_image("charts/sparsity_chart.png", format="png", width=1920, height=1080, scale=1)
