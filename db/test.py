import faiss
import ollama
import numpy as np

texts = [
"""
23. Juli
In Istanbul trafen sich Vertreter von Russland und der Ukraine zu Verhandlungen. Zu einer Waffenstillstandsvereinbarung kam es nicht. Stattdessen einigten sich beide Kriegsparteien auf einen weiteren Austausch von Kriegsgefangenen. Es war das dritte derartige Treffen in Istanbul im laufenden Jahr[295] nach den Treffen vom März und Mai 2025.
""","""
26. Juli
Durch nächtliche russische Luftangriffe wurden ukrainischen Angaben zufolge drei Menschen in der Oblast Dnipropetrowsk getötet sowie fünf Menschen in der Stadt Charkiw und drei in der Oblast Sumy verletzt. Die Angriffe lösten den Angaben zufolge außerdem Brände in den Oblasten Dnipropetrowsk und Saporischschja aus. Die ukrainische Luftwaffe gab an, Russland habe dabei 208 Drohnen und Drohnenattrappen, 12 ballistische Raketen des Typs „Iskander-M“ sowie 15 Marschflugkörper verschiedener Typen eingesetzt. Davon seien 183 Drohnen und 17 Raketen und Marschflugkörper abgefangen worden. Russische Behörden meldeten, es habe ukrainische Drohnenangriffe in der Oblast Rostow gegeben, dabei seien zwei Personen getötet worden.[296][297]
""","""
28. Juli
Hatte US-Präsident Donald Trump Russland am 14. Juli eine 50-tägige Frist zur Implementierung einer Waffenruhe gestellt, reduzierte er sie auf 24 bis 26 Tage bzw. beginnend ab 28. Juli „zehn bis zwölf Tage“. Trump zeigte sich wegen der nicht endenden russischen Luftangriffe erneut tief enttäuscht vom russischen Staatspräsidenten Wladimir Putin.[298]
"""
]

vec = ollama.embed("all-minilm",texts).embeddings
index = faiss.IndexFlatL2(len(vec[0]))
index.add(np.array(vec,dtype=np.float32))

query = ollama.embed("all-minilm","Was hat Donald Trump getan?").embeddings
distances, indices = index.search(np.array(query,dtype=np.float32), 1)
print(distances[0][0], texts[indices[0][0]])