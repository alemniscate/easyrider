import json
import re
import sys

def check_error(buslist):
    bus_id_err = 0
    stop_id_err = 0
    stop_name_err = 0
    next_stop_err = 0
    stop_type_err = 0
    a_time_err = 0
    for dict in buslist:
        bus_id = dict["bus_id"] # Integer
        if not isinstance(bus_id, int):
            bus_id_err += 1

        stop_id = dict["stop_id"] # Integer
        if not isinstance(stop_id, int):
            stop_id_err += 1

        stop_name = dict["stop_name"] # String
        if not isinstance(stop_name, str):
            stop_name_err += 1
        elif stop_name == "":
            stop_name_err += 1
        else:
            match = re.match(r"(([A-Z][a-z]+) ){1,2}(Road|Avenue|Boulevard|Street)$", stop_name)
            if not match:
                stop_name_err += 1
#            else:
#                print(stop_name)
   
        next_stop = dict["next_stop"] # Integer
        if not isinstance(next_stop, int):
            next_stop_err += 1

        stop_type = dict["stop_type"] # Character
        if not isinstance(stop_type, str):
            stop_type_err += 1            
        elif len(stop_type) > 1:
            stop_type_err += 1
        elif stop_type not in("S","O","F",""):
            stop_type_err += 1

        a_time = dict["a_time"] # String
        if not isinstance(a_time, str):
            a_time_err += 1
        elif a_time == "":
            a_time_err += 1
        else:
            match = re.match(r"(\d\d):(\d\d)$", a_time)
            if not match:
                a_time_err += 1
            else:
                hour = int(match.group(1))
                minute = int(match.group(2))
                if hour < 0 or hour > 23:
                    a_time_err += 1
                if minute < 0 or minute > 59:
                    a_time_err += 1
#                else:
#                    print(a_time)

    return bus_id_err, stop_id_err, stop_name_err, next_stop_err, stop_type_err, a_time_err

def print_err(buslist):
    bus_id_err, stop_id_err, stop_name_err, next_stop_err, stop_type_err, a_time_err = check_error(buslist)
    errcount = bus_id_err + stop_id_err + stop_name_err + next_stop_err + stop_type_err + a_time_err
    print(f"Format validation: {errcount} errors")
    # print(f"bus_id: {bus_id_err}")
    # print(f"stop_id: {stop_id_err}")
    print(f"stop_name: {stop_name_err}")
    # print(f"next_stop: {next_stop_err}")
    print(f"stop_type: {stop_type_err}")
    print(f"a_time: {a_time_err}")

def get_buslines(buslist):
    buslines = {}
    for dict in buslist:
        bus_id = dict["bus_id"]
        stop_id = dict["stop_id"]
        if bus_id in buslines:
            stop_id_set = buslines[bus_id]
        else:
            stop_id_set = set()
        stop_id_set.add(stop_id)
        buslines[bus_id] = stop_id_set
    return buslines

def print_buslines(buslist):
    buslines = get_buslines(buslist)
    print("Line names and number of stops:")
    for id in buslines:
        print(f"bus_id: {id}, stops: {len(buslines[id])}")

def get_start_end(buslist):
    buslines = {}
    for dict in buslist:
        bus_id = dict["bus_id"]
        stop_type = dict["stop_type"]
        if bus_id in buslines:
            stop_type_set = buslines[bus_id]
        else:
            stop_type_set = set()
        stop_type_set.add(stop_type)
        buslines[bus_id] = stop_type_set
    return buslines

def check_start_end(buslist):
    buslines = get_start_end(buslist)
    for id in buslines:
        stop_type_set = buslines[id]
        if "S" in stop_type_set and "F" in stop_type_set:
            continue
        else:
            return id
    return 0

def get_start_name(buslist):
    nameset = set()
    for dict in buslist:
        stop_type = dict["stop_type"]
        stop_name = dict["stop_name"]
        if stop_type == "S":
            nameset.add(stop_name)
    return nameset

def get_end_name(buslist):
    nameset = set()
    for dict in buslist:
        stop_type = dict["stop_type"]
        stop_name = dict["stop_name"]
        if stop_type == "F":
            nameset.add(stop_name)
    return nameset

