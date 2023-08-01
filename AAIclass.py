import time

from CONSTANTS import *
import pyaudio
import websockets
import asyncio
import json
import base64
from FLAGS import listening

# SETUP
FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

# START RECORDING
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=FRAMES_PER_BUFFER)

URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"


# SETUP ASSEMBLYAI
class AAIclass:

	def __init__(self):
		self.send_result = ""
		self.receive_result = ""

	@staticmethod
	async def send_receive():
		print(f'Connecting websocket to url ${URL}')

		async with websockets.connect(
				URL,
				extra_headers=(("Authorization", AAIAPIKEY),),
				ping_interval=5,
				ping_timeout=20
		) as _ws:

			await asyncio.sleep(0.1)
			print("Receiving Session Begins ...")

			session_begins = await _ws.recv()
			print(session_begins)
			print("Sending messages ...")

			async def send():
				while True:
					try:
						data = stream.read(FRAMES_PER_BUFFER)
						data = base64.b64encode(data).decode("utf-8")
						json_data = json.dumps({"audio_data": str(data)})
						await _ws.send(json_data)

					except websockets.ConnectionClosedError as e:

						print(e)
						assert e.code == 4008
						break

					except Exception as e:
						assert False, "Not a websocket 4008 error"

					await asyncio.sleep(0.01)

				return True

			async def receive():
				while True:
					try:
						result_str = await _ws.recv()
						if json.loads(result_str)['message_type'] == 'FinalTranscript':
							if listening:
								time.sleep(.2)
								if listening:
									currentText = json.loads(result_str)['text']
									print(currentText)

									with open('commands.txt', 'a') as f:
										if currentText != '':
											f.write(currentText + '\n')

									if 'quit' in currentText or 'Quit' in 'currentText' or 'quit.' in currentText or 'Quit.' in currentText:
										print('Quitting')

										with open('commands.txt', 'w'):
											pass

										with open('chat_answers.txt', 'w'):
											pass

										raise Exception('Quit')

					except websockets.ConnectionClosedError as e:
						print(e)
						assert e.code == 4008
						break

					except Exception as e:
						assert False, "Not a websocket 4008 error"

			send_result, receive_result = await asyncio.gather(send(), receive())

	while True:
		asyncio.run(send_receive())
