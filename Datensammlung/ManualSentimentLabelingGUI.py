import tkinter as tk
from tkinter import messagebox
import sqlite3

class SentimentLabeler(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sentiment Labeler")
        self.geometry("600x300")  # Adjust size as needed

        self.sentence_label = tk.Label(self, text="", wraplength=550)
        self.sentence_label.pack(pady=10)

        self.model_results_label = tk.Label(self, text="", wraplength=550)
        self.model_results_label.pack(pady=10)

        # Buttons for sentiment
        tk.Button(self, text="Bullish", command=lambda: self.update_label("bullish")).pack(side=tk.LEFT, padx=10)
        tk.Button(self, text="Bearish", command=lambda: self.update_label("bearish")).pack(side=tk.LEFT, padx=10)
        tk.Button(self, text="Neutral", command=lambda: self.update_label("neutral")).pack(side=tk.LEFT, padx=10)

        self.sentences = []
        self.current_index = 0
        self.load_sentences()
        self.display_sentence()

    def load_sentences(self):
        # Connect to the database and fetch all sentences with 'manual' label
        try:
            conn = sqlite3.connect('../sentiment.db')
            cursor = conn.cursor()
            # Adjust the SQL query to include the model result columns
            cursor.execute("SELECT id, sentence_text, finbert_result, finbert_score, dffnsa_result, dffnsa_score, fsa_result, fsa_score FROM sentences WHERE final_sentiment = 'manual'")
            self.sentences = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def display_sentence(self):
        # Display the current sentence and model results, or a completion message if done
        if self.current_index < len(self.sentences):
            row = self.sentences[self.current_index]
            self.current_id = row[0]
            sentence_text = row[1]
            model_results = f"FinBERT: {row[2]} (Score: {row[3]}), DFFNSA: {row[4]} (Score: {row[5]}), FSA: {row[6]} (Score: {row[7]})"
            
            self.sentence_label.config(text=sentence_text)
            self.model_results_label.config(text=model_results)
        else:
            self.sentence_label.config(text="No more sentences to label.")
            self.model_results_label.config(text="")
            self.current_id = None

    def update_label(self, sentiment):
        if self.current_id:
            try:
                # Connect to the database
                conn = sqlite3.connect('sentiment.db')
                cursor = conn.cursor()

                # Update the row with the label
                cursor.execute("UPDATE sentences SET final_sentiment = ? WHERE id = ?", (sentiment, self.current_id))
                # print(self.current_id, sentiment)
                conn.commit()
                # messagebox.showinfo("Info", f"Sentence labeled as {sentiment}")
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

            # Move to the next sentence
            self.current_index += 1
            self.display_sentence()
        else:
            messagebox.showwarning("Warning", "No sentence to label or end of data reached.")

if __name__ == "__main__":
    app = SentimentLabeler()
    app.mainloop()
