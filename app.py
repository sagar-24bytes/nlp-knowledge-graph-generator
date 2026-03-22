import streamlit as st
import spacy
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

# Page config
st.set_page_config(
    page_title="Knowledge Graph NLP",
    layout="wide"
)

# Load model
nlp = spacy.load("en_core_web_sm")

# Title
st.markdown("""
# 🧠 Knowledge Graph Generator  
### 📌 Transform Unstructured Text into Structured Knowledge  
---
""")

# Input text
text = st.text_area("✏️ Enter your text here:", height=150)

st.caption("💡 Example: Elon Musk founded SpaceX. SpaceX is based in USA.")

# Button
if st.button("🚀 Generate Knowledge Graph"):

    doc = nlp(text)
    relations = set()

    # -----------------------------------
    # RELATION EXTRACTION
    # -----------------------------------
    for sent in doc.sents:
        for token in sent:

            # Subject-Verb-Object
            if token.dep_ == "ROOT":
                subject = [w for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
                obj = [w for w in token.rights if w.dep_ in ("dobj", "attr")]

                if subject and obj:
                    subj = " ".join([w.text for w in subject[0].subtree]).strip().strip(".")
                    objt = " ".join([w.text for w in obj[0].subtree]).strip().strip(".")
                    rel = token.text.lower()

                    relations.add((subj, rel, objt))

            # Prepositional relations
            if token.dep_ == "prep":
                pobj = [w for w in token.children if w.dep_ == "pobj"]

                if pobj:
                    head = token.head
                    subject = [w for w in head.lefts if w.dep_ in ("nsubj", "nsubjpass")]

                    if subject:
                        subj = " ".join([w.text for w in subject[0].subtree]).strip().strip(".")
                        rel = head.text.lower() + " " + token.text.lower()
                        objt = pobj[0].text.strip().strip(".")

                        relations.add((subj, rel, objt))

    # -----------------------------------
    # SHOW RELATIONS
    # -----------------------------------
    st.markdown("## 🔗 Extracted Relations")
    df = pd.DataFrame(sorted(relations), columns=["Subject", "Relation", "Object"])
    st.dataframe(df, use_container_width=True)

    # -----------------------------------
    # SHOW ENTITIES
    # -----------------------------------
    st.markdown("## 🏷️ Named Entities")
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    entity_df = pd.DataFrame(entities, columns=["Entity", "Type"])
    st.dataframe(entity_df, use_container_width=True)

    # -----------------------------------
    # GRAPH CREATION
    # -----------------------------------
    G = nx.DiGraph()

    for subj, rel, obj in relations:
        G.add_node(subj)
        G.add_node(obj)
        G.add_edge(subj, obj, label=rel)

    net = Network(
        height="650px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black"
    )

    # Layout physics
    net.barnes_hut(
        gravity=-8000,
        central_gravity=0.2,
        spring_length=200,
        spring_strength=0.04
    )

    # Entity types for coloring
    entity_types = {ent.text: ent.label_ for ent in doc.ents}

    def get_color(node):
        if node in entity_types:
            if entity_types[node] == "PERSON":
                return "#ff4d6d"   # red
            elif entity_types[node] == "ORG":
                return "#2ecc71"   # green
            elif entity_types[node] == "GPE":
                return "#3498db"   # blue
        return "#9b59b6"  # default

    # Add nodes
    for node in G.nodes():
        net.add_node(
            node,
            label=node,
            size=28,
            color=get_color(node),
            font={"size": 16, "color": "black"}
        )

    # Add edges
    for u, v, data in G.edges(data=True):
        net.add_edge(
            u, v,
            label=data['label'],
            font={"align": "middle", "size": 12, "color": "#333"},
            color="#888",
            arrows="to"
        )

    # Smooth edges
    net.set_options("""
    var options = {
      "edges": {
        "smooth": {
          "type": "curvedCW",
          "roundness": 0.2
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "centralGravity": 0.2,
          "springLength": 200,
          "springConstant": 0.04
        },
        "minVelocity": 0.75
      }
    }
    """)

    # Save graph
    if not os.path.exists("output"):
        os.makedirs("output")

    net.save_graph("output/graph.html")

    # -----------------------------------
    # SHOW GRAPH
    # -----------------------------------
    st.markdown("## 🌐 Interactive Knowledge Graph")
    st.components.v1.html(open("output/graph.html").read(), height=650)

    # -----------------------------------
    # LEGEND (IMPORTANT)
    # -----------------------------------
    st.markdown("""
    ### 🎨 Legend:
    - 🔴 Person  
    - 🟢 Organization  
    - 🔵 Location  
    - 🟣 Other  
    """)

    # -----------------------------------
    # STATISTICS
    # -----------------------------------
    st.markdown("## 📊 Analysis & Statistics")

    col1, col2 = st.columns(2)

    col1.metric("Total Relations", len(relations))
    col2.metric("Total Entities", len(entities))

    # Chart
    rel_list = [r[1] for r in relations]
    rel_df = pd.DataFrame(rel_list, columns=["Relation"])

    st.bar_chart(rel_df["Relation"].value_counts(), height=300)