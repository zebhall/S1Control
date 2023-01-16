# S1Control by ZH for PSS
versionNum = 'v0.2.2'
versionDate = '2023/01/13'

import os
import sys
import threading
import time
import pandas as pd
import json
import shutil
import socket
import xmltodict
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, font
from tkinter.ttk import Progressbar, Treeview
import struct
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk



XRF_IP = '192.168.137.139'
XRF_PORT = 55204
xrf =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)



# BRUKER API COMMANDS to be used with sendCommand
bruker_query_loginstate = '<Query parameter="Login State"/>'
bruker_query_armedstate = '<Query parameter="Armed State"/>'
bruker_query_instdef = '<Query parameter="Instrument Definition"/>'
bruker_query_allapplications = '<Query parameter="Applications"/>'
bruker_query_currentapplication = '<Query parameter="ActiveApplication">Include Methods</Query>'
bruker_query_methodsforcurrentapplication = '<Query parameter="Method"></Query>'
bruker_query_currentapplicationprefs = '<Query parameter="User Preferences"></Query>'       # UAP - incl everything
bruker_query_currentapplicationphasetimes = '<Query parameter="Phase Times"/>'
bruker_query_softwareversion = '<Query parameter="Version"/>'       # S1 version, eg 2.7.58.392
bruker_query_nosetemp = '<Query parameter="Nose Temperature"/>'
bruker_command_login = '<Command>Login</Command>'
bruker_command_assaystart = '<Command parameter="Assay">Start</Command>'
bruker_command_assaystop = '<Command parameter="Assay">Stop</Command>'
#bruker_configure_setsystemtime = 
bruker_configure_transmitstatusenable = '<Configure parameter="Transmit Statusmsg">Yes</Configure>'     #Enable transmission of trigger pull/release and assay start/stop status messages
bruker_configure_transmitelementalresultsenable = '<Configure parameter="Transmit Results" grades="No" elements="Yes">Yes</Configure>'      #Enable transmission of elemental results, disables transmission of grade ID / passfail results
bruker_configure_transmitspectraenable = '<Configure parameter="Transmit Spectra">Yes</Configure>'
bruker_configure_transmitspectradisable = '<Configure parameter="Transmit Spectra">No</Configure>'
bruker_configure_transmitstatusmessagesenable = '<Configure parameter="Transmit Statusmsg">Yes</Configure>'


@dataclass
class Assay:
    index: str
    time_finished: str
    time_elapsed: str
    application: str
    results: pd.DataFrame
    spectra: list
    specenergies: list
    legends: list


def instrument_Connect():
    global xrf

    ping = os.system('ping -n 1 -w 40 '+XRF_IP)
    print(f'ping = {ping}')
    if ping != 0:
        if messagebox.askyesno(f'Connection Problem - S1Control {versionNum}', f'S1 Control has not recieved a response from the instrument at {XRF_IP}, and is unable to connect. Would you like to continue trying to connect?'):
            connection_attempt_count = 0
            while ping != 0:       # ping will only equal 0 if there are no errors or timeouts
                ping = os.system('ping -n 1 -w 40 '+XRF_IP)
                time.sleep(0.1)
                print(f'ping = {ping}')
                connection_attempt_count += 1
                if connection_attempt_count >= 50:
                    if messagebox.askyesno(f'Connection Problem - S1Control {versionNum}', f'S1 Control has still not recieved a response from the instrument at {XRF_IP}, and is still unable to connect. Would you like to continue trying to connect?'):
                        connection_attempt_count = 0
                    else:
                        gui.destroy()
        else:
            gui.destroy()

    try:
        xrf.connect((XRF_IP, XRF_PORT))
    except:
        print('Connection Error. Check instrument has booted to login screen and is properly connected before restarting the program.')

def instrument_Disconnect():
    global xrf
    xrf.close()
    printAndLog('Instrument Connection Closed.')

instr_assayrepeatsselected = 1  #initial set

def instrument_StartAssay():
    global spectra
    global assay_catalogue_num
    printAndLog(f'Starting Assay # {str(assay_catalogue_num).zfill(4)}')
    unselectAllAssays()
    clearCurrentSpectra()
    clearResultsfromTable()
    
    spectra = []
    sendCommand(xrf, bruker_command_assaystart)

def instrument_StopAssay():
    global instr_assayrepeatsleft
    instr_assayrepeatsleft = 0
    sendCommand(xrf, bruker_command_assaystop)

def instrument_Login():
    sendCommand(xrf, bruker_command_login)

def instrument_QueryLoginState():
    sendCommand(xrf, bruker_query_loginstate)

def instrument_QueryArmedState():
    sendCommand(xrf, bruker_query_armedstate)

def instrument_QueryCurrentApplicationPreferences():
    sendCommand(xrf, bruker_query_currentapplicationprefs)

def instrument_QueryCurrentApplicationPhaseTimes():
    sendCommand(xrf, bruker_query_currentapplicationphasetimes)

def instrument_QuerySoftwareVersion():
    global s1ver_inlog
    s1ver_inlog = False
    sendCommand(xrf, bruker_query_softwareversion)

def instrument_QueryNoseTemp():
    sendCommand(xrf, bruker_query_nosetemp)

def instrument_ConfigureSystemTime():
    currenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  #time should be format 2015-11-02 09:02:35
    set_time_command = f'<Configure parameter="System Time">{currenttime}</Configure>'      
    sendCommand(xrf, set_time_command)

def instrument_ConfigureTransmitSpectraEnable():
    sendCommand(xrf,bruker_configure_transmitspectraenable)

def instrument_ConfigureTransmitSpectraDisable():
    sendCommand(xrf,bruker_configure_transmitspectradisable)
    


def instrument_SetImportantStartupConfigurables():
    sendCommand(xrf,bruker_configure_transmitstatusmessagesenable)      # enable transmission of trigger pull, assay complete messages, etc. necessary for basic function.
    sendCommand(xrf,bruker_configure_transmitelementalresultsenable)    #Enable transmission of elemental results, disables transmission of grade ID / passfail results
    instrument_ConfigureTransmitSpectraEnable()                         #Enable transmission of trigger pull/release and assay start/stop status messages
    #printAndLog('Instrument Transmit settings have been configured automatically to allow program functionality.')



def printAndLog(data):
    if logFileName != "":
        print(data)
        with open(logFilePath, "a", encoding= 'utf-16') as logFile:
            logbox.configure(state = 'normal')
            logFile.write(time.strftime("%H:%M:%S", time.localtime()))
            logFile.write('\t')
            if type(data) is dict:
                logFile.write(json.dumps(data))
                logbox.insert('end',json.dumps(data))
            elif type(data) is str:
                logFile.write(data) 
                logbox.insert('end', data)
            elif type(data) is pd.DataFrame:    # Because results are printed normally to resultsbox, this should now print results table to log but NOT console.
                logFile.write(data.to_string(index = False).replace('\n','\n\t\t'))
                #logbox.insert('end', data.to_string(index = False))
                logbox.insert('end', 'Assay Results written to log file.')
            else:
                try:
                    logFile.write(data)
                    logbox.insert('end', data)
                except:
                    logFile.write(f'Error: Data type {type(data)} unable to be written to log.')
                    logbox.insert('end',(f'Error: Data type {type(data)} unable to be written to log.'))
            logFile.write("\n")
            logbox.insert('end','\n')
            logbox.see("end")
            logbox.configure(state = 'disabled')


    

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

    if (header[4:6] == b'\x17\x80'):          # 5 - XML PACKET (Usually results?)
        datatype = '5'
        data = data.decode("utf-8")#.replace('\n','').replace('\r','').replace('\t','')
        data = xmltodict.parse(data)
        if ('Response' in data) and ('@status' in data['Response']) and ('#text' in data['Response']):  # and ('ogged in ' in data['Response']['#text']):
            datatype = '5a'                     # 5a - XML PACKET, 'success, assay start' 'success, Logged in' etc response
        elif ('Response' in data) and ('@parameter' in data['Response']) and (data['Response']['@parameter'] == 'applications'):
            datatype = '5b'                     # 5b - XML PACKET, Applications present response
        elif ('Response' in data) and ('@parameter' in data['Response']) and (data['Response']['@parameter'] == 'activeapplication'):
            datatype = '5c'                     # 5c - XML PACKET, Active Application and Methods present response
        
        return data, datatype

    elif (header[4:6] == b'\x01\x80'):          # 1 - COOKED SPECTRUM
        datatype = '1'
        return data, datatype


    elif (header[4:6] == b'\x02\x80'):          # 2 - RESULTS SET (don't really know when this is used?)    // Deprecated?
        datatype = '2'
        return data, datatype

    elif (header[4:6] == b'\x03\x80'):          # 3 - RAW SPECTRUM  // Deprecated?
        datatype = '3'
        return data, datatype

    elif (header[4:6] == b'\x04\x80'):          # 4 - PDZ FILENAME // Deprecated, no longer works :(
        datatype = '4'
        return data, datatype

    elif (header[4:6] == b'\x18\x80'):          # 6 - STATUS CHANGE     (i.e. trigger pulled/released, assay start/stop/complete, phase change, etc.)
        datatype = '6'
        data = data.decode("utf-8").replace('\n','').replace('\r','').replace('\t','')
        data = xmltodict.parse(data)
        return data, datatype

    elif (header[4:6] == b'\x0b\x80'):          # 7 - SPECTRUM ENERGY PACKET
        datatype = '7'
        return data, datatype

    else:                                       # 0 - UNKNOWN DATA
        datatype = '0'
        print(f'****debug: unknown datatype. header = {header}, data = {data}')
        return data, datatype

    



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
    sendCommand(xrf, bruker_query_instdef)
    sendCommand(xrf, bruker_query_allapplications)
    sendCommand(xrf, bruker_query_currentapplication)
    instrument_QuerySoftwareVersion()
    

def printInstrumentInfo():
    printAndLog(f'Model: {instr_model}')
    printAndLog(f'Serial Number: {instr_serialnumber}')
    printAndLog(f'Build Number: {instr_buildnumber}')
    printAndLog(f'Detector: {instr_detectormodel}')
    printAndLog(f'Detector Specs: {instr_detectortype} - {instr_detectorwindowthickness} {instr_detectorwindowtype} window, {instr_detectorresolution} resolution, operating temps {instr_detectormaxTemp} - {instr_detectorminTemp}')
    printAndLog(f'Source: {instr_sourcemanufacturer} {instr_sourcemaxP}')
    printAndLog(f'Source Target: {instr_sourcetargetName}')
    printAndLog(f'Source Voltage Range: {instr_sourceminV} - {instr_sourcemaxV}')
    printAndLog(f'Source Current Range: {instr_sourceminI} - {instr_sourcemaxI}')

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def initialiseLogFile():
    global logFile
    global logFileArchivePath
    global logFileName
    global logFilePath
    global instr_serialnumber
        # Set PC user and name for log file
    try:
        pc_user = os.getlogin()
        pc_device = os.environ['COMPUTERNAME']
    except:
        pc_user = 'Unkown User'
        pc_device = 'Unknown Device'

    # Check for GDrive Paths to save backup of Log file
    if os.path.exists(R'C:\PXRFS\13. Service\Automatic Instrument Logs'):
        driveArchiveLoc = R'C:\PXRFS\13. Service\Automatic Instrument Logs'
    elif os.path.exists(R'G:\.shortcut-targets-by-id\1w2nUsja1tidZ-QYTuemO6DzCaclAmIlm\PXRFS\13. Service\Automatic Instrument Logs'):
        driveArchiveLoc = R'G:\.shortcut-targets-by-id\1w2nUsja1tidZ-QYTuemO6DzCaclAmIlm\PXRFS\13. Service\Automatic Instrument Logs'
    else:
        driveArchiveLoc = None

    if (driveArchiveLoc is not None) and not (os.path.exists(driveArchiveLoc + f'\{instr_serialnumber}')):
        os.makedirs(driveArchiveLoc + f'\{instr_serialnumber}')

    if not os.path.exists(f'{os.getcwd()}\Logs'):
        os.makedirs(f'{os.getcwd()}\Logs')

        # Create Log file using time/date/XRFserial      



    datetimeString = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    logFileName = f'S1Control_Log_{datetimeString}_{instr_serialnumber}.txt'
    logFilePath = f'{os.getcwd()}\Logs\{logFileName}'
    logFileArchivePath = None
    if driveArchiveLoc is not None:
        logFileArchivePath = driveArchiveLoc + f'\{instr_serialnumber}' + f'\{logFileName}'
    

    logFileStartTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    with open(logFilePath, "x", encoding= 'utf-16') as logFile:
        logFile.write(f'TIMESTAMP \tLog File Created: {logFileStartTime} by {pc_device}\{pc_user}, using S1Control {versionNum}. \n')
        logFile.write('--------------------------------------------------------------------------------------------------------------------------------------------\n')

    time.sleep(0.2)
        # Get info to add to Log file
    instrument_GetInfo()

    #     # CLosing **** around idf, app, method info
    # with open(logFilePath, "a", encoding= 'utf-16') as logFile:
    #     logFile.write('--------------------------------------------------------------------------------------------------------------------------------------------\n')


