# importing libraries 
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
from params import *

# create a speech recognition object
files = ["Final_Output/"+name+"."+file[-3:] for name in speaker_names]
r = sr.Recognizer()

def mp4_to_wav(video_file_path):
    wav, sr = librosa.load(video_file_path, sr=None)
    write("audio_data/audio.wav", 16000, wav)
    return "audio_data/audio.wav"
#convert mp3 to wav
def mp3_to_wav(audio_file_path):
    sound = AudioSegment.from_mp3(audio_file_path)
    audio_file_path = audio_file_path.split('.')[0] + '.wav'
    sound.export(audio_file_path, format="wav")
    return audio_file_path
# a function that splits the audio file into chunks
def get_large_audio_transcription(path):
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)  
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 1000,
        # adjust this per requirement
        silence_thresh = sound.dBFS-16,
        # keep the silence for 1 second, adjustable as well
        keep_silence=300,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened,language=lang_code)
            except sr.UnknownValueError as e:
                #print("chunk {} failed:".format(i), str(e))
                print("")
            else:
                text = f"{text.capitalize()}. "
                #print(chunk_filename, ":", text)
                whole_text += text
    # return the text for all chunks detected
    return whole_text

for x in files:
    f = open("Final_Output/"+x[13:-4]+".txt",'w')
    if x[-3:]=="mp3":
        file_path = mp3_to_wav(x)
    else:
        file_path = mp4_to_wav(x)
    f.write(get_large_audio_transcription(file_path))
    f.close()
    os.system("rm -r audio-chunks")