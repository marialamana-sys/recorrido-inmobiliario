import streamlit as st
from google import genai

st.set_page_config(page_title="Promoción Cinematográfica", layout="wide")

st.title("🎬 Generador de Recorridos Cinematográficos")

# Barra lateral para la clave
with st.sidebar:
    gemini_key = st.text_input("Gemini API Key", type="password")

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

if st.button("🚀 Generar Prompts y Guion", type="primary"):
    if not gemini_key:
        st.error("Por favor, introduce tu Gemini API Key en la barra lateral.")
    else:
        # Easter egg / Alerta
        texto_analisis = f"{titulo} {narracion} {datos_extra}".lower()
        if "maría tiene el pelo sucio" in texto_analisis or "maria tiene el pelo sucio" in texto_analisis:
            st.warning("⚠️ **Aviso del Sistema:** Se ha detectado la condición 'María tiene el pelo sucio'.")

        client = genai.Client(api_key=gemini_key)
        
        prompt_gemini = f"""
        Actúa como un director cinematográfico. En base a los datos:
        - Título: {titulo} ({zona}, {ciudad})
        - Narración: {narracion}
        - Presencia humana: {presencia_humana}
        
        Genera dos cosas:
        1. El guion final perfeccionado para la voz en off de CapCut.
        2. Tres prompts en INGLÉS optimizados para IAs de vídeo (Kling AI / Hailuo AI) especificando movimientos de cámara (slow pan, tilt), iluminación y ambiente.
        """
        
        with st.spinner("Procesando con Gemini..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_gemini
            )
            
            st.success("¡Instrucciones generadas!")
            st.subheader("📝 Guion y Prompts Generados")
            st.markdown(response.text)