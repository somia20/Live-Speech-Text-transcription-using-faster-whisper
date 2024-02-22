from multiprocessing import Process, Queue
import pyaudio
import wave
from faster_whisper import WhisperModel
import tkinter as tk

model_size = "small.en"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

producer_process = None 

def audio_producer(queue):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 10

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Producer: Recording...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    audio_data = b''.join(frames)

    # Convert audio data to WAV format
    with wave.open('output.wav', 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(audio_data)

    queue.put('output.wav')  # Put the WAV file path into the queue

def transcribe_audio(audio_path):
    print("Transcribing...")
    segments, info = model.transcribe(audio_path, beam_size=5)
    transcription = ""
    for segment in segments:
        transcription += "[%.2fs -> %.2fs] %s\n" % (segment.start, segment.end, segment.text)
    return transcription

def start_recording():
    audio_queue = Queue()
    producer_process = Process(target=audio_producer, args=(audio_queue,))
    producer_process.start()
    producer_process.join()  # Wait for the recording to finish
    audio_path = audio_queue.get()  # Get the path of the recorded audio
    transcription = transcribe_audio(audio_path)
    transcription_text.delete(1.0, tk.END)  # Clear previous transcription
    transcription_text.insert(tk.END, transcription)  # Display transcription

def stop_recording():
    global producer_process
    if producer_process:
        producer_process.terminate()
    else:
        print("Recording process is not running.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Speech Recognition")
    
    start_button = tk.Button(root, text="Start Recording", command=start_recording)
    start_button.pack()
    
    transcription_text = tk.Text(root, wrap=tk.WORD, width=50, height=10)
    transcription_text.pack()

    stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)
    stop_button.pack()
    
    root.mainloop()
