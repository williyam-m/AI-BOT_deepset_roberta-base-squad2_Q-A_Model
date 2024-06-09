from flask import Flask, render_template, request, session
from flask_wtf import CSRFProtect
from transformers import pipeline
import os

app = Flask(__name__)


app.secret_key = b'_53oi3uriq9pifpff;apl'
csrf = CSRFProtect(app)


conversation_history = []

model_name = "deepset/roberta-base-squad2"

nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        conversation_history.append(["Bot", "Sorry, only text (.txt) file format is allowed."])
        return render_template('question-answer.html', value = conversation_history)

    file = request.files['file']

    if file.filename == '':
        conversation_history.append(["Bot", "Sorry, only text (.txt) file format is allowed."])
        return render_template('question-answer.html', value = conversation_history)

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        context = read_text_file(filename)

        session['context'] = context
        session['filename'] = file.filename

        conversation_history.clear()  # Clear previous conversation history
        conversation_history.append(["Bot", f"File '{file.filename}' uploaded successfully. You can now ask questions."])

        return render_template('question-answer.html', value = conversation_history)
    else:
        return render_template('question-answer.html', value = conversation_history)


def read_text_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read()


@app.route('/ask-question-answer', methods=['POST'])
def ask():

    if request.method == 'POST':

        input_text = request.form['input']
        conversation_history.append(["You", input_text])

        context = session.get('context', '')

        if not context:
            answer = "Please upload a file first."
        else:
            QA_input = {"question": str(input_text),
                        "context": context}

            response = nlp(QA_input)

            answer = response.get('answer', 'No answer found')

        conversation_history.append(["Bot", answer])

        return render_template('question-answer.html', value = conversation_history)


@app.route('/question-answer')
def question_answer():

    return render_template('question-answer.html', value = conversation_history)

@app.route('/')
def home():

    return render_template('home.html', value='')




if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