def instrument_GetStates():
    instrument_QueryLoginState()
    instrument_QueryArmedState()


# def delay_func(t, func:function):
#     time.sleep(t)

    

plotLiveSpectra = True     # used for choosing whether live spectra should be plotted



# XRF Listen Loop Functions

def xrfListenLoop_Start(event):
    global listen_thread
    listen_thread = threading.Thread(target=xrfListenLoop)
    listen_thread.daemon = True
    listen_thread.start()
    gui.after(20, xrfListenLoop_Check)

def xrfListenLoop_Check():
    if listen_thread.is_alive():
        gui.after(20, xrfListenLoop_Check)
    else:
        printAndLog('xrf listen loop broke')

def xrfListenLoop():
    global instr_currentapplication
    global instr_currentmethod
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
    global instr_sourcespotsize
    global instr_sourcehaschangeablecollimator
    global instr_firmwareSUPversion
    global instr_firmwareUUPversion
    global instr_firmwareXILINXversion
    global instr_firmwareOMAPkernelversion
    global instr_softwareS1version
    global instr_isarmed
    global instr_isloggedin
    global instr_currentphases
    global instr_currentphase
    global instr_phasecount
    global instr_assayrepeatsleft
    global instr_applicationspresent
    global instr_currentassayspectra
    global instr_currentassayspecenergies
    global instr_currentassaylegends
    global instr_currentassayresults
    global instr_DANGER_stringvar
    global instr_assayisrunning
    global instr_currentnosetemp
    global s1ver_inlog
    global assay_start_time
    global assay_end_time

    while True:
        try:
            data, datatype = recvData(xrf)
        except:
            onInstrDisconnect()

        # 6 - STATUS CHANGE
        if datatype == '6':       

            if '@parameter' in data['Status']:      #   basic status change
                statusparam = data['Status']['@parameter']
                statustext = data['Status']['#text']

                printAndLog(f'Status Change: {statusparam} {statustext}')

                if statusparam == 'Assay' and statustext == 'Start':
                    assay_start_time = time.time()
                    instr_assayisrunning = True
                    instr_currentphase = 0
                    if plotLiveSpectra:
                        clearCurrentSpectra()

                elif statusparam == 'Assay' and statustext == 'Complete':
                    assay_end_time = time.time()
                    instr_assayisrunning = False
                    #print(spectra)
                    try:
                        instr_currentassayspectra.append(spectra[-1])
                        instr_currentassayspecenergies.append(specenergies[-1])
                        legend = f"Phase {instr_currentphase+1}: {txt['sngHVADC']}kV, {round(float(txt['sngCurADC']),2)}μA"
                        instr_currentassaylegends.append(legend)
                        plotSpectrum(spectra[-1], specenergies[-1], plotphasecolours[instr_currentphase],legend)
                    except: printAndLog('Issue with Spectra experienced after completion of Assay.')

                    instrument_QueryNoseTemp()
                    # add full assay with all phases to table and catalogue. this 'assay complete' response is usually recieved at very end of assay, when all other values are in place.
                    #try:
                    completeAssay(instr_currentapplication, instr_currentassayresults, instr_currentassayspectra, instr_currentassayspecenergies, instr_currentassaylegends)
                    #except:
                        #printAndLog('Error: Assay results and spectra were unable to be saved to the table. Was the assay too short to have results?')

                    #reset variables for next assay
                    instr_currentassayspectra = []
                    instr_currentassayspecenergies = []
                    instr_currentassaylegends = []

                    instr_assayrepeatsleft -= 1
                    if instr_assayrepeatsleft <= 0:
                        printAndLog('All Assays complete.')
                        endOfAssaysReset()
                    elif instr_assayrepeatsleft > 0:
                        printAndLog(f'Consecutive Assays remaining: {instr_assayrepeatsleft} more.')
                        instrument_StartAssay()
                    #instr_currentphase = 0
                
                elif statusparam == 'Phase Change':
                    instr_assayisrunning = True
                    #try:
                    instr_currentassayspectra.append(spectra[-1])
                    instr_currentassayspecenergies.append(specenergies[-1])
                    legend = f"Phase {instr_currentphase+1}: {txt['sngHVADC']}kV, {round(float(txt['sngCurADC']),2)}μA"
                    instr_currentassaylegends.append(legend)
                    if plotLiveSpectra:
                        plotSpectrum(spectra[-1], specenergies[-1], plotphasecolours[instr_currentphase],legend)
                    #except: printAndLog('Issue with Spectra experienced after completion of Phase.')
                    instr_currentphase += 1
                
                elif statusparam == 'Armed' and statustext == 'No':
                    instr_isarmed = False
                elif statusparam == 'Armed' and statustext == 'Yes':
                    instr_isarmed = True
                    instr_isloggedin = True
                    
            elif 'Application Selection' in data['Status']:     # new application selected
                printAndLog('New Application Selected.')
                sendCommand(xrf, bruker_query_currentapplication)
                gui.after(300,ui_UpdateCurrentAppAndPhases)            
                # need to find way of queuing app checker

            
            #printAndLog(data)


        elif datatype == '1':       # COOKED SPECTRUM
            txt, spectra = setSpectrum(data)
            #printAndLog(f'New cooked Spectrum Info: {txt}')
            #printAndLog(f'New cooked Spectrum: {spectra}')


        elif datatype == '4':       # PDZ FILENAME // Deprecated, no longer works :(
            printAndLog(f'New PDZ: {data}')


        elif datatype == '2':                     # RESULTS SET (don't really know when this is used?)
            #printAndLog(etree'.tostring(data, pretty_print=True))
            printAndLog(data)

        elif datatype == '3':       # RAW SPECTRA
            #data = hashlib.md5(data).hexdigest()
            printAndLog('Raw spectrum!')
            txt, spectra = setSpectrum(data)
            #printAndLog(data)
        

        # 5 - XML PACKET
        elif datatype == '5':       
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
                        instr_detectorwindowthickness = '?μM'
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
                instr_sourcespotsize = vers_info['SpotSize']['Size'] + 'mm'
                instr_sourcehaschangeablecollimator = vers_info['HasChangeableCollimator']

                instr_firmwareSUPversion = vers_info['SUP']['FirmwareVersion']
                instr_firmwareUUPversion = vers_info['UUP']['FirmwareVersion']
                instr_firmwareXILINXversion = vers_info['DPP']['XilinxFirmwareVersion']
                instr_firmwareOMAPkernelversion = vers_info['OMAP']['KernelVersion']
                # a = globals()
                # for i in a:
                #     printAndLog(i, ':', a[i])

                # Print Important info to Console
                printAndLog(f'Model: {instr_model}')
                printAndLog(f'Serial Number: {instr_serialnumber}')
                printAndLog(f'Build Number: {instr_buildnumber}')
                try: 
                    printAndLog(f'Software: S1 Version {instr_softwareS1version}')
                    s1ver_inlog = True
                except: 
                    s1ver_inlog = False
                printAndLog(f'Firmware: SuP {instr_firmwareSUPversion}, UuP {instr_firmwareUUPversion}')
                printAndLog(f'Detector: {instr_detectormodel}')
                printAndLog(f'Detector Specs: {instr_detectortype} - {instr_detectorwindowthickness} {instr_detectorwindowtype} window, {instr_detectorresolution} resolution, operating temps {instr_detectormaxTemp} - {instr_detectorminTemp}')
                printAndLog(f'Source: {instr_sourcemanufacturer} {instr_sourcemaxP}')
                printAndLog(f'Source Target: {instr_sourcetargetName}')
                printAndLog(f'Source Voltage Range: {instr_sourceminV} - {instr_sourcemaxV}')
                printAndLog(f'Source Current Range: {instr_sourceminI} - {instr_sourcemaxI}')
            
            elif ('Data' in data) and (data['Data']['Elements'] == None):
                printAndLog('ERROR: Calculation Error has occurred, no results provided by instrument. Try Rebooting.')

            # Results packet?
            elif ('Data' in data) and ('ElementData' in data['Data']['Elements']):      
                instr_currentassayresults_analysismode = data['Data']['AnalysisMode']
                instr_currentassayresults_chemistry = list(map(lambda x: {
                    'Z': int(x['AtomicNumber']['#text']),
                    'Compound': x['Compound'],
                    'Concentration(%)': np.around(float(x['Concentration']), 4),
                    'Error(1SD)': np.around(float(x['Error']), 4)},
                    data['Data']['Elements']['ElementData']))
                instr_currentassayresults = pd.DataFrame.from_dict(instr_currentassayresults_chemistry)
                #printAndLog(instr_currentassayresults)
                

            # Phase timings for current application
            elif ('Response' in data) and ('@parameter' in data['Response']) and (data['Response']['@parameter'] == 'phase times') and (data['Response']['@status'] == 'success'):
                instr_currentapplication = data['Response']['Application']
                phaselist = data['Response']['PhaseList']['Phase']
                #printAndLog(f'phaselist len = {len(phaselist)}')
                phasenums = []
                phasenames = []
                phasedurations = []
                try:
                    for phase in phaselist:
                        phasenums.append(phase['@number'])
                        phasenames.append(phase['Name'])
                        phasedurations.append(phase['Duration'])
                except:
                    phasenums.append(phaselist['@number'])
                    phasenames.append(phaselist['Name'])
                    phasedurations.append(phaselist['Duration'])

                instr_currentphases = list(zip(phasenums,phasenames,phasedurations))
                instr_phasecount = len(instr_currentphases)
                printAndLog(f'Current Phases: {instr_currentphases}')
                ui_UpdateCurrentAppAndPhases()


            
            # ERROR HAS OCCURRED
            elif ('InfoReport' in data):    
                printAndLog(data)

            else:
                printAndLog('non-idf xml packet.')
                printAndLog(data)
        
        # 5a - RESPONSE XML PACKET, 'logged in' response etc, usually.
        elif datatype == '5a':      
            if ('@parameter' in data['Response']) and ('login state' in data['Response']['@parameter']):
                if data['Response']['#text'] == 'Yes':
                    instr_isloggedin = True
                elif data['Response']['#text'] == 'No':
                    instr_isloggedin = False
                    instr_isarmed = False

            elif ('@parameter' in data['Response']) and ('armed state' in data['Response']['@parameter']):
                if data['Response']['#text'] == 'Yes':
                    #print(data)
                    instr_isarmed = True
                elif data['Response']['#text'] == 'No':
                    instr_isarmed = False
            
            elif ('@parameter' in data['Response']) and ('nose temperature' in data['Response']['@parameter']):
                instr_currentnosetemp = data['Response']['#text']
                printAndLog(f'Nose Temperature: {instr_currentnosetemp}°C')

            # Response confirming app change
            elif ('#text' in data['Response']) and ('Application successfully set to' in data['Response']['#text']):
                try:
                    s = data['Response']['#text'].split('::')[-1]     # gets app name from #text string like 'Configure:Application successfully set to::Geo'
                    printAndLog(f"Application Changed to '{s}'")
                except: pass
                instrument_QueryCurrentApplicationPhaseTimes()
                #ui_UpdateCurrentAppAndPhases()
            
            # phase times set response
            elif ('@parameter' in data['Response']) and ('phase times' in data['Response']['@parameter']) and ('#text' in data['Response']):
                printAndLog(f"{data['Response']['#text']}")

            elif ('@parameter' in data['Response']) and (data['Response']['@parameter'] == 'version'):
                try: instr_softwareS1version = data['Response']['#text']
                except: instr_softwareS1version = 'UNKNOWN'
                try: 
                    if s1ver_inlog == False:
                        printAndLog(f'Software: S1 Version {instr_softwareS1version}')
                        s1ver_inlog = True
                except: pass
            
            # Secondary Response for Assay Start and Stop for some instruments??? Idk why, should NOT RELY ON
            elif ('#text' in data['Response']) and ('Assay St' in data['Response']['#text']):
                if data['Response']['#text'] == 'Assay Start':
                    printAndLog('Response: Assay Start')
                    instr_assayisrunning = True
                elif data['Response']['#text'] == 'Assay Stop':
                    printAndLog('Response: Assay Stop')
                    instr_assayisrunning = False

            # Response Success log in OR already logged in
            elif ('#text' in data['Response']) and ('@status' in data['Response']) and ('ogged in as' in data['Response']['#text']) and ('success' in data['Response']['@status']):
                instr_isloggedin = True
                printAndLog(f"{data['Response']['@status']}: {data['Response']['#text']}")

            # Transmit results configuration change response ({'Response': {'@parameter': 'transmit spectra', '@status': 'success', '#text': 'Transmit Spectra configuration updated'}})
            elif ('@parameter' in data['Response']) and ('@status' in data['Response']) and ('#text' in data['Response']) and ('transmit' in data['Response']['@parameter']):
                printAndLog(f"{data['Response']['@status']}: {data['Response']['#text']}")

            # Catchall for OTHER unimportant responses confirming configure changes (like time and date set, etc) 
            elif ('#text' in data['Response']) and ('Configure:' in data['Response']['#text']):
                printAndLog(f"{data['Response']['@status']}: {data['Response']['#text']}")


            else: 
                # try: printAndLog(f"{data['Response']['@parameter']}: {data['Response']['#text']}")
                # except: pass
                # try: printAndLog(f"{data['Response']['@status']}: {data['Response']['#text']}")   
                # except:
                #     printAndLog(data)
                printAndLog(data)


        # 5b - XML PACKET, Applications present response
        elif datatype == '5b':      
            try:
                instr_applicationspresent = data['Response']['ApplicationList']['Application']
                printAndLog(f"Applications Available: {data['Response']['ApplicationList']['Application']}")
            except:
                printAndLog(f"Applications Available: Error: Not Found - Was the instrument busy when it was connected?")

        # 5c - XML PACKET, Active Application and Methods present response
        elif datatype == '5c':      
            try:
                instr_currentapplication = data['Response']['Application']
                instr_currentmethod = data['Response']['ActiveMethod']
                printAndLog(f"Current Application: {data['Response']['Application']} | Current Method: {data['Response']['ActiveMethod']} | Methods Available: {data['Response']['MethodList']['Method']}")
            except:
                printAndLog(f"Current Application: Error: Not Found - Was the instrument busy when it was connected?")


        # 7 - SPECTRUM ENERGY PACKET, contains the SpecEnergy structure, cal info (The instrument will transmit a SPECTRUM_ENERGY packet inmmediately before transmitting it’s associated COOKED_SPECTRUM packet. The SpecEnergy iPacketCount member contains an integer that associates the SpecEnergy values with the corresponding COOKED_SPECTRUM packet via the iPacket_Cnt member of the s1_cooked_header structure.)
        elif datatype == '7':       
            specenergies = setSpecEnergy(data)
            pass

        else: 
            printAndLog(data)

        #statusUpdateCheck()
        time.sleep(0.05)





