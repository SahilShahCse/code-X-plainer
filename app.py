from flask import Flask, render_template, request, redirect, url_for, flash
import re
import ast
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).decode('latin-1')  # Ensures secure sessions

def check_syntax(code, language):
    if language == 'python':
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax Error: {str(e)}"
    # NOTE i have checked for syntax error for python - check for java , c , c++ and more...
    return True, ""

def break_code(code):
    # Regex pattern to extract tokens including comments, strings, and various symbols
    pattern = r'\".*?\"|\'.*?\'|\/\/.*?$|\/\*[\s\S]*?\*\/|[A-Za-z_]\w*|[0-9]+|[.,<>?;:\"\'\\|\[\]{}()=!@#$%^&*\-+\/]'
    try:
        tokens = re.findall(pattern, code, re.MULTILINE)
        return list(set(tokens))  # Return unique tokens
    except Exception as e:
        return ["Error tokenizing code: " + str(e)]

def explain_token(token, language):
    # NOTE make it more perfect by adding more keywords
    explanations = {
        **{key: f"'{key}' : 'It is a keyword.'" for key in ["auto", "const", "extern", "register", "signed", "sizeof", "static", "typedef", "unsigned", "virtual", "delete", "inline", "mutable", "new", "java.io", "throw", "interface", "False", "True", "None", "and", "as", "from", "global", "in", "is", "lambda", "not", "or", "raise", "with", "yield"]},
        **{key: f"'{key}' : 'It is used to specify/include the libraries.'" for key in ["include"]},
        **{key: f"'{key}' : 'Input stream class.'" for key in ["System.in"]},
        **{key: f"'{key}': 'Print stream class.'" for key in ["System.out"]},
        **{op: f"'{op}' : 'Arithmetic operators.'" for op in ["+", "-", "*", "/", "%", "++", "--"]},
        **{op: f"'{op}' : 'Relational operators.'" for op in ["<", ">", "=", "==", "!=", "<=", ">="]},
        **{op: f"'{op}' : 'Logical operators.'" for op in ["&&", "||", "!"]},
        **{br: f"'{br}' : 'Is used for mathematical expressions and function calls.'" for br in ["(", ")"]},
        **{br: f"'{br}' : 'Is used to define arrays or lists.'" for br in ["[", "]"]},
        **{br: f"'{br}' : 'Is used to define dictionaries and code blocks.'" for br in ["{", "}"]},
    }
    return explanations.get(token, f"'{token}' : 'Unrecognized or variable identifier'.")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    language = request.form['language']
    code = request.form['code']
    syntax_ok, error = check_syntax(code, language)
    if not syntax_ok:
        flash(error)
        return redirect(url_for('index'))

    all_tokens = break_code(code)
    explanations = [explain_token(token, language) for token in sorted(all_tokens)]
    return render_template('results.html', explanations=explanations, language=language)

if __name__ == '__main__':
    app.run(debug=True)
