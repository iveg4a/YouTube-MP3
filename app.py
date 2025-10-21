from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import tempfile
from urllib.parse import urlparse, urlunparse
import shutil

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    quality = request.form.get('quality', 'default')
    custom_bitrate = request.form.get('custom_bitrate', '')

    # Limpiar URL (quitar parámetros extra)
    parsed_url = urlparse(url)
    clean_url = urlunparse(parsed_url._replace(query=''))

    # Validar bitrate personalizado
    if quality == 'custom':
        try:
            kbps = int(custom_bitrate)
            if not (1 <= kbps <= 320):
                return "Introduce un valor de 1 a 320 kbps."
        except:
            return "Valor de calidad inválido."
    else:
        kbps = quality if quality != 'highest' else '0'  # 0 = mejor calidad

    # Carpeta temporal
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

    # Revisar si se subió cookies.txt
    cookies_file = None
    if 'cookies' in request.files:
        file = request.files['cookies']
        if file.filename != '':
            cookies_path = os.path.join(temp_dir, 'cookies.txt')
            file.save(cookies_path)
            cookies_file = cookies_path

    # Opciones de yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': kbps
        }],
        'noplaylist': True,
        'quiet': True,
    }

    if cookies_file:
        ydl_opts['cookiefile'] = cookies_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            title = info.get('title', 'audio')
            mp3_file = os.path.join(temp_dir, f"{title}.mp3")

        if not os.path.exists(mp3_file):
            return "No se pudo generar el MP3."

        # Enviar archivo al navegador
        response = send_file(mp3_file, as_attachment=True, download_name=f"{title}.mp3")

        # Limpiar temporal después de enviar
        @response.call_on_close
        def cleanup():
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

        return response

    except yt_dlp.utils.DownloadError as de:
        return f"No se pudo descargar el video: {de}"
    except Exception as e:
        return f"Ocurrió un error inesperado: {e}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)