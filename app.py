from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import tempfile
from urllib.parse import urlparse, urlunparse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    quality = request.form.get('quality', 'default')
    custom_bitrate = request.form.get('custom_bitrate', '')

    # Limpiar URL: quitar parámetros extra
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
        kbps = custom_bitrate if custom_bitrate else '192'

    # Carpeta temporal
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': kbps
        }],
        'noplaylist': True,  # evitar playlists
        'quiet': True,       # menos logs
    }

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
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass

        return response

    except yt_dlp.utils.DownloadError as de:
        return f"No se pudo descargar el video: {de}"
    except Exception as e:
        return f"Ocurrió un error inesperado: {e}"

if __name__ == '__main__':
    app.run(debug=True)