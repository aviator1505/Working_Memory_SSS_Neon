#################################################################
#%%  Search for both glasses and start recording
#################################################################
import sys
import time
import tkinter as tk
from tkinter import messagebox
from pupil_labs.realtime_api.simple import Device

# Start GUI window
window = tk.Tk()
window.geometry('500x500')
window.title('Dual Mobile Eye Tracking Study')

# Instantiate list of devices and list of ips
# todo: specify your number of devices
num_devices = 2
devices = []
ips = []
recording_ids = []
recording_id = ""
events = ["smalltalk", "fastfriends", "end"]
previous_events = []


def ip_to_device(ips):
    print(ips)
    for ip in ips:
        device = Device(address=ip, port="8080")
        devices.append(device)
    if len(devices) == num_devices:
        messagebox.showinfo('IP address', 'IP address received for all devices')


# Add actions to buttons
def button_search_on_click():
    dialog = tk.Toplevel(window)
    dialog.title('IP Address Search')
    dialog.geometry('300x300')

    label1 = tk.Label(dialog, text="Enter 1st cellphone IP Address")
    label1.pack(pady=10)
    label2 = tk.Label(dialog, text="Enter 2nd cellphone IP Address")
    label2.pack(pady=10)

    entry1 = tk.Entry(dialog, width=30)
    entry1.insert(0, "192.168.2.101")
    entry1.pack(pady=10)
    entry2 = tk.Entry(dialog, width=30)
    entry2.insert(0, "192.168.2.102")
    entry2.pack(pady=10)

    ips = []

    def on_ok():
        cellphone1_ip = entry1.get()
        cellphone2_ip = entry2.get()
        ips.append(cellphone1_ip)
        ips.append(cellphone2_ip)
        ip_to_device(ips)
        button_search.configure(bg="green")
        dialog.destroy()

    ok_button = tk.Button(dialog, text="Ok", command=on_ok)
    ok_button.pack(pady=10)


def button_record_on_click():
    for device in devices:
        recording_id = device.recording_start()
        recording_ids.append(recording_id)
    if len(recording_ids) == num_devices:
        button_record.configure(bg="green")
        messagebox.showinfo('Recording info', 'Recording started in all devices')


def button_add_event_on_click():
    dialog = tk.Toplevel(window)
    dialog.title('Event phase')
    dialog.geometry('300x300')
    selected_option = tk.StringVar(value= "")
    for option in events:
        rb = tk.Radiobutton(dialog, text=option, variable=selected_option, value=option)
        rb.pack(anchor='w')

    def on_ok():
        choice = selected_option.get()
        if choice != "":
            phase = choice
            dialog.destroy()
            try:
                if len(previous_events) > 0:
                    devices[0].send_event(f"end_{previous_events[-1]}", event_timestamp_unix_ns=time.time_ns())
                    devices[1].send_event(f"end_{previous_events[-1]}", event_timestamp_unix_ns=time.time_ns())
                devices[0].send_event(f"start_{phase}", event_timestamp_unix_ns=time.time_ns())
                devices[1].send_event(f"start_{phase}", event_timestamp_unix_ns=time.time_ns())
                previous_events.append(f"{phase}")
            except:
                messagebox.showinfo('Error', 'Unable to send event')
    ok_button = tk.Button(dialog, text="Ok", command=on_ok)
    ok_button.pack(pady=10)


def button_smalltalk_on_click():
    try:
        if len(previous_events) > 0:
            devices[0].send_event(f"end_{previous_events[-1]}", event_timestamp_unix_ns=time.time_ns())
            devices[1].send_event(f"end_{previous_events[-1]}", event_timestamp_unix_ns=time.time_ns())
        devices[0].send_event(f"start_smalltalk", event_timestamp_unix_ns=time.time_ns())
        devices[1].send_event(f"start_smalltalk", event_timestamp_unix_ns=time.time_ns())
        previous_events.append(f"smalltalk")
        button_smalltalk.configure(bg="green")
        button_ff.configure(bg="lightgrey")
    except:
        messagebox.showinfo('Error', 'Unable to send event')


def button_ff_on_click():
    try:
        if len(previous_events) > 0:
            devices[0].send_event(f"end_{previous_events[-1]}", event_timestamp_unix_ns=time.time_ns())
            devices[1].send_event(f"end_{previous_events[-1]}", event_timestamp_unix_ns=time.time_ns())
        devices[0].send_event(f"start_fastfriends", event_timestamp_unix_ns=time.time_ns())
        devices[1].send_event(f"start_fastfriends", event_timestamp_unix_ns=time.time_ns())
        previous_events.append(f"fastfriends")
        button_ff.configure(bg="green")
        button_smalltalk.configure(bg="lightgrey")
    except:
        messagebox.showinfo('Error', 'Unable to send event')


