# 🌾 Project Samarth – Intelligent Agri Q&A System (MVP)

Project Samarth is a **Natural Language Processing (NLP)-powered Question & Answer system** that provides actionable insights from agricultural market data (Agmarknet) and climate data (IMD).  
It enables policymakers, researchers, and farmers to ask **natural language questions** like:

> “What is the tomato price trend in Karnataka this month?”  
> “Which market has the highest onion price?”  
> “Show me the latest rate of potato in Delhi.”

---

## 🧠 Features
✅ **NLP-Enabled Q&A:** Understands natural questions about prices, commodities, markets, and trends.  
✅ **Dynamic Data Refresh:** Fetches and cleans real-time agricultural data.  
✅ **Visual Insights:** Generates trend charts for commodity prices.  
✅ **Lightweight & Fast:** Uses pandas + spaCy for efficient processing.  
✅ **Streamlit Frontend:** Simple interactive UI for user-friendly querying.

---

## 🏗️ Project Structure
Project-Samarth/
│
├── data/
│ ├── mandi_data.json # Raw Agmarknet data
│ ├── mandi_clean.csv # Cleaned & processed data
│ ├── trend.png # Generated price trend chart
│
├── src/
│ ├── api_fetch.py # Fetch Agmarknet & IMD data
│ ├── data_process.py # Clean & aggregate mandi data
│ ├── nlp_qa_system.py # Core NLP-based Q&A system
│ ├── app.py # Streamlit frontend app
│
├── requirements.txt
└── README.md


---

## 🚀 How to Run Locally

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Project-Samarth.git
cd Project-Samarth/src

2️⃣ Create Virtual Environment

python -m venv venv
venv\Scripts\activate       # On Windows
# OR
source venv/bin/activate    # On Linux/Mac

3️⃣ Install Dependencies

pip install -r requirements.txt
python -m spacy download en_core_web_sm

4️⃣ Run Data Processing

python data_process.py

5️⃣ Launch the App

streamlit run app.py

Then open your browser at http://localhost:8501

🧪 Working Prototype

👉 Try it Live on Streamlit Cloud

(Replace this link after deployment)


🧰 Tech Stack

Python 3.9+

Streamlit – UI

spaCy – NLP Entity Recognition

pandas, numpy – Data processing

matplotlib – Visualizations

🧩 Example Queries
Type	Example Question
💰 Price	“What is the price of onion in Maharashtra?”
📈 Trend	“Show the price trend of tomato in Karnataka.”
🏪 Highest	“Which market has the highest potato price?”
📉 Lowest	“Where is wheat cheapest?”
📆 Time-based	“What was the average rice price last month?”
🎥 Demo Video

🎬 Watch the Loom demo here → (https://www.loom.com/share/d7592bba956447438fe9391c3e5896ff)

In this demo:

The app answers live price and trend questions.

Data is refreshed and cleaned automatically.

Visual charts and smart NLP understanding are showcased.


🏁 Future Enhancements

Integrate rainfall correlation (IMD data)

Support multilingual queries (Hindi, Kannada, etc.)

Advanced model fine-tuning using BERT-based QA


👨‍💻 Author

Vivek Y
📍 Bangalore, India
📧 Email: viveky9740@gmail.com