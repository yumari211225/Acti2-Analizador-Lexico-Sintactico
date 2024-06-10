from flask import Flask, request, render_template
import re

app = Flask(__name__)

# Definición de tokens para el analizador léxico
tokens = {
    'PR': r'\b(for|if|else|while|return)\b',
    'ID': r'\b[a-zA-Z_][a-zA-Z_0-9]*\b',
    'NUM': r'\b\d+\b',
    'SYM': r'[;{}()\[\]=<>!+-/*]',
    'ERR': r'.'
}

def analyze_lexical(code):
    results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    rows = []
    for line in code.split('\n'):
        row = [''] * 5
        for token_name, token_pattern in tokens.items():
            for match in re.findall(token_pattern, line):
                results[token_name] += 1
                row[list(tokens.keys()).index(token_name)] = 'x'
        rows.append(row)
    return rows, results

def correct_syntactic(code):
    corrected_code = re.sub(r'\bfor\s*\(\s*.*\s*\)\s*\{', r'for (int i = 1; i <= 19; i++) {', code)
    corrected_code = re.sub(r'\{.*\}', r'{\n    System.out.println("hola");\n}', corrected_code, flags=re.DOTALL)
    return corrected_code

def correct_semantic(code):
    corrected_code = re.sub(r'\bSystem\.out\.println\s*\(.*\)\s*;', r'System.out.println("hola");', code)
    return corrected_code

def analyze_syntactic(code):
    corrected_code = code
    errors = []

    if not re.search(r'\bfor\s*\(\s*int\s+\w+\s*=\s*\d+\s*;\s*\w+\s*<=\s*\d+\s*;\s*\w+\+\+\s*\)\s*\{', code):
        errors.append("Error en la sintaxis del bucle 'for'. Asegúrate de declarar el tipo de variable correctamente, por ejemplo: 'for (int i = 1; i <= 19; i++) {'.")
        corrected_code = correct_syntactic(corrected_code)

    if not re.search(r'\{\s*\n\s*System\.out\.println\s*\(\s*".*"\s*\)\s*;\s*\n\s*\}', code):
        errors.append("Error en el cuerpo del bucle 'for'. Asegúrate de usar 'System.out.println()' correctamente y de que las llaves estén bien colocadas.")
        corrected_code = correct_syntactic(corrected_code)

    if not errors:
        return "Sintaxis correcta", corrected_code
    else:
        return " ".join(errors), corrected_code

def analyze_semantic(code):
    errors = []
    if not re.search(r'\bSystem\.out\.println\s*\(\s*".*"\s*\)\s*;', code):
        errors.append("Error semántico en System.out.println. Asegúrate de usar 'System.out.println()' correctamente con comillas dobles para las cadenas.")
        corrected_code = correct_semantic(code)
    else:
        corrected_code = code

    if not errors:
        return "Uso correcto de System.out.println", corrected_code
    else:
        return " ".join(errors), corrected_code

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ''
    lexical_results = []
    total_results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    syntactic_result = ''
    semantic_result = ''
    corrected_code = ''
    if request.method == 'POST':
        code = request.form['code']
        lexical_results, total_results = analyze_lexical(code)
        syntactic_result, corrected_code = analyze_syntactic(code)
        semantic_result, corrected_code = analyze_semantic(corrected_code)
    return render_template('index.html', code=code, lexical=lexical_results, total=total_results, syntactic=syntactic_result, semantic=semantic_result, corrected_code=corrected_code)

if __name__ == '__main__':
    app.run(debug=True)
