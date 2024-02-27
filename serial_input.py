import threading
from psychopy import visual, core, event, gui
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from collections import deque
import numpy as np
import serial
import time
from scipy import signal
import struct
import csv
import os
import yaml
from datetime import datetime
from time import sleep

gui1 = []

time_start = 0
time_end = 0

timestamp = datetime.now().strftime("%d-%m-%Y-%H.%M.%S")

output_folder = 'artifacts/experiment_results'
os.makedirs(output_folder, exist_ok=True)

data_folder = 'artifacts/experiment_data'
os.makedirs(data_folder, exist_ok=True)

def record_data():
    # uncomment the lines 31 to 47 to record data from the serial port, and comment line 49.
    ser = serial.Serial('COM3', baudrate=230400)
    sensor_values = []
    sensor_values_notch = []
    
    duration = 5
    end_time = time.time() + duration

    
    try:
        while time.time() < end_time :
            data = ser.read(2)  # Assuming the Arduino sends a 2-byte integer
            print(data)
            sensor_value = struct.unpack('<H', data)[0]
            sensor_values.append(sensor_value)
    except Exception as e:
        print("Error reading from serial port: ", e)
    finally:
        ser.close()

    sensor_values = np.array(sensor_values)

    # sensor_values = np.random.rand(8000) ## comment this line when using arduino

    fs = 8000
    t = np.arange(len(sensor_values[:8000])) / fs
    bandpass_freq = [1, 19] 
    notch_freq = 50 
    sos_bandpass = signal.butter(4, np.array(bandpass_freq) / (fs / 2), 'band', output='sos')
    sensor_values_bandpass = signal.sosfiltfilt(sos_bandpass, sensor_values)

    # Lowpass filter
    lowpass_freq = 5
    sos_lowpass = signal.butter(4, lowpass_freq / (fs / 2), 'low', output='sos')
    sensor_values_lowpass = signal.sosfiltfilt(sos_lowpass, sensor_values_bandpass)

    # Highpass filter
    highpass_freq = 1
    sos_highpass = signal.butter(4, highpass_freq / (fs / 2), 'high', output='sos')
    sensor_values_highpass = signal.sosfiltfilt(sos_highpass, sensor_values_lowpass)

    sos_notch = signal.iirnotch(notch_freq, Q=10, fs=fs)
    sos_notch = signal.tf2sos(sos_notch[0], sos_notch[1]) 
    sensor_values_notch = signal.sosfiltfilt(sos_notch, sensor_values_highpass)

    timestamp1 = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")    
    csv_file_name = f'sensor_data_{timestamp1}.csv'
    csv_file_path = os.path.join(data_folder, csv_file_name)

    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for value in sensor_values_notch:
            csv_writer.writerow([value])

def Training():
    # Define task names and durations
    tasks = ["Right Jaw", "Left Jaw"]  # Task names
    task_duration = 5  # Duration for each task in seconds
    total_duration = 600  # Total duration of alternating tasks in seconds (10 minutes)

    # Display intro
    intro_duration = 3  
    print("Session starting in...")
    for i in range(intro_duration, 0, -1):
        print(i)
        time.sleep(1)

    # Create window
    win_exp = visual.Window(size=[800, 600], units='pix', fullscr=False)
    texts = [visual.TextStim(win_exp, text=task, pos=(0, 0), height=30, color='white') for task in tasks]
    countdown_text = visual.TextStim(win_exp, text="", pos=(0, 0), height=30, color='white')

    # Calculate the number of task switches needed to fill total duration
    num_switches = total_duration // (2 * task_duration)

    while not event.getKeys('escape'):
        # Display tasks and countdown alternately
        for _ in range(num_switches):
            for task in tasks:
                # Display task
                texts[tasks.index(task)].draw()
                win_exp.flip()
                
                # Display countdown
                for i in range(task_duration, 0, -1):
                    countdown_text.text = f"{task} - {i}"
                    countdown_text.draw()
                    win_exp.flip()
                    time.sleep(1)

    # Close window
    win_exp.close()


def MI(countdown_duration):
    win_exp = visual.Window(size=[800, 600], units='pix', fullscr=False)
    texts = [
            visual.TextStim(win_exp, text="Blink", pos=(0, 200), height=30, color='white'),  # North
            visual.TextStim(win_exp, text="Blink", pos=(0, -200), height=30, color='white'),  # South
            visual.TextStim(win_exp, text="Right Jaw", pos=(200, 0), height=30, color='white'),   # East
            visual.TextStim(win_exp, text="Left Jaw", pos=(-200, 0), height=30, color='white')   # West
            ]

    countdown_text = visual.TextStim(win_exp, text="", pos=(0, 0), height=30, color='white')

    # Display the countdown and texts
    for i in range(countdown_duration, 0, -1):
        texts[0].draw()
        texts[1].draw()
        texts[2].draw()
        texts[3].draw()
        countdown_text.text = str(i)
        win_exp.flip()
        countdown_text.draw()
        core.wait(1)

    win_exp.flip()

    core.wait(2)
    win_exp.close()


