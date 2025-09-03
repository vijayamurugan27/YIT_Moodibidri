from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
todos = []

@app.route('/')
def index():
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    name = request.form['name']
    dept = request.form['dept']
    # college = request.form['college']
    details = [name, dept]
    todos.append(details)
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_todo(index):
    try:
        del todos[index]
    except IndexError:
        pass
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
