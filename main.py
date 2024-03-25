import io
import os
import telebot
import random 
from io import BytesIO
from telebot import types
from typing import Dict,Union
from typing import List, NamedTuple, Text
from urllib.parse import quote, urljoin
from bisect import bisect_left
from telebot.types import ReplyKeyboardRemove


import pygame
from httpx import Client
from PIL import Image
from PyInquirer import prompt






"""
Telegram bot connection

"""
bot = telebot.TeleBot("7029972165:AAHBdv6qQSwOGk0kLtlJl-pdvuYApAVIF2M")





API_BASE = os.getenv("API_BASE", "https://framex-dev.wadrid.net/api/")
VIDEO_NAME = os.getenv(
    "VIDEO_NAME", "Falcon Heavy Test Flight (Hosted Webcast)-wbSwFU6tY1c"
)


class Size(NamedTuple):
    """
    Represents a size
    """

    width: int
    height: int


class Color(NamedTuple):
    """
    8-bit components of a color
    """

    r: int
    g: int
    b: int


class Video(NamedTuple):
    """
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
    Runs a bisection.

    - `n` is the number of elements to be bisected
    - `mapper` is a callable that will transform an integer from "0" to "n"
      into a value that can be tested
    - `tester` returns true if the value is within the "right" range
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
    Utility class to access the FrameX API
    """

    BASE_URL = API_BASE

    def __init__(self):
        self.client = Client(timeout=30)

    def video(self, video: Text) -> Video:
        """
        Fetches information about a video
        """

        r = self.client.get(urljoin(self.BASE_URL, f"video/{quote(video)}/"))
        r.raise_for_status()
        return Video(**r.json())

    def video_frame(self, video: Text, frame: int) -> bytes:
        """
        Fetches the JPEG data of a single frame
        """

        r = self.client.get(
            urljoin(self.BASE_URL, f'video/{quote(video)}/frame/{quote(f"{frame}")}/')
        )
        r.raise_for_status()
        return r.content


class FrameXBisector:
    """
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
        When a new index is written, download the new frame
        """

        self._index = v
        self.image = Frame(self.api.video_frame(self.video.name, v))

    @property
    def count(self):
        return self.video.frames

    def blit(self, disp):
        """
        Draws the current picture.
        """

        self.image.blit(disp)


def confirm(title):
    """
    Asks a yes/no question to the user
    """

    return prompt(
        [
            {
                "type": "confirm",
                "name": "confirm",
                "message": f"{title} - did the rocket launch yet?",
            }
        ]
    )["confirm"]





    """
    Runs a bisection algorithm on the frames of the video, the goal is
    to figure at which exact frame the rocket takes off.

    Images are displayed using pygame, but the interactivity happens in
    the terminal as it is much easier to do.
    """

    pygame.init()

    bisector = FrameXBisector(VIDEO_NAME)
    disp = pygame.display.set_mode(DISPLAY_SIZE)

    def mapper(n):
        """
        In that case there is no need to map (or rather, the mapping
        is done visually by the user)
        """

        return n

    def tester(n):
        """
        Displays the current candidate to the user and asks them to
        check if they see wildfire damages.
        """

        bisector.index = n
        disp.fill(BLACK)
        bisector.blit(disp)
        pygame.display.update()

        return confirm(bisector.index)

    culprit = bisect(bisector.count, mapper, tester)
    bisector.index = culprit

    print(f"Found! Take-off = {bisector.index}")

    pygame.quit()
    exit()


#------------------------------------------------------------------



"""

Global variables to maintain the state and index of the current frame

"""
confirmed_launch = False
markup = None
bisector = FrameXBisector(VIDEO_NAME)
current_frame_index = random.randint(10000, 20000)
MAX_ATTEMPTS = 15

"""
Create a dictionary to maintain the conversation state per user

"""
states: Dict[int, str] = {}

"""
List to store the frames

"""

frames = []
positive_responses_count = 0




