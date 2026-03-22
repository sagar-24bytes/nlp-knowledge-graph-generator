import spacy
import networkx as nx
from pyvis.network import Network
import os

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Read input file
with open("sample.txt", "r", encoding="utf-8") as file:
    text = file.read()

doc = nlp(text)

relations = set()

# -----------------------------------
# RELATION EXTRACTION (FINAL FIXED)
# -----------------------------------
for sent in doc.sents:
    for token in sent:

        # Case 1: Subject-Verb-Object
        if token.dep_ == "ROOT":
            subject = [w for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
            obj = [w for w in token.rights if w.dep_ in ("dobj", "attr")]

            if subject and obj:
                subj = " ".join([w.text for w in subject[0].subtree]).strip().strip(".")
                objt = " ".join([w.text for w in obj[0].subtree]).strip().strip(".")
                rel = token.text.lower()

                relations.add((subj, rel, objt))

        # Case 2: Prepositional relations (FIXED 🔥)
        if token.dep_ == "prep":
            pobj = [w for w in token.children if w.dep_ == "pobj"]

            if pobj:
                head = token.head
                subject = [w for w in head.lefts if w.dep_ in ("nsubj", "nsubjpass")]

                if subject:
                    subj = " ".join([w.text for w in subject[0].subtree]).strip().strip(".")
                    rel = head.text.lower() + " " + token.text.lower()
                    objt = pobj[0].text.strip().strip(".")

                    relations.add((subj, rel, objt))  # ✅ FIXED HERE

# -----------------------------------
# PRINT RELATIONS
# -----------------------------------
print("\nExtracted Relations:")
for r in sorted(relations):
    print(r)

# -----------------------------------
# PRINT ENTITIES
# -----------------------------------
print("\nDetected Entities:")
for ent in doc.ents:
    print(ent.text, "-", ent.label_)

# -----------------------------------
# BUILD GRAPH
# -----------------------------------
G = nx.DiGraph()

for subj, rel, obj in relations:
    G.add_node(subj)
    G.add_node(obj)
    G.add_edge(subj, obj, label=rel)

# -----------------------------------
# CREATE OUTPUT FOLDER
# -----------------------------------
if not os.path.exists("output"):
    os.makedirs("output")

# -----------------------------------
# VISUALIZATION
# -----------------------------------
net = Network(height="650px", width="100%", directed=True)

net.force_atlas_2based()
net.repulsion(node_distance=200, central_gravity=0.3)

# Add nodes
for node in G.nodes():
    net.add_node(node, label=node, color="#97c2fc", size=25)

# Add edges
for u, v, data in G.edges(data=True):
    net.add_edge(u, v, label=data['label'], color="gray")

# Save graph
output_file = "output/knowledge_graph.html"
net.write_html(output_file)

print(f"\nGraph saved to: {output_file}")