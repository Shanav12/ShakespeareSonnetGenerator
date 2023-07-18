# import requirements needed
import os

# import stuff for our web server
from flask import Flask, request, redirect, url_for, render_template, session
from utils import get_base_url
import requests

# setup the webserver
# port may need to be changed if there are multiple flask servers running on same server
port = 12345
base_url = get_base_url(port)

# if the base url is not empty, then the server is running in development, and we need to specify the static folder so that the static files are served
if base_url == '/':
  app = Flask(__name__)
else:
  app = Flask(__name__, static_url_path=base_url + 'static')

app.secret_key = os.urandom(64)


@app.route(f'{base_url}')
def home():
  return render_template('index.html', generated=None)


@app.route(f'{base_url}', methods=['POST'])
def home_post():
  return redirect(url_for('results'))


@app.route(f'{base_url}/results/')
def results():
  if 'data' in session:
    data = session['data']
    return render_template('results.html', generated=data)
  else:
    return render_template('results.html', generated=None)

# Setting the URL to the HuggingFace API to call our model
API_URL = "https://api-inference.huggingface.co/models/Shanav12/gpt2-sonnets"
headers = {"Authorization": "Bearer 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"}


# Sending a post request to the API and returning its response
def query(payload):
  response = requests.post(API_URL, headers=headers, json=payload)
  return response.json()


# Displaying the output of the model
@app.route(f'{base_url}/generate_text/', methods=["POST"])
def generate_text():
  user_input = request.form['prompt']

  # Specifiying hyperparamters
  payload = {
    "inputs": user_input,
    "parameters": {
      "top_p": 0.75,
      "top_k": None,
      "max_length": 150,  # Allows for longer sonnet responses while ensuring that the responses are sensible
      "temperature": 1.0,
      "repetition_penalty": 5  # Preventing the output from rambling on
    },
    "options" : {
      "use_cache":
      False, # Does not use previously cached responses that are similar
      "wait_for_model":
      True   # Waits for the response from the model rather than returning prior to the model loading
    }
  }
  json_output = query(payload)
  model_response = json_output[0]['generated_text']
  return render_template('results.html', generated=model_response)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=port, debug=True)