"""Handler for the /launch command"""
@bot.message_handler(commands=['launch'])
def handle_launch(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_btn_yes = types.KeyboardButton('Yes')
    item_btn_no = types.KeyboardButton('No')
    markup.row(item_btn_yes, item_btn_no)  
    bot.send_message(message.chat.id, "Has the rocket already launched?", reply_markup=markup)
    

    """Call the function to send the image and ask again"""
    send_image_and_confirm(current_frame_index, message.chat.id)
    

    """Set the conversation state for this user"""
    states[message.chat.id] = "waiting_for_confirmation"




"""Function to generate an index using the bisection algorithm"""
def generate_bisection_index(current_index, confirmation_count):
    if confirmation_count < 1:
        range_start = 0
        range_end = 59000
    else:
        range_start = max(0, current_index - (MAX_ATTEMPTS - confirmation_count) * 500)
        range_end = min(59000, current_index + (MAX_ATTEMPTS - confirmation_count) * 500)

    midpoint = (range_start + range_end) // 2
    if current_index > midpoint:
        midpoint = (current_index + range_end) // 2
    else:
        midpoint = (current_index + range_start) // 2

    return midpoint


"""Function to handle confirmation messages"""
@bot.message_handler(func=lambda message: states.get(message.chat.id) == "waiting_for_confirmation")
def handle_confirmation(message):
    global current_frame_index, positive_responses_count  
    
    if message.text.lower() == 'yes':
        positive_responses_count += 1
        
        frames.append(current_frame_index)
        bot.send_message(message.chat.id, "The rocket has already launched! 🚀🌌")
        print("Número de respuestas afirmativas:", positive_responses_count, "Fotograma actual:", current_frame_index)
        

        if positive_responses_count < 12:
            current_frame_index -= random.randint(100, 1000)
        else:
            current_frame_index -= random.randint(0, 300)

    elif message.text.lower() == 'no':
        positive_responses_count += 1
        bot.send_message(message.chat.id, "The rocket has not yet launched. 🌍" )
        print("Número de respuestas Negativas:", positive_responses_count, "Fotograma actual:", current_frame_index)
        
        if positive_responses_count < 9:
            current_frame_index += random.randint(5000, 10000)
        elif positive_responses_count > 12:
            current_frame_index += random.randint(0, 1000)
        else:
            current_frame_index += random.randint(1000, 2000)
    
    if positive_responses_count < MAX_ATTEMPTS:
        bot.send_message(message.chat.id, "Displaying another frame...")
        current_index = generate_bisection_index(current_frame_index, positive_responses_count)
        send_image_and_confirm(current_index, message.chat.id)
        states[message.chat.id] = "waiting_for_response"
        bot.send_message(message.chat.id, "Please respond with 'Yes' or 'No'.")
    else:
        send_image_and_confirm(current_frame_index, message.chat.id)
        bot.send_message(message.chat.id, f"🚀🌌The rocket was launched in frame:🚀🌌 {current_frame_index}")
        bot.send_message(message.chat.id, "Thank you for using our service. Goodbye! 👋")
        positive_responses_count = 0
        states[message.chat.id] = "idle"

        show_launch_keyboard(message.chat.id)




   
"""Function to send the image to the user and ask again"""
def send_image_and_confirm(index, chat_id):
    global current_frame_index  
    # Get the frame corresponding to the index
    frame_data = bisector.api.video_frame(bisector.video.name, index)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_btn_custom_yes = types.KeyboardButton('yes')
    item_btn_custom_no = types.KeyboardButton('no')
    markup.row(item_btn_custom_yes, item_btn_custom_no)  # Add the custom tags to the same row

    #Send the image to the user

    bot.send_photo(chat_id, frame_data, caption=f"Frame {index}")

    current_frame_index = index  


@bot.message_handler(commands=['start'])
def handle_start(message):
    global frames, positive_responses_count
    
    # Reiniciar los contadores y los fotogramas
    frames = []
    positive_responses_count = 0
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    bot.send_message(message.chat.id, "🚀¡Hello!🚀\nWelcome to the bot, to find out in which frame the rocket has been launched. Would you like to see information about the rocket launch?", reply_markup=markup)
    show_launch_keyboard(message.chat.id)


"""Function to display the launch keyboard"""
def show_launch_keyboard(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_btn_launch = telebot.types.KeyboardButton('Launch')
    markup.add(item_btn_launch)
    bot.send_message(chat_id, "🚀🌌Would you like to see the launch?", reply_markup=markup)



@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text.lower() == 'exit':
        bot.send_message(message.chat.id, "¡Exit!")
        handle_start(message)
    elif message.text.lower() == 'launch':
        handle_launch(message)
    elif message.text.lower() == "yes":
        handle_confirmation(message)
    elif message.text.lower() == "no":
        handle_confirmation(message)
    else:
        bot.reply_to(message, "I didn't understand that command. You can try /start, /launch, /exit")


# Run the bot
if __name__ == "__main__":
    bot.polling(none_stop=True)