def button_end_on_click():
    try:
        if len(previous_events) > 0:
            devices[0].send_event(f"end_{previous_events[-1]}", event_timestamp_unix_ns=time.time_ns())
            devices[1].send_event(f"end_{previous_events[-1]}", event_timestamp_unix_ns=time.time_ns())
        devices[0].send_event(f"end_conversation", event_timestamp_unix_ns=time.time_ns())
        devices[1].send_event(f"end_conversation", event_timestamp_unix_ns=time.time_ns())
        button_end.configure(bg="green")
        button_smalltalk.configure(bg="lightgrey")
        button_ff.configure(bg="lightgrey")
    except:
        messagebox.showinfo('Error', 'Unable to send event')


def button_sq_on_click():
    try:
        devices[0].send_event(f"start_question", event_timestamp_unix_ns=time.time_ns())
        devices[1].send_event(f"start_question", event_timestamp_unix_ns=time.time_ns())
        button_startquestion.configure(bg="green")
    except:
        messagebox.showinfo('Error', 'Unable to send event')


def button_eq_on_click():
    try:
        devices[0].send_event(f"end_question", event_timestamp_unix_ns=time.time_ns())
        devices[1].send_event(f"end_question", event_timestamp_unix_ns=time.time_ns())
        button_startquestion.configure(bg="lightgrey")
    except:
        messagebox.showinfo('Error', 'Unable to send event')


def button_save_on_click():
    for idx_device, device in enumerate(devices):
        device.recording_stop_and_save()
        device.close()
    button_save.configure(bg="green")
    messagebox.showinfo('End', 'Recording was stopped in all devices\n Recording was saved.')
    time.sleep(1)
    button_save.configure(bg="lightgrey")
    button_end.configure(bg="lightgrey")
    sys.exit(0)


def button_cancel_on_click():
    for device in devices:
        device.recording_cancel()
    button_cancel.configure(bg="green")
    messagebox.showinfo('Recording info', 'Recording discarded in all devices.')
    time.sleep(1)
    button_save.configure(bg="lightgrey")
    button_end.configure(bg="lightgrey")


# Create a LabelFrame
start_frame = tk.LabelFrame(window, text='Start')
events_frame = tk.LabelFrame(window, text='Add Events')
end_frame = tk.LabelFrame(window, text='End')

# Creates buttons used in Tkinter
button_search = tk.Button(start_frame, text='Find Devices', command=button_search_on_click)
button_record = tk.Button(start_frame, text='Start Recording', command=button_record_on_click)

button_smalltalk = tk.Button(events_frame, text='Start Smalltalk', command=button_smalltalk_on_click)
button_ff = tk.Button(events_frame, text='Start Fast Friends', command=button_ff_on_click)
button_startquestion = tk.Button(events_frame, text='Start Reading Out Question', command=button_sq_on_click)
button_endquestion = tk.Button(events_frame, text='End Reading Out Question', command=button_eq_on_click)
button_end = tk.Button(events_frame, text='End Conversation', command=button_end_on_click)

button_save = tk.Button(end_frame, text='Save Recording', command=button_save_on_click)
button_cancel = tk.Button(end_frame, text='Cancel Recording', command=button_cancel_on_click)

start_frame.pack(expand='yes', fill='both')
button_search.pack(pady=10)
button_record.pack(pady=10)
events_frame.pack(expand='yes', fill='both')
button_smalltalk.pack(pady=10)
button_ff.pack(pady=10)
button_startquestion.pack(pady=10)
button_endquestion.pack(pady=10)
end_frame.pack(expand='yes', fill='both')
button_end.pack(pady=10)
button_save.pack(pady=10)
button_cancel.pack(pady=10)

button_search.configure(bg="lightgrey")
button_record.configure(bg="lightgrey")
button_smalltalk.configure(bg="lightgrey")
button_ff.configure(bg="lightgrey")
button_startquestion.configure(bg="lightgrey")
button_endquestion.configure(bg="lightgrey")
button_end.configure(bg="lightgrey")
button_save.configure(bg="lightgrey")
button_end.configure(bg="lightgrey")

window.mainloop()
