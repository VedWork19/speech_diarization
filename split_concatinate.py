import io
from concurrent.futures import ThreadPoolExecutor
import requests
import os
import sys
import json
from pydub import AudioSegment

ip_file = sys.argv[1]

temp_array_first = []
command_array_for_splitting = []
command_array_for_concatinating = []
input_file_for_spliting = ip_file
output_location_after_split = "Output/"
output_format = "." + ip_file[-3:]


##This funcation is responsible for contracting the array.
def arr_shortner(input_array, difference_to_maintain):
    temp_array = []
    final_output_array = []
    temp = len(input_array)
    i = 0
    for x in input_array:
        if i == (temp-1):
            #print(i)
            x.append(round(x[2] - x[1]))
            x.append(x[2])
        else:
            #print(i, "This is inside else")
            x.append(round(x[2] - x[1]))
            x.append(round(input_array[i+1][1] - x[2]))
        i = i +1
        #print(x)

    i = 0
    while i < len(input_array):
        if input_array[i][3] < difference_to_maintain:
            if input_array[i][4] < difference_to_maintain:
                temp_array.append(input_array[i][0])
                temp_array.append(input_array[i][1])
                while input_array[i][4] < difference_to_maintain:
                    i = i + 1
                temp_array.append(input_array[i][2])
                final_output_array.append(temp_array)
                temp_array = []
                i = i + 1
            else:
                temp_array.append(input_array[i][0])
                temp_array.append(input_array[i][1])
                temp_array.append(input_array[i][2] + difference_to_maintain)
                final_output_array.append(temp_array)
                temp_array = []
                i = i + 1
        else:
            if input_array[i][4] < difference_to_maintain:
                temp_array.append(input_array[i][0])
                temp_array.append(input_array[i][1])
                while input_array[i][4] < difference_to_maintain:
                    i = i + 1
                temp_array.append(input_array[i][2])
                final_output_array.append(temp_array)
                temp_array = []
                i = i + 1
            else:
                temp_array.append(input_array[i][0])
                temp_array.append(input_array[i][1])
                temp_array.append(input_array[i][2])
                final_output_array.append(temp_array)
                temp_array = []
                i = i + 1

    ffmpeg_cut(final_output_array)
    return final_output_array

##This funcation is responsible for writing command for splitting, concatinating and writing txt file for concatinating.
def ffmpeg_cut(input_array):
    file_names = []
    i = 0
    #Make command array for splitting
    for x in input_array:
        command_array_for_splitting.append("ffmpeg -i "+ input_file_for_spliting +" -ss "+ str(x[1]) +" -to "+ str(x[2]) +" -c:v libx264 -crf 30 "+ output_location_after_split + x[0]+"_"+str(i)+output_format)
        file_names.append("file '"+x[0]+"_"+str(i)+output_format+"'\n")
        i = i + 1
    #Write txt file for conctinating
    with io.open(output_location_after_split+x[0]+".txt",'w',encoding='utf8') as f:
        f.writelines(file_names)
    #Make command array for concatinating
    command_array_for_concatinating.append("ffmpeg -f concat -safe 0 -i "+output_location_after_split+x[0]+".txt"+" -c copy "+"Final_Output/"+x[0]+output_format)

#This is for executing commands parallely.
def parallel_execution(session, command):
    os.system(command)

with open('labels.json', 'r') as openfile:
    json_object = json.load(openfile)
arr = json_object["label_array"]
arr = sorted(arr, key=lambda x:x[0])
name = arr[0][0]
for x in arr:
    if name == x[0]:
        temp_array_first.append(x)
    else:
        print(arr_shortner(temp_array_first, 2))
        temp_array_first = []
        name = x[0]
        temp_array_first.append(x)

arr_shortner(temp_array_first, 2)

lines = len(command_array_for_splitting) + 1
with ThreadPoolExecutor(max_workers=3) as executor:
    with requests.Session() as session:
        executor.map(parallel_execution, [session] * lines, command_array_for_splitting)
        executor.shutdown(wait=True)

lines = len(command_array_for_concatinating) + 1   
with ThreadPoolExecutor(max_workers=3) as executor:
    with requests.Session() as session:
        executor.map(parallel_execution, [session] * lines, command_array_for_concatinating)
        executor.shutdown(wait=True)