# S1Control by ZH for PSS
versionNum = 'v0.0.2'
versionDate = '2022/10/25'

import socket
import xmltodict
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font 
import os
import sys
import threading
import time
import hashlib



XRF_IP = '192.168.137.139'
XRF_PORT = 55204
s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((XRF_IP, XRF_PORT))


# BRUKER API COMMANDS to be used with sendCommand
bruker_query_loginstate = '<Query parameter="Login State"/>'
bruker_query_instdef = '<Query parameter="Instrument Definition"/>'
bruker_command_login = '<Command>Login</Command>'
bruker_command_assaystart = '<Command parameter=“Assay”>Start</Command>'
bruker_command_assaystop = '<Command parameter=“Assay”>Stop</Command>'


def instrument_Connect():
    global s
    s.connect((XRF_IP, XRF_PORT))
    instrument_GetInfo()
    instrument_Login()

def instrument_Disconnect():
    global s
    s.close()
    print('Instrument Connection Closed.')

def instrument_StartAssay():
    sendCommand(s, bruker_command_assaystart)

def instrument_StopAssay():
    sendCommand(s, bruker_command_assaystop)

def instrument_Login():
    sendCommand(s, bruker_command_login)




def sendCommand(s, command):
    msg = '<?xml version="1.0" encoding="utf-8"?>'+ command
    msgData = b'\x03\x02\x00\x00\x17\x80'+len(msg).to_bytes(4,'little')+msg.encode('utf-8')+b'\x06\x2A\xFF\xFF'
    sent = s.sendall(msgData)
    if sent == 0:
        raise Exception("XRF Socket connection broken")

def recvChunks(s, expected_len):
    chunks = []
    recv_len = 0
    while recv_len < expected_len:
        chunk = s.recv(expected_len-recv_len)
        if chunk == b'':
            raise Exception("XRF Socket connection broken")
        chunks.append(chunk)
        recv_len = recv_len + len(chunk)
    return b''.join(chunks)

def recvData(s):
    header = recvChunks(s, 10)
    data_size = int.from_bytes(header[6:10], 'little')
    data = recvChunks(s, data_size)
    footer = recvChunks(s, 4)

    if (header[4:6] == b'\x01\x80'):            # 1 - COOKED SPECTRUM
        datatype = '1'
        return data, datatype

    elif (header[4:6] == b'\x02\x80'):          # 2 - RESULTS SET (don't really know when this is used?)
        datatype = '2'
        return data, datatype

    elif (header[4:6] == b'\x03\x80'):          # 3 - RAW SPECTRUM
        datatype = '3'
        return data, datatype

    elif (header[4:6] == b'\x04\x80'):          # 4 - PDZ FILENAME
        datatype = '4'
        return data, datatype

    elif (header[4:6] == b'\x17\x80'):          # 5 - XML PACKET (Response, results?)
        datatype = '5'
        data = data.decode("utf-8").replace('\n','').replace('\r','').replace('\t','')
        data = xmltodict.parse(data)
        if ('Response' in data) and ('@status' in data['Response']) and ('#text' in data['Response']) and ('ogged in ' in data['Response']['#text']):
            datatype = '5a'                     # 5a - XML PACKET, 'Logged in' response
        return data, datatype

    elif (header[4:6] == b'\x18\x80'):          # 6 - STATUS CHANGE     (i.e. trigger pulled/released, assay start/stop/complete, phase change, etc.)
        datatype = '6'
        return data, datatype

    else:                                       # 0 - UNKNOWN DATA
        datatype = '0'
        return data, datatype

    



#sendCommand(s, commandLogin)
#sendCommand(s, queryLoginState)

#sendCommand(s, '<Query parameter="Instrument Definition"/>')


def elementZtoSymbol(Z):        # Returns 1-2 character Element symbol as a string
    if Z <= 118:
        elementSymbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']
        return elementSymbols[Z-1]
    else:
        return 'Error: Z out of range'

