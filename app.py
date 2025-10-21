from flask import Flask, render_template, request, send_file
import os
import subprocess
import tempfile
import glob
import shutil

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    quality = request.form.get("quality")
    custom_quality = request.form.get("customQuality")

    # Validar calidad personalizada
    if quality == "custom":
        try:
            kbps = int(custom_quality)
            if not (1 <= kbps <= 320):
                return "Por favor, introduce un valor entre 1 y 320 kbps."
        except:
            return "Valor de calidad inválido."
    else:
        kbps = quality if quality != "best" else "0"  # 0 = mejor calidad

    # Crear directorio temporal único
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

    # Comando yt-dlp
    if kbps == "0":
        cmd = ["yt-dlp", "-f", "bestaudio", "-x", "--audio-format", "mp3", "-o", output_template, url]
    else:
        cmd = ["yt-dlp", "-f", "bestaudio", "-x", "--audio-format", "mp3", "--audio-quality", str(kbps), "-o", output_template, url]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        shutil.rmtree(temp_dir)  # limpiar temporal
        return "No se pudo descargar el video. Verifica la URL."

    # Buscar el archivo MP3 generado
    mp3_files = glob.glob(os.path.join(temp_dir, "*.mp3"))
    if not mp3_files:
        shutil.rmtree(temp_dir)
        return "No se pudo generar el MP3."

    mp3_path = mp3_files[0]

    # Enviar el archivo al navegador
    response = send_file(mp3_path, as_attachment=True)

    # Limpiar el directorio temporal después de enviar
    @response.call_on_close
    def cleanup():
        shutil.rmtree(temp_dir)

    return response

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))