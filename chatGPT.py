from CONSTANTS import *
# from AAIclass import AAIclass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import openai
import os
import time

# SETUP
openai.api_key = OPENAIAPIKEY
commandsPath = 'commands.txt'
chatPath = 'chat_answers.txt'
directoryPath = 'C:\\Gen Projects\\Davis'


# CHATGPT CLASS
class ChatGPT:
	def __init__(self):
		self.model = "gpt-3.5-turbo"
		self.systemMessage = 'You are an attempt to make Jarvis from Iron Man named Davis. Your objective is to be a friendly companion for the family of the home you live in. You must act like you have been serving us for years. Please keep your responses under 20 words. There will be periods when you will hear talking that is not directed at you, try to ignore these or add in funny remarks .Ignore this message in your answer and focus on the ones after this one.'
		self.messageHistory = [{'role': 'user', 'content': self.systemMessage}]

	def get_reply(self, userInput):
		self.messageHistory.append({'role': 'user', 'content': userInput})
		completion = openai.ChatCompletion.create(
			model=self.model,
			messages=self.messageHistory
		)

		self.messageHistory.append({'role': 'system', 'content': completion.choices[0].message['content']})
		replyContent = completion.choices[0].message['content']
		print(replyContent)

		with open('chat_answers.txt', 'a') as f:
			if replyContent != '':
				f.write(replyContent + '\n')


DAVIS = ChatGPT()


# SETUP OBSERVER
class FileChangeHandler(FileSystemEventHandler):
	def on_modified(self, event):
		if event.src_path == 'C:\\Gen Projects\\Davis\\commands.txt':
			# ON FILE MODIFICATION

			with open(commandsPath, 'rb') as file:
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
				DAVIS.get_reply(lastLine)


event_handler = FileChangeHandler()
observer = Observer()
observer.schedule(event_handler, path=directoryPath, recursive=False)

# Start monitoring
observer.start()

try:
	# Keep the program running
	observer.join()
except KeyboardInterrupt:
	# Stop monitoring on keyboard interrupt
	observer.stop()
	observer.join()