def elementZtoSymbolZ(Z):       # Returns 1-2 character Element symbol formatted WITH atomic number in brackets
    if Z <= 118:
        elementSymbols = ['H (1)', 'He (2)', 'Li (3)', 'Be (4)', 'B (5)', 'C (6)', 'N (7)', 'O (8)', 'F (9)', 'Ne (10)', 'Na (11)', 'Mg (12)', 'Al (13)', 'Si (14)', 'P (15)', 'S (16)', 'Cl (17)', 'Ar (18)', 'K (19)', 'Ca (20)', 'Sc (21)', 'Ti (22)', 'V (23)', 'Cr (24)', 'Mn (25)', 'Fe (26)', 'Co (27)', 'Ni (28)', 'Cu (29)', 'Zn (30)', 'Ga (31)', 'Ge (32)', 'As (33)', 'Se (34)', 'Br (35)', 'Kr (36)', 'Rb (37)', 'Sr (38)', 'Y (39)', 'Zr (40)', 'Nb (41)', 'Mo (42)', 'Tc (43)', 'Ru (44)', 'Rh (45)', 'Pd (46)', 'Ag (47)', 'Cd (48)', 'In (49)', 'Sn (50)', 'Sb (51)', 'Te (52)', 'I (53)', 'Xe (54)', 'Cs (55)', 'Ba (56)', 'La (57)', 'Ce (58)', 'Pr (59)', 'Nd (60)', 'Pm (61)', 'Sm (62)', 'Eu (63)', 'Gd (64)', 'Tb (65)', 'Dy (66)', 'Ho (67)', 'Er (68)', 'Tm (69)', 'Yb (70)', 'Lu (71)', 'Hf (72)', 'Ta (73)', 'W (74)', 'Re (75)', 'Os (76)', 'Ir (77)', 'Pt (78)', 'Au (79)', 'Hg (80)', 'Tl (81)', 'Pb (82)', 'Bi (83)', 'Po (84)', 'At (85)', 'Rn (86)', 'Fr (87)', 'Ra (88)', 'Ac (89)', 'Th (90)', 'Pa (91)', 'U (92)', 'Np (93)', 'Pu (94)', 'Am (95)', 'Cm (96)', 'Bk (97)', 'Cf (98)', 'Es (99)', 'Fm (100)', 'Md (101)', 'No (102)', 'Lr (103)', 'Rf (104)', 'Db (105)', 'Sg (106)', 'Bh (107)', 'Hs (108)', 'Mt (109)', 'Ds (110)', 'Rg (111)', 'Cn (112)', 'Nh (113)', 'Fl (114)', 'Mc (115)', 'Lv (116)', 'Ts (117)', 'Og (118)']
        return elementSymbols[Z-1]
    else:
        return 'Error: Z out of range'

def elementZtoName(Z):          # Returns Element name 
    if Z <= 118:
        elementNames = ['Hydrogen', 'Helium', 'Lithium', 'Beryllium', 'Boron', 'Carbon', 'Nitrogen', 'Oxygen', 'Fluorine', 'Neon', 'Sodium', 'Magnesium', 'Aluminium', 'Silicon', 'Phosphorus', 'Sulfur', 'Chlorine', 'Argon', 'Potassium', 'Calcium', 'Scandium', 'Titanium', 'Vanadium', 'Chromium', 'Manganese', 'Iron', 'Cobalt', 'Nickel', 'Copper', 'Zinc', 'Gallium', 'Germanium', 'Arsenic', 'Selenium', 'Bromine', 'Krypton', 'Rubidium', 'Strontium', 'Yttrium', 'Zirconium', 'Niobium', 'Molybdenum', 'Technetium', 'Ruthenium', 'Rhodium', 'Palladium', 'Silver', 'Cadmium', 'Indium', 'Tin', 'Antimony', 'Tellurium', 'Iodine', 'Xenon', 'Caesium', 'Barium', 'Lanthanum', 'Cerium', 'Praseodymium', 'Neodymium', 'Promethium', 'Samarium', 'Europium', 'Gadolinium', 'Terbium', 'Dysprosium', 'Holmium', 'Erbium', 'Thulium', 'Ytterbium', 'Lutetium', 'Hafnium', 'Tantalum', 'Tungsten', 'Rhenium', 'Osmium', 'Iridium', 'Platinum', 'Gold', 'Mercury', 'Thallium', 'Lead', 'Bismuth', 'Polonium', 'Astatine', 'Radon', 'Francium', 'Radium', 'Actinium', 'Thorium', 'Protactinium', 'Uranium', 'Neptunium', 'Plutonium', 'Americium', 'Curium', 'Berkelium', 'Californium', 'Einsteinium', 'Fermium', 'Mendelevium', 'Nobelium', 'Lawrencium', 'Rutherfordium', 'Dubnium', 'Seaborgium', 'Bohrium', 'Hassium', 'Meitnerium', 'Darmstadtium', 'Roentgenium', 'Copernicium', 'Nihonium', 'Flerovium', 'Moscovium', 'Livermorium', 'Tennessine', 'Oganesson']
        return elementNames[Z-1]
    else:
        return 'Error: Z out of range'