spectra = []
specenergies = []
instr_currentassayspectra = []
instr_currentassayspecenergies = []
instr_currentassaylegends = []

def setSpectrum(data):
    global spectra
    a = {}
    (a['fEVPerChannel'],a['iTDur'],a['iRaw_Cnts'],a['iValid_Cnts'],a['iADur'],a['iADead'],a['iAReset'],a['iALive'],
        a['iPacket_Cnt'],a['Det_Temp'],a['Amb_Temp'],a['iRaw_Cnts_Acc'],a['iValid_Cnts_Acc'],
        a['fTDur'],a['fADur'],a['fADead'],a['fAReset'],a['fALive'],a['lPacket_Cnt'],
        a['iFilterNum'],a['fltElement1'],a['fltThickness1'],a['fltElement2'],a['fltThickness2'],a['fltElement3'],a['fltThickness3'],
        a['sngHVADC'],a['sngCurADC'],a['Toggle']) = struct.unpack('<f4xLLL4xLLLL6xH78xhHxxLL8xfffff4xLihhhhhhffxxbxxxxx', data[0:208])  #originally, struct.unpack('<f4xLLL4xLLLLLHH78xhH2xLLLLfffffLLihhhhhhff2xbbbbbb', data[0:208])
    txt = a
    a['data'] = list(map(lambda x: x[0], struct.iter_unpack('<L', data[208:])))
    idx = len(spectra)-1
    if idx<0 or a['lPacket_Cnt'] == 1:
        spectra.append(a)
    else:
        spectra[idx] = a
    #plotSpectra(spectra[-1]['data'])
    return txt, spectra

def setSpecEnergy(data):
    global specenergies
    b = {}
    (b['iPacketCount'],b['fEVChanStart'],b['fEVPerChannel']) = struct.unpack('<iff', data)
    idx = len(specenergies)-1
    if idx<0:
        specenergies.append(b)
    else:
        specenergies[idx] = b

    return specenergies

assay_catalogue = []
assay_catalogue_num = 1

def completeAssay(assay_application:str, assay_results:pd.DataFrame, assay_spectra:list, assay_specenergies:list, assay_legends:list):
    global assay_catalogue
    global assay_catalogue_num
    global assay_start_time
    global assay_end_time

    newassay = Assay(index = str(assay_catalogue_num).zfill(4),
                     time_finished = time.strftime("%H:%M:%S", time.localtime()),
                     time_elapsed = f'{round((assay_end_time - assay_start_time),2)}s',
                     application = assay_application,
                     results = assay_results,
                     spectra = assay_spectra,
                     specenergies = assay_specenergies,
                     legends=assay_legends
                        )

    assay_catalogue_num+=1

    # make new 'assay' var with results, spectra, time etc
    #assay = [assay_catalogue_num, assay_time, assay_application, assay_results, assay_spectra, assay_specenergies]

    # add assay with all relevant info to catalogue for later recall
    assay_catalogue.append(newassay)
    
    # add entry to assays table
    assaysTable.insert(parent = '',index='end',iid = newassay.index, values = [newassay.index, newassay.application, newassay.time_finished, newassay.time_elapsed])

    # plot, display, and print to log
    plotAssay(newassay)
    displayResults(newassay)
    printAndLog(assay_results)
    printAndLog(f'Assay # {newassay.index} processed sucessfully ({newassay.time_elapsed})')

    # increment catalogue index number for next assay
    
# COLOURS FOR ELEMENT GROUPS
ALKALI_METALS = '#FC8B12'            #'goldenrod1'
ALKALINE_EARTH_METALS = '#FAA23E'    #'DarkOrange1'
TRANSITION_METALS = '#0084FF'        #'RoyalBlue1'
OTHER_METALS = '#5F8DFF'     #'SteelBlue1'487BFA
METALLOIDS = '#9778FE'       #'light slate gray'
NON_METALS = '#FD81FF'       #'light goldenrod'
HALOGENS = '#FF3CD0'         #'plum1'
NOBLE_GASES = '#972EB4'       #'MediumOrchid1'
LANTHANIDES = '#e84f51'     #'firebrick1'
ACTINIDES = '#1BCA66'        #'spring green'

