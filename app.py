import streamlit as st
import sqlite3
import os
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ---------------------------
# Get Available Models
# ---------------------------
def get_available_models():
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    response = requests.get(url)
    return response.json()


# ---------------------------
# Gemini Call (Auto Model)
# ---------------------------
def get_gemini_response(question, prompt):
    models_data = get_available_models()

    if "models" not in models_data:
        return models_data  # show error if any

    # Pick first available model that supports generateContent
    model_name = None
    for model in models_data["models"]:
        if "generateContent" in model.get("supportedGenerationMethods", []):
            model_name = model["name"]
            break

    if not model_name:
        return {"error": "No suitable model found"}

    full_prompt = prompt + "\n" + question

    url = f"https://generativelanguage.googleapis.com/v1/{model_name}:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    return response.json()


# ---------------------------
# Execute SQL
# ---------------------------
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows


# ---------------------------
# Prompt
# ---------------------------
prompt = """
You are an expert in converting English questions to SQL query!
The SQL database has the name STUDENT and has the following columns - NAME, CLASS, SECTION.

Example 1:
How many entries of records are present?
SELECT COUNT(*) FROM STUDENT;

Example 2:
Tell me all the students studying in Data Science class?
SELECT * FROM STUDENT WHERE CLASS="Data Science";

Return ONLY SQL query.
"""

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Text to SQL Debug App")
st.header("Gemini Text-to-SQL App")

question = st.text_input("Enter your question:")
submit = st.button("Generate SQL")

if submit and question:
    result = get_gemini_response(question, prompt)

    st.subheader("Raw API Response:")
    st.write(result)

    # If valid response
    if "candidates" in result:
        sql_query = result["candidates"][0]["content"]["parts"][0]["text"]
        sql_query = sql_query.replace("```", "").replace("sql", "").strip()

        st.subheader("Generated SQL Query:")
        st.code(sql_query)

        try:
            data = read_sql_query(sql_query, "student.db")
            st.subheader("Query Result:")
            st.write(data)
        except Exception as e:
            st.error(f"SQL Error: {e}")
