# 🧠 NLP Knowledge Graph Generator

An interactive, NLP-based system that extracts entities and relationships from unstructured text and constructs a visual knowledge graph.

This is not just a script.
This is a complete **interactive NLP system with visualization and analysis**.



## What it does

The system takes natural language input and:

1. Identifies entities using Named Entity Recognition (NER)
2. Extracts relationships using dependency parsing
3. Converts unstructured text into structured triples
4. Builds a directed knowledge graph
5. Visualizes the graph interactively
6. Provides statistical insights on extracted data



## Core Architecture

```text
Input Layer
User Text (Streamlit UI)
↓
NLP Processing Layer
spaCy (NER + Dependency Parsing)
↓
Relation Extraction Layer
Subject → Relation → Object Triples
↓
Graph Construction Layer
NetworkX (Graph Model)
↓
Visualization Layer
PyVis (Interactive Graph)
↓
Analysis Layer
Pandas + Streamlit Charts
```



## Current Features

### NLP Processing

* 🔍 Named Entity Recognition (NER)
* 🧠 Dependency parsing for relation extraction
* 🔗 Subject–Verb–Object extraction
* 🔁 Basic pronoun handling (he/she → previous subject)

### Graph Generation

* 🌐 Interactive knowledge graph
* 🎨 Color-coded nodes (Person, Organization, Location)
* 🔄 Curved edges to avoid overlap
* ➡️ Directed relationships

### User Interface

* 💻 Streamlit-based GUI
* ✏️ Custom user input
* 📋 Tabular relation display
* 📊 Real-time statistics and charts

### Analysis

* 📊 Relation frequency visualization
* 📈 Entity count tracking
* 📉 Structured output for reporting



## Example

User input:

```text
Shivam works at IBM and he was born in Delhi
```

Generated knowledge:

```text
Shivam → works at → IBM
Shivam → born in → Delhi
```



## Visual Output

* Interactive knowledge graph
* Entity-relation table
* Statistical charts
  <img width="1786" height="374" alt="image" src="https://github.com/user-attachments/assets/603ff03d-eacb-472f-afab-568443a85c1d" />
  <img width="881" height="497" alt="image" src="https://github.com/user-attachments/assets/bd2b9c1d-f0a0-4ded-957d-ebb026bd4620" />
  <img width="1757" height="442" alt="image" src="https://github.com/user-attachments/assets/a7580b7a-1b30-4343-8869-3ea4cb1b6983" />






## Tech Stack

* Python 3.x
* spaCy (NLP processing)
* NetworkX (graph construction)
* PyVis (graph visualization)
* Streamlit (GUI)
* Pandas (data analysis)



## Project Structure

```text
nlp-knowledge-graph-generator/

app.py              # Main Streamlit application
main.py             # Core NLP logic (optional)
sample.txt          # Example input data
requirements.txt    # Dependencies
output/             # Generated graph files
```



## How to Run

### 1. Clone Repository



### 2. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```



### 3. Run Application

```bash
streamlit run app.py
```



## NLP Concepts Used

* Named Entity Recognition (NER)
* Dependency Parsing
* Relation Extraction
* Knowledge Graph Construction



## Limitations

* Some relations rely on rule-based enhancements
* Complex sentence structures may not be fully captured
* Small NLP model may misclassify entities



## Future Improvements

### Phase 1

* Improved relation extraction
* Better pronoun resolution
* Enhanced visualization

### Phase 2

* Transformer-based models (BERT, GPT)
* Coreference resolution
* Multi-document knowledge graphs

### Phase 3

* Automated knowledge base generation
* Real-time data integration
* Advanced reasoning capabilities



## Vision

This project aims to demonstrate how NLP can be used to:

* Transform unstructured text into structured knowledge
* Build intelligent systems for information extraction
* Enable visual understanding of relationships in data



## Author

**Sagar Chandra**


## License

MIT License
