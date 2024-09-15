from flask import Flask, request, jsonify
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from flask_cors import CORS
from cryptography.fernet import Fernet
import os


model_name = "deepset/roberta-base-squad2"

# a) Get predictions
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

def decrypt_text(encrypted_text, cipher):
    return cipher.decrypt(encrypted_text.encode()).decode()

def read_and_decrypt_file(cipher, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        encrypted_texts = file.readlines()
        decrypted_texts = [decrypt_text(encrypted_text.strip(), cipher) for encrypted_text in encrypted_texts]
    return "\n".join(decrypted_texts)

def save_key(key, key_file='secret.key'):
    with open(key_file, 'wb') as file:
        file.write(key)

def load_key(key_file):
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        save_key(key, key_file)
    else:
        with open(key_file, 'rb') as file:
            key = file.read()
    return key

# context = "My name is Ahmad
# I have a dgree in Software Engineering
# My specialty is Python programming
# I use Flask to build web applications"


app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return("<h1>API is Working</h1>")

@app.route('/docs', methods=['GET'])
def docs():
    # docs_list = [
    #     {"id" : 1, "name" : "tooba teaching resume"},
    #     {"id" : 2, "name" : "tooba resume"}
    # ]
    # return jsonify(docs_list)
    docs_list = []
    if os.path.exists('docs_info.txt'):
        with open('docs_info.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i, line in enumerate(lines, start=1):
                doc_name = line.strip()  # Remove any surrounding whitespace or newline characters
                docs_list.append({"id": i, "name": doc_name})
    else:
        print("docs_info.txt file not found.")
    
    return docs_list

@app.route('/chat', methods=['POST'])
def chat():
    question = request.form["question"]
    document_name = request.form["option"]
    document_name_context = document_name + "_data.txt"
    document_name_cipher = document_name + "_secret.key"
    key = load_key(document_name_cipher)
    cipher = Fernet(key)
    context = read_and_decrypt_file(cipher, document_name_context)

    # context = request.form["context"]
    QA_input = {
        'question': question,
        'context': context
    }
    res = nlp(QA_input)
    print(res)
    if res['start'] > 70:
        return res["answer"] + ""
    
    if res['start'] < 70:
        return res["answer"] + ""
    
    return res["answer"]

if __name__ == '__main__':
    app.run(debug=True)
"""

from flask import Flask, request, jsonify
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from flask_cors import CORS
from cryptography.fernet import Fernet
import os

model_name = "deepset/roberta-base-squad2"

# Initialize the question-answering pipeline
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

def decrypt_text(encrypted_text, cipher):
    return cipher.decrypt(encrypted_text.encode()).decode()

def read_and_decrypt_file(cipher, file_path='user_data.txt'):
    with open(file_path, 'r', encoding='utf-8') as file:
        encrypted_texts = file.readlines()
        decrypted_texts = [decrypt_text(encrypted_text.strip(), cipher) for encrypted_text in encrypted_texts]
    return "\n".join(decrypted_texts)

def save_key(key, key_file='secret.key'):
    with open(key_file, 'wb') as file:
        file.write(key)

def load_key(key_file='secret.key'):
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        save_key(key, key_file)
    else:
        with open(key_file, 'rb') as file:
            key = file.read()
    return key

key = load_key()
cipher = Fernet(key)

context = read_and_decrypt_file(cipher)

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return("<h1>API is Working</h1>")

def chunk_context(context, max_length=512, overlap=50):
    Splits the context into chunks with overlap.
    chunks = []
    context_length = len(context)
    start = 0
    while start < context_length:
        end = min(start + max_length, context_length)
        chunk = context[start:end]
        chunks.append(chunk)
        start += max_length - overlap
    return chunks

@app.route('/chat', methods=['POST'])
def chat():
    question = request.form["question"]

    # Split context into chunks
    context_chunks = chunk_context(context, max_length=512, overlap=50)

    best_answer = None
    best_score = 0

    # Iterate through each chunk
    for chunk in context_chunks:
        QA_input = {
            'question': question,
            'context': chunk
        }
        res = nlp(QA_input)
        print(res)
        if res['score'] > best_score:
            best_score = res['score']
            best_answer = res

    # Reference based on the start position
    if best_answer['start'] > 70:
        return best_answer["answer"] + " (Ref: ahmad resume)"
    
    if best_answer['start'] < 70:
        return best_answer["answer"] + " (Ref: ahmad Biodata)"
    
    return best_answer["answer"]

if __name__ == '__main__':
    app.run(debug=True)

"""



