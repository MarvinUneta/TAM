from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import google.generativeai as genai

# Flask setup
app = Flask(__name__)
CORS(app)

# Configure the Google Generative AI SDK
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))  # Ensure this is set in your environment

# Store conversation history in a global variable
user_history = {}

def generate_ai_response(user_input, user_id):
    generation_config = {
        "temperature": 2,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 3000,  # Adjust based on your needs
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=("Your name is Tam. Your job is to provide gaming pc recommendation for gamers. You need to ask the user his/her budget. Once the user inputs their budget, ask the user what games are going to be played. Include a monitor and the necessary peripherals in the pc build. You need to use Philippine peso currency. You must maximize the budget that the user provides. Be sure that your calculations for the total prices of the pc parts are correct. Give the name of the store for each source of the pc parts not online shopping links. You could recommend second-hand products if the user provides a low budget. Provide adjustments to the PC build if the game bottlenecks with the budget that has been provided by the user. Always provide dual sticks of RAM or more. You must not recommend a PC build that exceeds the budget provided by the user. Provide the benchmark. You could recommend a 720p cheap monitor to fit within the budget. Display the total amount of the pc parts."),
    )

    # Start chat session or continue the existing one
    chat_session = model.start_chat(history=user_history.get(user_id, []))
    response = chat_session.send_message(user_input)

    # Update the user's chat history
    user_history[user_id] = chat_session.history
    return response.text

# Home route to serve the HTML page
@app.route('/')
def index():
    return render_template('tam.html')  # Ensure 'tam.html' is in the 'templates' folder

# Chat route to handle user input and return AI response
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')
    user_id = data.get('user_id', 'default_user')  # Identify the user

    # Get AI response from the generative AI model
    response_text = generate_ai_response(user_input, user_id)

    # Return the response in JSON format
    return jsonify({"response": response_text})

# Route to clear the chat history for a user
@app.route('/clear_history', methods=['POST'])
def clear_history():
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')  # Identify the user

    # Clear the history for the specific user
    if user_id in user_history:
        del user_history[user_id]
    
    return jsonify({"response": "History cleared."})

if __name__ == '__main__':
    app.run(debug=True)
