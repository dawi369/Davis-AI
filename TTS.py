import pyttsx3
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import queue
import time

import FLAGS

# SETUP
chatPath = 'chat_answers.txt'
directoryPath = 'C:\\Gen Projects\\Davis'

engine = pyttsx3.init()
text_queue = queue.Queue()


def startedSpeaking():
	FLAGS.listening = False


def stoppedSpeaking():
	FLAGS.listening = True


# Connect the custom functions to the events
engine.connect('start-utterance', startedSpeaking)
engine.connect('end-utterance', stoppedSpeaking)


class FileChangeHandler(FileSystemEventHandler):
	def on_modified(self, event):
		if event.src_path == 'C:\\Gen Projects\\Davis\\chat_answers.txt':
			# ON FILE MODIFICATION
			print("MODIFIED")

			time.sleep(0.1)

			with open(chatPath, 'rb') as file:
				# Move to the end of the file
				file.seek(0, os.SEEK_END)

				# Check if the file is not empty
				if file.tell() > 0:
					file.seek(-2, os.SEEK_END)

					# Loop to find the beginning of the last line
					while file.read(1) != b'\n':
						file.seek(-2, os.SEEK_CUR)
						if file.tell() == 0:  # If the file has only one line
							file.seek(0)
							break

					# Read and decode the last line
					lastLine = file.readline().decode().strip()
				else:
					pass

			if type(lastLine) == str:
				# Use the engine to say the text
				text_queue.put(lastLine)


event_handler = FileChangeHandler()
observer = Observer()
observer.schedule(event_handler, path=directoryPath, recursive=False)

# Start monitoring
observer.start()

try:
	# Main loop`2ef
	while True:
		try:
			# Get the next text from the queue (non-blocking)
			text = text_queue.get_nowait()

			time.sleep(.5)

			# Speak the text
			engine.say(text)
			engine.runAndWait()

		except queue.Empty:
			# No text in the queue, continue waiting
			time.sleep(0.1)  # Add a short sleep to reduce CPU usage

except KeyboardInterrupt:
	# Stop monitoring on keyboard interrupt
	observer.stop()
	observer.join()
