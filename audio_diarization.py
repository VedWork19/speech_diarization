from resemblyzer import VoiceEncoder
import librosa
from audio_utils import *
from pathlib import Path
from params import *
import os
#check file format
if file[-3:]=="mp4":
	file_path = trim_silence(folder+"\\"+file)
	wav, source_sr = librosa.load(file_path, sr=None)
	wav = librosa.resample(wav, source_sr, 16000)
	duration = librosa.get_duration(y=wav,sr=16000)
elif file[-3:]=="mp3" or file[-3:]=="wav":
	wav_fpath = Path(folder, file)
	x, sr = librosa.load(wav_fpath, sr=None)
	wav = librosa.resample(x, sr, 16000)
	duration = librosa.get_duration(y=wav,sr=16000)
else:
	print("ERROR: Unsupported format " + file[-3:])
	exit()

speaker_wavs = [wav[int(s[0] * sampling_rate):int(s[1] * sampling_rate)] for s in segments]

encoder = VoiceEncoder("cpu")
print("Running the continuous embedding on cpu, this might take a while...")
_, cont_embeds, wav_splits = encoder.embed_utterance(wav, return_partials=True, rate=16)

# Get the continuous similarity for every speaker.
speaker_embeds = [encoder.embed_utterance(speaker_wav) for speaker_wav in speaker_wavs]
similarity_dict = {name: cont_embeds @ speaker_embed for name, speaker_embed in 
                   zip(speaker_names, speaker_embeds)}


## Run the interactive demo
interactive_diarization(duration,similarity_dict, wav, wav_splits)