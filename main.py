import io
import os
import telebot
import random
import time
from io import BytesIO
from telebot import types
from typing import Dict, Union
from typing import List, NamedTuple, Text
from urllib.parse import quote, urljoin
from bisect import bisect_left
from telebot.types import ReplyKeyboardRemove
from httpx import Client
from PIL import Image
from PyInquirer import prompt

"""
Conexión con el bot de Telegram
Telegram bot connection
"""
bot = telebot.TeleBot("7029972165:AAHBdv6qQSwOGk0kLtlJl-pdvuYApAVIF2M")

API_BASE = os.getenv("API_BASE", "https://framex-dev.wadrid.net/api/")
VIDEO_NAME = os.getenv(
    "VIDEO_NAME", "Falcon Heavy Test Flight (Hosted Webcast)-wbSwFU6tY1c"
)

class Size(NamedTuple):
    """
    Representa un tamaño
    Represents a size
    """
    width: int
    height: int

class Color(NamedTuple):
    """
    Componentes de 8 bits de un color
    8-bit components of a color
    """
    r: int
    g: int
    b: int

class Video(NamedTuple):
    """
    Un video de la API
    That's a video from the API
    """
    name: Text
    width: int
    height: int
    frames: int
    frame_rate: List[int]
    url: Text
    first_frame: Text
    last_frame: Text

DISPLAY_SIZE = Size(int(480 * 1.5), int(270 * 1.5))
BLACK = Color(0, 0, 0)

def bisect(n, mapper, tester):
    """
    Realiza una bisección.
    Runs a bisection.

    - `n` es el número de elementos a biseccionar
      `n` is the number of elements to be bisected
    - `mapper` es una función que transforma un entero de "0" a "n"
      en un valor que se puede probar
      `mapper` is a callable that will transform an integer from "0" to "n"
      into a value that can be tested
    - `tester` devuelve verdadero si el valor está dentro del rango "correcto"
      `tester` returns true if the value is within the "right" range
    """
    if n < 1:
        raise ValueError("Cannot bissect an empty array")

    left = 0
    right = n - 1

    while left + 1 < right:
        mid = int((left + right) / 2)

        val = mapper(mid)

        if tester(val):
            right = mid
        else:
            left = mid

    return mapper(right)

class Frame:
    """
    Envuelve los datos de un frame para ayudar a dibujarlo en la pantalla
    Wrapper around frame data to help drawing it on the screen
    """
    def __init__(self, data):
        self.data = data
        self.image = None

    def blit(self, disp):
        if not self.image:
            pil_img = Image.open(io.BytesIO(self.data))
            pil_img.thumbnail(DISPLAY_SIZE)
            buf = pil_img.tobytes()
            size = pil_img.width, pil_img.height
            self.image = pygame.image.frombuffer(buf, size, "RGB")

        disp.blit(self.image, (0, 0))

class FrameX:
    """
    Clase de utilidad para acceder a la API de FrameX
    Utility class to access the FrameX API
    """
    BASE_URL = API_BASE

    def __init__(self):
        self.client = Client(timeout=30)

    def video(self, video: Text) -> Video:
        """
        Obtiene información sobre un video
        Fetches information about a video
        """
        r = self.client.get(urljoin(self.BASE_URL, f"video/{quote(video)}/"))
        r.raise_for_status()
        return Video(**r.json())

    def video_frame(self, video: Text, frame: int) -> bytes:
        """
        Obtiene los datos JPEG de un frame único
        Fetches the JPEG data of a single frame
        """
        r = self.client.get(
            urljoin(self.BASE_URL, f'video/{quote(video)}/frame/{quote(f"{frame}")}/')
        )
        r.raise_for_status()
        return r.content

class FrameXBisector:
    """
    Ayuda a gestionar la visualización de imágenes del lanzamiento
    Helps managing the display of images from the launch
    """
    BASE_URL = API_BASE

    def __init__(self, name):
        self.api = FrameX()
        self.video = self.api.video(name)
        self._index = 0
        self.image = None

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, v):
        """
        Cuando se escribe un nuevo índice, descarga el nuevo frame
        When a new index is written, download the new frame
        """
        self._index = v
        self.image = Frame(self.api.video_frame(self.video.name, v))

    @property
    def count(self):
        return self.video.frames

    def blit(self, disp):
        """
        Dibuja la imagen actual.
        Draws the current picture.
        """
        self.image.blit(disp)