# ELEMENT LIST FOR BUTTONS - FORMAT IS (ATOMIC NUMBER, SYMBOL, NAME, PERIODIC TABLE ROW, PERIODIC TABLE COLUMN, CLASS for bg colour)
element_info = [
    (1, 'H', 'Hydrogen', 1, 1, NON_METALS),
    (2, 'He', 'Helium', 1, 18, NOBLE_GASES),
    (3, 'Li', 'Lithium', 2, 1, ALKALI_METALS),
    (4, 'Be', 'Beryllium', 2, 2, ALKALINE_EARTH_METALS),
    (5, 'B', 'Boron', 2, 13, METALLOIDS),
    (6, 'C', 'Carbon', 2, 14, NON_METALS),
    (7, 'N', 'Nitrogen', 2, 15, NON_METALS),
    (8, 'O', 'Oxygen', 2, 16, NON_METALS),
    (9, 'F', 'Fluorine', 2, 17, HALOGENS),
    (10, 'Ne', 'Neon', 2, 18, NOBLE_GASES),
    (11, 'Na', 'Sodium', 3, 1, ALKALI_METALS),
    (12, 'Mg', 'Magnesium', 3, 2, ALKALINE_EARTH_METALS),
    (13, 'Al', 'Aluminium', 3, 13, OTHER_METALS),
    (14, 'Si', 'Silicon', 3, 14, METALLOIDS),
    (15, 'P', 'Phosphorus', 3, 15, NON_METALS),
    (16, 'S', 'Sulfur', 3, 16, NON_METALS),
    (17, 'Cl', 'Chlorine', 3, 17, HALOGENS),
    (18, 'Ar', 'Argon', 3, 18, NOBLE_GASES),
    (19, 'K', 'Potassium', 4, 1, ALKALI_METALS),
    (20, 'Ca', 'Calcium', 4, 2, ALKALINE_EARTH_METALS),
    (21, 'Sc', 'Scandium', 4, 3, TRANSITION_METALS),
    (22, 'Ti', 'Titanium', 4, 4, TRANSITION_METALS),
    (23, 'V', 'Vanadium', 4, 5, TRANSITION_METALS),
    (24, 'Cr', 'Chromium', 4, 6, TRANSITION_METALS),
    (25, 'Mn', 'Manganese', 4, 7, TRANSITION_METALS),
    (26, 'Fe', 'Iron', 4, 8, TRANSITION_METALS),
    (27, 'Co', 'Cobalt', 4, 9, TRANSITION_METALS),
    (28, 'Ni', 'Nickel', 4, 10, TRANSITION_METALS),
    (29, 'Cu', 'Copper', 4, 11, TRANSITION_METALS),
    (30, 'Zn', 'Zinc', 4, 12, TRANSITION_METALS),
    (31, 'Ga', 'Gallium', 4, 13, OTHER_METALS),
    (32, 'Ge', 'Germanium', 4, 14, METALLOIDS),
    (33, 'As', 'Arsenic', 4, 15, METALLOIDS),
    (34, 'Se', 'Selenium', 4, 16, NON_METALS),
    (35, 'Br', 'Bromine', 4, 17, HALOGENS),
    (36, 'Kr', 'Krypton', 4, 18, NOBLE_GASES),
    (37, 'Rb', 'Rubidium', 5, 1, ALKALI_METALS),
    (38, 'Sr', 'Strontium', 5, 2, ALKALINE_EARTH_METALS),
    (39, 'Y', 'Yttrium', 5, 3, TRANSITION_METALS),
    (40, 'Zr', 'Zirconium', 5, 4, TRANSITION_METALS),
    (41, 'Nb', 'Niobium', 5, 5, TRANSITION_METALS),
    (42, 'Mo', 'Molybdenum', 5, 6, TRANSITION_METALS),
    (43, 'Tc', 'Technetium', 5, 7, TRANSITION_METALS),
    (44, 'Ru', 'Ruthenium', 5, 8, TRANSITION_METALS),
    (45, 'Rh', 'Rhodium', 5, 9, TRANSITION_METALS),
    (46, 'Pd', 'Palladium', 5, 10, TRANSITION_METALS),
    (47, 'Ag', 'Silver', 5, 11, TRANSITION_METALS),
    (48, 'Cd', 'Cadmium', 5, 12, TRANSITION_METALS),
    (49, 'In', 'Indium', 5, 13, OTHER_METALS),
    (50, 'Sn', 'Tin', 5, 14, OTHER_METALS),
    (51, 'Sb', 'Antimony', 5, 15, METALLOIDS),
    (52, 'Te', 'Tellurium', 5, 16, METALLOIDS),
    (53, 'I', 'Iodine', 5, 17, HALOGENS),
    (54, 'Xe', 'Xenon', 5, 18, NOBLE_GASES),
    (55, 'Cs', 'Caesium', 6, 1, ALKALI_METALS),
    (56, 'Ba', 'Barium', 6, 2, ALKALINE_EARTH_METALS),
    (57, 'La', 'Lanthanum', 6, 3, LANTHANIDES),
    (58, 'Ce', 'Cerium', 9, 4, LANTHANIDES),
    (59, 'Pr', 'Praseodymium', 9, 5, LANTHANIDES),
    (60, 'Nd', 'Neodymium', 9, 6, LANTHANIDES),
    (61, 'Pm', 'Promethium', 9, 7, LANTHANIDES),
    (62, 'Sm', 'Samarium', 9, 8, LANTHANIDES),
    (63, 'Eu', 'Europium', 9, 9, LANTHANIDES),
    (64, 'Gd', 'Gadolinium', 9, 10, LANTHANIDES),
    (65, 'Tb', 'Terbium', 9, 11, LANTHANIDES),
    (66, 'Dy', 'Dysprosium', 9, 12, LANTHANIDES),
    (67, 'Ho', 'Holmium', 9, 13, LANTHANIDES),
    (68, 'Er', 'Erbium', 9, 14, LANTHANIDES),
    (69, 'Tm', 'Thulium', 9, 15, LANTHANIDES),
    (70, 'Yb', 'Ytterbium', 9, 16, LANTHANIDES),
    (71, 'Lu', 'Lutetium', 9, 17, LANTHANIDES),
    (72, 'Hf', 'Hafnium', 6, 4, TRANSITION_METALS),
    (73, 'Ta', 'Tantalum', 6, 5, TRANSITION_METALS),
    (74, 'W', 'Tungsten', 6, 6, TRANSITION_METALS),
    (75, 'Re', 'Rhenium', 6, 7, TRANSITION_METALS),
    (76, 'Os', 'Osmium', 6, 8, TRANSITION_METALS),
    (77, 'Ir', 'Iridium', 6, 9, TRANSITION_METALS),
    (78, 'Pt', 'Platinum', 6, 10, TRANSITION_METALS),
    (79, 'Au', 'Gold', 6, 11, TRANSITION_METALS),
    (80, 'Hg', 'Mercury', 6, 12, TRANSITION_METALS),
    (81, 'Tl', 'Thallium', 6, 13, OTHER_METALS),
    (82, 'Pb', 'Lead', 6, 14, OTHER_METALS),
    (83, 'Bi', 'Bismuth', 6, 15, OTHER_METALS),
    (84, 'Po', 'Polonium', 6, 16, METALLOIDS),
    (85, 'At', 'Astatine', 6, 17, HALOGENS),
    (86, 'Rn', 'Radon', 6, 18, NOBLE_GASES),
    (87, 'Fr', 'Francium', 7, 1, ALKALI_METALS),
    (88, 'Ra', 'Radium', 7, 2, ALKALINE_EARTH_METALS),
    (89, 'Ac', 'Actinium', 7, 3, ACTINIDES),
    (90, 'Th', 'Thorium', 10, 4, ACTINIDES),
    (91, 'Pa', 'Protactinium', 10, 5, ACTINIDES),
    (92, 'U', 'Uranium', 10, 6, ACTINIDES),
    (93, 'Np', 'Neptunium', 10, 7, ACTINIDES),
    (94, 'Pu', 'Plutonium', 10, 8, ACTINIDES),
    (95, 'Am', 'Americium', 10, 9, ACTINIDES),
    (96, 'Cm', 'Curium', 10, 10, ACTINIDES),
    (97, 'Bk', 'Berkelium', 10, 11, ACTINIDES),
    (98, 'Cf', 'Californium', 10, 12, ACTINIDES),
    (99, 'Es', 'Einsteinium', 10, 13, ACTINIDES),
    (100, 'Fm', 'Fermium', 10, 14, ACTINIDES),
    (101, 'Md', 'Mendelevium', 10, 15, ACTINIDES),
    (102, 'No', 'Nobelium', 10, 16, ACTINIDES),
    (103, 'Lr', 'Lawrencium', 10, 17, ACTINIDES),
    (104, 'Rf', 'Rutherfordium', 7, 4, TRANSITION_METALS),
    (105, 'Db', 'Dubnium', 7, 5, TRANSITION_METALS),
    (106, 'Sg', 'Seaborgium', 7, 6, TRANSITION_METALS),
    (107, 'Bh', 'Bohrium', 7, 7, TRANSITION_METALS),
    (108, 'Hs', 'Hassium', 7, 8, TRANSITION_METALS),
    (109, 'Mt', 'Meitnerium', 7, 9, TRANSITION_METALS),
    (110, 'Ds', 'Darmstadtium', 7, 10, TRANSITION_METALS),
    (111, 'Rg', 'Roentgenium', 7, 11, TRANSITION_METALS),
    (112, 'Cn', 'Copernicium', 7, 12, TRANSITION_METALS),
    (113, 'Nh', 'Nihonium', 7, 13, OTHER_METALS),
    (114, 'Fl', 'Flerovium', 7, 14, OTHER_METALS),
    (115, 'Mc', 'Moscovium', 7, 15, OTHER_METALS),
    (116, 'Lv', 'Livermorium', 7, 16, OTHER_METALS),
    (117, 'Ts', 'Tennessine', 7, 17, HALOGENS),
    (118, 'Og', 'Oganesson', 7, 18, NOBLE_GASES)]


def onInstrDisconnect():
    messagebox.showwarning('Instrument Disconnected','Error: Connection to the XRF instrument has been lost. The software will be closed, and a log file will be saved.')
    printAndLog('Connection to the XRF instrument was unexpectedly lost. Software will shut down and log will be saved.')
    onClosing()


# GUI

ctk.set_appearance_mode("light")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

gui = ctk.CTk()
gui.title("S1Control")
#gui.wm_attributes('-toolwindow', 'True',)
gui.geometry('+5+5')
#gui.geometry('1380x855')
iconpath = resource_path("pss_lb.ico")
gui.iconbitmap(iconpath)

instr_isarmed = False
instr_isloggedin = False
instr_assayisrunning = False
instr_assayrepeatsleft = 1


# Functions for Widgets 

def statusUpdateCheckerLoop_Start(event):
    global status_thread
    status_thread = threading.Thread(target=statusUpdateChecker)
    status_thread.daemon = True
    status_thread.start()
    gui.after(30, statusUpdateCheckerLoop_Check)

def statusUpdateCheckerLoop_Check():
    if status_thread.is_alive():
        gui.after(20, statusUpdateCheckerLoop_Check)
    else:
        printAndLog('status checker loop machine broke')

def statusUpdateChecker():
    global instr_assayisrunning
    global instr_isarmed
    global instr_isloggedin
    global instr_DANGER_stringvar
    global statuslabel
    while True:
        if instr_isloggedin == False:
            instr_DANGER_stringvar.set('Not Logged In')
            statuslabel.configure(text_color = WHITEISH) 
            statuslabel.configure(fg_color = '#3A3A3A')
            statusframe.configure(fg_color = '#3A3A3A')

        elif instr_isarmed == False:
            instr_DANGER_stringvar.set('Not Armed')
            statuslabel.configure(text_color = WHITEISH) 
            statuslabel.configure(fg_color = '#4D4D4D') 
            statusframe.configure(fg_color = '#4D4D4D')

        elif instr_assayisrunning == True:
            instr_DANGER_stringvar.set('WARNING: X-RAYS')
            statuslabel.configure(text_color = WHITEISH) 
            statuslabel.configure(fg_color = '#D42525')
            statusframe.configure(fg_color = '#D42525')

        else:
            instr_DANGER_stringvar.set('Ready')
            statuslabel.configure(text_color = WHITEISH) 
            statuslabel.configure(fg_color = '#33AF56')
            statusframe.configure(fg_color = '#33AF56')
        
        # print(f'assay is running: {instr_assayisrunning}')
        # print(f'instr is armed: {instr_isarmed}')
        # print(f'instr is logged in: {instr_isloggedin}')
        # print(f'assay is running: {instr_assayisrunning}')


        time.sleep(0.2)
    


def assaySelected(event):
    selection = assaysTable.item(assaysTable.selection())
    selected_assay_catalogue_num = selection['values'][0]
    #selected_assay_application = selection['values'][2]
    assay = assay_catalogue[int(selected_assay_catalogue_num)-1]
    plotAssay(assay)
    displayResults(assay)


total_spec_channels = 2048
#spec_channels = np.array(list(range(1, total_spec_channels+1)))
spec_channels = np.array(list(range(0, total_spec_channels)))

plotphasecolours = ['blue', 'red', 'green', 'pink', 'yellow']
plottedspectra = []
plottedemissionlineslist = []

def plotSpectrum(spectrum, specenergy, colour, spectrum_legend):
    global spectratoolbar
    global spectra_ax
    global fig
    global plottedspectra

    counts = spectrum['data']

    ev_channel_start = specenergy['fEVChanStart']           # starting ev of spectrum channel 1
    ev_per_channel = specenergy['fEVPerChannel']     

    # Use ev per channel etc for bins instead of basic 
    bins = spec_channels * ev_per_channel
    bins = bins + ev_channel_start 
    bins = bins / 1000       # TO GET keV instead of eV

    plottedspectrum = spectra_ax.plot(bins, counts, color=colour,linewidth=0.5, label=spectrum_legend)
    spectra_ax.legend()
    
    plottedspectra.append(plottedspectrum)  # adds spectrum to list of currently plotted spectra, for ease of removal later

    #plotEmissionLines()

    #spectraplot.xlim(0,50)
    #spectraplot.ylim(bottom=0)
    #spectra_ax.autoscale_view(tight=True)
    #spectra_ax.autoscale(enable=True)
    spectratoolbar.update()
    spectracanvas.draw()


def clearCurrentSpectra():
    global spectra_ax
    global plottedspectra
    #spectra_ax.cla()   #clears all plots from ax
    for plottedspectrum in plottedspectra:
        plotref = plottedspectrum.pop(0)    # removes from list
        spectra_ax.lines.remove(plotref)
    try: spectra_ax.get_legend().remove()
    except: pass
    plottedspectra = []     # clears this list which is now probably full of empty refs?
    spectratoolbar.update()
    spectracanvas.draw()

emission_lines_to_plot = []
extraticks = []
extraticklabels = []

def plotEmissionLines():
    global spectratoolbar
    global spectra_ax
    global fig
    global plottedemissionlineslist
    global emission_lines_to_plot

    clearCurrentEmissionLines()

    #energies = [6.40, 7.06]

    linemax = (max((spectra_ax.get_ylim()[1]+2000),10_000))    #max height of emission lines will be at max of data +2000, OR 10000, whichever is higher

    for linedata in emission_lines_to_plot:
        linelabel = linedata[1]
        energy = linedata[2]
        linecol = 'black'
        linedash = (None, None)
        if linedata[1][-2] == 'L':
            linecol = 'grey'
        if linedata[1][-1] == 'β':
            linedash = (4, 2, 4, 2)
        plottedemissionline = spectra_ax.axvline(x = energy, ymin = 0, ymax = 1, color = linecol, dashes = linedash, linewidth = 0.5, label = linelabel)
        plottedemissionlineslist.append(plottedemissionline)
        # extraticks.append(energy)
        # extraticklabels.append(linelabel)   
    # spectra_ax.set_xticks(ticks = list(spectra_ax.get_xticks()).extend(extraticks), labels = (spectra_ax.get_xticklabels()).extend(extraticklabels))
    
    #labelLines(plottedemissionlineslist, align=True, yoffsets=1)

    spectra_ax.legend()
    spectratoolbar.update()
    spectracanvas.draw()


def clearCurrentEmissionLines():
    global spectra_ax
    global plottedemissionlineslist
    global emissionLinesElementslist
    #try:
    for plottedemissionline in plottedemissionlineslist:
        plottedemissionline.remove()
        # lineref = plottedemissionlines.pop()
        # spectra_ax.remove(lineref)
    
    plottedemissionlineslist = []
    emissionLinesElementslist = []
    # except: 
    #     print('error in clearing current emission lines')
    #     pass

    spectra_ax.legend()
    spectratoolbar.update()
    spectracanvas.draw()
        


