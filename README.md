**Speech Recognition Application**

This is a Python application for speech recognition using faster whisper and real-time transcription of audio recordings. The application allows users to record audio, transcribe the speech, and optionally translate it into English if the detected language is different.

**Features:**

- Real-time speech recognition using a pre-trained model.
- Transcription of recorded audio into text.
- Optional translation of non-English speech into English.
- Graphical user interface (GUI) for easy interaction.

**Dependencies:**

Make sure you have the following dependencies installed:
- Python (3.x recommended)
- PyAudio
- tkinter
- translate
- faster_whisper
Install the required dependencies using pip install -r requirements.txt.

**Usage:**

- Run the application by executing python main.py.
- Click on the "Start Recording" button to begin recording audio.
- Speak into the microphone to record your speech.
- Click on the "Stop Recording" button to stop recording.

- The transcribed text will be displayed in the text area.
- If the detected language is not English, the text will be translated into English.

