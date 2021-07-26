from resemblyzer import sampling_rate
from time import sleep, perf_counter as timer
from sys import stderr
import numpy as np
import json
import os
import sys
from params import *

def trim_silence(file_path):
    exit_stat = os.system("unsilence " + video + " audio_data\\Final_Video.mp4 -sl -15 -y")
    if not exit_stat:
        os.remove(video)
    return "audio_data\\Final_Video.mp4"

def interactive_diarization(duration,similarity_dict, wav, wav_splits, x_crop=5, show_time=True):
    name_array = []
    time_array = []
    similarity_array = []
    i_array = []
    i = 0
    
    times = [((s.start + s.stop) / 2) / sampling_rate for s in wav_splits]
    rate = 1 / (times[1] - times[0])
    crop_range = int(np.round(x_crop * rate))
    ticks = np.arange(0, len(wav_splits), rate)
    ref_time = timer()
    
    for i in range(len(wav_splits)):
        i_array.append(i)
        # Crop plot
        crop = (max(i - crop_range // 2, 0), i + crop_range // 2)
        if show_time:
            crop_ticks = ticks[(crop[0] <= ticks) * (ticks <= crop[1])]
            time_array.append(np.round(crop_ticks / rate).astype(np.int))

        # Plot the prediction
        similarities = [s[i] for s in similarity_dict.values()]
        best = np.argmax(similarities)
        name, similarity = list(similarity_dict.keys())[best], similarities[best]
        name_array.append(name)
        
    labelling = create_labelling(name_array,wav_splits)
    data = {"label_array": labelling}
    json_obj = json.dumps(data, indent=4)
    with open("labels.json", "w") as outfile:
        outfile.write(json_obj)

    if file[-3:]=="mp3" or file[-3:]=="wav":
        os.system("python split_concatinate.py audio_data/"+file)
    else:
        os.system("python split_concatinate.py audio_data/Final_Video.mp4")
    if duration <= 120:
        os.system("python speech_recognition_short.py")
    else:
        os.system("python speech_recognition_long.py")
    os.system("rm -r Output")
    
def create_labelling(labels,wav_splits):

    times = [((s.start + s.stop) / 2) / sampling_rate for s in wav_splits]
    labelling = []
    start_time = 0

    for i,time in enumerate(times):
        if i>0 and labels[i]!=labels[i-1]:
            temp = [str(labels[i-1]),start_time,time]
            labelling.append(list(temp))
            start_time = time
        if i==len(times)-1:
            temp = [str(labels[i]),start_time,time]
            labelling.append(list(temp))

    return labelling