def get_stop_namedict(buslist):
    stop_namedict = {}
    for dict in buslist:
        stop_id = dict["stop_id"]
        stop_name = dict["stop_name"]
        stop_namedict[stop_id] = stop_name
    return stop_namedict

def get_transfer_name(buslist):
    transfer_idset = set()
    stop_dict = get_buslines(buslist)
    stop_namedict = get_stop_namedict(buslist)
    for id in stop_dict:
        for id2 in stop_dict:
            if id == id2:
                continue
            set_ = stop_dict[id].intersection(stop_dict[id2])
            transfer_idset = transfer_idset.union(set_)
    transfer_nameset = set()
    for id in transfer_idset:
        transfer_nameset.add(stop_namedict[id])
    return transfer_nameset

def print_nameset(heading, nameset):
    namelist = list(nameset)
    namelist.sort()
    print(heading, len(namelist), namelist)

def print_stop_name(buslist):
    errid = check_start_end(buslist)
    if errid:
        print(f"There is no start or end stop for the line: {errid}.")
        sys.exit()
    start_set = get_start_name(buslist)
    transfer_set = get_transfer_name(buslist)
    end_set = get_end_name(buslist)
    print_nameset("Start stops:", start_set)
    print_nameset("Transfer stops:", transfer_set)
    print_nameset("Finish stops:", end_set)

def get_busstopdict(buslist):
    busstopdict = {}
    for dict in buslist:
        bus_id = dict["bus_id"]
        stop_id = dict["stop_id"]
        key = (bus_id, stop_id)
        busstopdict[key] = dict
    return busstopdict

def comp_a_time(a_time, next_a_time):
    match = re.match(r"(\d\d):(\d\d)$", a_time)
    hour = int(match.group(1))
    minute = int(match.group(2))
 
    match2 = re.match(r"(\d\d):(\d\d)$", next_a_time)
    hour2 = int(match2.group(1))
    minute2 = int(match2.group(2))

    if hour > hour2:
        return False
    elif hour == hour2:
        if minute > minute2:
            return False
    return True    
      

def check_arrive_time(buslist):
    errlist = []
    busstopdict = get_busstopdict(buslist)
    skip_bus_id = -1
    for key in busstopdict:
        bus_id, stop_id = key
        if bus_id == skip_bus_id:
            continue
        if stop_id == 0:
            continue
        dict = busstopdict[key]
        a_time = dict["a_time"]
        next_stop = dict["next_stop"]
        if next_stop == 0:
            continue
        nextdict = busstopdict[(bus_id, next_stop)]
        next_a_time = nextdict["a_time"]
        if comp_a_time(a_time, next_a_time) == False:
            next_stop_name = nextdict["stop_name"]
            errlist.append((bus_id, next_stop_name))
            skip_bus_id = bus_id
    return errlist

def print_arrival_time(buslist):
    errlist = check_arrive_time(buslist)
    print("Arrival time test:")
    if len(errlist) == 0:
        print("OK")
    else:
        for err in errlist:
            bus_id, next_stop_name = err 
            print(f"bus_id line {bus_id}: wrong time on {next_stop_name}")

def get_ondemand_namelist(buslist):
    ondemand_namelist = []
    for dict in buslist:
        stop_type = dict["stop_type"]
        stop_name = dict["stop_name"]
        if stop_type == "O":
            ondemand_namelist.append(stop_name)
    return ondemand_namelist

def check_ondemand_stop(buslist):
    errlist = []
    ondemand_list = get_ondemand_namelist(buslist)
    not_ondemand_list = ("Sesame Street","Sunset Boulevard","Elm Street","Prospekt Avenue","Bourbon Street","Pilotow Street")
    for name in ondemand_list:
        if name in not_ondemand_list:
            errlist.append(name)
    return errlist

def input_lines():
    text = ""
    while True:
        line = input()
        text += line
        if line == "]":
            break
    return text

text = input()
buslist = json.loads(text)
errlist = check_ondemand_stop(buslist)
print("On demand stops test:")
if len(errlist) == 0:
    print("OK")
else:
    print("Wrong stop type:", errlist)