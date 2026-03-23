import streamlit as st
import spacy
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

st.set_page_config(page_title="Knowledge Graph NLP", layout="wide")

nlp = spacy.load("en_core_web_sm")

st.markdown("""
# 🧠 Knowledge Graph Generator  
### 📌 Transform Unstructured Text into Structured Knowledge  
---
""")

text = st.text_area("✏️ Enter your text here:", height=150)
st.caption("💡 Example: Shivam works at IBM and he was born in Delhi.")

# -----------------------------------
# HELPER: clean a subtree to a short noun phrase
# -----------------------------------
def clean_span(token):
    """
    Return a clean label for a token's subtree.
    Only keeps determiners + compound + the token itself.
    Avoids pulling in prepositional phrases that bloat the label.
    """
    keep_deps = {"compound", "amod", "det", "poss", "nummod"}
    parts = []
    for t in token.subtree:
        if t == token:
            parts.append(t.text)
        elif t.dep_ in keep_deps and t.head == token:
            parts.append(t.text)
    # fallback: just the token text
    if not parts:
        return token.text
    # rebuild in original order
    ordered = [t for t in token.subtree if t.text in parts]
    return " ".join(t.text for t in ordered).strip()


# -----------------------------------
# RELATION EXTRACTION (FIXED)
# -----------------------------------
def extract_relations(text):
    doc = nlp(text)
    relations = set()
    last_subject = None
    pronouns = {"he", "she", "it", "they", "him", "her", "them", "his", "hers", "their"}

    for sent in doc.sents:

        sent_subj = None

        # --- Pass 1: find subject of this sentence ---
        for token in sent:
            if token.dep_ in ("nsubj", "nsubjpass"):
                if token.text.lower() in pronouns:
                    sent_subj = last_subject
                else:
                    # FIX: use clean_span, NOT full subtree string
                    sent_subj = clean_span(token)
                    last_subject = sent_subj
                break

        # Pronoun at sentence start fallback
        if sent_subj is None and doc[sent.start].text.lower() in pronouns:
            sent_subj = last_subject

        if sent_subj is None:
            sent_subj = last_subject

        if sent_subj is None:
            continue

        # --- Pass 2: extract relations from each token ---
        for token in sent:

            # ROOT → direct object / attribute
            if token.dep_ == "ROOT":
                for child in token.children:
                    if child.dep_ in ("dobj", "attr"):
                        obj = clean_span(child)
                        rel = token.lemma_.lower()
                        relations.add((sent_subj, rel, obj))

            # Prepositional relations: "born in Delhi", "works at IBM"
            if token.dep_ == "prep":
                head = token.head
                pobj_list = [w for w in token.children if w.dep_ == "pobj"]
                for pobj in pobj_list:
                    # Make sure the prep is attached to a verb/root in this sentence
                    if head.pos_ in ("VERB", "AUX") or head.dep_ == "ROOT":
                        rel = head.text.lower() + " " + token.text.lower()
                        obj = clean_span(pobj)
                        relations.add((sent_subj, rel, obj))

            # "X is a Y" (appositive / classifier)
            if token.dep_ == "ROOT" and token.lemma_ in ("be", "is", "are", "was", "were"):
                for child in token.children:
                    if child.dep_ in ("attr", "acomp"):
                        obj = clean_span(child)
                        relations.add((sent_subj, "is", obj))

    return relations, doc


# -----------------------------------
# BUTTON
# -----------------------------------
if st.button("🚀 Generate Knowledge Graph"):

    if not text.strip():
        st.warning("Please enter some text first.")
        st.stop()

    relations, doc = extract_relations(text)

    # -----------------------------------
    # RELATIONS TABLE
    # -----------------------------------
    st.markdown("## 🔗 Extracted Relations")
    if relations:
        df = pd.DataFrame(sorted(relations), columns=["Subject", "Relation", "Object"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No relations found. Try a sentence like: Shivam works at IBM and he was born in Delhi.")

    # -----------------------------------
    # NAMED ENTITIES
    # -----------------------------------
    st.markdown("## 🏷️ Named Entities")
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    if entities:
        entity_df = pd.DataFrame(entities, columns=["Entity", "Type"])
        st.dataframe(entity_df, use_container_width=True)
    else:
        st.info("No named entities detected.")

    # -----------------------------------
    # GRAPH
    # -----------------------------------
    if relations:
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
            if label == "PERSON":   return "#ff4d6d"
            if label == "ORG":      return "#2ecc71"
            if label in ("GPE", "LOC"): return "#3498db"
            return "#9b59b6"

        for node in G.nodes():
            net.add_node(
                node,
                label=node,
                title=f"Entity: {node}",
                size=30,
                color=get_color(node),
                font={"size": 16, "color": "black"}
            )

        for u, v, data in G.edges(data=True):
            net.add_edge(
                u, v,
                label=data["label"],
                font={"align": "middle", "size": 12, "color": "#333"},
                color="#888",
                arrows="to"
            )

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

        os.makedirs("output", exist_ok=True)
        net.save_graph("output/graph.html")

        st.markdown("## 🌐 Interactive Knowledge Graph")
        st.components.v1.html(open("output/graph.html").read(), height=650)

        st.markdown("""
        ### 🎨 Legend:
        - 🔴 Person  
        - 🟢 Organization  
        - 🔵 Location  
        - 🟣 Other  
        """)

        # -----------------------------------
        # STATS
        # -----------------------------------
        st.markdown("## 📊 Analysis & Statistics")
        col1, col2 = st.columns(2)
        col1.metric("Total Relations", len(relations))
        col2.metric("Total Entities", len(entities))

        rel_list = [r[1] for r in relations]
        rel_df = pd.DataFrame(rel_list, columns=["Relation"])
        st.bar_chart(rel_df["Relation"].value_counts(), height=300)