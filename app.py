import streamlit as st
import openai
import requests
import json

# Debug: Confirm the app is starting
st.write("App started!")

# Configure your OpenAI API key (adjust as needed)
# openai.api_key = st.secrets["openai"]["api_key"]   # or: os.getenv("OPENAI_API_KEY")

# Transaction API endpoint
TRANSACTION_API_URL = "http://13.51.243.214:3000/api/v1/wariportal/transactions"

# Function to fetch transaction data from the API
def fetch_transactions():
    st.write("Fetching transaction data...")
    try:
        response = requests.get(TRANSACTION_API_URL)
        st.write(f"API response status: {response.status_code}")
        if response.status_code == 200:
            st.write("Transaction data fetched successfully.")
            return response.json()  # Expected JSON structure as shown in your sample output
        else:
            st.error(f"Error fetching transactions: {response.status_code} {response.text}")
            return None
    except Exception as e:
        st.error(f"Exception fetching transactions: {e}")
        return None

# Function to call OpenAI's API with a given prompt
def query_openai(prompt):
    st.write("Querying OpenAI...")
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # or your preferred engine
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )
        st.write("OpenAI response received.")
        return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"Error with OpenAI API: {e}")
        return "There was an error processing your request."

# App title and role selection
st.title("AI Agent for Transaction Insights")

# Role selection radio button
role = st.radio("Select your role:", ["Employee", "Client"])
st.write(f"Role selected: {role}")

if role == "Employee":
    st.subheader("Employee Query")
    employee_query = st.text_input("Ask a question about transactions (e.g., 'How many transactions in September 2024?')", key="emp_query")
    
    if st.button("Submit Employee Query", key="employee"):
        st.write("Employee query submitted.")
        transactions_data = fetch_transactions()
        if transactions_data:
            # Pass only a truncated sample of the data to avoid hitting token limits
            sample_data = json.dumps(transactions_data, indent=2)[:1000]
            prompt = (
                f"You are an AI agent with access to transaction data. "
                f"Here is a sample of the transaction data:\n\n{sample_data}\n\n"
                f"Answer the following question in detail:\n{employee_query}"
            )
            answer = query_openai(prompt)
            st.markdown("**Answer:**")
            st.write(answer)
        else:
            st.error("No transaction data available.")

elif role == "Client":
    st.subheader("Client Query")
    client_name = st.text_input("Enter your name (as it appears in merchantDisplayName):", key="client_name")
    client_query = st.text_input("Ask your question about your transactions (e.g., 'When is my current transaction due?')", key="client_query")
    
    if st.button("Submit Client Query", key="client"):
        st.write("Client query submitted.")
        transactions_data = fetch_transactions()
        if transactions_data:
            # Filter transactions for the client name (case insensitive)
            client_transactions = [
                tx for tx in transactions_data.get("data", [])
                if tx.get("merchantDisplayName", "").strip().lower() == client_name.strip().lower()
            ]
            if not client_transactions:
                st.warning("No transactions found for that name.")
            else:
                prompt = (
                    f"You are an AI agent. The following transactions belong to the client '{client_name}':\n\n"
                    f"{json.dumps(client_transactions, indent=2)}\n\n"
                    f"Answer the following question in detail:\n{client_query}"
                )
                answer = query_openai(prompt)
                st.markdown("**Answer:**")
                st.write(answer)
        else:
            st.error("No transaction data available.")
