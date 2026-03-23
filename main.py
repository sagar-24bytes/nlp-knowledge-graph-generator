import spacy
import networkx as nx
from pyvis.network import Network
import os
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Read input file
with open("sample.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Preprocess: fix missing space after period, normalize whitespace
text = re.sub(r'\.([A-Z])', r'. \1', text)
text = re.sub(r'\s+', ' ', text).strip()


# -----------------------------------
# HELPER: clean subject/object label
# -----------------------------------
def clean_span(token):
    keep_deps = {"compound", "amod", "det", "poss", "nummod"}
    skip_pos  = {"PUNCT", "SPACE"}
    pronouns  = {"he", "she", "it", "they", "him", "her", "them",
                 "his", "hers", "their", "we", "i", "you"}

    parts = []
    for t in token.subtree:
        if t.pos_ in skip_pos:
            continue
        if t.text.lower() in pronouns:
            continue
        if t == token:
            parts.append(t)
        elif t.dep_ in keep_deps and t.head == token:
            parts.append(t)

    if not parts:
        return token.text.strip()

    parts_sorted = sorted(parts, key=lambda t: t.i)
    result = " ".join(t.text for t in parts_sorted).strip()
    result = result.strip(".,;:!?\"'()")
    return result


# -----------------------------------
# RELATION EXTRACTION
# -----------------------------------
pronouns = {"he", "she", "it", "they", "him", "her", "them",
            "his", "hers", "their"}

doc = nlp(text)
relations = set()
last_subject = None

for sent in doc.sents:

    sent_subj = None

    # --- Pass 1: find subject of this sentence ---
    for token in sent:
        if token.dep_ in ("nsubj", "nsubjpass"):
            if token.text.lower() in pronouns:
                sent_subj = last_subject
            else:
                sent_subj = clean_span(token)
                last_subject = sent_subj
            break

    # Fallback: first word is a pronoun
    if sent_subj is None and doc[sent.start].text.lower() in pronouns:
        sent_subj = last_subject

    if sent_subj is None:
        sent_subj = last_subject

    if sent_subj is None:
        continue

    # --- Pass 2: extract relations ---
    for token in sent:

        # ROOT → direct object or attribute
        if token.dep_ == "ROOT":
            for child in token.children:
                if child.dep_ in ("dobj", "attr"):
                    obj = clean_span(child)
                    rel = token.lemma_.lower()
                    relations.add((sent_subj, rel, obj))

        # Prepositional relations: "works at IBM", "born in Delhi"
        if token.dep_ == "prep":
            head = token.head
            pobj_list = [w for w in token.children if w.dep_ == "pobj"]
            for pobj in pobj_list:
                if head.pos_ in ("VERB", "AUX") or head.dep_ == "ROOT":
                    rel = head.text.lower() + " " + token.text.lower()
                    obj = clean_span(pobj)
                    relations.add((sent_subj, rel, obj))

        # "X is a Y" copula
        if token.dep_ == "ROOT" and token.lemma_ == "be":
            for child in token.children:
                if child.dep_ in ("attr", "acomp"):
                    obj = clean_span(child)
                    relations.add((sent_subj, "is", obj))


# -----------------------------------
# PRINT RELATIONS
# -----------------------------------
print("\nExtracted Relations:")
for r in sorted(relations):
    print(f"  {r[0]}  →  {r[1]}  →  {r[2]}")


# -----------------------------------
# ENTITY DETECTION (on full text)
# -----------------------------------
print("\nDetected Entities:")
for ent in doc.ents:
    print(f"  {ent.text}  -  {ent.label_}")


# -----------------------------------
# BUILD GRAPH
# -----------------------------------
G = nx.DiGraph()

for subj, rel, obj in relations:
    G.add_node(subj)
    G.add_node(obj)
    G.add_edge(subj, obj, label=rel)


# -----------------------------------
# VISUALIZATION
# -----------------------------------
net = Network(
    height="650px",
    width="100%",
    directed=True,
    bgcolor="#ffffff",
    font_color="black"
)

net.barnes_hut(
    gravity=-8000,
    central_gravity=0.2,
    spring_length=200,
    spring_strength=0.04
)

# Entity type → color
entity_types = {ent.text: ent.label_ for ent in doc.ents}

def get_color(node):
    label = entity_types.get(node, "")
    if label == "PERSON":           return "#ff4d6d"   # red
    if label == "ORG":              return "#2ecc71"   # green
    if label in ("GPE", "LOC"):     return "#3498db"   # blue
    return "#9b59b6"                                   # purple (other)

# Add nodes
for node in G.nodes():
    net.add_node(
        node,
        label=node,
        title=f"Entity: {node}",
        size=35,
        color=get_color(node),
        font={"size": 16, "color": "black"}
    )

# Add edges
for u, v, data in G.edges(data=True):
    net.add_edge(
        u, v,
        label=data["label"],
        font={"align": "middle", "size": 12, "color": "#333"},
        color="#888",
        arrows="to",
        smooth={"type": "curvedCW", "roundness": 0.25}
    )

# Save graph
os.makedirs("output", exist_ok=True)
output_file = "output/knowledge_graph.html"
net.write_html(output_file)

print(f"\nGraph saved to: {output_file}")