def instrument_GetInfo():
    global instr_model
    global instr_serialnumber
    global instr_buildnumber
    global instr_detectormodel
    global instr_detectortype
    global instr_detectorresolution
    global instr_detectormaxTemp
    global instr_detectorminTemp
    global instr_detectorwindowtype
    global instr_detectorwindowthickness
    global instr_sourcemanufacturer
    global instr_sourcetargetZ
    global instr_sourcetargetSymbol
    global instr_sourcetargetName
    global instr_sourcemaxV
    global instr_sourceminV
    global instr_sourcemaxI
    global instr_sourceminI
    global instr_sourcemaxP

    sendCommand(s, bruker_query_instdef)
    # header = recvData(s, 10)
    # data_size = int.from_bytes(header[6:10], 'little')
    # print(data_size)
    # data = recvData(s, data_size)
    # footer = recvData(s, 4)
    # XML Packet Received / Status Change

    data, datatype = recvData(s)

    if datatype == 5:   # If XML packet
        #print(msg)
        # If it returns valid IDF data
        if ('Response' in data) and ('@parameter' in data['Response']) and (data['Response']['@parameter'] == 'instrument definition') and (data['Response']['@status'] == 'success'):
            #All IDF data:
            vers_info = data['Response']['InstrumentDefinition']

            #Broken Down:
            instr_model = vers_info['Model']
            instr_serialnumber = vers_info['SerialNumber']
            instr_buildnumber = vers_info['BuildNumber']

            instr_detectormodel = vers_info['Detector']['DetectorModel']
            instr_detectortype = instr_buildnumber[0:3]
            if instr_detectortype[1] in 'PMK':  # Older detectors with Beryllium windows. eg SPX, SMA, SK6, etc
                instr_detectorwindowtype = 'Beryllium'
                try:
                    instr_detectorwindowthickness = vers_info['Detector']['BerylliumWindowThicknessInuM'] + 'μM'
                except KeyError:
                    instr_detectorwindowthickness = 'Unknown'
            if instr_detectortype[1] in 'G':
                instr_detectorwindowtype = 'Graphene'
                try:
                    instr_detectorwindowthickness = vers_info['Detector']['GrapheneWindowThicknessInuM'] + 'μM'    # In case instrument def is wrong (eg. Martin has graphene det, but only beryllium thickness listed)
                except KeyError:
                    instr_detectorwindowthickness = 'Unknown'
            instr_detectorresolution = vers_info['Detector']['TypicalResolutionIneV'] + 'eV'
            instr_detectormaxTemp = vers_info['Detector']['OperatingTempMaxInC'] + '°C'
            instr_detectorminTemp = vers_info['Detector']['OperatingTempMinInC'] + '°C'

            instr_sourcemanufacturer = vers_info['XrayTube']['Manufacturer']
            instr_sourcetargetZ = vers_info['XrayTube']['TargetElementNumber']
            instr_sourcetargetSymbol = elementZtoSymbol(int(instr_sourcetargetZ))
            instr_sourcetargetName = elementZtoName(int(instr_sourcetargetZ))
            instr_sourcemaxV = vers_info['XrayTube']['OperatingLimits']['MaxHighVoltage'] + 'kV'
            instr_sourceminV = vers_info['XrayTube']['OperatingLimits']['MinHighVoltage'] + 'kV'
            instr_sourcemaxI = vers_info['XrayTube']['OperatingLimits']['MaxAnodeCurrentInuA'] + 'μA'
            instr_sourceminI = vers_info['XrayTube']['OperatingLimits']['MinAnodeCurrentInuA'] + 'μA'
            instr_sourcemaxP = vers_info['XrayTube']['OperatingLimits']['MaxOutputPowerInmW'] + 'mW'

            # a = globals()
            # for i in a:
            #     print(i, ':', a[i])

            # Print Important info to Console
            print(f'Model: {instr_model}')
            print(f'Serial Number: {instr_serialnumber}')
            print(f'Build Number: {instr_buildnumber}')
            print(f'Detector: {instr_detectormodel}')
            print(f'Detector Specs: {instr_detectortype} - {instr_detectorwindowthickness} {instr_detectorwindowtype} window, {instr_detectorresolution} resolution, operating temps {instr_detectormaxTemp} - {instr_detectorminTemp}')
            print(f'Source: {instr_sourcemanufacturer} {instr_sourcemaxP}')
            print(f'Source Target: {instr_sourcetargetName}')
            print(f'Source Voltage Range: {instr_sourceminV} - {instr_sourcemaxV}')
            print(f'Source Current Range: {instr_sourceminI} - {instr_sourcemaxI}')
            


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def xrfListenLoop():
    while True:
        data, datatype = recvData(s)
        if datatype == '6':       # STATUS CHANGE
            msg = data.decode("utf-8").replace('\n','').replace('\r','').replace('\t','')#.replace('<?xml version="1.0" encoding="utf-8"?>','').replace('"','').removeprefix('<Status parameter=').removesuffix('</Status>')
            #if msg[0] == '<':
            #    msg = msg.replace('<','')
            #msg = xmltodict.parse(msg)
            print(msg)

        if datatype == '4':       # PDZ FILENAME
            print('New PDZ!')
            print(data)

        if datatype == '2':
            #print(etree'.tostring(data, pretty_print=True))
            print(data)

        if datatype == '3':       # RAW SPECTRA
            data = hashlib.md5(data).hexdigest()
            print('Raw spectrum')
            print(data)
        
        if datatype == '5':       # XML PACKET
            print(data)
        
        if datatype == '5a':      # XML PACKET, 'logged in' response
            print(f"{data['Response']['@status']}: {data['Response']['#text']}")

        else: 
            print(data)


        time.sleep(0.1)





