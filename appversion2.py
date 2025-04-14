import flet
from flet import (
    Page, TextField, ElevatedButton, Column, Text, Container,
    Colors, Dropdown, dropdown, FilePicker, FilePickerResultEvent,
    TextButton, Row
)
import requests
from dotenv import load_dotenv
import os
import cohere

# Cargar variables de entorno
load_dotenv()
cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))
WEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NOTICIAS_API_KEY')

# Funciones externas simplificadas (puedes personalizarlas)
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=es"
        response = requests.get(url)
        data = response.json()
        return f"🌤️ {data['name']}: {data['weather'][0]['description'].capitalize()}, {data['main']['temp']}°C"
    except:
        return "⚠️ No se pudo obtener el clima."

def get_math_result(expression):
    try:
        url = f"https://api.mathjs.org/v4/?expr={requests.utils.quote(expression)}"
        response = requests.get(url)
        if response.status_code == 200:
            return f"Resultado: {response.text}"
        else:
            return "No se pudo resolver la expresión matemática."
    except Exception as e:
        return f"Error al consultar Math.js: {str(e)}"

def get_news(query):
    try:
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&language=es&pageSize=3"
        response = requests.get(url)
        data = response.json()
        return "\n\n".join([f"📰 {article['title']}\n{article['url']}" for article in data['articles']])
    except:
        return "⚠️ No se pudo obtener noticias."

def get_cohere_response(prompt):
    try:
        response = cohere_client.chat(message=prompt)
        return response.text
    except Exception as e:
        return f"Error al consultar Cohere: {str(e)}"

# Descripciones por modo
mode_descriptions = {
    "cohere": "🧠 Modo ChatBot: Chat conversacional con Infiny G04.",
    "weather": "☁️ Modo Clima: Escribe una ciudad y te diré el clima actual.",
    "math": "➗ Modo Matemático: Escribe una operación y te doy el resultado.",
    "news": "📰 Modo Noticias: Busca titulares recientes sobre un tema."
}

def main(page: Page):
    page.title = "Infiny G04"
    page.bgcolor = Colors.BLUE_GREY_900
    page.theme_mode = "dark"

    # Área de entrada y chat
    input_box = TextField(
        label="Escribe tu mensaje",
        border_color=Colors.BLUE_200,
        focused_border_color=Colors.BLUE_400,
        text_style=flet.TextStyle(color=Colors.WHITE),
        expand=True
    )

    chat_area = Column(scroll='auto', expand=True)
    uploaded_file_path = ""
    upload_button = None

    mode_description_text = Text(value=mode_descriptions["cohere"], color=Colors.BLUE_100, size=12)

    def on_mode_change(e):
        selected = mode_dropdown.value
        mode_description_text.value = mode_descriptions.get(selected, "")
        upload_button.visible = selected == "cohere"
        page.update()

    mode_dropdown = Dropdown(
        options=[
            dropdown.Option("cohere", "Chat con Infiny G04"),
            dropdown.Option("weather", "Infiny G04 Clima"),
            dropdown.Option("math", "Infiny G04 Matemática"),
            dropdown.Option("news", "Infiny G04 Noticias")
        ],
        value="cohere",
        label="Modo",
        border_color=Colors.BLUE_200,
        color=Colors.WHITE,
        on_change=on_mode_change
    )

    # Función para manejar archivos
    def on_file_picked(e: FilePickerResultEvent):
        nonlocal uploaded_file_path
        if e.files:
            uploaded_file_path = e.files[0].path
            chat_area.controls.append(Text(f"📎 Archivo cargado: {uploaded_file_path}", color=Colors.ORANGE))
            page.update()

    file_picker = FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    # Crear botón de subir archivo
    upload_button = TextButton(
        text="📁 Subir Archivo",
        visible=True,  # visible solo en modo 'cohere'
        on_click=lambda _: file_picker.pick_files(allow_multiple=False)
    )

    # Leer contenido del archivo
    def read_file_content(path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"⚠️ Error al leer el archivo: {str(e)}"

    # Envío del mensaje
    def send_message(e):
        user_message = input_box.value
        if not user_message:
            return

        chat_area.controls.append(Text(f"👤 Usuario: {user_message}", color=Colors.WHITE))

        selected_mode = mode_dropdown.value

        if selected_mode == "weather":
            response = get_weather(user_message)
        elif selected_mode == "math":
            response = get_math_result(user_message)
        elif selected_mode == "news":
            response = get_news(user_message)
        elif selected_mode == "cohere":
            if uploaded_file_path:
                file_content = read_file_content(uploaded_file_path)
                prompt = f"Archivo cargado:\n{file_content}\n\nPregunta del usuario: {user_message}"
            else:
                prompt = user_message
            response = get_cohere_response(prompt)
        else:
            response = "⚠️ Modo GPT no implementado aún."

        chat_area.controls.append(Text(f"🤖 Chatbot: {response}", color=Colors.BLUE_200))
        input_box.value = ""
        page.update()

    send_button = ElevatedButton(
        text="Enviar",
        on_click=send_message,
        bgcolor=Colors.BLUE_700,
        color=Colors.WHITE
    )

    # Contenedor del chat
    chat_container = Container(
        content=chat_area,
        bgcolor=Colors.BLUE_GREY_800,
        padding=10,
        border_radius=10,
        expand=True
    )

    input_container = Container(
        content=Column(
            controls=[
                mode_dropdown,
                mode_description_text,
                Row(controls=[input_box, send_button, upload_button], spacing=10)
            ]
        )
    )

    # Mostrar elementos
    page.add(chat_container, input_container)
    page.window_width = 800
    page.window_height = 600
    page.update()

if __name__ == "__main__":
    flet.app(target=main)