def plotAssay(assay):
    clearCurrentSpectra()
    # assay[4] should be spectra (list), one entry per phase
    # assay[5] should be specenergies(list), same as above
    colouridx = 0
    for s, e, l, in zip(assay.spectra,assay.specenergies,assay.legends):
        plotSpectrum(s, e, plotphasecolours[colouridx],l)
        colouridx +=1


    clearCurrentEmissionLines()
    plotEmissionLines()

    #printAndLog(f'Assay {assay[0]} plotted.')


def displayResults_logbox_deprecated(assay):
    global resultsbox
    data = assay[3]
    resultsbox.configure(state = 'normal')
    resultsbox.delete(1.0,tk.END)
    resultsbox.insert('end', data.to_string(index = False))
    resultsbox.configure(state = 'disabled')

def clearResultsfromTable():     # Clears all data from results table
    for item in resultsTable.get_children():
      resultsTable.delete(item)


def displayResults(assay):
    global resultsTable
    clearResultsfromTable()
    data = assay.results
    for index, row in data.iterrows():
        resultsTable.insert(parent = '',index='end', values = [row[0],row[1],row[2],row[3]])


def loginClicked():
    instrument_Login()

def getInfoClicked():
    instrument_GetInfo()
    #getinfo_thread = threading.Thread(target = instrument_GetInfo).start()

def startAssayClicked():
    global instr_assayisrunning
    global instr_assayrepeatsselected
    global instr_assayrepeatsleft
    instr_assayrepeatsleft = instr_assayrepeatsselected
    if instr_assayisrunning:
        instrument_StopAssay()
        button_assay_text.set('\u2BC8 Start Assay')
        instr_assayisrunning = False
    else:
        if instr_assayrepeatsselected > 1:
            printAndLog(f'Starting Assays - {instr_assayrepeatsselected} consecutive selected.')
        instrument_StartAssay()
        button_assay_text.set('\u2BC0 Stop Assay')
        instr_assayisrunning = True

def endOfAssaysReset():     # Assumes this is called when assay is completed and no repeats remain to be done
    global instr_assayisrunning
    instr_assayisrunning = False
    if 'Stop Assay' in button_assay_text.get():
        button_assay_text.set('\u2BC8 Start Assay')


phasetimelabels = []
phasetimeentries = []
phasetime1_stringvar = ctk.StringVar()
phasetime2_stringvar = ctk.StringVar()
phasetime3_stringvar = ctk.StringVar()
phasename1_stringvar = ctk.StringVar()
phasename2_stringvar = ctk.StringVar()
phasename3_stringvar = ctk.StringVar()

ui_firsttime = 1

def ui_UpdateCurrentAppAndPhases():    #update application selected and phase timings in UI
    global instr_currentphases
    global instr_currentapplication
    global ui_firsttime
    global dropdown_application
    global dropdown_method
    global p1_entry
    global p2_entry
    global p3_entry
    global p1_label
    global p2_label
    global p3_label
    global applyphasetimes


    phasecount = len(instr_currentphases)

    if ui_firsttime == 1:
        dropdown_application = ctk.CTkOptionMenu(ctrltabview.tab("Assay Controls"), variable=applicationselected_stringvar, values=instr_applicationspresent, command=applicationChoiceMade)
        dropdown_application.grid(row=2,column=0,padx=4, pady=4, columnspan = 2, sticky=tk.NSEW)
        # label_currentapplication_text.set(f'Current Application: ')
        label_currentapplication = ctk.CTkLabel(phaseframe, textvariable=label_currentapplication_text)
        label_currentapplication.grid(row=0, column=0, padx=8, pady=4, columnspan = 2, sticky=tk.NSEW)

        p1_label = ctk.CTkLabel(phaseframe, textvariable=phasename1_stringvar)
        p1_label.grid(row = 1, column = 0, padx=[8,4], pady=4, sticky=tk.NSEW)
        p2_label = ctk.CTkLabel(phaseframe, textvariable=phasename2_stringvar)
        p2_label.grid(row = 2, column = 0, padx=[8,4], pady=4, sticky=tk.NSEW)
        p3_label = ctk.CTkLabel(phaseframe, textvariable=phasename3_stringvar)
        p3_label.grid(row = 3, column = 0, padx=[8,4], pady=4, sticky=tk.NSEW)
        p1_entry = ctk.CTkEntry(phaseframe, textvariable=phasetime1_stringvar)
        p1_entry.grid(row = 1, column = 1, padx=4, pady=4, sticky=tk.NSEW)
        p2_entry = ctk.CTkEntry(phaseframe, textvariable=phasetime2_stringvar)
        p2_entry.grid(row = 2, column = 1, padx=4, pady=4, sticky=tk.NSEW)
        p3_entry = ctk.CTkEntry(phaseframe, textvariable=phasetime3_stringvar)
        p3_entry.grid(row = 3, column = 1, padx=4, pady=4, sticky=tk.NSEW)

        applyphasetimes = ctk.CTkButton(phaseframe, width = 10, text = 'Apply', command = savePhaseTimes) # font=ctk.CTkFont('arial', 20))
        applyphasetimes.grid(row = 1, column = 2, rowspan = phasecount, padx=4, pady=4, ipadx=4, sticky=tk.NSEW)

        ui_firsttime = 0
    

    p1_label.grid_remove()
    p2_label.grid_remove()
    p3_label.grid_remove()
    p1_entry.grid_remove()
    p2_entry.grid_remove()
    p3_entry.grid_remove()

    #dropdown_application.configure(values=instr_applicationspresent)
    applicationselected_stringvar.set(instr_currentapplication)
    label_currentapplication_text.set(f'Current Application: {instr_currentapplication}')

    # for widget in phaseframe.winfo_children():    #first remove all prev widgets in phaseframe
    #     widget.destroy()

    if phasecount>=1:
        phasetime1_stringvar.set(instr_currentphases[0][2])
        phasename1_stringvar.set(instr_currentphases[0][1])
        p1_label.grid()
        p1_entry.grid()

    if phasecount>=2:
        phasetime2_stringvar.set(instr_currentphases[1][2])  
        phasename2_stringvar.set(instr_currentphases[1][1])      
        p2_label.grid()
        p2_entry.grid()

    if phasecount>=3:
        p3_label.grid()
        p3_entry.grid()
        phasetime3_stringvar.set(instr_currentphases[2][2])
        phasename3_stringvar.set(instr_currentphases[2][1])

    applyphasetimes.grid_configure(rowspan = phasecount)

    #gui.update()


def unselectAllAssays():
    global assaysTable
    for i in assaysTable.selection():
        assaysTable.selection_remove(i)

def unselectAllResultCompounds():
    global resultsTable
    for i in resultsTable.selection():
        resultsTable.selection_remove(i)


def treeview_sort_column(treeview, col, reverse):
    l = [(treeview.set(k, col), k) for k in treeview.get_children('')]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        treeview.move(k, '', index)

    # reverse sort next time
    treeview.heading(col, command=lambda _col=col: treeview_sort_column(treeview, _col, not reverse))


def repeatsChoiceMade(val):
    # global instr_assayrepeatsleft
    global instr_assayrepeatsselected
    printAndLog(f'Consecutive Tests Selected: {val}')
    instr_assayrepeatsselected = int(val)
    # instr_assayrepeatsleft = int(val)

def applicationChoiceMade(val):
    cmd = f'<Configure parameter="Application">{val}</Configure>'
    sendCommand(xrf,cmd)


def savePhaseTimes():
    global instr_currentphases
    phasecount = len(instr_currentphases)
    msg = '<Configure parameter="Phase Times"><PhaseList>'
    # len_1 = int(phasetime1_stringvar.get())
    # len_2 = int(phasetime2_stringvar.get())
    # len_3 = int(phasetime3_stringvar.get())
    # num_1 = instr_currentphases[0][0]
    # num_2 = instr_currentphases[1][0]
    # num_3 = instr_currentphases[2][0]
    msg_end = '</PhaseList></Configure>'    
    if phasecount>=1:
        len_1 = int(phasetime1_stringvar.get())
        num_1 = instr_currentphases[0][0]
        ph1 = f'<Phase number="{num_1}" enabled="Yes"><Duration unlimited="No">{len_1}</Duration></Phase>'
        msg = msg+ph1
    if phasecount>=2:
        len_2 = int(phasetime2_stringvar.get())
        num_2 = instr_currentphases[1][0]
        ph2 = f'<Phase number="{num_2}" enabled="Yes"><Duration unlimited="No">{len_2}</Duration></Phase>'
        msg = msg+ph2
    if phasecount>=3:
        len_3 = int(phasetime3_stringvar.get())
        num_3 = instr_currentphases[2][0]
        ph3 = f'<Phase number="{num_3}" enabled="Yes"><Duration unlimited="No">{len_3}</Duration></Phase>'
        msg = msg+ph3
    msg = msg+msg_end
    sendCommand(xrf,msg)
    
    
def onClosing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if logFileArchivePath is not None:
            printAndLog(f'Log File archived to: {logFileArchivePath}')
            printAndLog('S1Control software Closed.')
            shutil.copyfile(logFilePath,logFileArchivePath)
        else:
            printAndLog('Desired Log file archive path was unable to be found. The Log file has not been archived.')
            printAndLog('S1Control software Closed.')
        gui.destroy()

emissionLineElementButtonIDs = []
emissionLinesElementslist = []

linecfg_firsttime = True
linecfgwindows = []

def configureEmissionLinesClicked():
    global linecfg_firsttime
    global linecfgwindows
    global emissionLineElementButtonIDs
    global iconpath
    if linecfg_firsttime:
        linecfg_firsttime = False
        linecfgwindow = ctk.CTkToplevel()
        #linecfgwindow.geometry("700x380")
        linecfgwindow.title('Configure Emission Lines')
        linecfgwindow.iconbitmap(iconpath)
        linecfgwindows.append(linecfgwindow)

        periodictableframe = ctk.CTkFrame(linecfgwindow, width=20, height = 20, corner_radius=5)
        periodictableframe.pack(side=tk.TOP, fill = 'both', expand = True, padx=4, pady=4, ipadx = 4, ipady = 4)

        # Select Element(s) to display Emission Lines:
        for col in range(1,19):
            periodictableframe.columnconfigure(col,weight=1,uniform='third')

        instruc = ctk.CTkLabel(periodictableframe, text = 'Select Element(s) to display Emission Lines:', font=ctk_consolas14B)
        instruc.grid(row=0,column=0, columnspan = 10, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW)

        for e in element_info:
            button = ctk.CTkButton(periodictableframe, text=(str(e[0])+'\n'+(e[1])), width=20, height=30, fg_color=e[5], text_color=WHITEISH, font=ctk_consolas14B, command=lambda Z=int(e[0]): toggleEmissionLine(Z), corner_radius=6)
            button.grid(row=e[3], column=e[4], padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW)
            emissionLineElementButtonIDs.append(button)
        linecfgwindow.protocol("WM_DELETE_WINDOW", lineCfgOnClosing)
    else:
        #Brings back window from being withdrawn instead of fully creating again.
        linecfgwindows[0].deiconify()

def clearEmissionLinesClicked():
    global emissionLinesElementslist
    for z in emissionLinesElementslist:
        toggleEmissionLine(z)



def lineCfgOnClosing():
    # .withdraw() hides, .deiconify() brings back.
    linecfgwindows[0].withdraw()

