from flask import Flask, render_template, request
from plantuml_parser import parse_plantuml_to_sql

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        plantuml_code = request.form['plantuml_code']
        sql_output = parse_plantuml_to_sql(plantuml_code)
        return render_template('index.html', sql_output=sql_output)
    return render_template('index.html', sql_output=None)

if __name__ == '__main__':
    app.run(debug=True)
