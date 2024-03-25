# Telegram Bot to Find Rocket Launch Moment

This repository contains the code to create a Telegram bot that helps find the exact moment of a rocket launch in a video. The bot will show images from the video to the user and ask if the rocket has launched. Based on the user's responses, it will use a bisection algorithm to find the first frame where the rocket launches.

## Setup

1. Clone this repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Create a bot on Telegram via [BotFather](https://core.telegram.org/bots#6-botfather) and get your token.
4. Replace `'YOUR_TOKEN_HERE'` in `main.py` with your token.
5. Run the bot using `python main.py`.

## Features

- Responds to the commands '/start' and '/launch'.
- Shows images from the video to the user.
- Asks the user if the rocket has launched.
- Uses a bisection algorithm to find the launch moment.
- Provides the estimated launch date to the user.

## Usage

1. Start the bot using the `/start` command.
2. Use the `/launch` command to begin searching for the launch moment.
3. The bot will show images from the video and ask if the rocket has launched.
4. Based on the responses, the bot will continue showing images and adjusting the search until finding the launch moment.
5. Once found, the bot will provide the estimated launch date to the user.

## Tools Used

- Python 3: Programming language used to develop the bot.
- Telebot: Python library for interacting with the Telegram API and creating bots.
- Pygame: Library for displaying images and graphics.
- HTTPX: HTTP client for making requests to the FrameX API.
- PIL (Python Imaging Library): Library for image processing.

## Code Maintenance

- Modular structure was implemented for easier understanding and maintenance of the code.
- Descriptive comments were used to explain the different parts of the code.
- Errors and exceptions were handled appropriately to ensure the bot's robustness.
- Best programming practices were followed to ensure code readability and efficiency.

Enjoy using the bot and finding the rocket launch moment! 🚀🌌

---

# Bot de Telegram para encontrar el momento del lanzamiento del cohete

Este repositorio contiene el código para crear un bot de Telegram que ayuda a encontrar el momento exacto del lanzamiento de un cohete en un video. El bot mostrará imágenes del video al usuario y preguntará si el cohete ha despegado. Basado en las respuestas del usuario, utilizará un algoritmo de bisección para encontrar el primer fotograma donde el cohete se lanza.

## Configuración

1. Clona este repositorio.
2. Instala las dependencias usando `pip install -r requirements.txt`.
3. Crea un bot en Telegram a través de [BotFather](https://core.telegram.org/bots#6-botfather) y obtén tu token.
4. Reemplaza `'TU_TOKEN_AQUI'` en `main.py` con tu token.
5. Ejecuta el bot usando `python main.py`.

## Funcionalidades

- Responde a los comandos '/start' y '/launch'.
- Muestra imágenes del video al usuario.
- Pregunta al usuario si el cohete ha despegado.
- Utiliza un algoritmo de bisección para encontrar el momento del lanzamiento.
- Proporciona la fecha estimada del lanzamiento al usuario.

## Uso

1. Inicia el bot utilizando el comando `/start`.
2. Utiliza el comando `/launch` para comenzar la búsqueda del momento del lanzamiento.
3. El bot mostrará imágenes del video y preguntará si el cohete ha despegado.
4. Basado en las respuestas, el bot continuará mostrando imágenes y ajustando la búsqueda hasta encontrar el momento del lanzamiento.
5. Una vez encontrado, el bot proporcionará la fecha estimada del lanzamiento al usuario.

## Herramientas Utilizadas

- Python 3: Lenguaje de programación utilizado para desarrollar el bot.
- Telebot: Biblioteca de Python para interactuar con la API de Telegram y crear bots.
- Pygame: Biblioteca para mostrar imágenes y gráficos.
- HTTPX: Cliente HTTP para realizar solicitudes a la API de FrameX.
- PIL (Python Imaging Library): Biblioteca para procesar imágenes.

## Mantenimiento del Código

- Se implementó una estructura modular para facilitar la comprensión y el mantenimiento del código.
- Se utilizaron comentarios descriptivos para explicar las diferentes partes del código.
- Se manejaron los errores y excepciones de manera adecuada para garantizar la robustez del bot.
- Se siguieron las mejores prácticas de programación para garantizar la legibilidad y la eficiencia del código.

¡Disfruta usando el bot y encontrando el momento del lanzamiento del cohete! 🚀🌌
