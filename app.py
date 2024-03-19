from multiprocessing import Process, Queue
import pyaudio
import wave
from faster_whisper import WhisperModel
import tkinter as tk
from translate import Translator  # Assuming you have a translation library installed
import time


model_size = "small"
model = WhisperModel(model_size, device="cpu", compute_type="int8")


producer_process = None
consumer_process = None


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

def audio_consumer(queue):
    while True:
        if not queue.empty():
            audio_data = queue.get()
            print("Consumer: Transcribing...")
            segments, info = model.transcribe(audio_data, beam_size=5)
            print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
            if info.language != "en":
                translator = Translator(to_lang="en", from_lang=info.language)
                for segment in segments:
                    # Retry fetching the token up to 3 times
                    for _ in range(3):
                        try:
                            segment1 = translator.translate(segment.text)
                            print(segment1)
                            break  # Exit the retry loop if successful
                        except Exception as e:
                            print("Error fetching token:", e)
                            time.sleep(1)  # Wait for 1 second before retrying
                    else:
                        print("Failed to fetch token after retries.")
                    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            else:
                for segment in segments:
                    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

def start_recording(audio_queue):
    producer_process = Process(target=audio_producer, args=(audio_queue,))
    producer_process.start()
    producer_process.join()  # Wait for the recording to finish
    audio_path = audio_queue.get()  # Get the path of the recorded audio

    transcription = ""  # Initialize transcription variable
    print("Consumer: Transcribing...")
    custom_vad_parameters = {
                            "threshold": 0.5,
                            "min_speech_duration_ms": 200,
                            "max_speech_duration_s": 20,
                            "min_silence_duration_ms": 1000,
                            "window_size_samples": 1024,
                            "speech_pad_ms": 400
                            }
    # Transcribe audio and handle translation if needed
    segments, info = model.transcribe(audio_path, beam_size=5, vad_filter=True, vad_parameters=custom_vad_parameters)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    if info.language != "en":  # Translate if language is not English
        translator = Translator(to_lang="en", from_lang=info.language)
        for segment in segments:
            # Retry fetching the token up to 3 times
            for _ in range(3):
                try:
                    translated_text = translator.translate(segment.text)
                    transcription += "[%.2fs -> %.2fs] %s (Translated: %s)\n" % (
                        segment.start, segment.end, segment.text, translated_text)
                    break  # Exit the retry loop if successful
                except Exception as e:
                    print("Error fetching token:", e)
                    time.sleep(1)  # Wait for 1 second before retrying
            else:
                print("Failed to fetch token after retries.")
    else:
        for segment in segments:
            transcription += "[%.2fs -> %.2fs] %s\n" % (segment.start, segment.end, segment.text)

    # Clear previous transcription and insert the new transcription into the interface
    transcription_text.delete(1.0, tk.END)
    transcription_text.insert(tk.END, transcription)
    transcription_text.config(state=tk.DISABLED)  # Disable editing


def stop_recording():
    global producer_process, consumer_process
    if producer_process:
        producer_process.terminate()
    else:
        print("Recording process is not running.")
    if consumer_process:
        consumer_process.terminate()
    else:
        print("Consumer process is not running.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Speech Recognition")

    audio_queue = Queue()

    start_button = tk.Button(root, text="Start Recording", command=lambda: start_recording(audio_queue))
    start_button.pack()

    transcription_text = tk.Text(root, wrap=tk.WORD, width=50, height=10)
    transcription_text.pack()

    stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)
    stop_button.pack()

    root.mainloop()

    # Start the producer process after the GUI loop starts
    producer_process = Process(target=audio_producer, args=(audio_queue,))
    producer_process.start()

    # Call the audio_consumer function to process audio data
    audio_consumer(audio_queue)