all_lines = [['Be', 'Be Kα', 0.108], ['B', 'B Kα', 0.183], ['C', 'C Kα', 0.277], ['N', 'N Kα', 0.392], ['O', 'O Kα', 0.525], ['F', 'F Kα', 0.677], ['Ne', 'Ne Kα', 0.849], ['Na', 'Na Kα', 1.04], ['Mg', 'Mg Kα', 1.254], ['Mg', 'Mg Kβ', 1.302], ['Al', 'Al Kα', 1.486], ['Al', 'Al Kβ', 1.557], ['Si', 'Si Kα', 1.74], ['Si', 'Si Kβ', 1.837], ['P', 'P Kα', 2.01], ['P', 'P Kβ', 2.139], ['S', 'S Kα', 2.309], ['S', 'S Kβ', 2.465], ['Cl', 'Cl Kα', 2.622], ['Cl', 'Cl Kβ', 2.812], ['Ar', 'Ar Kα', 2.958], ['Ar', 'Ar Kβ', 3.19], ['K', 'K Kα', 3.314], ['K', 'K Kβ', 3.59], ['Ca', 'Ca Kα', 3.692], ['Ca', 'Ca Kβ', 4.013], ['Sc', 'Sc Kα', 4.093], ['Sc', 'Sc Kβ', 4.464], ['Ti', 'Ti Kα', 4.512], ['Ti', 'Ti Kβ', 4.933], ['Ti', 'Ti Lβ', 0.458], ['Ti', 'Ti Lα', 0.452], ['V', 'V Kα', 4.953], ['V', 'V Kβ', 5.428], ['V', 'V Lβ', 0.518], ['V', 'V Lα', 0.51], ['Cr', 'Cr Kα', 5.415], ['Cr', 'Cr Kβ', 5.947], ['Cr', 'Cr Lβ', 0.582], ['Cr', 'Cr Lα', 0.572], ['Mn', 'Mn Kα', 5.9], ['Mn', 'Mn Kβ', 6.492], ['Mn', 'Mn Lβ', 0.648], ['Mn', 'Mn Lα', 0.637], ['Fe', 'Fe Kα', 6.405], ['Fe', 'Fe Kβ', 7.059], ['Fe', 'Fe Lβ', 0.718], ['Fe', 'Fe Lα', 0.705], ['Co', 'Co Kα', 6.931], ['Co', 'Co Kβ', 7.649], ['Co', 'Co Lβ', 0.79], ['Co', 'Co Lα', 0.775], ['Ni', 'Ni Kα', 7.48], ['Ni', 'Ni Kβ', 8.267], ['Ni', 'Ni Lβ', 0.866], ['Ni', 'Ni Lα', 0.849], ['Cu', 'Cu Kα', 8.046], ['Cu', 'Cu Kβ', 8.904], ['Cu', 'Cu Lβ', 0.947], ['Cu', 'Cu Lα', 0.928], ['Zn', 'Zn Kα', 8.637], ['Zn', 'Zn Kβ', 9.57], ['Zn', 'Zn Lβ', 1.035], ['Zn', 'Zn Lα', 1.012], ['Ga', 'Ga Kα', 9.251], ['Ga', 'Ga Kβ', 10.267], ['Ga', 'Ga Lβ', 1.125], ['Ga', 'Ga Lα', 1.098], ['Ge', 'Ge Kα', 9.886], ['Ge', 'Ge Kβ', 10.982], ['Ge', 'Ge Lβ', 1.218], ['Ge', 'Ge Lα', 1.188], ['As', 'As Kα', 10.543], ['As', 'As Kβ', 11.726], ['As', 'As Lβ', 1.317], ['As', 'As Lα', 1.282], ['Se', 'Se Kα', 11.224], ['Se', 'Se Kβ', 12.497], ['Se', 'Se Lβ', 1.419], ['Se', 'Se Lα', 1.379], ['Br', 'Br Kα', 11.924], ['Br', 'Br Kβ', 13.292], ['Br', 'Br Lβ', 1.526], ['Br', 'Br Lα', 1.481], ['Kr', 'Kr Kα', 12.648], ['Kr', 'Kr Kβ', 14.112], ['Kr', 'Kr Lβ', 1.636], ['Kr', 'Kr Lα', 1.585], ['Rb', 'Rb Kα', 13.396], ['Rb', 'Rb Kβ', 14.961], ['Rb', 'Rb Lβ', 1.751], ['Rb', 'Rb Lα', 1.692], ['Sr', 'Sr Kα', 14.165], ['Sr', 'Sr Kβ', 15.835], ['Sr', 'Sr Lβ', 1.871], ['Sr', 'Sr Lα', 1.806], ['Y', 'Y Kα', 14.958], ['Y', 'Y Kβ', 16.739], ['Y', 'Y Lβ', 1.998], ['Y', 'Y Lα', 1.924], ['Zr', 'Zr Kα', 15.775], ['Zr', 'Zr Kβ', 17.668], ['Zr', 'Zr Lβ', 2.126], ['Zr', 'Zr Lα', 2.044], ['Nb', 'Nb Kα', 16.615], ['Nb', 'Nb Kβ', 18.625], ['Nb', 'Nb Lβ', 2.26], ['Nb', 'Nb Lα', 2.169], ['Mo', 'Mo Kα', 17.48], ['Mo', 'Mo Kβ', 19.606], ['Mo', 'Mo Lβ', 2.394], ['Mo', 'Mo Lα', 2.292], ['Tc', 'Tc Kα', 18.367], ['Tc', 'Tc Kβ', 20.626], ['Tc', 'Tc Lβ', 2.535], ['Tc', 'Tc Lα', 2.423], ['Ru', 'Ru Kα', 19.279], ['Ru', 'Ru Kβ', 21.655], ['Ru', 'Ru Lβ', 2.683], ['Ru', 'Ru Lα', 2.558], ['Rh', 'Rh Kα', 20.216], ['Rh', 'Rh Kβ', 22.724], ['Rh', 'Rh Lβ', 2.834], ['Rh', 'Rh Lα', 2.697], ['Pd', 'Pd Kα', 21.177], ['Pd', 'Pd Kβ', 23.818], ['Pd', 'Pd Lβ', 2.99], ['Pd', 'Pd Lα', 2.838], ['Ag', 'Ag Kα', 22.163], ['Ag', 'Ag Kβ', 24.941], ['Ag', 'Ag Lβ', 3.15], ['Ag', 'Ag Lα', 2.983], ['Cd', 'Cd Kα', 23.173], ['Cd', 'Cd Kβ', 26.093], ['Cd', 'Cd Lβ', 3.315], ['Cd', 'Cd Lα', 3.133], ['In', 'In Kα', 24.21], ['In', 'In Kβ', 27.275], ['In', 'In Lβ', 3.487], ['In', 'In Lα', 3.286], ['Sn', 'Sn Kα', 25.271], ['Sn', 'Sn Kβ', 28.485], ['Sn', 'Sn Lβ', 3.663], ['Sn', 'Sn Lα', 3.444], ['Sb', 'Sb Kα', 26.359], ['Sb', 'Sb Kβ', 29.725], ['Sb', 'Sb Lβ', 3.842], ['Sb', 'Sb Lα', 3.604], ['Te', 'Te Kα', 27.473], ['Te', 'Te Kβ', 30.993], ['Te', 'Te Lβ', 4.029], ['Te', 'Te Lα', 3.768], ['I', 'I Kα', 28.612], ['I', 'I Kβ', 32.294], ['I', 'I Lβ', 4.221], ['I', 'I Lα', 3.938], ['Xe', 'Xe Kα', 29.775], ['Xe', 'Xe Kβ', 33.62], ['Xe', 'Xe Lβ', 4.418], ['Xe', 'Xe Lα', 4.11], ['Cs', 'Cs Kα', 30.973], ['Cs', 'Cs Kβ', 34.982], ['Cs', 'Cs Lβ', 4.619], ['Cs', 'Cs Lα', 4.285], ['Ba', 'Ba Kα', 32.194], ['Ba', 'Ba Kβ', 36.378], ['Ba', 'Ba Lβ', 4.828], ['Ba', 'Ba Lα', 4.466], ['La', 'La Kα', 33.442], ['La', 'La Kβ', 37.797], ['La', 'La Lβ', 5.038], ['La', 'La Lα', 4.647], ['Ce', 'Ce Kα', 34.72], ['Ce', 'Ce Kβ', 39.256], ['Ce', 'Ce Lβ', 5.262], ['Ce', 'Ce Lα', 4.839], ['Pr', 'Pr Kα', 36.027], ['Pr', 'Pr Kβ', 40.749], ['Pr', 'Pr Lβ', 5.492], ['Pr', 'Pr Lα', 5.035], ['Nd', 'Nd Kα', 37.361], ['Nd', 'Nd Kβ', 42.272], ['Nd', 'Nd Lβ', 5.719], ['Nd', 'Nd Lα', 5.228], ['Pm', 'Pm Kα', 38.725], ['Pm', 'Pm Kβ', 43.827], ['Pm', 'Pm Lβ', 5.961], ['Pm', 'Pm Lα', 5.432], ['Sm', 'Sm Kα', 40.118], ['Sm', 'Sm Kβ', 45.414], ['Sm', 'Sm Lβ', 6.201], ['Sm', 'Sm Lα', 5.633], ['Eu', 'Eu Kα', 41.542], ['Eu', 'Eu Kβ', 47.038], ['Eu', 'Eu Lβ', 6.458], ['Eu', 'Eu Lα', 5.849], ['Gd', 'Gd Kα', 42.996], ['Gd', 'Gd Kβ', 48.695], ['Gd', 'Gd Lβ', 6.708], ['Gd', 'Gd Lα', 6.053], ['Tb', 'Tb Kα', 44.482], ['Tb', 'Tb Kβ', 50.385], ['Tb', 'Tb Lβ', 6.975], ['Tb', 'Tb Lα', 6.273], ['Dy', 'Dy Kα', 45.999], ['Dy', 'Dy Kβ', 52.113], ['Dy', 'Dy Lβ', 7.248], ['Dy', 'Dy Lα', 6.498], ['Ho', 'Ho Kα', 47.547], ['Ho', 'Ho Kβ', 53.877], ['Ho', 'Ho Lβ', 7.526], ['Ho', 'Ho Lα', 6.72], ['Er', 'Er Kα', 49.128], ['Er', 'Er Kβ', 55.674], ['Er', 'Er Lβ', 7.811], ['Er', 'Er Lα', 6.949], ['Tm', 'Tm Kα', 50.742], ['Tm', 'Tm Kβ', 57.505], ['Tm', 'Tm Lβ', 8.102], ['Tm', 'Tm Lα', 7.18], ['Yb', 'Yb Kα', 52.388], ['Yb', 'Yb Kβ', 59.382], ['Yb', 'Yb Lβ', 8.402], ['Yb', 'Yb Lα', 7.416], ['Lu', 'Lu Kα', 54.07], ['Lu', 'Lu Kβ', 61.29], ['Lu', 'Lu Lβ', 8.71], ['Lu', 'Lu Lα', 7.655], ['Hf', 'Hf Kα', 55.79], ['Hf', 'Hf Kβ', 63.244], ['Hf', 'Hf Lβ', 9.023], ['Hf', 'Hf Lα', 7.899], ['Ta', 'Ta Kα', 57.535], ['Ta', 'Ta Kβ', 65.222], ['Ta', 'Ta Lβ', 9.343], ['Ta', 'Ta Lα', 8.146], ['W', 'W Kα', 59.318], ['W', 'W Kβ', 67.244], ['W', 'W Lβ', 9.672], ['W', 'W Lα', 8.398], ['Re', 'Re Kα', 61.141], ['Re', 'Re Kβ', 69.309], ['Re', 'Re Lβ', 10.01], ['Re', 'Re Lα', 8.652], ['Os', 'Os Kα', 63.0], ['Os', 'Os Kβ', 71.414], ['Os', 'Os Lβ', 10.354], ['Os', 'Os Lα', 8.911], ['Ir', 'Ir Kα', 64.896], ['Ir', 'Ir Kβ', 73.56], ['Ir', 'Ir Lβ', 10.708], ['Ir', 'Ir Lα', 9.175], ['Pt', 'Pt Kα', 66.831], ['Pt', 'Pt Kβ', 75.75], ['Pt', 'Pt Lβ', 11.071], ['Pt', 'Pt Lα', 9.442], ['Au', 'Au Kα', 68.806], ['Au', 'Au Kβ', 77.982], ['Au', 'Au Lβ', 11.443], ['Au', 'Au Lα', 9.713], ['Hg', 'Hg Kα', 70.818], ['Hg', 'Hg Kβ', 80.255], ['Hg', 'Hg Lβ', 11.824], ['Hg', 'Hg Lα', 9.989], ['Tl', 'Tl Kα', 72.872], ['Tl', 'Tl Kβ', 82.573], ['Tl', 'Tl Lβ', 12.213], ['Tl', 'Tl Lα', 10.269], ['Pb', 'Pb Kα', 74.97], ['Pb', 'Pb Kβ', 84.939], ['Pb', 'Pb Lβ', 12.614], ['Pb', 'Pb Lα', 10.551], ['Bi', 'Bi Kα', 77.107], ['Bi', 'Bi Kβ', 87.349], ['Bi', 'Bi Lβ', 13.023], ['Bi', 'Bi Lα', 10.839], ['Po', 'Po Kα', 79.291], ['Po', 'Po Kβ', 89.803], ['Po', 'Po Lβ', 13.446], ['Po', 'Po Lα', 11.131], ['At', 'At Kα', 81.516], ['At', 'At Kβ', 92.304], ['At', 'At Lβ', 13.876], ['At', 'At Lα', 11.427], ['Rn', 'Rn Kα', 83.785], ['Rn', 'Rn Kβ', 94.866], ['Rn', 'Rn Lβ', 14.315], ['Rn', 'Rn Lα', 11.727], ['Fr', 'Fr Kα', 86.106], ['Fr', 'Fr Kβ', 97.474], ['Fr', 'Fr Lβ', 14.771], ['Fr', 'Fr Lα', 12.031], ['Ra', 'Ra Kα', 88.478], ['Ra', 'Ra Kβ', 100.13], ['Ra', 'Ra Lβ', 15.236], ['Ra', 'Ra Lα', 12.339], ['Ac', 'Ac Kα', 90.884], ['Ac', 'Ac Kβ', 102.846], ['Ac', 'Ac Lβ', 15.713], ['Ac', 'Ac Lα', 12.652], ['Th', 'Th Kα', 93.351], ['Th', 'Th Kβ', 105.605], ['Th', 'Th Lβ', 16.202], ['Th', 'Th Lα', 12.968], ['Pa', 'Pa Kα', 95.868], ['Pa', 'Pa Kβ', 108.427], ['Pa', 'Pa Lβ', 16.703], ['Pa', 'Pa Lα', 13.291], ['U', 'U Kα', 98.44], ['U', 'U Kβ', 111.303], ['U', 'U Lβ', 17.22], ['U', 'U Lα', 13.614], ['Np', 'Np Kα', 101.059], ['Np', 'Np Kβ', 114.234], ['Np', 'Np Lβ', 17.751], ['Np', 'Np Lα', 13.946], ['Pu', 'Pu Kα', 103.734], ['Pu', 'Pu Kβ', 117.228], ['Pu', 'Pu Lβ', 18.296], ['Pu', 'Pu Lα', 14.282], ['Am', 'Am Kα', 106.472], ['Am', 'Am Kβ', 120.284], ['Am', 'Am Lβ', 18.856], ['Am', 'Am Lα', 14.62], ['Cm', 'Cm Kα', 109.271], ['Cm', 'Cm Kβ', 123.403], ['Cm', 'Cm Lβ', 19.427], ['Cm', 'Cm Lα', 14.961], ['Bk', 'Bk Kα', 112.121], ['Bk', 'Bk Kβ', 126.58], ['Bk', 'Bk Lβ', 20.018], ['Bk', 'Bk Lα', 15.308], ['Cf', 'Cf Kα', 115.032], ['Cf', 'Cf Kβ', 129.823], ['Cf', 'Cf Lβ', 20.624], ['Cf', 'Cf Lα', 15.66]]