# GUI

global gui
gui = tk.Tk()
gui.title("S1Control")
#gui.wm_attributes('-toolwindow', 'True',)
#gui.geometry('+5+5')
gui.geometry('400x400')
iconpath = resource_path("pss.ico")
gui.iconbitmap(iconpath)


# Functions for Widgets 

def loginClicked():
    instrument_Login()

def getInfoClicked():
    instrument_GetInfo()
    #listen_thread = threading.Thread(target = instrument_GetInfo)
    #listen_thread.start()

def startAssayClicked():
    instrument_StartAssay()

def listenLoopThreading():
    listen_thread = threading.Thread(target = xrfListenLoop)
    listen_thread.start()



# Fonts
consolas24 = font.Font(family='Consolas', size=24)
consolas20 = font.Font(family='Consolas', size=20)
consolas18 = font.Font(family='Consolas', size=18)
consolas18B = font.Font(family='Consolas', size=18, weight = 'bold')
consolas16 = font.Font(family='Consolas', size=16)
consolas12 = font.Font(family='Consolas', size=12)
consolas10 = font.Font(family='Consolas', size=10)
consolas10B = font.Font(family='Consolas', size=10, weight = 'bold')
consolas09 = font.Font(family='Consolas', size=9)
consolas08 = font.Font(family='Consolas', size=8)

# Colour Assignments
WHITEISH = "#FAFAFA"
NAVYGREY = "#566573"
CHARCOAL = "#181819"
GRAPHITE = "#29292B"

PSS_DARKBLUE = "#252D5C"
PSS_LIGHTBLUE = "#1B75BC"
PSS_ORANGE = "#D85820"
PSS_GREY = "#9E9FA3"

CROW_LGREY = "#4e576c"
CROW_DGREY = "#394d60"
CROW_LBLUE = "#316d90"
CROW_MBLUE = "#1e5073"
CROW_DBLUE = "#062435"

# Colours Used
buttonbg1 = CROW_LBLUE
buttonfg1 = WHITEISH
buttonbg2 = CROW_MBLUE
buttonfg2 = WHITEISH
buttonbg3 = CROW_DBLUE
buttonfg3 = WHITEISH

textfg1 = CHARCOAL


# Frames



# Buttons
button_inst_reconnect = tk.Button(width = 15, text = "Login", font = consolas10, fg = buttonfg1, bg = buttonbg1, command = loginClicked).pack(ipadx=8,ipady=2)
button_inst_startassay = tk.Button(width = 15, text = "Start Assay", font = consolas10, fg = buttonfg2, bg = buttonbg2, command = startAssayClicked).pack(ipadx=8,ipady=2)
button_inst_startlistener = tk.Button(width = 15, text = "start listen", font = consolas10, fg = buttonfg3, bg = buttonbg3, command = listenLoopThreading).pack(ipadx=8,ipady=2)
button_inst_startlistener = tk.Button(width = 15, text = "get instdef", font = consolas10, fg = buttonfg3, bg = buttonbg3, command = getInfoClicked).pack(ipadx=8,ipady=2)



# rest of gui here






def main():
    gui.mainloop()
    #instrument_Connect()
    
    #EXECUTOR.submit(startGUI)
    #EXECUTOR.submit(xrfListenLoop)




if __name__ == "__main__":
    main()


