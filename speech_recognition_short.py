import speech_recognition as sr
from pydub import AudioSegment
from params import *
import librosa
from scipy.io.wavfile import write

# Input audio file to be sliced
files = ["Final_Output/"+name+"."+file[-3:] for name in speaker_names]

def mp4_to_wav(video_file_path):
    wav, sr = librosa.load(video_file_path, sr=None)
    write("audio_data/audio.wav", 16000, wav)
    return "audio_data/audio.wav"

def mp3_to_wav(audio_file_path):
    sound = AudioSegment.from_mp3(audio_file_path)
    audio_file_path = audio_file_path.split('.')[0] + '.wav'
    sound.export(audio_file_path, format="wav")
    return audio_file_path

for x in files:
    f = open("Final_Output/"+x[13:-4]+".txt",'w')
    if x[-3:] == "mp3":
        file_path = mp3_to_wav(x)
    else:
        file_path = mp4_to_wav(x)
    audio = sr.AudioFile(file_path)
    r = sr.Recognizer()
    with audio as source:
        audio_listened = r.record(source)
    try:    
        rec = r.recognize_google(audio_listened,language=lang_code)
              
        # If recognized, write into the file.
        f.write(rec)    
        f.close()
        # If google could not understand the audio
    except sr.UnknownValueError:
        print("Error: Could not understand audio")
        # If the results cannot be requested from Google.
        # Probably an internet connection error.
    except sr.RequestError as e:
        print("Error: Could not request results.")