def toggleEmissionLine(Z):
    global emissionLinesElementslist
    global emissionLineElementButtonIDs
    global emission_lines_to_plot
    #lookup energies for Z, add to list called energies, then call plotemissionlines(energies) etc
    button = emissionLineElementButtonIDs[Z-1]
    element_sym = elementZtoSymbol(Z)
    origfgcolour = element_info[Z-1][5]
    lines = [] # list of lists eg ('Fe', 'Fe Ka', 6.40)
    # for name, line in xraydb.xray_lines(Z).items():
    #     if name in ['Ka1','Ka2','Kb1','Kb2','La1','Lb1']:
    #         ene = float(line.energy)/1000
    #         linedata = [f'{elementZtoSymbol(Z)} {name}',ene]
    #         lines.append(linedata)
    #         #print(f'Adding line: {linedata}')
    for linedata in all_lines:
        if linedata[0] == element_sym:  # symbol
            lines.append(linedata)

    if button.cget("fg_color") == origfgcolour: # ADD TO PLOT LIST AND CHANGE COLOUR TO 'SELECTED'
        button.configure(text_color = CHARCOAL)
        button.configure(fg_color = WHITEISH)
        for linedata in lines:
            emission_lines_to_plot.append(linedata)

    else:                                       # REMOVE FROM PLOT LIST AND CHANGE COLOUR BACK
        button.configure(text_color = WHITEISH)
        button.configure(fg_color = origfgcolour)
        for linedata in lines:
            emission_lines_to_plot.remove(linedata)
        

    # add to list of elements displayed
    emissionLinesElementslist.append(Z)

    #energies = [6.40, 7.06]
    linecfgwindows[0].update()
    plotEmissionLines()
    




# Fonts
consolas24 = font.Font(family='Consolas', size=24)
consolas20 = font.Font(family='Consolas', size=20)
consolas18 = font.Font(family='Consolas', size=18)
consolas18B = font.Font(family='Consolas', size=18, weight = 'bold')
consolas16 = font.Font(family='Consolas', size=16)
consolas13 = font.Font(family='Consolas', size=13)
consolas12 = font.Font(family='Consolas', size=12)
consolas10 = font.Font(family='Consolas', size=10)
consolas10B = font.Font(family='Consolas', size=10, weight = 'bold')
consolas09 = font.Font(family='Consolas', size=9)
consolas08 = font.Font(family='Consolas', size=8)
consolas07 = font.Font(family='Consolas', size=7)
plotfont = {'fontname':'Consolas'}
ctk_segoe14B = ctk.CTkFont(family = 'Segoe UI', size = 14, weight= 'bold')
ctk_segoe12B = ctk.CTkFont(family = 'Segoe UI', size = 12, weight= 'bold')
ctk_consolas08 = ctk.CTkFont(family = 'Consolas', size = 8)
ctk_consolas10 = ctk.CTkFont(family = 'Consolas', size = 10)
ctk_consolas11 = ctk.CTkFont(family = 'Consolas', size = 11)
ctk_consolas12 = ctk.CTkFont(family = 'Consolas', size = 12)
ctk_consolas12B = ctk.CTkFont(family = 'Consolas', size = 12, weight = 'bold')
ctk_consolas13 = ctk.CTkFont(family = 'Consolas', size = 13)
ctk_consolas14B = ctk.CTkFont(family = 'Consolas', size = 14, weight = 'bold')
ctk_consolas15B = ctk.CTkFont(family = 'Consolas', size = 15, weight = 'bold')
ctk_consolas18B = ctk.CTkFont(family = 'Consolas', size = 18, weight = 'bold')
ctk_consolas20B = ctk.CTkFont(family = 'Consolas', size = 20, weight = 'bold')
ctk_default_largeB = ctk.CTkFont(weight = 'bold')


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

# Styles
# Astyle = ttk.Style()
# Astyle.configure('my.TMenubutton', font = consolas10)

guiStyle = ttk.Style()
guiStyle.configure('mystyle.Treeview', highlightthickness=0, bd=0, font= consolas10)        # Modify the font of the body
guiStyle.configure('mystyle.Treeview.Heading', font = consolas10B)                                    # Modify the font of the headings)



# Frames
# LHSframe = ctk.CTkFrame(gui, width=340, corner_radius=0)
# LHSframe.grid(row=0,column=0, rowspan=4, sticky = tk.NSEW)
LHSframe = ctk.CTkFrame(gui, width=340, corner_radius=0)
LHSframe.pack(side=tk.LEFT, anchor = tk.W, fill = 'y', expand = False, padx = 0, pady = 0, ipadx = 0)

# RHSframe = ctk.CTkFrame(gui, width=200, corner_radius=0, fg_color= 'transparent')
# RHSframe.grid(row=0,column=1, columnspan=3, rowspan=4, sticky = tk.NSEW)
RHSframe = ctk.CTkFrame(gui, corner_radius=0, fg_color= 'transparent')
RHSframe.pack(side=tk.RIGHT, anchor = tk.W, fill = 'both', expand = True, padx = 0, pady = 0, ipadx = 0)

# spectraframe = ctk.CTkFrame(RHSframe, width = 700, height = 50, corner_radius = 5)
# spectraframe.grid(row=0, column=0, pady = 10, padx = 10, ipadx = 10, ipady = 5, sticky= tk.NSEW)
spectraframe = ctk.CTkFrame(RHSframe, width = 700, height = 50, corner_radius = 5)
spectraframe.pack(side=tk.TOP, fill = 'both', anchor = tk.N, expand = True, padx = 8, pady = [8,4], ipadx = 4, ipady = 4)

# resultsframe = ctk.CTkFrame(RHSframe, width = 700, height = 300)
# resultsframe.grid(row=1, column=0, pady = 10, padx = 10, ipadx = 10, ipady = 10, sticky= tk.NSEW)
resultsframe = ctk.CTkFrame(RHSframe, width = 700, height = 300)
resultsframe.pack(side=tk.BOTTOM, fill = 'x', anchor = tk.SW, expand = False, padx = 8, pady = [4,8], ipadx = 4, ipady = 4)


# tableframe = tk.Frame(resultsframe, width = 550, height = 300)
# tableframe.grid(row=0, column=0, padx=[10,0], pady=[10,0], ipadx = 0, ipady = 0, sticky= tk.NSEW)
assaytableframe = tk.Frame(resultsframe, width = 450, height = 300)
assaytableframe.pack(side=tk.LEFT, fill = 'both', anchor = tk.SW, expand = False, padx = [8,0], pady = 8, ipadx = 0, ipady = 0)
assaytableframe.pack_propagate(0)


# Status Frame stuff

statusframe = ctk.CTkFrame(LHSframe, width=50, height = 30, corner_radius=5)
statusframe.pack(side = tk.BOTTOM, anchor = tk.S, fill = 'x', expand = False, padx=8, pady=[4, 8])
instr_DANGER_stringvar = tk.StringVar()
statuslabel = ctk.CTkLabel(statusframe, textvariable = instr_DANGER_stringvar, font= ctk_consolas18B)
statuslabel.pack(side = tk.TOP, fill = 'both', anchor = tk.N, expand = True, padx = 2, pady = 2)



# Tabview for controls LHS
ctrltabview = ctk.CTkTabview(LHSframe, height = 300)
#ctrltabview.grid(row=1, column=1, padx=10, pady=[10, 5], sticky=tk.NSEW)
ctrltabview.pack(side = tk.TOP, anchor = tk.N, fill = 'x', expand = False, padx=8, pady=[8, 4])
ctrltabview.add('Assay Controls')
ctrltabview.add('Instrument Settings')
ctrltabview.add('About')
ctrltabview.tab('Assay Controls').grid_columnconfigure(0, weight=1)
ctrltabview.tab('Instrument Settings').grid_columnconfigure(0, weight=1)
ctrltabview.tab('About').grid_columnconfigure(0, weight=1)

phaseframe = ctk.CTkFrame(ctrltabview.tab('Assay Controls'))
phaseframe.grid(row=3, column=0, columnspan = 2, rowspan = 2, padx=4, pady=4, sticky=tk.NSEW)

# About Section
about_blurb1 = ctk.CTkLabel(ctrltabview.tab('About'), text=f'S1Control {versionNum} ({versionDate})\nCreated by Zeb Hall for Portable Spectral Services\nContact: service@portaspecs.com', justify = tk.LEFT, font=ctk_consolas11, text_color=CHARCOAL)
about_blurb1.grid(row=1, column=0, columnspan = 2, rowspan = 2, padx=4, pady=4, sticky=tk.NSEW)
# Buttons
button_assay_text = ctk.StringVar()
button_assay_text.set('\u2BC8 Start Assay')
#button_assay_text.set('\u2715 Stop Assay')
#\u2BC0
button_assay = ctk.CTkButton(ctrltabview.tab('Assay Controls'), width = 13, textvariable = button_assay_text, command = startAssayClicked)#, font = ctk_default_largeB,)
button_assay.grid(row=1, column=0, padx=4, pady=4, sticky=tk.NSEW)

#button_startlistener = tk.Button(width = 15, text = "start listen", font = consolas10, fg = buttonfg3, bg = buttonbg3, command = lambda:xrfListenLoop_Start(None)).pack(ipadx=8,ipady=2)