def flashing(frequency, tex):
    # tex = np.array([[1, -1], [-1, 1]])
    cycles = 8
    size = 500
    # frequency = 8
    win = visual.Window(size=[1024, 700], units='pix', fullscr=False, allowGUI=True)
    stim = visual.GratingStim(win, tex=tex, size=size, units='pix', sf=cycles / size, interpolate=False)
    # Create a TextStim
    text_stim1 = visual.TextStim(win, text="Space to start", pos=(400, 310), height=30, color='white')
    text_stim2 = visual.TextStim(win, text="'r' to start record", pos=(400, 270), height=30, color='white')
    text_stim3 = visual.TextStim(win, text="'t' to stop record", pos=(400, 240), height=30, color='white')
    text_stim4 = visual.TextStim(win, text="'s' to stop", pos=(400, 210), height=30, color='white')
    countdown_text = visual.TextStim(win, text="", pos=(0, 300), height=30, color='white')

    frame_rate = win.getActualFrameRate()
    frame_interval = 1 / frame_rate
    interval = 1 / frequency
    stim_frames = int(np.round(interval / frame_interval))

    # print("Frame rate is {0}. Actual Flashing Frequency will be {1}".format(frame_rate, str(1 / (stim_frames * frame_interval))))

    win.flip()
    n = 0
    recording = False
    paused = False
    time_start = None
    record = False
    i = 0

    exit_program = threading.Event()
    serial_thread = threading.Thread(target=record_data)
    serial_thread.start()

    while not event.getKeys('escape'):
        keys = event.getKeys(['space', 's', 'r','t'])
        if record:
            countdown_text.text = str(i)
            countdown_text.draw()
            i+=1
             
        if 'space' in keys:
            recording = True
            paused = False
            
        elif 's' in keys:
            paused = not paused
        
        elif 'r' in keys:
            time_start = datetime.now()
            # start recording
            record = not record
            print("started...")
            
            record_data()
                
        elif 't' in keys:
            # pause recording
            time_end = datetime.now()
            record = not record
            print("paused...")
            # record_data(record, com_port= gui1[5])

            
        if (recording) and not paused and n % stim_frames == 0:
            stim.tex = -stim.tex

        stim.draw()
        text_stim1.draw()
        text_stim2.draw()
        text_stim3.draw()
        text_stim4.draw()
        win.flip()
        n += 1
    core.wait(frame_interval)
    win.close()

    exit_program.set()
    serial_thread.join()

    flashing_freq = str(1 / (stim_frames * frame_interval))
    duration = time_end - time_start

    return (flashing_freq, duration, frame_rate)

# GUI 1
myDlg = gui.Dlg(title="EEG experiment")

myDlg.addText("Time :" + timestamp)
myDlg.addText(" ")
myDlg.addText('Participant Information')
myDlg.addField('Name:', "Participant 1")
myDlg.addField('Age:', 21)
myDlg.addField('Frequency:', 8)
myDlg.addField('Notch Filtering:', choices=["50Hz", "60Hz", "None"])
myDlg.addField('Stimuls type:', choices=["Flashing", "Checkerboard", "Motor Imagery", "Training", "None"])
myDlg.addField('Countdown Duration:', 5)
myDlg.addField('Serial Port:', choices=["COM4", "COM10", "COM11"])
myDlg.addField('Group:', choices=["Test"])
gui1  = myDlg.show() 

if myDlg.OK:
    print(gui1)
else:
    print('user cancelled')

# GUI 2
if gui1[4] == "Checkerboard":
    tex = np.array([[1, -1], [-1, 1]])
    flashing_freq, duration, frame_rate = flashing(gui1[2], tex)
elif gui1[4] == "Flashing":
    tex = np.array([[-1, 1], [-1, -1]])
    flashing_freq, duration, frame_rate = flashing(gui1[2], tex)
elif gui1[4] == "Motor Imagery":
    MI(gui1[5])
elif gui1[4] == "Training":
    Training()

# GUI 3
myDlg = gui.Dlg(title="EEG experiment - Results", size=600 )
myDlg.addText("Name: Participant 1")
myDlg.addText("Frame Rate" + str(frame_rate))
myDlg.addText("Flashing Frequency" + str(flashing_freq) )
gui2  = myDlg.show()  

if myDlg.OK:
    metrics = {
        'time' : timestamp,
        'Name': gui1[0],
        'Age': gui1[1],  
        'Frequency': gui1[2], 
        'Notch Filtering': gui1[3],
        'Serial Port': gui1[5],
        'Stimulus' : gui1[4],
        'Frame Rate': str(frame_rate),
        'Flashing Frequency': str(flashing_freq),
        'Experiment Duration': str(duration) + ' seconds',
    }

    
    yaml_file_name = f'experiment_metrics_{timestamp}.yaml'
    yaml_file_path = os.path.join(output_folder, yaml_file_name)
    
    with open(yaml_file_path, 'w') as yaml_file:
        yaml.dump(metrics, yaml_file, default_flow_style=False)

else:
    print('user cancelled')


core.quit()