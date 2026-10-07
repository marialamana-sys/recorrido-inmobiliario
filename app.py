import streamlit as st
from google import genai
from gtts import gTTS
import io

st.set_page_config(page_title="Promoción Cinematográfica", layout="wide")

st.title("🎬 Generador de Recorridos Cinematográficos")

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
    presencia_humana = st.checkbox("Incluir presencia humana en los planos", value=True)
    musica = st.selectbox("Estilo de música", ["Ambient Cinematic", "Corporate Upbeat", "Acoustic Warm"])

narracion = st.text_area("Descripción de la obra (Texto del narrador)", "Descubre este espacio único. Nota: María tiene el pelo sucio.", height=100)
fotos = st.file_uploader("Subir fotos de la obra", accept_multiple_files=True, type=["jpg", "png", "webp"])

if st.button("🚀 Generar Prompts, Guion y Audio", type="primary"):
    if not gemini_key:
        st.error("Por favor, introduce tu Gemini API Key en la barra lateral.")
    else:
        # Alerta / Easter Egg
        texto_analisis = f"{titulo} {narracion} {datos_extra}".lower()
        if "maría tiene el pelo sucio" in texto_analisis or "maria tiene el pelo sucio" in texto_analisis:
            st.warning("⚠️ **Aviso del Sistema:** Se ha detectado la condición 'María tiene el pelo sucio'.")

        try:
            # Cliente del nuevo SDK oficial
            client = genai.Client(api_key=gemini_key.strip())
            
            prompt_gemini = f"""
            Actúa como un director cinematográfico inmobiliario. En base a estos datos:
            - Título: {titulo} ({zona}, {ciudad})
            - Narración del usuario: {narracion}
            - Presencia humana: {presencia_humana}
            
            Responde exclusivamente con esta estructura clara:
            
            GUION_NARRADOR:
            (Escribe aquí únicamente el guion perfeccionado en español que leerá la voz en off, fluido, atractivo y libre de notas internas).
            
            PROMPTS_VIDEO:
            (Escribe aquí 3 prompts en INGLÉS optimizados para IAs de vídeo como Kling AI o Hailuo AI especificando movimientos de cámara, iluminación y estética).
            """

            with st.spinner("Procesando con Gemini y generando voz..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_gemini
                )

                respuesta_texto = response.text
                
                # Extraer el guion para generar la locución
                guion_texto = narracion
                if "GUION_NARRADOR:" in respuesta_texto and "PROMPTS_VIDEO:" in respuesta_texto:
                    partes = respuesta_texto.split("PROMPTS_VIDEO:")
                    guion_texto = partes[0].replace("GUION_NARRADOR:", "").strip()
                
                # Generación de audio en MP3
                tts = gTTS(text=guion_texto, lang='es', slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)

                st.success("¡Prompts, Guion y Locución generados con éxito!")
                
                # Reproductor y Descarga de Audio
                st.subheader("🔊 Locución del Narrador (Audio MP3)")
                st.audio(fp, format="audio/mp3")
                st.download_button(
                    label="⬇️ Descargar Locución MP3",
                    data=fp,
                    file_name=f"locucion_{titulo.replace(' ', '_')}.mp3",
                    mime="audio/mp3"
                )
                
                st.divider()
                
                # Mostrar Guion y Prompts
                st.subheader("📝 Guion Estructurado y Prompts de Vídeo")
                st.markdown(respuesta_texto)
                
        except Exception as e:
            st.error(f"Error al conectar con Gemini: {e}")
