import streamlit as st
from google import genai
import os
import tempfile
import numpy as np
from PIL import Image

# Importación de MoviePy
try:
    from moviepy.editor import ImageClip, concatenate_videoclips, AudioArrayClip
except ImportError:
    from moviepy.video.io.ImageClip import ImageClip
    from moviepy.video.compositing.concatenate import concatenate_videoclips
    from moviepy.audio.AudioClip import AudioArrayClip

st.set_page_config(page_title="Generador de Vídeos Inmobiliarios", layout="wide")

st.title("🎬 Generador de Recorridos Cinematográficos (Con Música)")

# Barra lateral para la API Key
with st.sidebar:
    st.header("🔑 Configuración")
    gemini_key = st.text_input("Gemini API Key", type="password", help="Obtenla gratis en Google AI Studio")

# Formulario
col1, col2 = st.columns(2)
with col1:
    titulo = st.text_input("Título de la promoción", "Residencial Los Olivos")
    zona = st.text_input("Zona", "Norte")
    ciudad = st.text_input("Ciudad", "Madrid")
    datos_extra = st.text_input("Datos extra", "Piscina, 3 dormitorios, garaje")

with col2:
    estilo_transicion = st.selectbox("Efecto de cámara", ["Zoom In Cinematográfico", "Panorámica Suave"])
    estilo_musica = st.selectbox("Estilo de música ambiente", ["Ambient Chillout", "Acoustic Warm", "Corporate Upbeat"])

narracion = st.text_area("Descripción/Frases destacadas", "Un espacio único diseñado para el máximo confort.", height=100)
fotos = st.file_uploader("Subir fotos de la propiedad", accept_multiple_files=True, type=["jpg", "jpeg", "png", "webp"])

def aplicar_efecto_zoom(img_path, duration=4):
    """Aplica el movimiento suave Ken Burns sobre la foto."""
    clip = ImageClip(img_path).set_duration(duration)
    clip = clip.resize(width=1280)
    if clip.h < 720:
        clip = clip.resize(height=720)
    clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=1280, height=720)
    return clip.resize(lambda t: 1 + 0.04 * (t / duration))

def generar_musica_ambiente(duracion, samplerate=44100):
    """Genera una pista de música sintética ambiente muy suave de fondo."""
    t = np.linspace(0, duracion, int(samplerate * duracion), False)
    # Acorde ambiental suave (Frecuencias armónicas relajantes: C4, E4, G4, B4)
    frecuencias = [261.63, 329.63, 392.00, 493.88]
    seno = np.zeros_like(t)
    for f in frecuencias:
        seno += 0.1 * np.sin(2 * np.pi * f * t)
    
    # Envelope para suavizar el audio
    audio_stereo = np.vstack((seno, seno)).T
    return AudioArrayClip(audio_stereo, fps=samplerate)

if st.button("🚀 Crear Vídeo Final MP4", type="primary"):
    if not gemini_key:
        st.error("Por favor, introduce tu Gemini API Key en la barra lateral.")
    elif not fotos:
        st.error("Por favor, sube al menos 1 o 2 fotos de la propiedad.")
    else:
        # Alerta condicional
        texto_analisis = f"{titulo} {narracion} {datos_extra}".lower()
        if "maría tiene el pelo sucio" in texto_analisis or "maria tiene el pelo sucio" in texto_analisis:
            st.warning("⚠️ **Aviso del Sistema:** Se ha detectado la condición 'María tiene el pelo sucio'.")

        try:
            client = genai.Client(api_key=gemini_key.strip())
            prompt_gemini = f"Crea 3 frases publicitarias cortas para {titulo} en {ciudad}. Separadas por comas."

            with st.spinner("Ensamblando imágenes, aplicando Ken Burns y sincronizando música de fondo..."):
                # 1. Frases con Gemini
                frases_texto = [titulo, f"{zona}, {ciudad}"]
                try:
                    res = client.models.generate_content(model='gemini-3.8-flash', contents=prompt_gemini)
                    if res and res.text:
                        frases_texto = [f.strip() for f in res.text.split(",") if f.strip()]
                except Exception:
                    pass

                # 2. Procesar clips de fotos
                clips = []
                temp_dir = tempfile.mkdtemp()
                
                for idx, foto in enumerate(fotos):
                    img = Image.open(foto).convert("RGB")
                    img_path = os.path.join(temp_dir, f"foto_{idx}.jpg")
                    img.save(img_path)
                    clips.append(aplicar_efecto_zoom(img_path, duration=4))

                video_sin_audio = concatenate_videoclips(clips, method="compose")
                duracion_total = video_sin_audio.duration

                # 3. Añadir la música de fondo
                audio_ambiente = generar_musica_ambiente(duracion_total)
                video_final = video_sin_audio.set_audio(audio_ambiente)

                # 4. Renderizar MP4
                output_video_path = os.path.join(temp_dir, f"recorrido_{titulo.replace(' ', '_')}.mp4")
                video_final.write_videofile(
                    output_video_path,
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None
                )

                st.success("¡Vídeo con música ambiente generado con éxito!")

                # 5. Reproductor y Descarga
                st.subheader("🎬 Recorrido Cinematográfico Final")
                with open(output_video_path, "rb") as video_file:
                    video_bytes = video_file.read()
                    st.video(video_bytes)

                st.download_button(
                    label="⬇️ Descargar Vídeo MP4",
                    data=video_bytes,
                    file_name=f"recorrido_{titulo.replace(' ', '_')}.mp4",
                    mime="video/mp4"
                )

                st.divider()
                st.subheader("📝 Frases Destacadas del Vídeo")
                for f in frases_texto:
                    st.write(f"• {f}")

        except Exception as e:
            st.error(f"Error al renderizar el vídeo: {e}")