#button_getinstdef = tk.Button(width = 15, text = "get instdef", font = consolas10, fg = buttonfg3, bg = buttonbg3, command = getInfoClicked).pack(ipadx=8,ipady=2)
button_enablespectra = ctk.CTkButton(ctrltabview.tab("Instrument Settings"), width = 13, text = "Enable Spectra Transmit", command = instrument_ConfigureTransmitSpectraEnable)
button_enablespectra.grid(row=1, column=0, padx=4, pady=4, sticky=tk.NSEW)
button_disablespectra = ctk.CTkButton(ctrltabview.tab("Instrument Settings"), width = 13, text = "Disable Spectra Transmit", command = instrument_ConfigureTransmitSpectraDisable)
button_disablespectra.grid(row=2, column=0, padx=4, pady=4, sticky=tk.NSEW)
button_setsystemtime = ctk.CTkButton(ctrltabview.tab("Instrument Settings"), width = 13, text = "Sync System Time", command = instrument_ConfigureSystemTime)
button_setsystemtime.grid(row=1, column=1, padx=4, pady=4, sticky=tk.NSEW)

button_gets1softwareversion = ctk.CTkButton(ctrltabview.tab("Instrument Settings"), width = 13, text = "Check Software Version", command = instrument_QuerySoftwareVersion)
button_gets1softwareversion.grid(row=3, column=0, padx=4, pady=4, sticky=tk.NSEW)

button_getnosetemp = ctk.CTkButton(ctrltabview.tab("Instrument Settings"), width = 13, text = "Get Nose Temp", command = instrument_QueryNoseTemp)
button_getnosetemp.grid(row=3, column=1, padx=4, pady=4, sticky=tk.NSEW)


#button_getapplicationprefs = tk.Button(configframe, width = 25, text = "get current app prefs", font = consolas10, fg = buttonfg3, bg = buttonbg3, command = instrument_QueryCurrentApplicationPreferences)
#button_getapplicationprefs.grid(row=7, column=1, padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)

button_getapplicationphasetimes = ctk.CTkButton(ctrltabview.tab("Instrument Settings"), width = 13, text = "Get Phase Times", command = instrument_QueryCurrentApplicationPhaseTimes)
button_getapplicationphasetimes.grid(row=2, column=1, padx=4, pady=4, sticky=tk.NSEW)


# Current Instrument Info stuff
label_currentapplication_text = ctk.StringVar()
applicationselected_stringvar = ctk.StringVar(value='Application')
instr_applicationspresent = []

# Consecutive Tests Section
repeats_choice_var = ctk.StringVar(value='\u2B6F Consecutive Tests')
repeats_choice_list = ['1','2','3','4','5','6','7','8','9','10','15','20','50','100']
dropdown_repeattests = ctk.CTkOptionMenu(ctrltabview.tab("Assay Controls"), variable=repeats_choice_var, values=repeats_choice_list, command=repeatsChoiceMade)
dropdown_repeattests.grid(row=1,column=1,padx=4, pady=4, sticky=tk.NSEW)


# Log Box

#logbox_xscroll = tk.Scrollbar(infoframe, orient = 'horizontal')
#logbox_xscroll.grid(row = 3, column = 1, columnspan = 2, sticky = tk.NSEW)
#logbox_yscroll = tk.Scrollbar(infoframe, orient = 'vertical')
#logbox_yscroll.grid(row = 1, column = 3, columnspan = 1, rowspan= 2, sticky = tk.NSEW)
logbox = ctk.CTkTextbox(LHSframe, corner_radius=5, height = 250, width = 320, font = ctk_consolas11, text_color=WHITEISH, fg_color=CHARCOAL, wrap = tk.NONE)
logbox.pack(side = tk.TOP, anchor = tk.N, fill = 'both', expand = True, padx=8, pady=[4, 4])
#logbox.pack(side = tk.TOP, fill = 'both', expand = True, anchor = tk.N)
logbox.configure(state = 'disabled')
#logbox_xscroll.config(command = logbox.xview)
#logbox_yscroll.config(command = logbox.yview)

# Spectraframe Stuff

fig = Figure(figsize = (10, 4), dpi = 100, frameon=False)
#fig.subplots_adjust(left=0.07, bottom=0.095, right=0.99, top=0.98, wspace=None, hspace=None)
fig.set_tight_layout(True)
fig.set_facecolor('#dbdbdb')
fig.set_edgecolor('#dbdbdb')
#print(plt.style.available)
#plt.style.use('seaborn-paper')
plt.style.use('seaborn-whitegrid')
plt.rcParams["font.family"] = "Consolas"
plt.rcParams["font.sans-serif"] = "Helvetica"
spectra_ax = fig.add_subplot(111)
spectra_ax.set_xlabel('Energy (keV)')
spectra_ax.set_ylabel('Counts')
spectra_ax.set_xlim(xmin=0, xmax=50)
#spectra_ax.set_ylim(ymin=0, ymax=50000)
#spectra_ax.autoscale_view()
spectra_ax.autoscale(enable=True,tight=True)
#spectra_ax.axhline(y=0, color='k')
#spectra_ax.axvline(x=0, color='k')
spectracanvas = FigureCanvasTkAgg(fig,master = spectraframe)

spectracanvas.draw()
spectratoolbar = NavigationToolbar2Tk(spectracanvas,spectraframe,pack_toolbar=False)

spectratoolbar.config(background='#dbdbdb')
spectratoolbar._message_label.config(background='#dbdbdb')
spectracanvas.get_tk_widget().pack(side=tk.TOP, fill = 'both', expand = True, padx = 8, pady = [8,0])
spectratoolbar.pack(side=tk.LEFT, fill = 'x', padx = 8, pady = 4, ipadx = 5)
for child in spectratoolbar.winfo_children():
    child.config(background='#dbdbdb')

# Other Toolbar widgets
button_configureemissionlines = ctk.CTkButton(spectraframe, width = 13, text = "Configure Emission Lines", command = configureEmissionLinesClicked)
button_configureemissionlines.pack(side=tk.RIGHT, fill = 'x', padx = 8, pady = 4)

# button_clearemissionlines = ctk.CTkButton(spectraframe, width = 13, text = "Clear Emission Lines", command = clearEmissionLinesClicked)
# button_clearemissionlines.pack(side=tk.RIGHT, fill = 'x', padx = 0, pady = 4)



# Assays Frame Stuff
assaysColumns = ('t_num', 't_app', 't_time', 't_timeelapsed')
assaysTable = Treeview(assaytableframe, columns = assaysColumns, height = "14",  selectmode = "browse", style = 'mystyle.Treeview')
assaysTable.pack(side="top", fill="both", expand=True)

assaysTable.heading('t_num', text = "Assay", anchor = tk.W, command=lambda _col='t_num': treeview_sort_column(assaysTable, _col, False))                  
assaysTable.heading('t_app', text = "Application", anchor = tk.W, command=lambda _col='t_app': treeview_sort_column(assaysTable, _col, False)) 
assaysTable.heading('t_time', text = "Time Completed", anchor = tk.W, command=lambda _col='t_time': treeview_sort_column(assaysTable, _col, False))
assaysTable.heading('t_timeelapsed', text = "Elapsed", anchor = tk.W, command=lambda _col='t_timeelapsed': treeview_sort_column(assaysTable, _col, False))     

assaysTable.column('t_num', minwidth = 50, width = 60, stretch = 0, anchor = tk.W)
assaysTable.column('t_app', minwidth = 125, width = 100, stretch = 1, anchor = tk.W)
assaysTable.column('t_time', minwidth = 100, width = 115, stretch = 0, anchor = tk.W)
assaysTable.column('t_timeelapsed', minwidth = 80, width = 60, stretch = 0, anchor = tk.W)

# assaysTableScrollbarY = ttk.Scrollbar(resultsframe, command=assaysTable.yview)
# assaysTableScrollbarY.grid(column=1, row=0, padx=[0,2], pady=0, sticky = tk.NS)

# resultsTableScrollbarX = ttk.Scrollbar(resultsframe, orient = 'horizontal', command=assaysTable.xview)
# resultsTableScrollbarX.grid(column=0, row=1, padx=0, pady=[0,2], sticky = tk.EW)

# assaysTableScrollbarY = ctk.CTkScrollbar(resultsframe, command=assaysTable.yview)
# assaysTableScrollbarY.grid(column=1, row=0, padx=[0,2], pady=[8,0], sticky = tk.NS)
assaysTableScrollbarY = ctk.CTkScrollbar(resultsframe, command=assaysTable.yview)
assaysTableScrollbarY.pack(side = tk.LEFT, fill = 'y', expand = False, padx=[0,8], pady=8)

# resultsTableScrollbarX = ctk.CTkScrollbar(resultsframe, orientation= 'horizontal', command=assaysTable.xview)
# resultsTableScrollbarX.grid(column=0, row=1, padx=0, pady=[0,2], sticky = tk.EW)

assaysTable.configure(yscrollcommand=assaysTableScrollbarY.set)
# assaysTable.configure(xscrollcommand=resultsTableScrollbarX.set)

assaysTable.bind('<<TreeviewSelect>>', assaySelected)
assaysTable.configure(show = 'headings')

tables = []
tables.append(assaysTable)

# Resultsbox stuff

# resultsbox = ctk.CTkTextbox(resultsframe, corner_radius=5, height = 250, width = 150, font = ctk_consolas11, wrap = tk.NONE)
# resultsbox.pack(side = tk.RIGHT, fill = 'both', expand = True, padx=8, pady=8)
# resultsbox.configure(state = 'disabled')

resultsColumns = ('results_Z', 'results_Compound', 'results_Concentration', 'results_Error')
resultsTable = Treeview(resultsframe, columns = resultsColumns, height = "14",  selectmode = "browse", style = 'mystyle.Treeview')
resultsTable.pack(side = tk.LEFT, fill = 'both', expand = True, padx=[8,0], pady=8)

resultsTable.heading('results_Z', text = 'Z', anchor = tk.W, command=lambda _col='results_Z': treeview_sort_column(resultsTable, _col, False))    
resultsTable.heading('results_Compound', text = 'Compound', anchor = tk.W, command=lambda _col='results_Compound': treeview_sort_column(resultsTable, _col, False))    
resultsTable.heading('results_Concentration', text = 'Concentration %', anchor = tk.W, command=lambda _col='results_Concentration': treeview_sort_column(resultsTable, _col, False))    
resultsTable.heading('results_Error', text = 'Error (1\u03C3)', anchor = tk.W, command=lambda _col='results_Error': treeview_sort_column(resultsTable, _col, False))    

resultsTable.column('results_Z', minwidth = 25, width = 30, stretch = 0, anchor = tk.W)
resultsTable.column('results_Compound', minwidth = 80, width = 90, stretch = 0, anchor = tk.W)
resultsTable.column('results_Concentration', minwidth = 125, width = 140, stretch = 0, anchor = tk.W)
resultsTable.column('results_Error', minwidth = 110, width = 120, anchor = tk.W)

resultsTableScrollbarY = ctk.CTkScrollbar(resultsframe, command=resultsTable.yview)
resultsTableScrollbarY.pack(side = tk.LEFT, fill = 'y', expand = False, padx=[0,8], pady=8)
#resultsTable.bind('<<TreeviewSelect>>', resultCompoundSelected)
resultsTable.configure(show = 'headings')
resultsTable.configure(yscrollcommand=resultsTableScrollbarY.set)

tables.append(resultsTable)


logFileName = ""

# Begin Instrument Connection
instrument_Connect()
statusUpdateCheckerLoop_Start(None)
xrfListenLoop_Start(None)
time.sleep(0.2)
instrument_GetStates()
time.sleep(0.05)
instrument_GetInfo()        # Get info from IDF for log file NAMING purposes
time.sleep(0.3)
initialiseLogFile()     # Must be called after instrument and listen loop are connected and started, and getinfo has been called once, and time has been allowed for loop to read all info into vars
try: gui.title(f"S1Control - {instr_serialnumber}")
except: pass
if instr_isloggedin == False:
    instrument_Login()
time.sleep(0.05)
instrument_SetImportantStartupConfigurables()
time.sleep(0.05)
instrument_QueryCurrentApplicationPhaseTimes()

gui.protocol("WM_DELETE_WINDOW", onClosing)
gui.mainloop()





