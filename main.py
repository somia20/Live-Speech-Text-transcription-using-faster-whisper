'''from multiprocessing import Process, Queue
import whisper
import numpy as np
import torch
import speech_recognition as sr

def audio_producer(queue):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Producer: Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        while True:
            print("Producer: Listening...")
            audio_data = recognizer.listen(source)
            queue.put(audio_data)


def audio_consumer(queue, model):
    print("Consumer: Loading Whisper model...")
    audio_model = whisper.load_model("medium.en")  # Loading Whisper model
    print("Consumer: Whisper model loaded successfully.")
    
    while True:
        if not queue.empty():
            audio_data = queue.get()
            try:
                print("Consumer: Transcribing...")
                audio_np = np.frombuffer(audio_data.frame_data, dtype=np.int16).astype(np.float32) / 32768.0
                print("Audio Data:", audio_np)  # Print and inspect audio data
                result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                print("Transcription Result:", result)
                text = result['text'].strip()
                print(f"Transcribed Text: {text}")
            except Exception as e:
                print(f"Consumer: Error occurred during transcription: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="medium", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the english model.")
    args = parser.parse_args()

    audio_queue = Queue()

    producer_process = Process(target=audio_producer, args=(audio_queue,))
    consumer_process = Process(target=audio_consumer, args=(audio_queue, args.model))

    producer_process.start()
    consumer_process.start()

    producer_process.join()
    consumer_process.join()'''