def confirm(bot, chat_id, title):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_btn_yes = types.KeyboardButton('Yes')
    item_btn_no = types.KeyboardButton('No')
    markup.row(item_btn_yes, item_btn_no)
    
    bot.send_message(chat_id, f"{title} - Did the rocket launch yet?", reply_markup=markup)

# Estado para rastrear el progreso de la búsqueda binaria
# State to track the progress of the binary search
state: Dict[int, Dict[str, Union[bool, int]]] = {}

def send_frame(chat_id, frame_index):
    bisector.index = frame_index

    frame_data = io.BytesIO(bisector.image.data)
    bot.send_photo(chat_id, frame_data, caption=f"Frame Candidate: {frame_index}")
    confirm(bot, chat_id, "")

    # Inicializar el estado para esta iteración
    # Initialize the state for this iteration
    state[chat_id] = {'answered': False, 'index': frame_index}

def main(chat_id):
    bisector = FrameXBisector(VIDEO_NAME)
    def mapper(n):
        return n
    def tester(n, chat_id):
        send_frame(chat_id, n)

        # Esperar la respuesta del usuario
        # Wait for the user's response
        wait_for_user_response(chat_id)

        return state[chat_id]['answer']

    culprit = bisect(bisector.count, mapper, lambda n: tester(n, chat_id))
    bisector.index = culprit

    final_frame_data = io.BytesIO(bisector.image.data)
    bot.send_photo(chat_id, final_frame_data, caption=f"Final Frame: {culprit}")
    bot.send_message(chat_id, f"Found! Take-off = {culprit}")

def wait_for_user_response(chat_id):
    while not state[chat_id]['answered']:
        time.sleep(5)  # Esperar 5 segundos antes de verificar de nuevo
                       # Wait 5 seconds before checking again

# Función para manejar la respuesta del usuario
# Function to handle the user's response
@bot.message_handler(func=lambda message: message.text.lower() in ['yes', 'no'])
def handle_user_message(message):
    chat_id = message.chat.id
    user_response = message.text.lower()

    if chat_id in state:
        state[chat_id]['answered'] = True
        state[chat_id]['answer'] = user_response == 'yes'

def handle_confirmation(user_response, chat_id):
    print("Respuesta del usuario recibida:", user_response)
    print("User response received:", user_response)
    
    # Continuar con el envío de frames solo si la respuesta es 'yes'
    # Continue sending frames only if the response is 'yes'
    if user_response == 'yes':
        main(chat_id)
    elif user_response == 'no':
        # Detener la transmisión de frames
        # Stop frame transmission
        bot.send_message(chat_id, "Ok, stopping frame transmission.")

# Variables globales para mantener el estado y el índice del frame actual
# Global variables to maintain the state and index of the current frame
confirmed_launch = False
markup = None
bisector = FrameXBisector(VIDEO_NAME)
current_frame_index = random.randint(10000, 20000)
MAX_ATTEMPTS = 15

# Lista para almacenar los frames
# List to store the frames
frames = []
positive_responses_count = 0

@bot.message_handler(commands=['launch'])
def handle_launch(message):
    bot.send_message(message.chat.id, "Searching for the frame where the rocket takes off...")

    # Execute the bisection algorithm to find the takeoff frame.
    main(message.chat.id)
    show_launch_keyboard(message.chat.id)

@bot.message_handler(commands=['start'])
def handle_start(message):
    global frames, positive_responses_count
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    bot.send_message(message.chat.id, "🚀¡Hello!🚀\nWelcome to the bot, to find out in which frame the rocket has been launched. Would you like to see information about the rocket launch?", reply_markup=markup)
    show_launch_keyboard(message.chat.id)

"""
Función para mostrar el teclado de lanzamiento
Function to display the launch keyboard
"""
def show_launch_keyboard(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_btn_launch = telebot.types.KeyboardButton('Launch')
    markup.add(item_btn_launch)
    bot.send_message(chat_id, "🚀🌌Would you like to see the launch?", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text.lower() == 'exit':
        bot.send_message(message.chat.id, "¡Exit!")
    elif message.text.lower() == 'launch':
        handle_launch(message)
    elif message.text.lower() == "yes":
        handle_confirmation(message.text.lower(), message.chat.id)
    elif message.text.lower() == "no":
        handle_confirmation(message.text.lower(), message.chat.id)
    else:
        bot.reply_to(message, "I didn't understand that command. You can try /start, /launch, /exit")

# Ejecutar el bot
# Run the bot
if __name__ == "__main__":
    bot.polling(none_stop=True)