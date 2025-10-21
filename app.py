import os

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    quality = request.form.get('quality')
    custom_quality = request.form.get('custom_quality')

    # Por ahora solo mostramos los datos ingresados
    return f"URL: {url} | Calidad elegida: {quality} | Calidad personalizada: {custom_quality}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))