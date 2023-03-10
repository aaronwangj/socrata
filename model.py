import os
from threading import Thread
import torch
from transformers import Speech2TextProcessor, Speech2TextForConditionalGeneration
from datasets import load_dataset
import soundfile as sf
from moviepy.editor import *
from transformers import pipeline
import openai
import time
# summarizer = pipeline("summarization", model="philschmid/flan-t5-base-samsum")

openai.api_key = "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"
model = Speech2TextForConditionalGeneration.from_pretrained("facebook/s2t-small-librispeech-asr")
processor = Speech2TextProcessor.from_pretrained("facebook/s2t-small-librispeech-asr")

class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
 
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
             
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
    
    def value(self):
        return self._return
    

def MP4ToMP3(mp4, wav):
    print("Start Conversion")
    start = time.time()
    FILETOCONVERT = AudioFileClip(mp4)
    FILETOCONVERT.write_audiofile(wav, ffmpeg_params=["-ac", "1", "-ar", "16000"], logger=None)
    FILETOCONVERT.close()
    end = time.time()
    print("CONVERSION TOOK: ", end-start)

MAX_TOKENS = 1024
VIDEO_FILE_PATH = "/Users/aaron/Downloads/test.mp4"
AUDIO_FILE_PATH = "/Users/aaron/Downloads/test.wav"

def map_to_array(wav_file):
    print("Start Mapping")
    start = time.time()
    speech_array, _ = sf.read(wav_file)
    end = time.time()
    print("MAPPING TOOK: ", end-start)
    return speech_array

def speech2text(mp4_file, audio_path='/test.wav'):
    MP4ToMP3(mp4_file, audio_path)
    print("Start Transcription")
    start = time.time()
    new_audio_data = map_to_array(audio_path)

    inputs = processor(new_audio_data, sampling_rate=16000, return_tensors="pt")
    generated_ids = model.generate(inputs["input_features"], attention_mask=inputs["attention_mask"])

    transcript = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    end = time.time()

    print("TRANSCRIPTION TOOK: ", end-start)

    return transcript


def generate_summary(transcript):
    print("Start Summary")
    start = time.time()

    summary_prompting = "write a summary of the following text: "
    sum_response_1 = openai.Completion.create(
    model="text-davinci-001",
    prompt=summary_prompting + transcript,
    temperature=0.4,
    max_tokens=MAX_TOKENS,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )["choices"][0]["text"]

    sum_response_2 = openai.Completion.create(
    model="text-davinci-003",
    prompt=summary_prompting + transcript,
    temperature=0.4,
    max_tokens=MAX_TOKENS,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )["choices"][0]["text"]
    end = time.time()

    print("SUMMARY TOOK: ", end-start)


    return [sum_response_1, sum_response_2]

def generate_quiz(transcript):
    print("Start Quiz")
    start = time.time()

    quiz_prompting = "write me five multiple choice quiz questions on the content of the following: "
    quiz_response_1 = openai.Completion.create(
    model="text-davinci-001",
    prompt=quiz_prompting + transcript,
    temperature=0.4,
    max_tokens=MAX_TOKENS,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )["choices"][0]["text"]

    quiz_response_2 = openai.Completion.create(
    model="text-davinci-003",
    prompt=quiz_prompting + transcript,
    temperature=0.4,
    max_tokens=MAX_TOKENS,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )["choices"][0]["text"]

    end = time.time()
    print("QUIZ TOOK: ", end-start)


    return [quiz_response_1, quiz_response_2]


def main_func(mp4_file, audio_path='test.wav'):
    transcript = speech2text(mp4_file, audio_path)
    summary_thread = CustomThread(target=generate_summary, args=(transcript,))
    summary_thread.start()
    quiz_thread = CustomThread(target=generate_quiz, args=(transcript,))
    quiz_thread.start()
    summary_thread.join()
    summary = summary_thread.value()
    quiz_thread.join()
    quiz = quiz_thread.value()
    print("TRANSCRIPT: ", transcript)
    print("SUMMARY: ", summary)
    print("QUIZ: ", quiz)
    return transcript, summary, quiz 

# main_func(VIDEO_FILE_PATH, AUDIO_FILE_PATH)