from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure the LLM model client
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found! Please set the GOOGLE_API_KEY in your environment.")

genai.configure(api_key=api_key)

# Initialize the LLM model and chat session
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(prompt):
    try:
        response = chat.send_message(prompt, stream=False)
        return response.text.strip() if response else "No response received."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            # Capture form inputs
            name = request.form.get('name')
            email = request.form.get('email')
            physical_environment = request.form.get('physical_environment')
            technology_usability = request.form.get('technology_usability')
            collaboration_tools = request.form.get('collaboration_tools')
            wellness_programs = request.form.get('wellness_programs')
            managerial_support = request.form.get('managerial_support')

            # Validate input data
            if not all([name, email, physical_environment, technology_usability, collaboration_tools, wellness_programs, managerial_support]):
                return jsonify({'error': 'All fields are required.'})

            # Ensure ratings are between 1 and 5
            ratings = [physical_environment, technology_usability, collaboration_tools, wellness_programs, managerial_support]
            for rating in ratings:
                if not (1 <= int(rating) <= 5):
                    return jsonify({'error': "Please enter a rating between 1 and 5 for all fields."})

            # Prepare prompt for the AI model based on user input
            prompt = (
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Physical Environment Rating: {physical_environment}\n"
                f"Technology Usability Rating: {technology_usability}\n"
                f"Collaboration Tools Rating: {collaboration_tools}\n"
                f"Wellness Programs Rating: {wellness_programs}\n"
                f"Managerial Support Rating: {managerial_support}\n"
                f"Generate a workplace score out of 5 and suggestions for improvement based on the survey data."
            )

            # Get AI response
            ai_response_text = get_gemini_response(prompt)

            # Remove the "Your Workplace Score: /5" line and reformat the response
            ai_response_lines = ai_response_text.split("\n")
            workplace_score = ai_response_lines[0]  # First line should be the score
            suggestions = ai_response_lines[1:]  # Remaining lines should be suggestions

            # Return AI response as JSON
            return jsonify({
                'workplace_score': workplace_score,
                'suggestions': suggestions
            })

        except Exception as e:
            return jsonify({'error': str(e)})

    return render_template('kunal.html')

if __name__ == '__main__':
    app.run(debug=True)
