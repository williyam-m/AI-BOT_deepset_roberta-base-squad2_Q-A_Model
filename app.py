from flask import Flask, render_template, request
from flask_wtf import CSRFProtect
from transformers import pipeline

app = Flask(__name__)


app.secret_key = b'_53oi3uriq9pifpff;apl'
csrf = CSRFProtect(app)


conversation_history = []

model_name = "deepset/roberta-base-squad2"

nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

def read_text_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read()


@app.route('/ask-question-answer', methods=['POST'])
def ask():

    if request.method == 'POST':

        input_text = request.form['input']
        conversation_history.append(["You", input_text])

        context = read_text_file("./dsa_question-answer.txt")

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
    app.run(debug=True)

