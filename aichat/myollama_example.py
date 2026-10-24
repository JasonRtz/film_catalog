'''
Installation:
In your virtual environment:
pip install ollama
and then go to https://ollama.com/download, download for Windows
Run the OllamaSetup.exe
Once the installation is complete, run ollama in the pop-up window that'll appear in the bottom-right of your screen:
A powershell starts, which suggest you to run:
ollama run llama3.2
which you should run, and after the model is downloaded, a prompt will appear.
Type hi, and it will ask you how to help you. That means that the installation is successful.

For the assignment, create a new file, e.g. name it myollama.py, to implement the methods that you are going to need. Careful not to name the file ollama.py.
'''

# https://github.com/ollama/ollama-python
# 
from ast import literal_eval

from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='llama3.2', messages=[
  {
    'role': 'user',
    #'content': 'Translate the following question in Greek please, responsing with a single question: Why is the sky blue?',
    #'content': 'Translate in Greek the following list of English words [Drama, Thriller, Sci-fi].',
    #'content': 'Replace each word in the following list with its Greek translation (in Greek letters), and respond with only the list of the translated words, nothing else: [Drama, Thriller, Sci-fi]. The output list must be of the same length with the input list.',
    #'content': 'Translate the following word in Greek please, responsing only with a translated single word in Greek letters: Drama',
    'content': 'Generate a list as a response, in the format of ["x", "x", ...], where each x will be replaced with the corresponding translated in Greek word from the input list: [Drama, Thriller, Sci-fi]. Your response must be only a list, of equal length to the input list.',
  },
])
result_str = response['message']['content']
print(f"{result_str}")
converted_result = literal_eval(result_str)
print(converted_result)
# or access fields directly from the response object (does not work) print(response.message.content)