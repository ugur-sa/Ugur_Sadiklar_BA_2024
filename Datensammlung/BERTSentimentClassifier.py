from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import sqlite3

# ProsusAI/finbert
# mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis
# Sigma/financial-sentiment-analysis
model_name = "ProsusAI/finbert"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Verbinde mit der Datenbank
conn = sqlite3.connect("sentiment.db")
c = conn.cursor()

# Abrufen aller Sätze, die in der sentences Tabelle sind
c.execute("SELECT * FROM sentences")
rows = c.fetchall()

for row in rows:
    id = row[0]
    sentence_text = row[2]

    # Tokenisiere den Satz
    inputs = tokenizer(sentence_text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Wende das Modell an
    with torch.no_grad():
        outputs = model(**inputs)

    # Hole die Modellvorhersagen
    predictions = outputs.logits

    # Konvertiere Vorhersagen in Wahrscheinlichkeiten und hole das maximale
    predictions = torch.nn.functional.softmax(predictions, dim=1)
    predicted_class = torch.argmax(predictions).item()

    # Behalte die Wahrscheinlichkeit für die Vorhersage
    predicted_probability = predictions.flatten()[predicted_class].item()

    # Klassen sind für FinBERT in umgekehrter Reihenfolge
    classesFINBERT = ["bullish", "bearish", "neutral"]
    classes = ["bearish", "neutral", "bullish"]

    # Update der Spalten _result und _score für jedes Modell, aber nur 3 Dezimalstellen für _score
    c.execute("UPDATE sentences SET finbert_result = ?, finbert_score = ? WHERE id = ?", (classesFINBERT[predicted_class], round(predicted_probability, 3), id))
    if(id % 100 == 0):
        print(id) # Fortschrittsanzeige

conn.commit()
conn.close()