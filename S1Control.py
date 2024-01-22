# S1Control by ZH for PSS
versionNum = "v0.9.6"  # v0.9.6 was the first GeRDA-control version
versionDate = "2024/01/22"

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
from tkinter import ttk, messagebox, font
from tkinter.ttk import Treeview
import struct
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image
import csv
from decimal import Decimal
from plyer import notification as plyer_notification
import subprocess
import ctypes
import logging
import serial
from element_string_lists import (
    elementstr_symbolsonly,
    elementstr_namesonly,
    elementstr_symbolswithzinbrackets,
)


@dataclass
class Assay:
    index: str  # Index num used to track order assays were taken in software. DOES NOT NECESSARILY EQUAL PDZ FILE NUMBER !!!!
    date_completed: str  # Date str showing date assay was completed. format YYYY/MM/DD
    time_completed: str  # Time str showing time assay was completed. format HH:mm:ss
    time_elapsed: str  # Actual elapsed time for Assay (finish time minus start time). from Start pressed to assay completed. typically = (time_total_set + 5n), where n is number of phases
    time_total_set: int  # Total num seconds set for the analysis, i.e. sum of all set phase lengths. (e.g. for 3-phase analysis set to 20s per phase, would equal 60)
    cal_application: str  # Calibration Application used (e.g. GeoExploration, REE_IDX, etc)
    cal_method: str  # Method of the calibration application (e.g. Oxide3Phase for GeoExploration)
    results: pd.DataFrame
    spectra: list
    specenergies: list
    legends: list
    temps: str
    note: str
    sanity_check_passed: str  # 'PASS', 'FAIL', or 'N/A'


@dataclass
class Illumination:
    name: str  # aka 'ID', e.g. 'Exploration_15', 'Std Alloy Hi-Z'
    voltage: int  # tube voltage in kV
    current: float  # tube current in uA
    current_isdefault: bool  # current tuning status for this illumination? 'Yes' = has NOT been tuned (IS default), 'No' = has been tuned (IS NOT default)
    filterposition: str  # actually filter description. e.g. 'Cu 75um:Ti 25um:Al 200um'
    testsample: str  # sample used for autotuning illumination. typically one of 'Al 7075', 'Cu 1100', '2205 SS', etc.
    countrange_min: int  # min counts threshold for autotuning
    countrange_max: int  # max counts threshold for autotuning
    actualcounts: int  # actual tuned counts value at specififed current


def instrument_Connect(instant_connect: bool = False):
    global xrf
    # try:
    #     ping_result = os.system("ping -n 1 -w 40 " + XRF_IP_USB)
    #     print('normal ping failed')
    if instant_connect:
        ping_result = True
    else:
        ping_result = universalPing(XRF_IP_USB, 1)
    # print(f'ping = {ping}')
    # xrf.connect((XRF_IP_USB, XRF_PORT_USB))
    if ping_result == False:
        if messagebox.askyesno(
            f"Connection Problem - S1Control {versionNum}",
            f"S1Control has not recieved a response from the instrument at {XRF_IP_USB}, and is unable to connect. Would you like to continue trying to connect?",
        ):
            connection_attempt_count = 0
            while ping_result == False:
                # ping will only equal 0 if there are no errors or timeouts
                ping_result = universalPing(XRF_IP_USB, 1)
                # os.system('ping -n 1 -w 40 '+XRF_IP_USB)
                time.sleep(0.1)
                # print(f'ping = {universalPing}')
                connection_attempt_count += 1
                if connection_attempt_count >= 5:
                    if messagebox.askyesno(
                        f"Connection Problem - S1Control {versionNum}",
                        f"S1Control has still not recieved a response from the instrument at {XRF_IP_USB}, and is still unable to connect. Would you like to continue trying to connect?",
                    ):
                        connection_attempt_count = 0
                    else:
                        raise SystemExit(0)
                        closeAllThreads()
                        gui.destroy()
        else:
            raise SystemExit(0)
            closeAllThreads()
            gui.destroy()

    try:
        xrf.connect((XRF_IP_USB, XRF_PORT_USB))
    except:
        print(
            "Connection Error. Check instrument has booted to login screen and is properly connected before restarting the program."
        )


def instrument_Disconnect():
    global xrf
    xrf.close()
    printAndLog("Instrument Connection Closed.", "WARNING")


def universalPing(host, num_tries):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    num_tries = str(num_tries)
    # Option for the number of packets as a function of
    param = "-n" if sys.platform.startswith("win") else "-c"
    # Building the command. Ex: "ping -c 1 google.com"
    command = ["ping", param, num_tries, host]
    return subprocess.call(command) == 0


def instrument_StartAssay(
    customassay: bool = False,
    customassay_filter: str = None,
    customassay_voltage: int = None,
    customassay_current: float = None,
    customassay_duration: int = None,
):
    global spectra
    global assay_catalogue_num
    global assay_time_total_set_seconds
    printAndLog(f"Starting Assay # {str(assay_catalogue_num).zfill(4)}", "INFO")
    unselectAllAssays()
    clearCurrentSpectra()
    clearResultsfromTable()

    spectra = []

    if not customassay:
        # if just starting a normal (non-spectrum-only) assay
        sendCommand(xrf, bruker_command_assaystart)

    else:
        printAndLog(
            f"Spectrum-Only Assay Started: ({customassay_voltage:.1f}kV {customassay_current:.1f}uA, {customassay_filter} Filter.)"
        )
        # custom spectrum assay start, with params. assuming:
        customassay_backscatterlimit: int = 0
        # backscatter: 0 = disabled, -1 = intelligent algorithm, >1 = raw counts per second limit
        customassay_rejectpackets: int = 1

        # set phase time for estimate
        assay_time_total_set_seconds = customassay_duration

        # fix formatting of values
        customassay_command = f'<Command parameter="Assay"><StartParameters><Filter>{customassay_filter}</Filter><HighVoltage>{customassay_voltage:.1f}</HighVoltage><AnodeCurrent>{customassay_current:.1f}</AnodeCurrent><AssayDuration>{customassay_duration}</AssayDuration><BackScatterLimit>{customassay_backscatterlimit}</BackScatterLimit><RejectPackets>{customassay_rejectpackets}</RejectPackets></StartParameters></Command>'

        sendCommand(xrf, customassay_command)


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
    sendCommand(xrf, bruker_query_softwareversion)


def instrument_QueryNoseTemp():
    sendCommand(xrf, bruker_query_nosetemp)


def instrument_QueryNosePressure():
    sendCommand(xrf, bruker_query_nosepressure)


def instrument_QueryEditFields():
    sendCommand(xrf, bruker_query_editfields)


def instrument_ConfigureSystemTime():
    currenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # time should be format 2015-11-02 09:02:35
    set_time_command = f'<Configure parameter="System Time">{currenttime}</Configure>'
    sendCommand(xrf, set_time_command)


def instrument_ConfigureTransmitSpectraEnable():
    sendCommand(xrf, bruker_configure_transmitspectraenable)


def instrument_ConfigureTransmitSpectraDisable():
    sendCommand(xrf, bruker_configure_transmitspectradisable)


def instrument_ConfigureProximityEnable():
    sendCommand(xrf, bruker_configure_proximityenable)


def instrument_ConfigureProximityDisable():
    sendCommand(xrf, bruker_configure_proximitydisable)


def instrument_toggleProximity(prox_button_bool: bool):
    if prox_button_bool == True:
        instrument_ConfigureProximityEnable()
    elif prox_button_bool == False:
        instrument_ConfigureProximityDisable()
    else:
        printAndLog("ERROR: Cannot toggle proximity. Toggle value invalid.")


def instrument_ConfigureStoreResultsEnable():
    sendCommand(xrf, bruker_configure_storeresultsenable)


def instrument_ConfigureStoreResultsDisable():
    sendCommand(xrf, bruker_configure_storeresultsdisable)


def instrument_toggleStoreResultFiles(store_results_button_bool: bool):
    if store_results_button_bool == True:
        instrument_ConfigureStoreResultsEnable()
    elif store_results_button_bool == False:
        instrument_ConfigureStoreResultsDisable()
    else:
        printAndLog("ERROR: Cannot toggle store-results. Toggle value invalid.")


def instrument_ConfigureStoreSpectraEnable():
    sendCommand(xrf, bruker_configure_storespectraenable)


def instrument_ConfigureStoreSpectraDisable():
    sendCommand(xrf, bruker_configure_storespectradisable)


def instrument_toggleStoreSpectraFiles(store_spectra_button_bool: bool):
    if store_spectra_button_bool == True:
        instrument_ConfigureStoreSpectraEnable()
    elif store_spectra_button_bool == False:
        instrument_ConfigureStoreSpectraDisable()
    else:
        printAndLog("ERROR: Cannot toggle store-spectra. Toggle value invalid.")


def instrument_ResetInfoFields():
    sendCommand(xrf, bruker_configure_resetinfofields)


def instrument_SetImportantStartupConfigurables():
    # enable transmission of trigger pull, assay complete messages, etc. necessary for basic function.
    sendCommand(xrf, bruker_configure_transmitstatusmessagesenable)
    # Enable transmission of elemental results, disables transmission of grade ID / passfail results
    sendCommand(xrf, bruker_configure_transmitelementalresultsenable)
    # Enable transmission of trigger pull/release and assay start/stop status messages
    instrument_ConfigureTransmitSpectraEnable()
    # printAndLog('Instrument Transmit settings have been configured automatically to allow program functionality.')


def instrument_AcknowledgeError(TxMsgID):
    sendCommand(xrf, f'<Acknowledge RxMsgID="{TxMsgID}" UserAcked="Yes"></Acknowledge>')


def printAndLog(data, logbox_colour_tag="BASIC"):
    """prints data to UI logbox and txt log file. logbox_colour_tag can be:

    'ERROR' (red), 'WARNING' (yellow/orange), 'INFO' (blue), or 'BASIC' (white).

    This colour selection may be overidden if the message contains 'ERROR' or 'WARNING'
    """

    if logFileName != "":
        # print(data)
        # Check for validity of logbox colour tag value. if invalid, set to default.
        if logbox_colour_tag not in ["ERROR", "WARNING", "INFO", "BASIC"]:
            logbox_colour_tag = "BASIC"
        with open(logFilePath, "a", encoding="utf-16") as logFile:
            logbox.configure(state="normal")
            logFile.write(time.strftime("%H:%M:%S", time.localtime()))
            logFile.write("\t")
            if type(data) is dict:
                logFile.write(json.dumps(data))
                logbox.insert("end", json.dumps(data), logbox_colour_tag)
            elif type(data) is str:
                logFile.write(data)
                if "ERROR" in data:
                    logbox.insert("end", data, "ERROR")
                elif "WARNING" in data:
                    logbox.insert("end", data, "WARNING")
                else:
                    logbox.insert("end", data, logbox_colour_tag)
            elif type(data) is pd.DataFrame:
                # Because results are printed normally to resultsbox, this should now print results table to log but NOT console.
                logFile.write(data.to_string(index=False).replace("\n", "\n\t\t"))
                # logbox.insert('end', data.to_string(index = False))
                if "Energy (keV)" in data.columns:
                    # If df contains energy column (i.e. is from peak ID, not results), then print to logbox.
                    logbox.insert("end", data.to_string(index=False), "INFO")
                elif "Grade" in data.columns:  # grade library results (*alloys etc*)
                    logbox.insert("end", data.to_string(index=False), "INFO")
                else:  # Else, df is probably results, so don't print to logbox.
                    logbox.insert(
                        "end", "Assay Results written to log file.", logbox_colour_tag
                    )
            elif type(data) is list:
                listastext = ", ".join(str(e) for e in data)
                logFile.write(f"[{listastext}]")
                logbox.insert("end", (f"[{listastext}]"), logbox_colour_tag)
            else:
                try:
                    logFile.write(data)
                    logbox.insert("end", data, logbox_colour_tag)
                except:
                    logFile.write(
                        f"ERROR: Data type {type(data)} unable to be written to log."
                    )
                    logbox.insert(
                        "end",
                        (f"ERROR: Data type {type(data)} unable to be written to log."),
                        "ERROR",
                    )
            logFile.write("\n")
            logbox.insert("end", "\n")
            logbox.see("end")
            logbox.configure(state="disabled")
    else:
        print(f"(Logfile/Logbox uninitialised) Tried to print: {data}")


def sendCommand(s, command):
    msg = '<?xml version="1.0" encoding="utf-8"?>' + command
    msgData = (
        b"\x03\x02\x00\x00\x17\x80"
        + len(msg).to_bytes(4, "little")
        + msg.encode("utf-8")
        + b"\x06\x2A\xFF\xFF"
    )
    sent = s.sendall(msgData)
    if sent == 0:
        raise Exception("XRF Socket connection broken")


def recvChunks(s, expected_len):
    chunks = []
    recv_len = 0
    while recv_len < expected_len:
        chunk = s.recv(expected_len - recv_len)
        if chunk == b"":
            raise Exception("XRF Socket connection broken")
        chunks.append(chunk)
        recv_len = recv_len + len(chunk)
    return b"".join(chunks)


def recvData(s):
    header = recvChunks(s, 10)
    data_size = int.from_bytes(header[6:10], "little")
    data = recvChunks(s, data_size)
    footer = recvChunks(s, 4)

    if header[4:6] == b"\x17\x80":  # 5 - XML PACKET (Usually results?)
        datatype = XML_PACKET
        data = data.decode("utf-8")
        # print(data)
        data = xmltodict.parse(data)
        if (
            ("Response" in data)
            and ("@status" in data["Response"])
            and ("#text" in data["Response"])
        ):  # and ('ogged in ' in data['Response']['#text']):
            datatype = XML_SUCCESS_RESPONSE  # 5a - XML PACKET, 'success, assay start' 'success, Logged in' etc response
        elif (
            ("Response" in data)
            and ("@parameter" in data["Response"])
            and (data["Response"]["@parameter"] == "applications")
        ):
            datatype = XML_APPS_PRESENT_RESPONSE  # 5b - XML PACKET, Applications present response
        elif (
            ("Response" in data)
            and ("@parameter" in data["Response"])
            and (data["Response"]["@parameter"] == "activeapplication")
        ):
            datatype = XML_ACTIVE_APP_RESPONSE  # 5c - XML PACKET, Active Application and Methods present response

        return data, datatype

    # 1 - COOKED SPECTRUM
    elif header[4:6] == b"\x01\x80":
        datatype = COOKED_SPECTRUM
        return data, datatype
    # 2 - RESULTS SET (don't really know when this is used?)    // Deprecated?
    elif header[4:6] == b"\x02\x80":
        datatype = RESULTS_SET
        return data, datatype
    # 3 - RAW SPECTRUM  // Deprecated?
    elif header[4:6] == b"\x03\x80":
        datatype = RAW_SPECTRUM
        return data, datatype
    # 4 - PDZ FILENAME // Deprecated, no longer works :(
    elif header[4:6] == b"\x04\x80":
        datatype = PDZ_FILENAME
        return data, datatype
    # 6 - STATUS CHANGE     (i.e. trigger pulled/released, assay start/stop/complete, phase change, etc.)
    elif header[4:6] == b"\x18\x80":
        datatype = STATUS_CHANGE
        data = (
            data.decode("utf-8").replace("\n", "").replace("\r", "").replace("\t", "")
        )
        data = xmltodict.parse(data)
        return data, datatype
    # 7 - SPECTRUM ENERGY PACKET
    elif header[4:6] == b"\x0b\x80":
        datatype = SPECTRUM_ENERGY_PACKET
        return data, datatype
    # 0 - UNKNOWN DATA
    else:
        datatype = UNKNOWN_DATA
        printAndLog(f"****debug: unknown datatype. header = {header}, data = {data}")
        return data, datatype


def elementZtoSymbol(Z):
    """Returns 1-2 character Element symbol as a string"""
    if Z == 0:
        return ""
    elif Z <= 118:
        return elementstr_symbolsonly[Z - 1]
    else:
        return "Error: Z out of range"


def elementZtoSymbolZ(Z):
    """Returns 1-2 character Element symbol formatted WITH atomic number in brackets"""
    if Z <= 118:
        return elementstr_symbolswithzinbrackets[Z - 1]
    else:
        return "Error: Z out of range"


def elementZtoName(Z):
    """Returns Element name from element Z"""
    if Z <= 118:
        return elementstr_namesonly[Z - 1]
    else:
        return "Error: Z out of range"


def elementSymboltoName(sym: str):
    """returns element name from element symbol e.g. 'He' -> 'Helium'"""
    if len(sym) < 4:
        try:
            i = elementstr_symbolsonly.index(sym)
            return elementstr_namesonly[i]
        except:
            print("Element symbol unrecognised")
    else:
        return "Error: Symbol too long"


def instrument_GetInfo():
    sendCommand(xrf, bruker_query_instdef)
    sendCommand(xrf, bruker_query_allapplications)
    sendCommand(xrf, bruker_query_currentapplicationinclmethods)
    instrument_QuerySoftwareVersion()


def printInstrumentInfo():
    printAndLog(f"Model: {instr_model}")
    printAndLog(f"Serial Number: {instr_serialnumber}")
    printAndLog(f"Build Number: {instr_buildnumber}")
    printAndLog(f"Detector: {instr_detectormodel}")
    printAndLog(
        f"Detector Specs: {instr_detectortype} - {instr_detectorwindowthickness} {instr_detectorwindowtype} window, {instr_detectorresolution} resolution, operating temps {instr_detectormaxTemp} - {instr_detectorminTemp}"
    )
    printAndLog(f"Source: {instr_sourcemanufacturer} {instr_sourcemaxP}")
    printAndLog(f"Source Target: {instr_sourcetargetName}")
    printAndLog(f"Source Voltage Range: {instr_sourceminV} - {instr_sourcemaxV}")
    printAndLog(f"Source Current Range: {instr_sourceminI} - {instr_sourcemaxI}")


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def notifyAllAssaysComplete(number_completed: int):
    """Send a platform-suitable notification to the system/desktop to alert the user that all assays have completed. This is in case the user is not looking at the screen or does not have the S1Control window open."""
    if enableendofassaynotifications_var.get() == "on":
        try:
            # Set notification verbage to suit multiple assays
            n_title = "All Assays Complete!"
            n_message = f"All {number_completed} Assays have been completed. Instrument is now idle."
            n_ticker = "All Assays Complete!"

            if number_completed == 1:
                # Set notification verbage to suit single assay
                n_title = "Assay Complete!"
                n_message = "Assay has been completed. Instrument is now idle."
                n_ticker = "Assay Complete!"

            plyer_notification.notify(
                title=n_title,
                message=n_message,
                ticker=n_ticker,
                app_name="S1Control",
                app_icon=iconpath,
                timeout=10,
            )
        except:
            printAndLog(
                "Minor UI Error: Assays complete notification was unable to execute. This is likely due to plyer/windows jank."
            )


def initialiseLogFile():
    global logFile
    global logFileArchivePath
    global logFileName
    global logFilePath
    global driveFolderStr
    global instr_serialnumber
    global datetimeString
    # Set PC user and name for log file
    try:
        pc_user = os.getlogin()
        pc_device = os.environ["COMPUTERNAME"]
    except:
        pc_user = "Unkown User"
        pc_device = "Unknown Device"

    driveArchiveLoc = None
    driveFolderStr = ""
    logFileArchivePath = None

    # Check for GDrive Paths to save backup of Log file
    if os.path.exists(
        R"G:/.shortcut-targets-by-id/1w2nUsja1tidZ-QYTuemO6DzCaclAmIlm/PXRFS/13. Service/Automatic Instrument Logs"
    ):
        # use gdrive path if available
        driveArchiveLoc = R"G:/.shortcut-targets-by-id/1w2nUsja1tidZ-QYTuemO6DzCaclAmIlm/PXRFS/13. Service/Automatic Instrument Logs"

    if instr_serialnumber == "UNKNOWN":
        messagebox.showwarning(
            "SerialNumber Error",
            "Warning: The instrument's serial number was not retrieved in time to use it in the initialisation of the log file for this session. For this reason, the log file will likely display 'UNKNOWN' as the serial number in the filename.",
        )
        # print("serial number lookup failed. using 'UNKNOWN'")

    # Check for slightly renamed folder for this instrument in drive e.g. '800N8573 Ruffo' to use preferably
    foundAlternateFolderName = False
    if driveArchiveLoc != None:
        for subdir, dirs, files in os.walk(driveArchiveLoc):
            for dir in dirs:
                # print(os.path.join(subdir, dir))
                if instr_serialnumber in dir:
                    driveFolderStr = dir
                    foundAlternateFolderName = True
                    break

    # Use just serial num if no renamed folder exists
    if foundAlternateFolderName == False:
        driveFolderStr = instr_serialnumber

    # Make folder in drive archive if doesn't already exist
    if (driveArchiveLoc is not None) and not os.path.exists(
        driveArchiveLoc + rf"/{driveFolderStr}"
    ):
        os.makedirs(driveArchiveLoc + rf"/{instr_serialnumber}")

    # Standard log file location in dir of program
    if not os.path.exists(rf"{os.getcwd()}/Logs"):
        os.makedirs(rf"{os.getcwd()}/Logs")

        # Create Log file using time/date/XRFserial

    datetimeString = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    logFileName = f"S1Control_Log_{datetimeString}_{instr_serialnumber}.txt"
    logFilePath = rf"{os.getcwd()}/Logs/{logFileName}"
    if driveArchiveLoc is not None:
        logFileArchivePath = rf"{driveArchiveLoc}/{driveFolderStr}/{logFileName}"

    logFileStartTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    with open(logFilePath, "x", encoding="utf-16") as logFile:
        logFile.write(
            f"TIMESTAMP \tLog File Created: {logFileStartTime} by {pc_device}/{pc_user}, using S1Control {versionNum}.\n"
        )
        logFile.write(
            "--------------------------------------------------------------------------------------------------------------------------------------------\n"
        )

    #     # CLosing **** around idf, app, method info
    # with open(logFilePath, "a", encoding= 'utf-16') as logFile:
    #     logFile.write('--------------------------------------------------------------------------------------------------------------------------------------------\n')


def instrument_GetStates():
    instrument_QueryLoginState()
    instrument_QueryArmedState()
    gui.after(800, getOtherStates)


def getOtherStates():
    sendCommand(xrf, bruker_query_proximityrequired)
    sendCommand(xrf, bruker_query_storeresults)
    sendCommand(xrf, bruker_query_storespectra)


# XRF Listen Loop Functions


def xrfListenLoopThread_Start(event):
    global listen_thread
    listen_thread = threading.Thread(target=xrfListenLoop)
    listen_thread.daemon = True
    listen_thread.start()
    gui.after(20, xrfListenLoopThread_Check)


def xrfListenLoopThread_Check():
    global listen_thread
    if listen_thread.is_alive():
        gui.after(20, xrfListenLoopThread_Check)
    else:
        printAndLog("ERROR: XRF listen loop broke", "ERROR")
        raise SystemExit(0)


# TESTING OUT LISTEN LOOP PROCESS instead of thread
# def xrfListenLoopProcess_Start():
#     global listen_process
#     listen_process = Process(target=xrfListenLoop)
#     listen_process.start()


def xrfListenLoop():
    # I know this many globals is disgusting but it just devolved into this
    # and I haven't had time to fix it yet I'M SORRY FUTURE ZEB
    global instr_currentapplication
    global instr_currentmethod
    global instr_methodsforcurrentapplication
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
    global instr_currentphaselength_s
    global instr_assayrepeatsleft
    global instr_assayrepeatschosenforcurrentrun
    global instr_approxsingleassaytime
    global instr_applicationspresent
    global instr_filterspresent
    global instr_illuminations
    global instr_currentassayspectra
    global instr_currentassayspecenergies
    global instr_currentassaylegends
    global instr_currentassayresults
    global instr_DANGER_stringvar
    global instr_assayisrunning
    global instr_currentnosetemp
    global instr_currentnosepressure
    global s1vermanuallyrequested
    global assay_start_time
    global assay_end_time
    global assay_time_total_set_seconds
    global xraysonbar
    global assay_phase_spectrumpacketcounter
    global proximitysensor_var
    global storeresultsoninstrument_var
    global storespectraoninstrument_var

    while True:
        try:
            data, datatype = recvData(xrf)
        except:
            printAndLog("XRF CONNECTION LOST", "ERROR")
            onInstrDisconnect()

            # data = None
            # datatype = None
            # time.sleep(1)
            # instrument_Connect(instant_connect=True)

            # printAndLog(
            #     "XRF CONNECTION LOST, ATTEMPTING TO RE-ESTABLISH...",
            #     logbox_colour_tag="ERROR",
            # )
            # try:
            #     instrument_Connect()
            #     time.sleep(5)
            #     # if connection lost, try reconnecting and then waiting 1s before recv again
            #     data, datatype = recvData(xrf)
            #     printAndLog(
            #         "XRF CONNECTION RE-ESTABLISHED!",
            #         logbox_colour_tag="WARNING",
            #     )
            # except:
            #     printAndLog(
            #         "XRF CONNECTION COULD NOT BE RE-ESTABLISHED, SHUTTING DOWN.",
            #         logbox_colour_tag="ERROR",
            #     )
            #     onInstrDisconnect()

        if thread_halt:
            break

        # print(data)

        # 6 - STATUS CHANGE
        if datatype == STATUS_CHANGE:
            if "@parameter" in data["Status"]:  #   basic status change
                statusparam = data["Status"]["@parameter"]
                statustext = data["Status"]["#text"]

                printAndLog(f"Status Change: {statusparam} {statustext}")

                if statusparam == "Assay" and statustext == "Start":
                    instr_currentphase = 0
                    instr_currentphaselength_s = int(phasedurations[instr_currentphase])
                    assay_time_total_set_seconds = 0
                    for dur in phasedurations:
                        assay_time_total_set_seconds += int(dur)
                    assay_start_time = time.time()
                    instr_assayisrunning = True
                    assay_phase_spectrumpacketcounter = 0

                    # set variables for assay
                    instr_currentassayspectra = []
                    instr_currentassayspecenergies = []
                    instr_currentassaylegends = []
                    instr_currentassayresults = default_assay_results_df

                    xraysonbar.start()

                    if doAutoPlotSpectra_var.get():
                        clearCurrentSpectra()

                elif statusparam == "Assay" and statustext == "Complete":
                    assay_end_time = time.time()
                    instr_assayisrunning = False
                    xraysonbar.stop()
                    # print(spectra)
                    try:
                        instr_currentassayspectra.append(spectra[-1])
                        instr_currentassayspecenergies.append(specenergies[-1])
                        # legend = f"Phase {instr_currentphase+1}: {txt['sngHVADC']}kV, {round(float(txt['sngCurADC']),2)}\u03bcA"
                        legend = f"Phase {instr_currentphase+1}({instr_currentphaselength_s}s): {txt['sngHVADC']}kV, {round(float(txt['sngCurADC']),2)}\u03bcA {txt['fltDescription']}"
                        instr_currentassaylegends.append(legend)
                        # plotSpectrum(spectra[-1], specenergies[-1], plotphasecolours[instr_currentphase],legend)
                    except:
                        printAndLog(
                            "Issue with Spectra experienced after completion of Assay.",
                            "WARNING",
                        )

                    # REPORT TEMPS EACH ASSAY COMPLETE
                    assay_finaltemps = f"Detector {instr_currentdettemp}°C, Ambient {instr_currentambtemp}°C"
                    # if detector temp or ambient temp are out of range, change colour of message.
                    temp_msg_colour = "BASIC"  # set as default
                    try:
                        if (
                            float(instr_currentdettemp) > (-26)
                            or float(instr_currentdettemp) < (-28)
                            or float(instr_currentambtemp) > (55)
                        ):
                            temp_msg_colour = "WARNING"
                            printAndLog(
                                "WARNING: Instrument Temperatures appear to be outside of the normal range!",
                                "WARNING",
                            )
                        if (
                            float(instr_currentdettemp) > (-25)
                            or float(instr_currentdettemp) < (-29)
                            or float(instr_currentambtemp) > (60)
                        ):
                            temp_msg_colour = "ERROR"
                    except:  # likely no spectra packets sent
                        pass
                    printAndLog(f"Temps: {assay_finaltemps}", temp_msg_colour)
                    # printAndLog(f'Amb Temp F: {instr_currentambtemp_F}°F')
                    # instrument_QueryNoseTemp()

                    # add full assay with all phases to table and catalogue. this 'assay complete' response is usually recieved at very end of assay, when all other values are in place.
                    if instr_currentassayresults.equals(default_assay_results_df):
                        completeAssay(
                            instr_currentapplication,
                            instr_currentmethod,
                            assay_time_total_set_seconds,
                            default_assay_results_df,
                            instr_currentassayspectra,
                            instr_currentassayspecenergies,
                            instr_currentassaylegends,
                            assay_finaltemps,
                        )
                    else:
                        completeAssay(
                            instr_currentapplication,
                            instr_currentmethod,
                            assay_time_total_set_seconds,
                            instr_currentassayresults,
                            instr_currentassayspectra,
                            instr_currentassayspecenergies,
                            instr_currentassaylegends,
                            assay_finaltemps,
                        )

                    # reset variables for next assay
                    instr_currentassayspectra = []
                    instr_currentassayspecenergies = []
                    instr_currentassaylegends = []
                    instr_currentassayresults = default_assay_results_df

                    instr_assayrepeatsleft -= 1
                    if instr_assayrepeatsleft <= 0:
                        printAndLog("All Assays complete.")
                        notifyAllAssaysComplete(instr_assayrepeatschosenforcurrentrun)
                        assayprogressbar.set(1)
                        endOfAssaysReset()
                    elif instr_assayrepeatsleft > 0:
                        printAndLog(
                            f"Consecutive Assays remaining: {instr_assayrepeatsleft} more."
                        )
                        # if custom spectrum is selected, need to re-provide the parameters, as it is not an actual application on the instrument.
                        if applicationselected_stringvar.get() == "Custom Spectrum":
                            instrument_StartAssay(
                                customassay=True,
                                customassay_filter=customspectrum_filter_dropdown.get(),
                                customassay_voltage=int(
                                    customspectrum_voltage_entry.get()
                                ),
                                customassay_current=float(
                                    customspectrum_current_entry.get()
                                ),
                                customassay_duration=int(
                                    customspectrum_duration_entry.get()
                                ),
                            )
                        else:
                            instrument_StartAssay()
                    # instr_currentphase = 0

                elif statusparam == "Phase Change":
                    instr_assayisrunning = True
                    # print(f'spec packets this phase: {assay_phase_spectrumpacketcounter}')
                    assay_phase_spectrumpacketcounter = 0
                    instr_currentphaselength_s = int(phasedurations[instr_currentphase])
                    # try:
                    spectra[-1]["normalised_data"] = normaliseSpectrum(
                        spectra[-1]["data"], spectra[-1]["fTDur"]
                    )
                    instr_currentassayspectra.append(spectra[-1])
                    instr_currentassayspecenergies.append(specenergies[-1])
                    legend = f"Phase {instr_currentphase+1}({instr_currentphaselength_s}s): {txt['sngHVADC']}kV, {round(float(txt['sngCurADC']),2)}\u03bcA {txt['fltDescription']}"
                    # legend = f"Phase {instr_currentphase+1}: {txt['sngHVADC']}kV, {round(float(txt['sngCurADC']),2)}\u03bcA"
                    instr_currentassaylegends.append(legend)

                    # printAndLog(f'Temps: Detector {instr_currentdettemp}°C, Ambient {instr_currentambtemp}°F')

                    if doAutoPlotSpectra_var.get():
                        plotSpectrum(
                            spectra[-1],
                            specenergies[-1],
                            plotphasecolours[instr_currentphase],
                            legend,
                        )
                    # except: printAndLog('Issue with Spectra experienced after completion of Phase.')
                    instr_currentphase += 1
                    instr_currentphaselength_s = int(phasedurations[instr_currentphase])

                elif statusparam == "Armed" and statustext == "No":
                    instr_isarmed = False
                elif statusparam == "Armed" and statustext == "Yes":
                    instr_isarmed = True
                    instr_isloggedin = True

            elif (
                "Application Selection" in data["Status"]
            ):  # new application selected DOESN"T WORK? only plays if selected on instr screen?
                printAndLog("New Application Selected.")
                sendCommand(xrf, bruker_query_currentapplicationinclmethods)
                # gui.after(200,ui_UpdateCurrentAppAndPhases)
                # need to find way of queuing app checker

            # printAndLog(data)

        elif datatype == COOKED_SPECTRUM:  # COOKED SPECTRUM
            txt, spectra = setSpectrum(data)
            assay_phase_spectrumpacketcounter += 1
            # printAndLog(f'New cooked Spectrum Info: {txt}')
            # printAndLog(f"New cooked Spectrum")

            if doDisplayVitals_var.get():
                # if option box is checked for 'Display Count Rate and Dead Time %', and if so, update relevant display widget
                updateCurrentVitalsDisplay(spectra)

        elif datatype == PDZ_FILENAME:  # PDZ FILENAME // Deprecated, no longer works :(
            printAndLog(f"New PDZ: {data}")

        elif (
            datatype == RESULTS_SET
        ):  # RESULTS SET (don't really know when this is used?)
            # printAndLog(etree'.tostring(data, pretty_print=True))
            printAndLog(data)

        elif datatype == RAW_SPECTRUM:  # RAW SPECTRA
            # data = hashlib.md5(data).hexdigest()
            printAndLog("Raw spectrum!")
            txt, spectra = setSpectrum(data)
            # printAndLog(data)

        # 5 - XML PACKET
        elif datatype == XML_PACKET:
            if (
                ("Response" in data)
                and ("@parameter" in data["Response"])
                and (data["Response"]["@parameter"] == "instrument definition")
                and (data["Response"]["@status"] == "success")
            ):
                # All IDF data:
                idf: dict = data["Response"]["InstrumentDefinition"]
                # from pprint import pprint
                # pprint(idf)

                # Broken Down:
                instr_model = idf.get("Model", "N/A")
                instr_serialnumber = idf.get("SerialNumber", "N/A")
                instr_buildnumber = idf.get("BuildNumber", "N/A")
                instr_detectortype = instr_buildnumber[0:3]

                instr_detector = idf.get("Detector", "N/A")

                if instr_detector != "N/A":
                    instr_detectormodel = instr_detector.get("DetectorModel", "N/A")
                    if instr_detectortype[1] in "PMK":
                        # Older detectors with Beryllium windows. eg SPX, SMA, SK6, etc
                        instr_detectorwindowtype = "Beryllium"
                        instr_detectorwindowthickness = (
                            instr_detector.get("BerylliumWindowThicknessInuM", "?")
                            + "\u03bcM"
                        )
                    elif instr_detectortype[1] in "G":
                        instr_detectorwindowtype = "Graphene"
                        instr_detectorwindowthickness = (
                            instr_detector.get("GrapheneWindowThicknessInuM", "?")
                            + "\u03bcM"
                        )
                        # In case instrument def is wrong (eg. Martin has graphene det, but only beryllium thickness listed)
                    instr_detectorresolution = (
                        instr_detector.get("TypicalResolutionIneV", "?") + "eV"
                    )
                    instr_detectormaxTemp = (
                        instr_detector.get("OperatingTempMaxInC", "?") + "°C"
                    )
                    instr_detectorminTemp = (
                        instr_detector.get("OperatingTempMinInC", "?") + "°C"
                    )
                else:
                    instr_detectormodel = "N/A"
                    instr_detectorwindowtype = "N/A"
                    instr_detectorwindowthickness = "N/A"
                    instr_detectorresolution = "N/A"
                    instr_detectormaxTemp = "N/A"
                    instr_detectorminTemp = "N/A"

                instr_source: dict = idf.get("XrayTube", "N/A")
                # from pprint import pprint
                # pprint(instr_source)
                if instr_source != "N/A":
                    instr_sourceoplimits: dict = instr_source.get(
                        "OperatingLimits", "N/A"
                    )
                    instr_sourcemanufacturer = instr_source.get("Manufacturer", "N/A")
                    instr_sourcetargetZ = instr_source.get("TargetElementNumber", 0)
                    instr_sourcetargetSymbol = elementZtoSymbol(
                        int(instr_sourcetargetZ)
                    )
                    instr_sourcetargetName = elementZtoName(int(instr_sourcetargetZ))
                    if instr_sourceoplimits != "N/A":
                        instr_sourcemaxV = (
                            instr_sourceoplimits.get("MaxHighVoltage", "?") + "kV"
                        )
                        instr_sourceminV = (
                            instr_sourceoplimits.get("MinHighVoltage", "?") + "kV"
                        )
                        instr_sourcemaxI = (
                            instr_sourceoplimits.get("MaxAnodeCurrentInuA", "?")
                            + "\u03bcA"
                        )
                        instr_sourceminI = (
                            instr_sourceoplimits.get("MinAnodeCurrentInuA", "?")
                            + "\u03bcA"
                        )
                        instr_sourcemaxP = (
                            instr_sourceoplimits.get("MaxOutputPowerInmW", "?") + "mW"
                        )
                    else:
                        printAndLog(
                            "IDF: NO OP LIMITS FOUND: Instrument Definition File does not report any xTube Operating Limits. This is normal for some older instruments.",
                            "WARNING",
                        )
                        instr_sourcemaxV = "N/A"
                        instr_sourceminV = "N/A"
                        instr_sourcemaxI = "N/A"
                        instr_sourceminI = "N/A"
                        instr_sourcemaxP = "N/A"

                    # get illuminations
                    instr_rawilluminationdefs: list[dict] = instr_source.get(
                        "IlluminationDefinition", "N/A"
                    )
                    # only proceed with processing illuminations IF it hasn't been done already.
                    if instr_rawilluminationdefs != "N/A" and instr_illuminations == []:
                        for entry in instr_rawilluminationdefs:
                            # first, fix 'AnodeCurrent', which is a dict.
                            anodecurrent_dict: dict = entry.get(
                                "AnodeCurrent", {"#text": "0.0", "@default": "Yes"}
                            )
                            # an entry in this list is NOT NECESSARILY JUST ONE ILLUMINATION. IF TWO ILLUMINATIONS ARE IDENTICAL IN ALL, THEN THEY CAN BE ONE ENTRY IN THE IDF ILLUMINATIONDEFINITION WITH 2 ID FIELDS. IN THIS CASE, THEY WILL APPEAR IN THE DICT WITH A LIST OF NAMES UNDER THE 'ID' ENTRY!!!
                            # so, first check for  list type in ID entry, if no list then make a list of len 1, then can just iterate over list either way:
                            if isinstance(entry.get("ID"), list):
                                # if multiple 'ID' values in this entry, use list.
                                id_list = entry.get("ID")
                            else:
                                # if only 1 ID in entry, treat as a list anyway for ease of reusing code
                                id_list = [entry.get("ID")]
                            # then, iterate over list of id(s) and assign to Illumination dataclass.
                            for _id in id_list:
                                # create new Illumination dataclass object and add to list of illuminations
                                instr_illuminations.append(
                                    Illumination(
                                        name=str(_id),
                                        voltage=int(entry.get("HighVoltage", 0)),
                                        current=float(anodecurrent_dict.get("#text")),
                                        current_isdefault=(
                                            False
                                            if (
                                                anodecurrent_dict.get("#text").lower()
                                                == "no"
                                            )
                                            else True
                                        ),
                                        filterposition=str(
                                            entry.get("FilterPosition") or ""
                                        ),  # if no filter specified, then entry.get('FilterPosition') returns None, so the or statement is used.
                                        testsample=str(entry.get("TestSample", "")),
                                        countrange_min=int(
                                            entry.get("CountRangeMin", 0)
                                        ),
                                        countrange_max=int(
                                            entry.get("CountRangeMax", 0)
                                        ),
                                        actualcounts=int(entry.get("ActualCounts", 0)),
                                    )
                                )
                        # after all illuminations have been scanned, sort the list of illuminations.
                        instr_illuminations.sort(key=lambda x: x.name)
                        # print("illuminations SORTED")
                        # for illum in instr_illuminations:
                        #     print(
                        #         f"{illum.name}: {illum.voltage=}, {illum.current=}, {illum.current_isdefault=}, {illum.filterposition=}, {illum.testsample=}, {illum.countrange_min=}, {illum.countrange_max=}, {illum.actualcounts=}............"
                        #     )

                else:
                    instr_sourcemanufacturer = "N/A"
                    instr_sourcetargetZ = "N/A"
                    instr_sourcetargetSymbol = "N/A"
                    instr_sourcetargetName = "N/A"
                    instr_sourcemaxV = "N/A"
                    instr_sourceminV = "N/A"
                    instr_sourcemaxI = "N/A"
                    instr_sourceminI = "N/A"
                    instr_sourcemaxP = "N/A"

                try:
                    instr_sourcespotsize = idf["SpotSize"]["Size"] + "mm"
                except:
                    instr_sourcespotsize = "N/A"

                instr_sourcehaschangeablecollimator = idf.get(
                    "HasChangeableCollimator", "N/A"
                )

                instr_filterspresent = []
                for filterdesc_dict in idf["Filter"]["FilterPosition"]:
                    try:
                        instr_filterspresent.append(filterdesc_dict["#text"])
                    except:
                        instr_filterspresent.append("")

                try:
                    instr_firmwareSUPversion = idf["SUP"]["FirmwareVersion"]
                except:
                    instr_firmwareSUPversion = "N/A"
                try:
                    instr_firmwareUUPversion = idf["UUP"]["FirmwareVersion"]
                except:
                    instr_firmwareUUPversion = "N/A"
                try:
                    instr_firmwareXILINXversion = idf["DPP"]["XilinxFirmwareVersion"]
                except:
                    instr_firmwareXILINXversion = "N/A"
                try:
                    instr_firmwareOMAPkernelversion = idf["OMAP"]["KernelVersion"]
                except:
                    instr_firmwareOMAPkernelversion = "N/A"

                # a = globals()
                # for i in a:
                #     printAndLog(i, ':', a[i])

                # Print Important info to Console
                printAndLog(f"Model: {instr_model}")
                printAndLog(f"Serial Number: {instr_serialnumber}")
                printAndLog(f"Build Number: {instr_buildnumber}")
                try:
                    printAndLog(f"Software: S1 Version {instr_softwareS1version}")
                except:
                    pass  # This is in case the ver isn't retrieved or reported early enough. lazy, but oh well. It stops it failing or doublereporting
                printAndLog(
                    f"Firmware: SuP {instr_firmwareSUPversion}, UuP {instr_firmwareUUPversion}"
                )
                printAndLog(f"Detector: {instr_detectormodel}")
                printAndLog(
                    f"Detector Specs: {instr_detectortype} - {instr_detectorwindowthickness} {instr_detectorwindowtype} window, {instr_detectorresolution} resolution, operating temps {instr_detectormaxTemp} - {instr_detectorminTemp}"
                )
                printAndLog(f"Source: {instr_sourcemanufacturer} {instr_sourcemaxP}")
                printAndLog(f"Source Target: {instr_sourcetargetName}")
                printAndLog(
                    f"Source Spot Size: {instr_sourcespotsize} (Changeable: {instr_sourcehaschangeablecollimator})"
                )
                printAndLog(
                    f"Source Voltage Range: {instr_sourceminV} - {instr_sourcemaxV}"
                )
                printAndLog(
                    f"Source Current Range: {instr_sourceminI} - {instr_sourcemaxI}"
                )

            elif ("Data" in data) and (data["Data"]["Elements"] == None):
                printAndLog(
                    "WARNING: Calculation Error has occurred, no results provided by instrument. If this is unexpected, try Rebooting.",
                    "WARNING",
                )

            # Results packet?
            elif ("Data" in data) and ("ElementData" in data["Data"]["Elements"]):
                instr_currentassayresults_analysismode = data["Data"]["AnalysisMode"]
                # print(instr_currentassayresults_analysismode)
                elementdata = data["Data"]["Elements"]["ElementData"]
                # print(type(elementdata))
                if isinstance(elementdata, dict):
                    elementdata = [elementdata]
                    # in case of some calibrations that only report 1 element conc. input needs to be list!
                # convert units if necessary (default units used by instrument is %)
                if displayunits_var.get() == "ppm":
                    # ppm conversion, multiply by 10000000 to convert from wt%
                    instr_currentassayresults_chemistry = list(
                        map(
                            lambda x: {
                                "Z": int(x["AtomicNumber"]["#text"]),
                                "Compound": x["Compound"],
                                "Concentration": np.around(
                                    float(x["Concentration"]) * 10000, 0
                                ),
                                "Error(1SD)": np.around(float(x["Error"]) * 10000, 0),
                            },
                            elementdata,
                        )
                    )

                elif displayunits_var.get() == "ppb":
                    # ppb conversion, multiply by 10000000 to convert from wt%
                    instr_currentassayresults_chemistry = list(
                        map(
                            lambda x: {
                                "Z": int(x["AtomicNumber"]["#text"]),
                                "Compound": x["Compound"],
                                "Concentration": np.around(
                                    float(x["Concentration"]) * 10000000, 0
                                ),
                                "Error(1SD)": np.around(
                                    float(x["Error"]) * 10000000, 0
                                ),
                            },
                            elementdata,
                        )
                    )

                elif displayunits_var.get() == "%":
                    # units are in wt% by default on instr, BUT need to round to 4 decimal places for easy eyeballing ppm conv.
                    instr_currentassayresults_chemistry = list(
                        map(
                            lambda x: {
                                "Z": int(x["AtomicNumber"]["#text"]),
                                "Compound": x["Compound"],
                                "Concentration": np.around(
                                    float(x["Concentration"]), 4
                                ),
                                "Error(1SD)": np.around(float(x["Error"]), 4),
                            },
                            elementdata,
                        )
                    )

                instr_currentassayresults = pd.DataFrame.from_dict(
                    instr_currentassayresults_chemistry
                )

                if instr_currentassayresults_analysismode == "LIBRARY SEARCH":
                    try:
                        gradedata = data["Data"]["Grades"]["GradeData"]
                        if isinstance(gradedata, dict):
                            gradedata = [gradedata]
                        instr_currentassayresults_grades = list(
                            map(
                                lambda x: {
                                    "Grade": x["Grade"]["#text"],
                                    "Match Value": float(x["MatchValue"]),
                                },
                                gradedata,
                            )
                        )
                        instr_currentassayresults_grades_df = pd.DataFrame.from_dict(
                            instr_currentassayresults_grades
                        )
                        printAndLog(
                            f"Assay # {str(assay_catalogue_num).zfill(4)} Grade Matches:",
                            logbox_colour_tag="INFO",
                        )
                        printAndLog(instr_currentassayresults_grades_df)
                    except Exception:
                        printAndLog(
                            "Grade Result display error occurred.",
                            logbox_colour_tag="WARNING",
                        )

                # printAndLog(instr_currentassayresults)

            # Phase timings for current application
            elif (
                ("Response" in data)
                and ("@parameter" in data["Response"])
                and (data["Response"]["@parameter"] == "phase times")
                and (data["Response"]["@status"] == "success")
            ):
                instr_currentapplication = data["Response"]["Application"]
                phaselist = data["Response"]["PhaseList"]["Phase"]
                # printAndLog(f'phaselist len = {len(phaselist)}')
                phasenums = []
                phasenames = []
                phasedurations = []
                try:
                    for phase in phaselist:
                        phasenums.append(phase["@number"])
                        phasenames.append(phase["Name"])
                        phasedurations.append(phase["Duration"])
                except:
                    phasenums.append(phaselist["@number"])
                    phasenames.append(phaselist["Name"])
                    phasedurations.append(phaselist["Duration"])

                instr_currentphases = list(zip(phasenums, phasenames, phasedurations))
                instr_phasecount = len(instr_currentphases)

                instr_approxsingleassaytime = 0
                for dur in phasedurations:
                    instr_approxsingleassaytime += int(dur) + 5
                    # add 4 seconds per phase for general slowness and processing time on S1 titan, Tracer, CTX.

                # printAndLog(f'Current Phases: {instr_currentphases}')
                ui_UpdateCurrentAppAndPhases()

            # Response detailing the current 'Edit Fields' aka edit info fields aka notes.
            elif (
                ("Response" in data)
                and ("@parameter" in data["Response"])
                and "edit fields" in data["Response"]["@parameter"]
            ):
                try:
                    instr_editfielddata = data["Response"]["EditFieldList"]
                except KeyError:
                    instr_editfielddata = None
                printAndLog(f"Info-Fields Data Retrieved.")
                if instr_editfielddata == None:
                    printAndLog(
                        "NOTE: The Bruker OEM Protocol does not allow info-fields with blank values to be communicated over the protocol. If you cannot retrieve your info-fields properly, try filling the fields with some text on the instrument, then try retrieving it again.",
                        "INFO",
                    )
                else:
                    if type(instr_editfielddata["EditField"]) is list:
                        instr_editfielddata = instr_editfielddata["EditField"]
                    elif type(instr_editfielddata["EditField"]) is dict:
                        instr_editfielddata = [instr_editfielddata["EditField"]]
                    fillEditInfoFields(instr_editfielddata)

            # INFO/WARNING - e.g. Sent when active app is changed or user adjusts settings in spectrometer mode setup screen. It displays the hardware configuration required by the active instrument setup.
            elif "InfoReport" in data:
                # printAndLog(data)
                TxMsgID = data["InfoReport"]["@TxMsgID"]
                isuseracknowldegable = data["InfoReport"][
                    "@UserAckable"
                ]  # 'Yes' or 'No'
                infomsg = data["InfoReport"]["#text"]
                # e.g. "Nose Door Open. Close it to Continue."
                printAndLog(f"Instrument INFO/WARNING: {infomsg}")
                if isuseracknowldegable == "Yes":
                    instrument_AcknowledgeError(TxMsgID)
                    printAndLog(
                        "Info/Warning Acknowledgment Sent. Attempting to resume..."
                    )
                else:
                    printAndLog(
                        "ERROR: Info/Warning Message Cannot be Acknowledged Remotely. Please evaluate info/warning on instrument."
                    )
                if "Backscatter Limit Failure::Count Rate too Low" in infomsg:
                    printAndLog(
                        "'Count Rate Too Low' error occurred. Remaining repeat assays will be cancelled.",
                        "ERROR",
                    )
                    instr_assayrepeatsleft = 0

            # ERROR HAS OCCURRED
            elif "ErrorReport" in data:
                # Must respond to these. If an acknowledgement message is not received within 5 seconds ofthe initial transmission the message will be retransmitted. This process continues until an acknowledge is received or the message is transmitted 5 times.
                TxMsgID = data["ErrorReport"]["@TxMsgID"]
                isuseracknowldegable = data["ErrorReport"][
                    "@UserAckable"
                ]  # 'Yes' or 'No'
                ErrorMsg = data["ErrorReport"]["#text"]
                # e.g. "System temperature out of range."
                printAndLog(f"Instrument ERROR: {ErrorMsg}")
                if isuseracknowldegable == "Yes":
                    instrument_AcknowledgeError(TxMsgID)
                    printAndLog("Error Acknowledgment Sent. Attempting to resume...")
                else:
                    printAndLog(
                        "ERROR: Error Message Cannot be Acknowledged Remotely. Please evaluate error on instrument."
                    )

            else:
                printAndLog(f"WARNING: Uncategorised XML Packet Recieved: {data}")

        # 5a - RESPONSE XML PACKET, 'logged in' response etc, usually.
        elif datatype == XML_SUCCESS_RESPONSE:
            if ("@parameter" in data["Response"]) and (
                "login state" in data["Response"]["@parameter"]
            ):
                if data["Response"]["#text"] == "Yes":
                    instr_isloggedin = True
                elif data["Response"]["#text"] == "No":
                    instr_isloggedin = False
                    instr_isarmed = False

            elif ("@parameter" in data["Response"]) and (
                "armed state" in data["Response"]["@parameter"]
            ):
                if data["Response"]["#text"] == "Yes":
                    # print(data)
                    instr_isarmed = True
                elif data["Response"]["#text"] == "No":
                    instr_isarmed = False

            elif ("@parameter" in data["Response"]) and (
                "nose temperature" in data["Response"]["@parameter"]
            ):
                instr_currentnosetemp = data["Response"]["#text"]
                printAndLog(f"Nose Temperature: {instr_currentnosetemp}°C")

            elif ("@parameter" in data["Response"]) and (
                "nose pressure" in data["Response"]["@parameter"]
            ):
                instr_currentnosepressure = data["Response"]["#text"]
                printAndLog(f"Nose Pressure: {instr_currentnosepressure}mBar")

            # Response confirming app change
            elif ("#text" in data["Response"]) and (
                "Application successfully set to" in data["Response"]["#text"]
            ):
                try:
                    s = data["Response"]["#text"].split("::")[-1]
                    # gets app name from #text string like 'Configure:Application successfully set to::Geo'
                    printAndLog(f"Application Changed to '{s}'")
                except:
                    pass
                sendCommand(xrf, bruker_query_currentapplicationinclmethods)
                instrument_QueryCurrentApplicationPhaseTimes()
                # ui_UpdateCurrentAppAndPhases()

            # phase times set response
            elif (
                ("@parameter" in data["Response"])
                and ("phase times" in data["Response"]["@parameter"])
                and ("#text" in data["Response"])
            ):
                printAndLog(f"{data['Response']['#text']}")
                instrument_QueryCurrentApplicationPhaseTimes()

            # s1 version response
            elif ("@parameter" in data["Response"]) and (
                data["Response"]["@parameter"] == "version"
            ):
                try:
                    instr_softwareS1version = data["Response"]["#text"]
                except:
                    instr_softwareS1version = "UNKNOWN"
                if s1vermanuallyrequested == True:
                    printAndLog(f"Software: S1 Version {instr_softwareS1version}")

            # Secondary Response for Assay Start and Stop for some instruments??? Idk why, should NOT RELY ON
            elif ("#text" in data["Response"]) and (
                "Assay St" in data["Response"]["#text"]
            ):
                if data["Response"]["#text"] == "Assay Start":
                    printAndLog("Response: Assay Start")
                    instr_assayisrunning = True
                elif data["Response"]["#text"] == "Assay Stop":
                    printAndLog("Response: Assay Stop")
                    instr_assayisrunning = False

            # Response Success log in OR already logged in
            elif (
                ("#text" in data["Response"])
                and ("@status" in data["Response"])
                and ("ogged in as" in data["Response"]["#text"])
                and ("success" in data["Response"]["@status"])
            ):
                instr_isloggedin = True
                printAndLog(
                    f"{data['Response']['@status']}: {data['Response']['#text']}"
                )

            # Transmit results configuration change response ({'Response': {'@parameter': 'transmit spectra', '@status': 'success', '#text': 'Transmit Spectra configuration updated'}})
            elif (
                ("@parameter" in data["Response"])
                and ("@status" in data["Response"])
                and ("#text" in data["Response"])
                and ("transmit" in data["Response"]["@parameter"])
            ):
                printAndLog(
                    f"{data['Response']['@status']}: {data['Response']['#text']}"
                )

            # Respose to if query if result files are stored on instrument (csv, tsv, etc)
            elif (
                ("@parameter" in data["Response"])
                and ("@status" in data["Response"])
                and ("#text" in data["Response"])
                and ("store results" in data["Response"]["@parameter"])
            ):
                if data["Response"]["#text"] in ["Yes", "yes"]:
                    storeresultsoninstrument_var.set(True)
                elif data["Response"]["#text"] in ["No", "no"]:
                    storeresultsoninstrument_var.set(False)
                else:
                    printAndLog(
                        f"{data['Response']['@status']}: {data['Response']['#text']}"
                    )

            # Respose to if query if spectra files are stored on instrument (pdz)
            elif (
                ("@parameter" in data["Response"])
                and ("@status" in data["Response"])
                and ("#text" in data["Response"])
                and ("store spectra" in data["Response"]["@parameter"])
            ):
                if data["Response"]["#text"] in ["Yes", "yes"]:
                    storespectraoninstrument_var.set(True)
                elif data["Response"]["#text"] in ["No", "no"]:
                    storespectraoninstrument_var.set(False)
                else:
                    printAndLog(
                        f"{data['Response']['@status']}: {data['Response']['#text']}"
                    )

            # Response to proximity sensor query
            elif (
                ("@parameter" in data["Response"])
                and ("@status" in data["Response"])
                and ("#text" in data["Response"])
                and ("proximity required" in data["Response"]["@parameter"])
            ):
                if data["Response"]["#text"] in ["Yes", "yes"]:
                    proximitysensor_var.set(True)
                elif data["Response"]["#text"] in ["No", "no"]:
                    proximitysensor_var.set(False)
                else:
                    printAndLog(
                        f"{data['Response']['@status']}: {data['Response']['#text']}"
                    )

            # Catchall for OTHER unimportant responses confirming configure changes (like time and date set, etc)
            elif ("#text" in data["Response"]) and (
                "Configure:" in data["Response"]["#text"]
            ):
                printAndLog(
                    f"{data['Response']['@status']}: {data['Response']['@parameter']}: {data['Response']['#text']}"
                )

            else:
                # try: printAndLog(f"{data['Response']['@parameter']}: {data['Response']['#text']}")
                # except: pass
                # try: printAndLog(f"{data['Response']['@status']}: {data['Response']['#text']}")
                # except:
                #     printAndLog(data)
                printAndLog(data)

        # 5b - XML PACKET, Applications present response
        elif datatype == XML_APPS_PRESENT_RESPONSE:
            try:
                instr_applicationspresent = data["Response"]["ApplicationList"][
                    "Application"
                ]
                if isinstance(instr_applicationspresent, str):
                    instr_applicationspresent = [instr_applicationspresent]
                printAndLog(f"Applications Available: {instr_applicationspresent}")
            except:
                printAndLog(
                    f"Applications Available: Error: Not Found - Was the instrument busy when it was connected?"
                )

        # 5c - XML PACKET, Active Application and Methods present response
        elif datatype == XML_ACTIVE_APP_RESPONSE:
            try:
                instr_currentapplication = data["Response"]["Application"]
                printAndLog(f"Current Application: {instr_currentapplication}")
            except:
                printAndLog(f"Current Application: Not Found / Spectrometer Mode")
            try:
                instr_methodsforcurrentapplication = data["Response"]["MethodList"][
                    "Method"
                ]
                if isinstance(instr_methodsforcurrentapplication, str):
                    instr_methodsforcurrentapplication = [
                        instr_methodsforcurrentapplication
                    ]
                printAndLog(f"Methods Available: {instr_methodsforcurrentapplication}")
            except:
                instr_methodsforcurrentapplication = [""]
                printAndLog(f"Methods Available: Not Found / Spectrometer Mode")
            try:
                instr_currentmethod = data["Response"]["ActiveMethod"]
                printAndLog(f"Current Method: {instr_currentmethod}")
            except:
                instr_currentmethod = ""
                printAndLog(f"Current Method: Not Found / Spectrometer Mode")
            try:
                methodselected_stringvar.set(instr_currentmethod)
                dropdown_method.configure(values=instr_methodsforcurrentapplication)
            except:
                print("error updating method dropdown")

        # 7 - SPECTRUM ENERGY PACKET, contains the SpecEnergy structure, cal info (The instrument will transmit a SPECTRUM_ENERGY packet inmmediately before transmitting it’s associated COOKED_SPECTRUM packet. The SpecEnergy iPacketCount member contains an integer that associates the SpecEnergy values with the corresponding COOKED_SPECTRUM packet via the iPacket_Cnt member of the s1_cooked_header structure.)
        elif datatype == SPECTRUM_ENERGY_PACKET:
            specenergies = setSpecEnergy(data)
            pass

        else:
            if data != None and datatype != None:
                printAndLog(data)

        # statusUpdateCheck()
        time.sleep(0.1)


def setSpectrum(data):
    global spectra
    global instr_currentambtemp
    global instr_currentambtemp_F
    global instr_currentdettemp
    a = {}
    (
        a["fEVPerChannel"],
        a["iTDur"],
        a["iRaw_Cnts"],
        a["iValid_Cnts"],
        a["iADur"],
        a["iADead"],
        a["iAReset"],
        a["iALive"],
        a["iPacket_Cnt"],
        a["Det_Temp"],
        a["Amb_Temp"],
        a["iRaw_Cnts_Acc"],
        a["iValid_Cnts_Acc"],
        a["fTDur"],
        a["fADur"],
        a["fADead"],
        a["fAReset"],
        a["fALive"],
        a["lPacket_Cnt"],
        a["iFilterNum"],
        a["fltElement1"],
        a["fltThickness1"],
        a["fltElement2"],
        a["fltThickness2"],
        a["fltElement3"],
        a["fltThickness3"],
        a["sngHVADC"],
        a["sngCurADC"],
        a["Toggle"],
    ) = struct.unpack(
        "<f4xLLL4xLLLL6xH78xhHxxLL8xfffff4xLihhhhhhffxxbxxxxx", data[0:208]
    )
    # originally, struct.unpack('<f4xLLL4xLLLLLHH78xhH2xLLLLfffffLLihhhhhhff2xbbbbbb', data[0:208])
    txt = a
    a["data"] = list(map(lambda x: x[0], struct.iter_unpack("<L", data[208:])))

    # GET CURRENT TEMPS  - I think this is not working properly, or needs some offsets or something to be taken into account?
    # Operating under the assumption that the det temp is actually double what it should be (often reading -54 degrees) and ambient temp value is actually 1/10 of a degree F, (e.g. reading 1081 instead of 108.1)
    instr_currentambtemp = float(a["Amb_Temp"])
    instr_currentambtemp_F = instr_currentambtemp
    instr_currentambtemp = round((((instr_currentambtemp / 10) - 32) * (5 / 9)), 2)
    # shifts decimal place one left (see above comment) and converts to C from F, then rounds to 2 dp.
    instr_currentdettemp = float(a["Det_Temp"])
    instr_currentdettemp = round((instr_currentdettemp / 2), 2)
    # halves and rounds (halves because see above comment)
    # printAndLog(f'Temps: Detector {instr_currentdettemp}°C, Ambient {instr_currentambtemp}°F')

    e1 = elementZtoSymbol(int(txt["fltElement1"]))
    e2 = elementZtoSymbol(int(txt["fltElement2"]))
    e3 = elementZtoSymbol(int(txt["fltElement3"]))

    if txt["fltThickness1"] == 0:
        t1 = ""
    else:
        t1 = f":{txt['fltThickness1']}\u03bcm"

    if txt["fltThickness2"] == 0:
        t2 = ""
    else:
        t2 = f":{txt['fltThickness2']}\u03bcm"
        t1 = f"{t1}/"

    if txt["fltThickness3"] == 0:
        t3 = ""
    else:
        t3 = f":{txt['fltThickness3']}\u03bcm"
        t2 = f"{t2}/"

    txt["fltDescription"] = f"({e1}{t1}{e2}{t2}{e3}{t3})"
    if txt["fltDescription"] == "()":
        txt["fltDescription"] = "(No Filter)"

    idx = len(spectra) - 1
    if idx < 0 or a["lPacket_Cnt"] == 1:
        spectra.append(a)
    else:
        spectra[idx] = a
    # plotSpectra(spectra[-1]['data'])
    return txt, spectra


def setSpecEnergy(data):
    global specenergies
    b = {}
    (b["iPacketCount"], b["fEVChanStart"], b["fEVPerChannel"]) = struct.unpack(
        "<iff", data
    )
    idx = len(specenergies) - 1
    if idx < 0:
        specenergies.append(b)
    else:
        specenergies[idx] = b

    return specenergies


def normaliseSpectrum(spectrum_counts, time_in_milliseconds):
    """Normalises 1 Spectrum by time and area(total counts). spectrum_counts should be list of counts (usually spectrum['data']) and spectrum time in ms (usually spectrum['fTDur']). Returns a normalised counts list that should probably be stored in spectrum['normalised_data']"""

    time_in_seconds = time_in_milliseconds / 1000

    # normalise first by time, by dividing all bins by number of seconds spectrum was taken over
    counts_per_second_spectrum = [
        Decimal(b) / Decimal(time_in_seconds) for b in spectrum_counts
    ]

    # then normalise by area, by dividing all bins by the sum of all bins
    area_normalised_spectrum = [
        Decimal(b) / Decimal(sum(counts_per_second_spectrum))
        for b in counts_per_second_spectrum
    ]

    # Return as floats (not decimals) and multiply by 100 to get effective percentage (sum of all counts roughly equals 100)
    float_area_normalised_spectrum = [float(b) * 100 for b in area_normalised_spectrum]

    return float_area_normalised_spectrum


def updateCurrentVitalsDisplay(spectra=None, override=None):
    """given a spectra list dump from phase in progress (usually 1/second is sent), update the relevant display widget with the latest values"""
    if not override:
        # testing live counts per second readout
        instantaneous_iRaw_Cnts = int(spectra[-1]["iRaw_Cnts"])
        instantaneous_iValid_Cnts = int(spectra[-1]["iValid_Cnts"])
        instantaneous_iADur = int(spectra[-1]["iADur"])
        # instantaneous_iTDur = int(spectra[-1]["iTDur"])
        # instantaneous_iALive = int(spectra[-1]["iALive"])
        # instantaneous_iAReset = int(spectra[-1]["iAReset"])
        instantaneous_sngHVADC = round(float(spectra[-1]["sngHVADC"]))
        instantaneous_sngCurADC = round(float(spectra[-1]["sngCurADC"]), 2)

        # as per BIT decomp:
        # input counts per second seems to be (iRaw_Cnts / iADur) * 1000
        # output counts per second seems to be (iValid_Cnts / iADur) * 1000
        # dead % seems to be ((iRaw_Cnts - iValid_Cnts) / iRaw_Cnts) * 100

        # print values each time this func is called. only temporary!
        # printAndLog(f"Counts/Sec: {int((instantaneous_iRaw_Cnts / instantaneous_iADur) * 1000)}, Deadtime:{(((instantaneous_iRaw_Cnts - instantaneous_iValid_Cnts) / instantaneous_iRaw_Cnts) * 100):6.2f}%")
        # printAndLog(f'{txt["sngHVADC"]}kV, {round(float(txt["sngCurADC"]),2)}\u03bcA')
        # try-excepts in case of assay failure, can't divide by zero
        try:
            instr_countrate_stringvar.set(
                f"{int((instantaneous_iRaw_Cnts / instantaneous_iADur) * 1000)}cps"
            )
        except:
            instr_countrate_stringvar.set("0cps")
        try:
            instr_deadtime_stringvar.set(
                f"{(((instantaneous_iRaw_Cnts - instantaneous_iValid_Cnts) / instantaneous_iRaw_Cnts) * 100):6.2f}%dead"
            )
        except:
            instr_deadtime_stringvar.set("0%dead")

        instr_tubevoltagecurrent_stringvar.set(
            f"{instantaneous_sngHVADC}kV / {instantaneous_sngCurADC}\u03bcA"
        )
    else:
        instr_countrate_stringvar.set("0cps")
        instr_deadtime_stringvar.set("0%dead")
        instr_tubevoltagecurrent_stringvar.set(f"0kV / 0\u03bcA")
        # update current values if tube is off to 0/0


def completeAssay(
    assay_application: str,
    assay_method: str,
    assay_time_total_set: int,
    assay_results: pd.DataFrame,
    assay_spectra: list,
    assay_specenergies: list,
    assay_legends: list,
    assay_finaltemps: str,
):
    global assay_catalogue
    global assay_catalogue_num
    global assay_start_time
    global assay_end_time

    t = time.localtime()
    assay_sane = "N/A"

    if doNormaliseSpectra_var.get():
        for i in range(len(assay_spectra)):
            if "normalised_data" in assay_spectra[i]:
                # Only calculate normalised spectra if it hasn't been done already
                pass
            else:
                assay_spectra[i]["normalised_data"] = normaliseSpectrum(
                    assay_spectra[i]["data"], assay_spectra[i]["fTDur"]
                )

    # perform assay sanity checks
    any_phases_failed_sanity_check = False
    if doSanityCheckSpectra_var.get():
        for i in range(len(assay_spectra)):
            _counts = assay_spectra[i]["data"]
            _sourcevoltage = assay_spectra[i]["sngHVADC"]
            _evchannelstart = assay_specenergies[i][
                "fEVChanStart"
            ]  # starting ev of spectrum channel 1
            _evperchannel = assay_specenergies[i]["fEVPerChannel"]
            # Use ev per channel etc for bins instead of basic 20
            _energies = spec_channels * _evperchannel
            _energies = _energies + _evchannelstart
            _energies = _energies / 1000  # TO GET keV instead of eV
            if (
                sanityCheckSpectrum_SumMethod(
                    spectrum_counts=_counts,
                    spectrum_energies=_energies,
                    source_voltage_in_kV=_sourcevoltage,
                )
                == False
            ):
                any_phases_failed_sanity_check = True
                printAndLog(
                    f"SPECTRA SANITY CHECK FAILED: Assay # {assay_catalogue_num}, Phase {i+1}. Check Spectrum for Possible Incorrect Voltage! Note: This function has no way of checking for sum peaks or low-fluorescence samples, so false positives may occur.",
                    "WARNING",
                )
                break
        if any_phases_failed_sanity_check:
            assay_sane = "FAIL"
        else:
            assay_sane = "PASS"

    # get notes / info fields data for notes column of assay table
    assay_notes_list = []
    assay_note = ""
    if not editinfo_firsttime:
        for infofieldval in editinfo_fieldvalues:
            if infofieldval.get() != "":
                assay_notes_list.append(infofieldval.get())
        if assay_notes_list != []:
            if len(assay_notes_list) == 1:
                assay_note = assay_notes_list[0]
            else:
                assay_note = ",".join(assay_notes_list)

    # after getting notes, safe to increment counter fields
    incrementInfoFieldCounterValues()

    newassay = Assay(
        index=str(assay_catalogue_num).zfill(4),
        date_completed=time.strftime("%Y/%m/%d", t),
        time_completed=time.strftime("%H:%M:%S", t),
        time_elapsed=f"{round((assay_end_time - assay_start_time),2)}s",
        time_total_set=assay_time_total_set,
        cal_application=assay_application,
        cal_method=assay_method,
        results=assay_results,
        spectra=assay_spectra,
        specenergies=assay_specenergies,
        legends=assay_legends,
        temps=assay_finaltemps,
        note=assay_note,
        sanity_check_passed=assay_sane,
    )

    # increment catalogue index number for next assay
    assay_catalogue_num += 1

    # make new 'assay' var with results, spectra, time etc
    # assay = [assay_catalogue_num, assay_time, assay_application, assay_results, assay_spectra, assay_specenergies]

    # add assay with all relevant info to catalogue for later recall
    assay_catalogue.append(newassay)

    # add entry to assays table
    assaysTable.insert(
        parent="",
        index="end",
        iid=newassay.index,
        values=[
            newassay.index,
            newassay.cal_application,
            newassay.time_completed,
            newassay.time_elapsed,
            newassay.sanity_check_passed,
            newassay.note,
        ],
    )

    # plot, display, and print to log (v0.6.7 changed to use selection_set instead of manually plotting and displaying results.)
    if doAutoPlotSpectra_var.get():
        assaysTable.selection_set(assaysTable.get_children()[-1])

    assaysTable.yview_moveto(1)
    # plotAssay(newassay)
    # displayResults(newassay)

    printAndLog(assay_results)
    printAndLog(
        f"Assay # {newassay.index} processed sucessfully ({newassay.time_elapsed})"
    )

    if enableautoassayCSV_var.get() == "on":
        saveAssayToCSV(newassay)
    if enableresultsCSV_var.get() == "on":
        addAssayToResultsCSV(newassay)


def onInstrDisconnect():
    messagebox.showwarning(
        "Instrument Disconnected",
        "Error: Connection to the XRF instrument has been lost. The software will be closed, and a log file will be saved.",
    )
    printAndLog(
        "Connection to the XRF instrument was unexpectedly lost. Software will shut down and log will be saved.",
        "ERROR",
    )
    onClosing()


# Functions for Widgets


def statusUpdateCheckerLoop_Start(event):
    global status_thread
    status_thread = threading.Thread(target=statusUpdateChecker)
    status_thread.daemon = True
    status_thread.start()
    gui.after(30, statusUpdateCheckerLoop_Check)


def statusUpdateCheckerLoop_Check():
    if status_thread.is_alive():
        gui.after(100, statusUpdateCheckerLoop_Check)
    else:
        printAndLog("ERROR: Status Checker loop broke", "ERROR")


def statusUpdateChecker():
    global instr_assayisrunning
    global instr_isarmed
    global instr_isloggedin
    global instr_DANGER_stringvar
    global status_label
    global xraysonbar
    global assayprogressbar
    global button_assay

    while True:
        if thread_halt:
            break

        if instr_isloggedin == False:
            instr_DANGER_stringvar.set("Not Logged In!")
            status_label.configure(text_color=WHITEISH, fg_color=("#939BA2", "#454D50"))
            # Def background colour: '#3A3A3A'
            statusframe.configure(fg_color=("#939BA2", "#454D50"))
            xraysonbar.configure(progress_color=("#939BA2", "#454D50"))
            if button_assay.cget("state") == "normal":
                button_assay.configure(state="disabled")

            updateCurrentVitalsDisplay(override=True)

        elif instr_isarmed == False:
            instr_DANGER_stringvar.set("Not Armed!")
            status_label.configure(text_color=WHITEISH, fg_color=("#939BA2", "#454D50"))
            statusframe.configure(fg_color=("#939BA2", "#454D50"))
            xraysonbar.configure(progress_color=("#939BA2", "#454D50"))
            if button_assay.cget("state") == "normal":
                button_assay.configure(state="disabled")

            updateCurrentVitalsDisplay(override=True)

        elif instr_assayisrunning == True:
            instr_DANGER_stringvar.set("WARNING: X-RAYS")
            status_label.configure(text_color=WHITEISH, fg_color="#D42525")
            # X-RAY WARNING YELLOW = '#FFCC00', NICE RED = '#D42525'
            statusframe.configure(fg_color="#D42525")
            xraysonbar.configure(progress_color="#D42525")
            if button_assay.cget("state") == "disabled":
                button_assay.configure(state="normal")

            # Calculating progress of total assays incl repeats, for progressbar
            num_phases_in_each_assay = len(instr_currentphases)
            progress_phases_done = (
                (
                    num_phases_in_each_assay
                    * (instr_assayrepeatsselected - instr_assayrepeatsleft)
                )
                + instr_currentphase
                + (assay_phase_spectrumpacketcounter / (instr_currentphaselength_s + 2))
            )
            progress_phases_amounttotal = (
                num_phases_in_each_assay * instr_assayrepeatsselected
            )

            # Convert to float of range 0 -> 1
            current_assay_progress = progress_phases_done / progress_phases_amounttotal

            # Sanity check to stop overflowing progress bar when laggy or otherwise weird
            if current_assay_progress > 1:
                current_assay_progress = 1

            assayprogressbar.set(current_assay_progress)

        else:
            instr_DANGER_stringvar.set("Ready")
            status_label.configure(text_color=WHITEISH, fg_color=("#3A3A3A", "#454D50"))
            statusframe.configure(
                fg_color=("#3A3A3A", "#454D50")
            )  # default ctk blue '#3B8ED0' - complim green '#33AF56'
            xraysonbar.configure(progress_color=("#939BA2", "#454D50"))
            if button_assay.cget("state") == "disabled":
                button_assay.configure(state="normal")
            updateCurrentVitalsDisplay(override=True)

        # print(f'assay is running: {instr_assayisrunning}')
        # print(f'instr is armed: {instr_isarmed}')
        # print(f'instr is logged in: {instr_isloggedin}')
        # print(f'assay is running: {instr_assayisrunning}')
        time.sleep(0.2)


def getAssayPlurality(startorstop: str):
    """returns either 'Start Assay', 'Start Assays', 'Stop Assay', or 'Stop Assays', depending on the number of consecutive tests selected."""

    if startorstop.lower() == "start":
        if instr_assayrepeatsselected > 1:
            return "Start Assays"
        else:
            return "Start Assay"
    elif startorstop.lower() == "stop":
        if instr_assayrepeatsselected > 1:
            return "Stop Assays"
        else:
            return "Stop Assay"
    else:
        return "Assay(s)"


def assaySelected(event):
    global colouridx
    current_assaytable_selection = assaysTable.selection()
    # print(len(current_assaytable_selection))
    # print(current_assaytable_selection)
    currently_selected_assays_items = [
        assaysTable.item(selected_item)
        for selected_item in current_assaytable_selection
    ]
    # print(f'sel values = {selection["values"]}')
    try:
        selected_assay_catalogue_nums = [
            assay_item["values"][0] for assay_item in currently_selected_assays_items
        ]
    except IndexError:
        # Treeview is buggy, and doesn't like when an assay is started when another assay is selected. - when this happens, selection['values'] will be '' instead of a dict
        return
    # print(f'selected_assay_catalogue_num={selected_assay_catalogue_num}')
    # selected_assay_application = selection['values'][2]
    assays_to_plot = [
        assay_catalogue[int(assay_num) - 1]
        for assay_num in selected_assay_catalogue_nums
    ]

    # clear current spectra before plotting
    clearCurrentEmissionLines()
    clearCurrentSpectra()
    if len(current_assaytable_selection) == 1:
        plotAssay(assays_to_plot[0])
        displayResults(assays_to_plot[0])
    elif len(current_assaytable_selection) > 1:
        for assay in assays_to_plot:
            plotAssay(assay, clean_plot=False)
            displayResults(assay)
    plotEmissionLines()


def plotSpectrum(spectrum, specenergy, colour, spectrum_legend):
    global spectratoolbar
    global spectra_ax
    global fig
    global plottedspectra

    if doNormaliseSpectra_var.get():
        try:
            counts = spectrum["normalised_data"]
            spectra_ax.set_ylabel("Normalised Counts (%)")
        except:
            print("Normalised data not found, using raw data instead")
            counts = spectrum["data"]
            spectra_ax.set_ylabel("Counts (Total)")
    else:
        counts = spectrum["data"]
        spectra_ax.set_ylabel("Counts (Total)")

    ev_channel_start = specenergy["fEVChanStart"]  # starting ev of spectrum channel 1
    ev_per_channel = specenergy["fEVPerChannel"]

    # Use ev per channel etc for bins instead of basic
    bins = spec_channels * ev_per_channel
    bins = bins + ev_channel_start
    bins = bins / 1000  # TO GET keV instead of eV

    plottedspectrum = spectra_ax.plot(
        bins, counts, color=colour, linewidth=1, label=spectrum_legend
    )
    leg = spectra_ax.legend()
    for line, text in zip(leg.get_lines(), leg.get_texts()):
        text.set_color(plottextColour)

    plottedspectra.append(plottedspectrum)
    # adds spectrum to list of currently plotted spectra, for ease of removal later

    spectratoolbar.update()
    spectra_ax.autoscale(enable=True, axis="y", tight=False)  ####
    spectra_ax.relim(True)
    spectra_ax.autoscale_view(tight=True)
    spectracanvas.draw_idle()


def clearCurrentSpectra():
    global spectra_ax
    global plottedspectra
    global colouridx
    colouridx = 0
    # spectra_ax.cla()   #clears all plots from ax
    for plottedspectrum in plottedspectra:
        # plotref = plottedspectrum.pop(0)    # removes from list
        spectra_ax.lines[0].remove()
    try:
        spectra_ax.get_legend().remove()
    except:
        pass
    # WAS THIS IN MATPLOTLIB 3.6.3
    # for plottedspectrum in plottedspectra:
    #     plotref = plottedspectrum.pop(0)    # removes from list
    #     spectra_ax.lines.remove(plotref)
    # try: spectra_ax.get_legend().remove()
    # except: pass
    plottedspectra = []  # clears this list which is now probably full of empty refs?
    spectratoolbar.update()
    spectracanvas.draw_idle()


def plotEmissionLines():
    global spectratoolbar
    global spectra_ax
    global fig
    global plottedemissionlineslist
    global emission_lines_to_plot

    # clearCurrentEmissionLines()

    # energies = [6.40, 7.06]

    # linemax = (max((spectra_ax.get_ylim()[1]+2000),10_000))    #max height of emission lines will be at max of data +2000, OR 10000, whichever is higher

    for linedata in emission_lines_to_plot:
        linelabel = linedata[1]
        energy = linedata[2]
        linecol = "black"
        linedash = (None, None)
        if linedata[1][-2] == "L":
            linecol = "grey"
        if linedata[1][-1] == "β":
            linedash = (4, 2, 4, 2)
        plottedemissionline = spectra_ax.axvline(
            x=energy,
            ymin=0,
            ymax=1,
            color=linecol,
            dashes=linedash,
            linewidth=0.5,
            label=linelabel,
        )
        plottedemissionlineslist.append(plottedemissionline)
        # extraticks.append(energy)
        # extraticklabels.append(linelabel)
    # spectra_ax.set_xticks(ticks = list(spectra_ax.get_xticks()).extend(extraticks), labels = (spectra_ax.get_xticklabels()).extend(extraticklabels))

    # labelLines(plottedemissionlineslist, align=True, yoffsets=1)

    leg = spectra_ax.legend()
    for line, text in zip(leg.get_lines(), leg.get_texts()):
        text.set_color(plottextColour)
    spectratoolbar.update()
    spectracanvas.draw_idle()


def clearCurrentEmissionLines():
    global spectra_ax
    global plottedemissionlineslist
    global emissionLinesElementslist
    # print(f"REMOVING: {spectra_ax.lines}")
    # for plottedemissionline in plottedemissionlineslist:
    #     plottedemissionline.remove()

    # Get all lines in the plot
    lines_to_remove = [
        line
        for line in spectra_ax.lines
        if isinstance(line, plt.Line2D) and hasattr(line, "_x") and len(line._x) == 2
    ]

    # Remove axvlines
    for line in lines_to_remove:
        line.remove()

    plottedemissionlineslist = []
    emissionLinesElementslist = []

    leg = spectra_ax.legend()
    for line, text in zip(leg.get_lines(), leg.get_texts()):
        text.set_color(plottextColour)
    spectratoolbar.update()
    spectracanvas.draw_idle()


def onPlotCanvasMotion(event):
    x, y = event.xdata, event.ydata
    if x is not None and y is not None:
        plot_coords_strvar.set(f"{x:.4f} keV / {y:.0f} Counts")
    else:
        plot_coords_strvar.set("")


def plotAssay(assay: Assay, clean_plot: bool = True):
    global colouridx
    clearCurrentEmissionLines()
    if clean_plot:
        clearCurrentSpectra()
        colouridx = 0

    for (
        s,
        e,
        l,
    ) in zip(assay.spectra, assay.specenergies, assay.legends):
        plotSpectrum(s, e, plotphasecolours[colouridx], f"{assay.index}. {l}")
        colouridx += 1
        # print(f'colouridx={colouridx}')

    # plotEmissionLines()


def onPlotClick(event):  # gets coordinates for click on plot
    global ix, iy
    global cid
    global button_analysepeak
    ix, iy = event.xdata, event.ydata
    # print(f"plot click: x={ix}, y={iy}")
    button_analysepeak.configure(
        text="Identify Peak ",
        fg_color=("#3B8ED0", "#1F6AA5"),
        hover_color=("#36719F", "#144870"),
    )
    getNearbyEnergies(ix, 10)

    fig.canvas.mpl_disconnect(cid)  # Disconnects the listener


def startPlotClickListener():  # Starts the listener for click on plot so it isn't active at all times.
    global cid
    global button_analysepeak
    button_analysepeak.configure(
        text="Click a Peak to Analyse... ", fg_color="#D85820", hover_color="#973d16"
    )
    cid = fig.canvas.mpl_connect("button_press_event", onPlotClick)


def getNearbyEnergies(energy, qty):
    global energies_df
    global energiesfirsttime
    if energiesfirsttime:
        energies_df = pd.read_csv(energiescsvpath)
        energiesfirsttime = False

    closest = energies_df.iloc[(energies_df["Energy"] - energy).abs().argsort()[:qty]]

    closest["Element"] = closest["Element"].apply(elementSymboltoName)
    closest["Line"] = closest["Line"].str.replace("a", "\u03B1")  # replace a with alpha
    closest["Line"] = closest["Line"].str.replace("b", "\u03B2")  # replace b with beta
    closest.rename(columns={"Energy": "Energy (keV)"}, inplace=True)
    printAndLog(f"Peak Identification: {round(energy, 4)}keV", "INFO")
    printAndLog(f"The {qty} closest possibilities are:", "INFO")
    printAndLog(closest, "INFO")


def sanityCheckSpectrum(
    spectrum_counts: list, spectrum_energies: list, source_voltage_in_kV: int
) -> bool:
    """Checks that a spectrum is sensible, and that the listed voltage is accurate.
    This is required because of a bug in Bruker pXRF instrument software, sometimes causing phases of an assay to use an incorrect voltage.
    Returns TRUE if sanity check PASSES, return FALSE if not.
    DEPRECATED 2024/01/08, USE sanityCheckSpectrum_SumMethod instead."""
    # Calculate the standard deviation of the spectrum
    std_dev = np.std(spectrum_counts)
    # print(f"spectrum std dev = {std_dev}")

    # Set a threshold for noise detection (too small might be prone to noise, too high isn't useful. starting with stddev/100. UPDATE - using /50, 100 was too sensitive in some cases. /40 now. need to come up with a better method for this, it gives a lot of false positives.)
    threshold = std_dev / 40
    # print(f"{threshold=}")

    # reverse iterate list to search backwards - no zero peak to worry about, and generally should be faster.
    for i in range(len(spectrum_counts) - 1, 0, -1):
        if spectrum_counts[i] > threshold:
            # Found a peak above the noise threshold
            peak_index = i
            break
    else:
        # No peak above the noise threshold found
        peak_index = None

    if peak_index is not None:
        # print(f"Latest point with a peak above noise: energy={spectrum_energies[peak_index]}, counts={spectrum_counts[peak_index]}")
        if spectrum_energies[peak_index] < source_voltage_in_kV:
            # this point should be LOWER than source voltage *almost* always. some exclusions, incl. sum peaks, but those should be niche.
            return True
        else:
            printAndLog(
                f"Failed Sanity Check Details: highest meaningful energy present={spectrum_energies[peak_index]:.2f}, meaningful counts threshold={threshold:.0f}, reported source voltage={source_voltage_in_kV:.0f}"
            )
            return False

    else:
        # No peak above noise detected - flat spectra?
        return False


def sanityCheckSpectrum_SumMethod(
    spectrum_counts: list, spectrum_energies: list, source_voltage_in_kV: int
) -> bool:
    """Checks that a spectrum is sensible, and that the listed voltage is accurate.
    This is required because of a bug in Bruker pXRF instrument software, sometimes causing phases of an assay to use an incorrect voltage.
    Returns TRUE if sanity check passed, return FALSE if not.
    An UPDATED version of the sanityCheckSpectrum function that should be less prone to false positives, and faster.
    """
    counts_sum = np.sum(spectrum_counts)
    two_percent_counts_threshold = counts_sum * 0.02
    sum_counting = 0
    for i in range(len(spectrum_counts) - 1, 0, -1):
        sum_counting += spectrum_counts[i]
        if sum_counting > two_percent_counts_threshold:
            abovethreshold_index = i
            break
    if spectrum_energies[abovethreshold_index] < source_voltage_in_kV:
        # this point should be LOWER than source voltage always.
        # printAndLog(
        #     f"PASSED Sanity Check Details: The 2%-total-counts threshold energy ({spectrum_energies[abovethreshold_index]:.2f}kV) was LOWER than the Reported source voltage ({source_voltage_in_kV}kV).""
        # )
        return True
    else:
        printAndLog(
            f"FAILED Sanity Check Details: The 2%-total-counts threshold energy ({spectrum_energies[abovethreshold_index]:.2f}kV) was HIGHER than the Reported source voltage ({source_voltage_in_kV}kV).",
            "WARNING",
        )
        return False


def clearResultsfromTable():  # Clears all data from results table
    for item in resultsTable.get_children():
        resultsTable.delete(item)


def displayResults(assay):
    global resultsTable
    clearResultsfromTable()
    data = assay.results
    for index, row in data.iterrows():
        # print(row)
        if displayunits_var.get() == "%":
            resultsTable.insert(
                parent="",
                index="end",
                values=[f"{row[0]:03}", row[1], f"{row[2]:.4f}", f"{row[3]:.4f}"],
            )
        else:
            resultsTable.insert(
                parent="",
                index="end",
                values=[
                    f"{row.iloc[0]:03}",
                    row.iloc[1],
                    f"{row.iloc[2]:.0f}",
                    f"{row.iloc[3]:.0f}",
                ],
            )
    # TODO: add update method for concentrataion units based on assay selected


def loginClicked():
    instrument_Login()


def getInfoClicked():
    instrument_GetInfo()
    # getinfo_thread = threading.Thread(target = instrument_GetInfo).start()


def getS1verClicked():
    global s1vermanuallyrequested
    s1vermanuallyrequested = True
    instrument_QuerySoftwareVersion()


def startAssayClicked():
    global instr_assayisrunning
    global instr_assayrepeatsselected
    global instr_assayrepeatsleft
    global instr_assayrepeatschosenforcurrentrun
    global button_assay
    instr_assayrepeatsleft = instr_assayrepeatsselected
    instr_assayrepeatschosenforcurrentrun = instr_assayrepeatsselected
    if instr_assayisrunning:
        instrument_StopAssay()
        instr_assayisrunning = False
        # button_assay_text.set('\u2BC8 Start Assay')
        button_assay.configure(
            text=getAssayPlurality("start"),
            image=icon_startassay,
            fg_color="#33AF56",
            hover_color="#237A3C",
        )
    else:
        if instr_assayrepeatsselected > 1:
            printAndLog(
                f"Starting Assays - {instr_assayrepeatsselected} consecutive selected."
            )
        if applicationselected_stringvar.get() == "Custom Spectrum":
            instrument_StartAssay(
                customassay=True,
                customassay_filter=customspectrum_filter_dropdown.get(),
                customassay_voltage=int(customspectrum_voltage_entry.get()),
                customassay_current=float(customspectrum_current_entry.get()),
                customassay_duration=int(customspectrum_duration_entry.get()),
            )
        else:
            instrument_StartAssay()

        approx_secs_total = instr_assayrepeatsleft * instr_approxsingleassaytime
        approx_mins = approx_secs_total // 60
        approx_secs = approx_secs_total % 60
        printAndLog(
            f"Approximate time until completion: {approx_mins}:{approx_secs:02}"
        )

        instr_assayisrunning = True
        # button_assay_text.set('\u2BC0 Stop Assay')
        button_assay.configure(
            text=getAssayPlurality("stop"),
            image=icon_stopassay,
            fg_color="#D42525",
            hover_color="#7F1616",
        )


def endOfAssaysReset():  # Assumes this is called when assay is completed and no repeats remain to be done
    global instr_assayisrunning
    instr_assayisrunning = False
    if "Stop Assay" in button_assay.cget("text"):
        # button_assay_text.set('\u2BC8 Start Assay')
        button_assay.configure(
            text=getAssayPlurality("start"),
            image=icon_startassay,
            fg_color="#33AF56",
            hover_color="#237A3C",
        )


def ui_UpdateCurrentAppAndPhases():  # update application selected and phase timings in UI
    global instr_currentphases
    global instr_currentapplication
    global instr_methodsforcurrentapplication
    global ui_firsttime
    global dropdown_application
    global dropdown_method
    global p1_entry
    global p2_entry
    global p3_entry
    global p1_label
    global p2_label
    global p3_label
    global p1_s
    global p2_s
    global p3_s
    global applyphasetimes
    global customspectrum_filter_dropdown

    phasecount = len(instr_currentphases)

    if ui_firsttime == 1:
        label_application = ctk.CTkLabel(
            appmethodframe, text="Application ", anchor="w", font=ctk_jbm12
        )
        label_application.grid(row=2, column=0, padx=[8, 4], pady=4, sticky=tk.NSEW)
        dropdown_application = ctk.CTkOptionMenu(
            appmethodframe,
            variable=applicationselected_stringvar,
            values=instr_applicationspresent + ["Custom Spectrum"],
            command=applicationChoiceMade,
            dynamic_resizing=False,
            font=ctk_jbm12B,
            dropdown_font=ctk_jbm12,
        )
        dropdown_application.grid(
            row=2, column=1, padx=4, pady=4, columnspan=2, sticky=tk.NSEW
        )
        # label_currentapplication_text.set(f'Current Application: ')
        # label_currentapplication = ctk.CTkLabel(phaseframe, textvariable=label_currentapplication_text, anchor='w')
        # label_currentapplication.grid(row=0, column=0, padx=8, pady=4, columnspan = 4, sticky=tk.NSEW)
        phaseframe.columnconfigure(0, weight=1)
        appmethodframe.columnconfigure(1, weight=1)

        label_method = ctk.CTkLabel(
            appmethodframe, text="Method ", anchor="w", font=ctk_jbm12
        )
        label_method.grid(row=3, column=0, padx=[8, 4], pady=4, sticky=tk.NSEW)
        dropdown_method = ctk.CTkOptionMenu(
            appmethodframe,
            variable=methodselected_stringvar,
            values=instr_methodsforcurrentapplication,
            command=methodChoiceMade,
            dynamic_resizing=False,
            font=ctk_jbm12B,
            dropdown_font=ctk_jbm12,
        )
        dropdown_method.grid(
            row=3, column=1, padx=4, pady=4, columnspan=4, sticky=tk.NSEW
        )

        p1_label = ctk.CTkLabel(
            phaseframe,
            width=5,
            textvariable=phasename1_stringvar,
            anchor="w",
            font=ctk_jbm12,
        )
        p1_label.grid(row=1, column=0, padx=[8, 4], pady=4, sticky=tk.EW)
        p2_label = ctk.CTkLabel(
            phaseframe,
            width=5,
            textvariable=phasename2_stringvar,
            anchor="w",
            font=ctk_jbm12,
        )
        p2_label.grid(row=2, column=0, padx=[8, 4], pady=4, sticky=tk.EW)
        p3_label = ctk.CTkLabel(
            phaseframe,
            width=5,
            textvariable=phasename3_stringvar,
            anchor="w",
            font=ctk_jbm12,
        )
        p3_label.grid(row=3, column=0, padx=[8, 4], pady=4, sticky=tk.EW)
        p1_entry = ctk.CTkEntry(
            phaseframe,
            width=40,
            justify="right",
            textvariable=phasetime1_stringvar,
            border_width=1,
            font=ctk_jbm12,
        )
        p1_entry.grid(row=1, column=1, padx=4, pady=4, sticky=tk.EW)
        p2_entry = ctk.CTkEntry(
            phaseframe,
            width=40,
            justify="right",
            textvariable=phasetime2_stringvar,
            border_width=1,
            font=ctk_jbm12,
        )
        p2_entry.grid(row=2, column=1, padx=4, pady=4, sticky=tk.EW)
        p3_entry = ctk.CTkEntry(
            phaseframe,
            width=40,
            justify="right",
            textvariable=phasetime3_stringvar,
            border_width=1,
            font=ctk_jbm12,
        )
        p3_entry.grid(row=3, column=1, padx=4, pady=4, sticky=tk.EW)
        p1_s = ctk.CTkLabel(phaseframe, width=1, text="s", anchor="w", font=ctk_jbm12)
        p1_s.grid(row=1, column=2, padx=[0, 8], pady=4, sticky=tk.EW)
        p2_s = ctk.CTkLabel(phaseframe, width=1, text="s", anchor="w", font=ctk_jbm12)
        p2_s.grid(row=2, column=2, padx=[0, 8], pady=4, sticky=tk.EW)
        p3_s = ctk.CTkLabel(phaseframe, width=1, text="s", anchor="w", font=ctk_jbm12)
        p3_s.grid(row=3, column=2, padx=[0, 8], pady=4, sticky=tk.EW)

        applyphasetimes = ctk.CTkButton(
            phaseframe,
            width=10,
            image=icon_apply,
            compound="top",
            anchor="top",
            text="Apply",
            command=savePhaseTimes,
            font=ctk_jbm12B,
        )
        applyphasetimes.grid(
            row=1,
            column=3,
            rowspan=phasecount,
            padx=4,
            pady=4,
            ipadx=4,
            ipady=4,
            sticky=tk.NSEW,
        )

        ui_firsttime = 0

    p1_label.grid_remove()
    p2_label.grid_remove()
    p3_label.grid_remove()
    p1_entry.grid_remove()
    p2_entry.grid_remove()
    p3_entry.grid_remove()
    p1_s.grid_remove()
    p2_s.grid_remove()
    p3_s.grid_remove()

    # dropdown_application.configure(values=instr_applicationspresent)
    applicationselected_stringvar.set(instr_currentapplication)
    methodselected_stringvar.set(instr_currentmethod)
    # label_currentapplication_text.set(f'{instr_currentapplication} | {instr_currentmethod}')

    # for widget in phaseframe.winfo_children():    #first remove all prev widgets in phaseframe
    #     widget.destroy()

    dropdown_method.configure(values=instr_methodsforcurrentapplication)

    if phasecount >= 1:
        phasetime1_stringvar.set(instr_currentphases[0][2])
        if len(instr_currentphases[0][1]) > 18:
            phasename1_stringvar.set(f"{instr_currentphases[0][1][0:18]}...")
        else:
            phasename1_stringvar.set(instr_currentphases[0][1])
        p1_label.grid()
        p1_entry.grid()
        p1_s.grid()

    if phasecount >= 2:
        phasetime2_stringvar.set(instr_currentphases[1][2])
        if len(instr_currentphases[1][1]) > 18:
            phasename2_stringvar.set(f"{instr_currentphases[1][1][0:18]}...")
        else:
            phasename2_stringvar.set(instr_currentphases[1][1])
        p2_label.grid()
        p2_entry.grid()
        p2_s.grid()

    if phasecount >= 3:
        phasetime3_stringvar.set(instr_currentphases[2][2])
        if len(instr_currentphases[2][1]) > 18:
            phasename3_stringvar.set(f"{instr_currentphases[2][1][0:18]}...")
        else:
            phasename3_stringvar.set(instr_currentphases[2][1])
        p3_label.grid()
        p3_entry.grid()
        p3_s.grid()

    applyphasetimes.grid_configure(rowspan=phasecount)

    customspectrum_filter_dropdown.configure(values=instr_filterspresent)
    customspectrum_illumination_dropdown.configure(
        values=[illum.name for illum in instr_illuminations]
    )
    # gui.update()


def unselectAllAssays():
    global assaysTable
    for i in assaysTable.selection():
        assaysTable.selection_remove(i)


def unselectAllResultCompounds():
    global resultsTable
    for i in resultsTable.selection():
        resultsTable.selection_remove(i)


def treeview_sort_column(treeview, col, reverse):
    # l = [(treeview.set(k, col), k) for k in treeview.get_children('')]
    # l.sort(reverse=reverse)
    # # rearrange items in sorted positions
    # for index, (val, k) in enumerate(l):
    #     treeview.move(k, '', index)
    # # reverse sort next time
    # treeview.heading(col, command=lambda _col=col: treeview_sort_column(treeview, _col, not reverse))
    """
    to sort the table by column when clicking in column
    """
    try:
        data_list = [
            (float(treeview.set(k, col)), k) for k in treeview.get_children("")
        ]
    except Exception:
        data_list = [(treeview.set(k, col), k) for k in treeview.get_children("")]

    data_list.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(data_list):
        treeview.move(k, "", index)

    # reverse sort next time
    treeview.heading(
        column=col,
        command=lambda _col=col: treeview_sort_column(treeview, _col, not reverse),
    )


def repeatsChoiceMade(val):
    global instr_assayrepeatsselected
    printAndLog(f"Consecutive Tests Selected: {val}")
    instr_assayrepeatsselected = int(val)
    if instr_assayisrunning == False:
        button_assay.configure(
            text=getAssayPlurality("start"),
            image=icon_startassay,
            fg_color="#33AF56",
            hover_color="#237A3C",
        )
    else:
        button_assay.configure(
            text=getAssayPlurality("stop"),
            image=icon_stopassay,
            fg_color="#D42525",
            hover_color="#7F1616",
        )


def applicationChoiceMade(val):
    global phaseframe
    global instr_currentapplication
    global instr_currentmethod
    if val == "Custom Spectrum":
        # destroy/unpack phase timing frame
        # button_editinfofields.grid_remove()
        phaseframe.grid_remove()
        # pack customspectrumconfig frame
        customspectrumconfigframe.grid()
        # button_editinfofields.grid()
        # set current application to Custom Spectrum (because it's usually done via isntrument message) and fix method display
        instr_currentapplication = "Custom Spectrum"
        instr_currentmethod = "None"
        methodselected_stringvar.set("None")
        dropdown_method.configure(values=["None"])
    else:
        # pack phase timing frame
        phaseframe.grid()
        # destroy/unpack customspectrumconfig frame
        customspectrumconfigframe.grid_remove()
        cmd = f'<Configure parameter="Application">{val}</Configure>'
        sendCommand(xrf, cmd)


def methodChoiceMade(val):
    cmd = f'<Configure parameter="Method">{val}</Configure>'
    sendCommand(xrf, cmd)


def savePhaseTimes():
    global instr_currentphases
    phasecount = len(instr_currentphases)
    msg = '<Configure parameter="Phase Times"><PhaseList>'
    msg_end = "</PhaseList></Configure>"
    if phasecount >= 1:
        len_1 = int(phasetime1_stringvar.get())
        num_1 = instr_currentphases[0][0]
        ph1 = f'<Phase number="{num_1}" enabled="Yes"><Duration unlimited="No">{len_1}</Duration></Phase>'
        msg = msg + ph1
    if phasecount >= 2:
        len_2 = int(phasetime2_stringvar.get())
        num_2 = instr_currentphases[1][0]
        ph2 = f'<Phase number="{num_2}" enabled="Yes"><Duration unlimited="No">{len_2}</Duration></Phase>'
        msg = msg + ph2
    if phasecount >= 3:
        len_3 = int(phasetime3_stringvar.get())
        num_3 = instr_currentphases[2][0]
        ph3 = f'<Phase number="{num_3}" enabled="Yes"><Duration unlimited="No">{len_3}</Duration></Phase>'
        msg = msg + ph3
    msg = msg + msg_end
    sendCommand(xrf, msg)


def customSpectrumIlluminationChosen(choice):
    # get data for choice
    for illum in instr_illuminations:
        if illum.name == choice:
            customspectrum_voltage_entry.delete(0, ctk.END)
            customspectrum_voltage_entry.insert(0, illum.voltage)
            customspectrum_current_entry.delete(0, ctk.END)
            customspectrum_current_entry.insert(0, illum.current)
            customspectrum_filter_dropdown.set(illum.filterposition)


@dataclass
class GerdaSingleSampleInfo:
    """DataClass to contain all info and data for single Gerda Sample.
    scan_number:int
    name_or_note:str
    x_position:int
    y_position:int
    optional_illumination_name:str = None # optional
    optional_time_in_s:int = None # optional"""

    scan_number: int
    name_or_note: str
    x_position: int
    y_position: int
    optional_illumination_name: str = None  # optional
    optional_time_in_s: int = None  # optional

    def __post_init__(self):
        if self.optional_illumination_name == "":
            self.optional_illumination_name = None
        if self.optional_time_in_s == "":
            self.optional_time_in_s = None
        if (self.optional_illumination_name != None) and (
            self.optional_time_in_s == None
        ):
            # Time (s) (optional, IF COLUMN E SPECIFIES ILLUMINATION NAME IT WILL DEFAULT TO 60s.)
            self.optional_time_in_s = 60
        if (self.optional_illumination_name != None) and (
            self.optional_illumination_name
            not in [illum.name for illum in instr_illuminations]
        ):
            printAndLog(
                f"Illumination '{self.optional_illumination_name}' was not found on instrument. Illumination set from CSV has been overridden. Please check instrument or CSV and try again.",
                "ERROR",
            )
            self.optional_illumination_name = None
            self.optional_time_in_s = None


class GerdaSampleList:
    """Class to initialise and generate co-ordinate - sample name pairs.
    input should be CSV file of following format: first row HEADERS, info starts on second row.
    Col A: # (1->)
    Col B: Name of sample / desired pdz file name (will be stored in notes field, then later used to rename pdz files?)
    Col C: x coordinate on gerda (mm)
    Col D: y coordinate on gerda (mm)
    Col E: Illumination Name (optional, if missing will use whatever application is currently selected.)
    Col F: Time (s) (optional, IF COLUMN E SPECIFIES ILLUMINATION NAME IT WILL DEFAULT TO 60s.)
    """

    def __init__(self, csv_file_path: str = None) -> None:
        self.init_sucessful = False
        self.known_good_headers = [
            "ScanNumber",
            "Name/Note",
            "XPosition(mm)",
            "YPosition(mm)",
            "Illumination(optional)",
            "Time(sec)(optional)",
        ]
        self.listofsampleobjects: list[GerdaSingleSampleInfo] = []
        try:
            # open csv and iterate over rows
            with open(csv_file_path, "r") as csv_file:
                self.csv_reader = csv.reader(csv_file)
                self.headers = next(self.csv_reader)
                if self.headers == self.known_good_headers:
                    # get indexes (to avoid mistakes after editing/expanding headers)
                    self.colindex_scannumber = self.headers.index("ScanNumber")
                    self.colindex_namenote = self.headers.index("Name/Note")
                    self.colindex_xpos = self.headers.index("XPosition(mm)")
                    self.colindex_ypos = self.headers.index("YPosition(mm)")
                    self.colindex_illumination = self.headers.index(
                        "Illumination(optional)"
                    )
                    self.colindex_time = self.headers.index("Time(sec)(optional)")
                    for row in self.csv_reader:
                        # if row is empty, ignore
                        if row:
                            self.listofsampleobjects.append(
                                GerdaSingleSampleInfo(
                                    scan_number=int(row[self.colindex_scannumber]),
                                    name_or_note=row[self.colindex_namenote],
                                    x_position=int(row[self.colindex_xpos]),
                                    y_position=int(row[self.colindex_ypos]),
                                    optional_illumination_name=row[
                                        self.colindex_illumination
                                    ],
                                    optional_time_in_s=int(row[self.colindex_time]),
                                )
                            )
                            # process each row
                            print(row)

                    printAndLog(f"Sample List CSV File successfully processed.", "INFO")
                    self.init_sucessful = True
                    self.listofsamplenames = [
                        sample.name_or_note for sample in self.listofsampleobjects
                    ]
                else:
                    printAndLog(
                        f"ERROR: Sample List CSV: Headers do not match known headers: correct format = {self.known_good_headers}",
                        "ERROR",
                    )
        except Exception as e:
            # Handle exceptions (e.g., file not found, invalid CSV format)
            printAndLog(f"ERROR: Sample List CSV: {e}", "ERROR")


def loadGerdaSampleListCSV_clicked() -> None:
    """called when 'load gerda sample list csv' button is clicked."""
    global gerda_sample_list
    gerda_sample_list = None
    # prompt user to browse and open csv file
    file_path = ctk.filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    # check if file selected
    if file_path:
        gerda_sample_list = GerdaSampleList(csv_file_path=file_path)
        if gerda_sample_list.init_sucessful:
            printAndLog(
                f"CSV Sample List Loaded successfully. Total Scans: {len(gerda_sample_list)}",
                "INFO",
            )
            printAndLog(f"{gerda_sample_list.listofsamplenames}")
            # if csv was processed properly, then continue.
            # update ui stuff to recognise loaded sample list
            pass
    else:
        printAndLog("Sample List: No CSV File selected.", "WARNING")


class GerdaCNCController:
    """Class representing the control system of the CNC that allows xrf to be moved. Intended to be addressed"""

    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, timeout=30) -> None:
        printAndLog("Attempting to connect to GeRDA CNC Controller...", "INFO")
        try:
            self.cnc_serial = serial.Serial(port, baudrate, timeout=timeout)
            printAndLog("CNC Controller successfully connected.", "INFO")
        except serial.serialutil.SerialException as e:
            printAndLog(f"ERROR CONNECTING TO CNC: SerialException: {e}", "ERROR")
            self.cnc_serial = None
        except FileNotFoundError as e:
            printAndLog(f"ERROR CONNECTING TO CNC: FileNotFoundError: {e}", "ERROR")
            self.cnc_serial = None
        except PermissionError as e:
            printAndLog(f"ERROR CONNECTING TO CNC: PermissionError: {e}", "ERROR")
            self.cnc_serial = None
        except Exception as e:
            printAndLog(f"ERROR CONNECTING TO CNC: An unexpected error occurred: {e}")
            self.cnc_serial = None

        self.lock = threading.Lock()  # apparently ensures thread safety
        self.event = threading.Event()  # for synchronization
        self.thread = None
        self.last_command_response = (
            []
        )  # store the last response lines for threaded shit

    def send_command(self, command):
        """DON'T CALL DIRECTLY OUTSIDE CLASS. MEANT TO BE USED BY THREADED SEND COMMAND. send command to GeRDA CNC control board. returns list containing all responses from cnc control board upon completion or error."""
        with self.lock:
            if self.cnc_serial != None:
                self.cnc_serial.write((command + "\n").encode())
                printAndLog(f"Sent CNC Command: '{command}'", "INFO")
                # Read all available response lines until completed or error
                response_lines = []
                while True:
                    response = self.cnc_serial.readline().decode().strip()
                    printAndLog(f"CNC Repsonse: {response}")
                    response_lines.append(response)
                    if "error" in response.lower():
                        printAndLog(f"CNC ERROR HAS OCCURRED!", "ERROR")
                        break
                    elif response == "ok":
                        printAndLog(f"CNC Command completed successfully.", "INFO")
                        break
                self.last_command_response = response_lines
                return response_lines
            else:
                printAndLog("ERROR: No GeRDA CNC Device Connected", "ERROR")
                return None

    def send_command_in_thread(self, command):
        if self.thread and self.thread.is_alive():
            return  # A thread is already running, don't start another one

        self.thread = threading.Thread(target=self.send_command, args=(command,))
        self.thread.start()

    def move_to(self, x: int, y: int, z: int):
        """Send command to GeRDA CNC controller to move the head to coordinates x,y,z. (mm)"""
        command = f"G0 X{x} Y{y} Z{z}"
        self.send_command_in_thread(command)

    def get_current_position(self):
        self.send_command_in_thread("?")
        self.wait_for_completion()
        response = self.last_command_response
        printAndLog(f"current position response: {response}")
        return response

    def home(self):
        response = self.send_command_in_thread("$H")
        return response

    def wait_for_completion(self):
        # Wait for the event to be set, means the current step has been completed
        self.event.clear()
        self.event.wait()

    def begin_sample_sequence(
        self,
        xy_coordinates: list[tuple],
        names: list[str],
        wait_time_between_samples_s: int = 1,
    ):
        self.home()
        self.wait_for_completion()

        time.sleep(wait_time_between_samples_s)


def gerdaCNC_MoveTo(
    controller: GerdaCNCController, x: int, y: int, z: int, home_first: bool = False
):
    pass


def gerdaCNC_InitialiseConnectionIfPossible() -> None:
    """Initialises the gerda CNC serial connection if possible / if it is connected"""
    global gerdaCNC
    if gerdaCNC == None:
        # gerdaCNC = None is set near top of main(). if it equals None, it means it still hasn't been initialised.
        gerdaCNC = GerdaCNCController()
    else:
        pass
        # already connected


def gerdaCNC_Home_clicked() -> None:
    """on click function for home button for gerda ui"""
    if gerdaCNC != None:
        gerdaCNC.home()
    else:
        printAndLog(
            "ERROR: GeRDA CNC Serial Connection has not been initialised, cannot Home.",
            "ERROR",
        )


def gerdaCNC_GetCurrentPosition_clicked() -> None:
    """on click function for get pos for gerda ui"""
    if gerdaCNC != None:
        position_response_list = gerdaCNC.get_current_position
        printAndLog(position_response_list)  # TODO fix this for actual coords.
    else:
        printAndLog(
            "ERROR: GeRDA CNC Serial Connection has not been initialised, cannot Get Current Position.",
            "ERROR",
        )


def gerdaCNC_HelpMe_clicked() -> None:
    """on click function for HELP ME in gerda ui. supposed to provide description of what gerda is and does."""
    messagebox.showinfo(
        "GeRDA Help",
        "GeRDA stands for 'GEochemical Research and Documentation Assistant'. It is a CNC-platform-based system designed by MeffaLab and Lab127. S1Control can be installed on the Raspberry Pi SBC that controls GeRDA and used instead of the standard UI. This is achieved by interfacing directly with GeRDA's CNC control board. For this to work, the CNC controller USB cable must be connected to /dev/ttyUSB0 on the Pi. \n\n This functionality is a work in progress. Contact ZH@PSS for assistance.",
    )


# CTK appearance mode switcher
def ctk_change_appearance_mode_event(new_appearance_mode: str):
    ctk.set_appearance_mode(new_appearance_mode)
    global plottoolbarColour
    global treeviewColour_bg
    global plotbgColour
    global plottextColour
    global plotgridColour
    match new_appearance_mode:
        case "dark":
            plottoolbarColour = "#333333"  # "#4a4a4a"
            treeviewColour_bg = "#333333"  # "#4a4a4a"
            plotbgColour = "#414141"
            plottextColour = WHITEISH
            plotgridColour = "#666666"

            guiStyle.configure(
                "Treeview",
                background="#3d3d3d",
                foreground=WHITEISH,
                rowheight=20,
                fieldbackground="#3d3d3d",
                bordercolor="#3d3d3d",
                borderwidth=0,
            )
            guiStyle.map("Treeview", background=[("selected", "#144870")])
            guiStyle.configure(
                "Treeview.Heading",
                background="#333333",
                foreground="white",
                relief="flat",
            )
            guiStyle.map("Treeview.Heading", background=[("active", "#1f6aa5")])

        case "light":
            plottoolbarColour = "#dbdbdb"
            treeviewColour_bg = "#FFFFFF"
            plotbgColour = "#F5F5F5"
            plottextColour = CHARCOAL
            plotgridColour = "#DCDCDC"

            guiStyle.configure(
                "Treeview",
                background="#ebebeb",
                foreground=CHARCOAL,
                rowheight=20,
                fieldbackground="#ebebeb",
                bordercolor="#ebebeb",
                borderwidth=0,
            )
            guiStyle.map("Treeview", background=[("selected", "#36719f")])
            guiStyle.configure(
                "Treeview.Heading",
                background="#dbdbdb",
                foreground="black",
                relief="flat",
            )
            guiStyle.map("Treeview.Heading", background=[("active", "#3b8ed0")])

        case _:
            plottoolbarColour = "#dbdbdb"
            treeviewColour_bg = "#FFFFFF"
            plotbgColour = "#F5F5F5"
            plottextColour = CHARCOAL
            plotgridColour = "#DCDCDC"

            guiStyle.configure(
                "Treeview",
                background="#ebebeb",
                foreground=CHARCOAL,
                rowheight=20,
                fieldbackground="#ebebeb",
                bordercolor="#ebebeb",
                borderwidth=0,
            )
            guiStyle.map("Treeview", background=[("selected", "#36719f")])
            guiStyle.configure(
                "Treeview.Heading",
                background="#dbdbdb",
                foreground="black",
                relief="flat",
            )
            guiStyle.map("Treeview.Heading", background=[("active", "#3b8ed0")])

    setPlotColours()


def setPlotColours():
    global fig
    global spectra_ax
    fig.patch.set_edgecolor(plottoolbarColour)
    fig.patch.set_facecolor(plottoolbarColour)
    spectra_ax.set_facecolor(plotbgColour)
    spectra_ax.tick_params(axis="both", color=plottextColour, labelcolor=plottextColour)
    spectra_ax.yaxis.label.set_color(plottextColour)
    spectra_ax.xaxis.label.set_color(plottextColour)
    spectra_ax.yaxis.grid(color=plotgridColour)
    spectra_ax.xaxis.grid(color=plotgridColour)
    spectratoolbar.config(background=plottoolbarColour)
    spectratoolbar._message_label.config(background=plottoolbarColour)
    for child in spectratoolbar.winfo_children():
        child.config(background=plottoolbarColour)
    spectratoolbar.update()
    spectracanvas.draw_idle()


def onClosing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        closeAllThreads()
        if logFileArchivePath is not None:
            shutil.copyfile(logFilePath, logFileArchivePath)
            printAndLog(rf"Log File archived to: {logFileArchivePath}")
            printAndLog("S1Control software Closed.")
        else:
            printAndLog(
                "ERROR: Desired Log file archive path was unable to be found. The Log file has not been archived.",
                "ERROR",
            )
            printAndLog("S1Control software Closed.")
        raise SystemExit(0)
        gui.destroy()
        instrument_Disconnect()


def closeAllThreads():
    global thread_halt
    thread_halt = True


def configureEmissionLinesClicked():
    global linecfg_firsttime
    global linecfgwindows
    global emissionLineElementButtonIDs
    if linecfg_firsttime:
        linecfg_firsttime = False
        linecfgwindow = ctk.CTkToplevel()
        # linecfgwindow.bind("<Configure>", window_on_configure)
        # linecfgwindow.geometry("700x380")
        linecfgwindow.title("Configure Emission Lines")

        # after delay to fix toplevel icon bug in customtkinter.
        if sys.platform.startswith("win"):
            linecfgwindow.after(220, lambda: linecfgwindow.iconbitmap(bitmap=iconpath))
        else:
            linecfgwindow.after(
                220, lambda: linecfgwindow.iconphoto(False, iconphoto_linux)
            )
        linecfgwindow.after(100, lambda: linecfgwindow.lift())
        linecfgwindows.append(linecfgwindow)

        periodictableframe = ctk.CTkFrame(
            linecfgwindow, width=20, height=20, corner_radius=5
        )
        periodictableframe.pack(
            side=tk.TOP, fill="both", expand=True, padx=4, pady=4, ipadx=4, ipady=4
        )

        # Select Element(s) to display Emission Lines:
        for col in range(1, 19):
            periodictableframe.columnconfigure(col, weight=1, uniform="third")

        instruc = ctk.CTkLabel(
            periodictableframe,
            text="Select Element(s) to display Emission Lines:",
            font=ctk_jbm14B,
        )
        instruc.grid(
            row=0,
            column=0,
            columnspan=10,
            padx=2,
            pady=2,
            ipadx=0,
            ipady=0,
            sticky=tk.NSEW,
        )

        for e in element_info:
            button = ctk.CTkButton(
                periodictableframe,
                text=(str(e[0]) + "\n" + (e[1])),
                width=20,
                height=30,
                fg_color=e[5],
                text_color=WHITEISH,
                font=ctk_jbm14B,
                command=lambda Z=int(e[0]): toggleEmissionLine(Z),
                corner_radius=6,
            )
            button.grid(
                row=e[3], column=e[4], padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
            )
            emissionLineElementButtonIDs.append(button)
        linecfgwindow.protocol("WM_DELETE_WINDOW", lineCfgOnClosing)
    else:
        # Brings back window from being withdrawn instead of fully creating again.
        linecfgwindows[0].deiconify()


def clearEmissionLinesClicked():
    global emissionLinesElementslist
    for z in emissionLinesElementslist:
        toggleEmissionLine(z)


def toggleEmissionLine(Z):
    global emissionLinesElementslist
    global emissionLineElementButtonIDs
    global emission_lines_to_plot
    # lookup energies for Z, add to list called energies, then call plotemissionlines(energies) etc
    button = emissionLineElementButtonIDs[Z - 1]
    element_sym = elementZtoSymbol(Z)
    origfgcolour = element_info[Z - 1][5]
    lines = []  # list of lists eg ('Fe', 'Fe Ka', 6.40)
    # for name, line in xraydb.xray_lines(Z).items():
    #     if name in ['Ka1','Ka2','Kb1','Kb2','La1','Lb1']:
    #         ene = float(line.energy)/1000
    #         linedata = [f'{elementZtoSymbol(Z)} {name}',ene]
    #         lines.append(linedata)
    #         #print(f'Adding line: {linedata}')
    for linedata in all_lines:
        if linedata[0] == element_sym:  # symbol
            lines.append(linedata)

    if button.cget("fg_color") == origfgcolour:
        # ADD TO PLOT LIST AND CHANGE COLOUR TO 'SELECTED'
        button.configure(text_color=CHARCOAL)
        button.configure(fg_color=WHITEISH)
        for linedata in lines:
            emission_lines_to_plot.append(linedata)

    else:
        # REMOVE FROM PLOT LIST AND CHANGE COLOUR BACK
        button.configure(text_color=WHITEISH)
        button.configure(fg_color=origfgcolour)
        for linedata in lines:
            emission_lines_to_plot.remove(linedata)

    # add to list of elements displayed
    emissionLinesElementslist.append(Z)

    # energies = [6.40, 7.06]
    linecfgwindows[0].update()
    clearCurrentEmissionLines()
    plotEmissionLines()


def lineCfgOnClosing():
    # .withdraw() hides, .deiconify() brings back.
    linecfgwindows[0].withdraw()


def editInfoOnClosing():
    # .withdraw() hides, .deiconify() brings back.
    editinfo_windows[0].withdraw()


def window_on_configure(e):
    """This function is from https://stackoverflow.com/questions/71884285/tkinter-root-window-mouse-drag-motion-becomes-slower and supposedly will fix lag after move/resize? weird mouse issue."""
    if e.widget == gui:
        # gui.update_idletasks()
        time.sleep(0.008)


def saveAssayToCSV(assay: Assay):
    """Saves a CSV file with all of the info from a single Assay."""
    assayFolderName = f"Assays_{datetimeString}_{instr_serialnumber}"
    assayFolderPath = rf"{os.getcwd()}/Results/{assayFolderName}"
    assayFileName = f"{assay.index}_{assay.cal_application}_{datetimeString}.csv"

    if not os.path.exists(assayFolderPath):
        os.makedirs(assayFolderPath)

    with open(
        (f"{assayFolderPath}/{assayFileName}"), "x", newline="", encoding="utf-8"
    ) as assayFile:
        writer = csv.writer(assayFile)
        writer.writerow(["Instrument", instr_serialnumber])
        writer.writerow(["Date", assay.date_completed])
        writer.writerow(["Time", assay.time_completed])
        writer.writerow(["Assay #", assay.index])
        writer.writerow(["Application", assay.cal_application])
        writer.writerow(["Method", assay.cal_method])
        writer.writerow(["Assay Duration (set)", f"{assay.time_total_set}s"])
        writer.writerow(["Assay Duration (total actual)", assay.time_elapsed])
        writer.writerow(
            [
                "Temperature (Detector)",
                assay.temps.split(",")[0].split()[1].replace("°", " "),
            ]
        )
        writer.writerow(
            [
                "Temperature (Ambient)",
                assay.temps.split(",")[1].split()[1].replace("°", " "),
            ]
        )
        writer.writerow(["Phase Count", len(assay.spectra)])
        writer.writerow(
            [
                "Phases",
                (
                    assay.legends[0].replace("\u03bc", "u")
                    if 0 < len(assay.legends)
                    else ""
                ),
                (
                    assay.legends[1].replace("\u03bc", "u")
                    if 1 < len(assay.legends)
                    else ""
                ),
                (
                    assay.legends[2].replace("\u03bc", "u")
                    if 2 < len(assay.legends)
                    else ""
                ),
            ]
        )
        writer.writerow([" "])
        writer.writerow([" "])
        writer.writerow(["RESULTS:"])
        writer.writerow(list(assay.results.columns))
        for index, row in assay.results.iterrows():
            writer.writerow(row)
        writer.writerow([" "])
        writer.writerow([" "])
        writer.writerow(["SPECTRA:"])
        writer.writerow(
            [
                "eV Channel Start",
                (
                    assay.specenergies[0]["fEVChanStart"]
                    if 0 < len(assay.specenergies)
                    else ""
                ),
                (
                    assay.specenergies[1]["fEVChanStart"]
                    if 1 < len(assay.specenergies)
                    else ""
                ),
                (
                    assay.specenergies[2]["fEVChanStart"]
                    if 2 < len(assay.specenergies)
                    else ""
                ),
            ]
        )
        writer.writerow(
            [
                "eV per Channel",
                (
                    assay.specenergies[0]["fEVPerChannel"]
                    if 0 < len(assay.specenergies)
                    else ""
                ),
                (
                    assay.specenergies[1]["fEVPerChannel"]
                    if 1 < len(assay.specenergies)
                    else ""
                ),
                (
                    assay.specenergies[2]["fEVPerChannel"]
                    if 2 < len(assay.specenergies)
                    else ""
                ),
            ]
        )
        writer.writerow([" "])
        writer.writerow(
            [
                "Energy (eV)",
                "Counts (Phase 1)",
                "Counts (Phase 2)",
                "Counts (Phase 3)",
            ]
        )
        n = 0
        inc = assay.specenergies[0]["fEVPerChannel"]
        energy = assay.specenergies[0]["fEVChanStart"]

        phasect = len(assay.spectra)
        for channel in assay.spectra[0]["data"]:
            writer.writerow(
                [
                    energy,
                    (assay.spectra[0]["data"][n] if 0 < phasect else ""),
                    (assay.spectra[1]["data"][n] if 1 < phasect else ""),
                    (assay.spectra[2]["data"][n] if 2 < phasect else ""),
                ]
            )
            energy += inc
            n += 1

        # writer.writerow(['']) want to put dead time % here?

        # for row in timestamps:
        #     writer.writerow(row)
    printAndLog(f"Assay # {assay.index} saved as CSV file.")


def addAssayToResultsCSV(assay: Assay):
    """given an Assay object, add the results of that assay to the results CSV file. designed to mimic results CSV output of instrument."""
    global current_session_results_df

    resultsFileName = f"Results_{datetimeString}_{instr_serialnumber}.csv"
    resultsFolderPath = rf"{os.getcwd()}/Results"
    resultsFilePath = rf"{resultsFolderPath}/{resultsFileName}"
    # create /Results folder in local dir if not there already
    if not os.path.exists(resultsFolderPath):
        os.makedirs(resultsFolderPath)

    new_assay_results_dict = {}
    new_assay_results_dict["Assay #"] = [assay.index]
    new_assay_results_dict["Serial #"] = [instr_serialnumber]
    new_assay_results_dict["Date"] = [assay.date_completed]
    new_assay_results_dict["Time"] = [assay.time_completed]
    new_assay_results_dict["Application"] = [assay.cal_application]
    new_assay_results_dict["Method"] = [assay.cal_method]
    new_assay_results_dict["Duration (Actual)"] = [assay.time_elapsed]
    new_assay_results_dict["Sanity Check"] = [assay.sanity_check_passed]
    # TODO: separate notes into individual columns
    new_assay_results_dict["Info Fields (Combined)"] = [assay.note]
    # TODO: replace/add live times for each beam
    # TODO: add notes fields?

    compound_names = assay.results["Compound"].tolist()
    conc_vals = assay.results["Concentration"].tolist()
    conc_err_vals = assay.results["Error(1SD)"].tolist()
    for compound_name, conc_val, conc_err_val in zip(
        compound_names, conc_vals, conc_err_vals
    ):
        new_assay_results_dict[f"{compound_name}"] = [conc_val]
        new_assay_results_dict[f"{compound_name} Err"] = [conc_err_val]

    # convert new assay results dict to df
    new_assay_results_df = pd.DataFrame(data=new_assay_results_dict)

    # update current session results df with new assay data. this will add new columns if needed (if element wasn't present before, etc)
    current_session_results_df = pd.concat(
        [current_session_results_df, new_assay_results_df], ignore_index=True
    )

    # Actually write to the CSV file
    results_csv_not_saved = True
    while results_csv_not_saved:
        try:
            current_session_results_df.to_csv(
                rf"{resultsFolderPath}/{resultsFileName}", index=False
            )
            results_csv_not_saved = False
        except PermissionError:
            # Most likely, user has opened results file between readings, and it is unable to be overwritten.
            if messagebox.askyesno(
                title="Results File Overwrite Error",
                message=f"S1Control was unable to write to '{resultsFileName}' with new assay result data. This is likely due to the file being open in another program. If you would like to try to save the new result data again, close the file or program and then click 'Yes' to reattempt. Otherwise click 'No', and the program will try to save the results at the end of the next assay.",
            ):
                results_csv_not_saved = True
            else:
                results_csv_not_saved = False

    # with open((f'{resultsFolderPath}\{resultsFileName}'), 'x', newline='', encoding= 'utf-8') as resultsFile:
    #     resultsWriter = csv.writer(resultsFile)
    #     # write updated results dataframe to csv:
    #     resultsWriter.writerow(newResultsRow)

    printAndLog(f"Assay # {assay.index} results saved to {resultsFileName}.")


def clearAllEditInfoFields():
    field1_name_strvar.set("")
    field1_val_strvar.set("")
    field2_name_strvar.set("")
    field2_val_strvar.set("")
    field3_name_strvar.set("")
    field3_val_strvar.set("")
    field4_name_strvar.set("")
    field4_val_strvar.set("")
    field5_name_strvar.set("")
    field5_val_strvar.set("")
    field6_name_strvar.set("")
    field6_val_strvar.set("")


def fillEditInfoFields(infofields: list):
    i = 1
    clearAllEditInfoFields()
    for field_dict in infofields:
        field_name = field_dict["@FieldName"]
        field_val = field_dict["#text"]
        match i:
            case 1:
                field1_name_strvar.set(field_name)
                field1_val_strvar.set(field_val)
                # field1_iscounter_boolvar.set(False)
            case 2:
                field2_name_strvar.set(field_name)
                field2_val_strvar.set(field_val)
                # field2_iscounter_boolvar.set(False)
            case 3:
                field3_name_strvar.set(field_name)
                field3_val_strvar.set(field_val)
                # field3_iscounter_boolvar.set(False)
            case 4:
                field4_name_strvar.set(field_name)
                field4_val_strvar.set(field_val)
                # field4_iscounter_boolvar.set(False)
            case 5:
                field5_name_strvar.set(field_name)
                field5_val_strvar.set(field_val)
                # field5_iscounter_boolvar.set(False)
            case 6:
                field6_name_strvar.set(field_name)
                field6_val_strvar.set(field_val)
                # field6_iscounter_boolvar.set(False)
        i += 1


def editInfoFieldsClicked():
    global editinfo_firsttime
    global editinfo_windows
    global editinfo_fieldnames
    global editinfo_fieldvalues
    global editinfo_fieldcounters
    global iconpath
    if editinfo_firsttime:
        editinfo_firsttime = False
        editinfowindow = ctk.CTkToplevel()
        # editinfowindow.bind("<Configure>", window_on_configure)
        # linecfgwindow.geometry("700x380")
        editinfowindow.title("Edit Info Fields")
        if sys.platform.startswith("win"):
            editinfowindow.after(
                250, lambda: editinfowindow.iconbitmap(bitmap=iconpath)
            )
        else:
            editinfowindow.after(
                250, lambda: editinfowindow.iconphoto(False, iconphoto_linux)
            )
        editinfowindow.after(100, lambda: editinfowindow.lift())
        editinfo_windows.append(editinfowindow)

        infobuttonframe = ctk.CTkFrame(
            editinfowindow, width=20, height=20, corner_radius=5
        )
        infobuttonframe.pack(
            side=tk.BOTTOM, fill="x", expand=True, padx=4, pady=4, ipadx=4, ipady=4
        )

        button_getinfofields = ctk.CTkButton(
            infobuttonframe,
            width=13,
            image=icon_getinfofields,
            text="Copy Info-Fields From Instrument",
            font=ctk_jbm12B,
            command=queryEditFields_clicked,
        )
        button_getinfofields.pack(
            side=tk.LEFT, fill="x", expand=True, padx=(8, 2), pady=4, ipadx=0, ipady=0
        )

        button_resetinfofields = ctk.CTkButton(
            infobuttonframe,
            width=13,
            image=icon_resetinfofields,
            text="Reset All to Default",
            font=ctk_jbm12B,
            fg_color="#D85820",
            hover_color="#973d16",
            command=resetEditFields_clicked,
        )
        button_resetinfofields.pack(
            side=tk.LEFT, fill="x", expand=True, padx=(2, 2), pady=4, ipadx=0, ipady=0
        )

        button_applyinfofields = ctk.CTkButton(
            infobuttonframe,
            width=13,
            image=icon_applysmall,
            text="Apply Changes",
            font=ctk_jbm12B,
            command=instrument_ApplyInfoFields,
        )
        button_applyinfofields.pack(
            side=tk.LEFT, fill="x", expand=True, padx=(2, 8), pady=4, ipadx=0, ipady=0
        )

        editinfoframe = ctk.CTkFrame(
            editinfowindow, width=20, height=20, corner_radius=5
        )
        editinfoframe.pack(
            side=tk.TOP, fill="both", expand=True, padx=4, pady=4, ipadx=4, ipady=4
        )
        editinfoframe.grid_columnconfigure(3, weight=1)

        # Col/Row legends
        field_name_column_label = ctk.CTkLabel(
            editinfoframe, text="Field Name", font=ctk_jbm12, anchor=tk.W
        )
        field_name_column_label.grid(
            row=2, column=2, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field_value_column_label = ctk.CTkLabel(
            editinfoframe, text="Field Value", font=ctk_jbm12, anchor=tk.W
        )
        field_value_column_label.grid(
            row=2, column=3, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field_counter_column_label = ctk.CTkLabel(
            editinfoframe, text="Counter", font=ctk_jbm12, anchor=tk.W
        )
        field_counter_column_label.grid(
            row=2, column=4, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field1_row_label = ctk.CTkLabel(
            editinfoframe, text="1", font=ctk_jbm12, anchor=tk.W
        )
        field1_row_label.grid(
            row=3, column=1, padx=4, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field2_row_label = ctk.CTkLabel(
            editinfoframe, text="2", font=ctk_jbm12, anchor=tk.W
        )
        field2_row_label.grid(
            row=4, column=1, padx=4, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field3_row_label = ctk.CTkLabel(
            editinfoframe, text="3", font=ctk_jbm12, anchor=tk.W
        )
        field3_row_label.grid(
            row=5, column=1, padx=4, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field4_row_label = ctk.CTkLabel(
            editinfoframe, text="4", font=ctk_jbm12, anchor=tk.W
        )
        field4_row_label.grid(
            row=6, column=1, padx=4, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field5_row_label = ctk.CTkLabel(
            editinfoframe, text="5", font=ctk_jbm12, anchor=tk.W
        )
        field5_row_label.grid(
            row=7, column=1, padx=4, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field6_row_label = ctk.CTkLabel(
            editinfoframe, text="6", font=ctk_jbm12, anchor=tk.W
        )
        field6_row_label.grid(
            row=8, column=1, padx=4, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )

        # FIELD 1
        field1_name_entry = ctk.CTkEntry(
            editinfoframe,
            width=170,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field1_name_strvar,
        )
        field1_name_entry.grid(
            row=3, column=2, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field1_value_entry = ctk.CTkEntry(
            editinfoframe,
            width=260,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field1_val_strvar,
        )
        field1_value_entry.grid(
            row=3, column=3, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field1_counter_checkbox = ctk.CTkCheckBox(
            editinfoframe,
            text="",
            variable=field1_iscounter_boolvar,
            onvalue=True,
            offvalue=False,
        )
        field1_counter_checkbox.grid(
            row=3, column=4, padx=8, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW
        )
        editinfo_fieldnames.append(field1_name_strvar)
        editinfo_fieldvalues.append(field1_val_strvar)
        editinfo_fieldcounters.append(field1_iscounter_boolvar)

        # FIELD 2
        field2_name_entry = ctk.CTkEntry(
            editinfoframe,
            width=170,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field2_name_strvar,
        )
        field2_name_entry.grid(
            row=4, column=2, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field2_value_entry = ctk.CTkEntry(
            editinfoframe,
            width=260,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field2_val_strvar,
        )
        field2_value_entry.grid(
            row=4, column=3, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field2_counter_checkbox = ctk.CTkCheckBox(
            editinfoframe,
            text="",
            variable=field2_iscounter_boolvar,
            onvalue=True,
            offvalue=False,
        )
        field2_counter_checkbox.grid(
            row=4, column=4, padx=8, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW
        )
        editinfo_fieldnames.append(field2_name_strvar)
        editinfo_fieldvalues.append(field2_val_strvar)
        editinfo_fieldcounters.append(field2_iscounter_boolvar)

        # FIELD 3
        field3_name_entry = ctk.CTkEntry(
            editinfoframe,
            width=170,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field3_name_strvar,
        )
        field3_name_entry.grid(
            row=5, column=2, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field3_value_entry = ctk.CTkEntry(
            editinfoframe,
            width=260,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field3_val_strvar,
        )
        field3_value_entry.grid(
            row=5, column=3, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field3_counter_checkbox = ctk.CTkCheckBox(
            editinfoframe,
            text="",
            variable=field3_iscounter_boolvar,
            onvalue=True,
            offvalue=False,
        )
        field3_counter_checkbox.grid(
            row=5, column=4, padx=8, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW
        )
        editinfo_fieldnames.append(field3_name_strvar)
        editinfo_fieldvalues.append(field3_val_strvar)
        editinfo_fieldcounters.append(field3_iscounter_boolvar)

        # FIELD 4
        field4_name_entry = ctk.CTkEntry(
            editinfoframe,
            width=170,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field4_name_strvar,
        )
        field4_name_entry.grid(
            row=6, column=2, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field4_value_entry = ctk.CTkEntry(
            editinfoframe,
            width=260,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field4_val_strvar,
        )
        field4_value_entry.grid(
            row=6, column=3, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field4_counter_checkbox = ctk.CTkCheckBox(
            editinfoframe,
            text="",
            variable=field4_iscounter_boolvar,
            onvalue=True,
            offvalue=False,
        )
        field4_counter_checkbox.grid(
            row=6, column=4, padx=8, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW
        )
        editinfo_fieldnames.append(field4_name_strvar)
        editinfo_fieldvalues.append(field4_val_strvar)
        editinfo_fieldcounters.append(field4_iscounter_boolvar)

        # FIELD 5
        field5_name_entry = ctk.CTkEntry(
            editinfoframe,
            width=170,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field5_name_strvar,
        )
        field5_name_entry.grid(
            row=7, column=2, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field5_value_entry = ctk.CTkEntry(
            editinfoframe,
            width=260,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field5_val_strvar,
        )
        field5_value_entry.grid(
            row=7, column=3, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field5_counter_checkbox = ctk.CTkCheckBox(
            editinfoframe,
            text="",
            variable=field5_iscounter_boolvar,
            onvalue=True,
            offvalue=False,
        )
        field5_counter_checkbox.grid(
            row=7, column=4, padx=8, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW
        )
        editinfo_fieldnames.append(field5_name_strvar)
        editinfo_fieldvalues.append(field5_val_strvar)
        editinfo_fieldcounters.append(field5_iscounter_boolvar)

        # FIELD 6
        field6_name_entry = ctk.CTkEntry(
            editinfoframe,
            width=170,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field6_name_strvar,
        )
        field6_name_entry.grid(
            row=8, column=2, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field6_value_entry = ctk.CTkEntry(
            editinfoframe,
            width=260,
            justify="left",
            font=ctk_jbm12,
            border_width=1,
            textvariable=field6_val_strvar,
        )
        field6_value_entry.grid(
            row=8, column=3, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW
        )
        field6_counter_checkbox = ctk.CTkCheckBox(
            editinfoframe,
            text="",
            variable=field6_iscounter_boolvar,
            onvalue=True,
            offvalue=False,
        )
        field6_counter_checkbox.grid(
            row=8, column=4, padx=8, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW
        )
        editinfo_fieldnames.append(field6_name_strvar)
        editinfo_fieldvalues.append(field6_val_strvar)
        editinfo_fieldcounters.append(field6_iscounter_boolvar)

        # editinfo_instruc = ctk.CTkLabel(editinfoframe, text = 'Select Element(s) to display Emission Lines:', font=ctk_jbm14B)
        # editinfo_instruc.grid(row=0,column=0, columnspan = 10, padx=2, pady=2, ipadx=0, ipady=0, sticky=tk.NSEW)

        editinfowindow.protocol("WM_DELETE_WINDOW", editInfoOnClosing)
    else:
        # Brings back window from being withdrawn instead of fully creating again.
        editinfo_windows[0].deiconify()


def instrument_ApplyInfoFields():
    global editinfo_validcounterfieldsused
    proceedwithapplying = True
    for i in range(6):
        if editinfo_fieldcounters[i].get() == True:
            editinfo_validcounterfieldsused = True
            if editinfo_fieldvalues[i].get().isdigit() == False:
                proceedwithapplying = False
                editinfo_validcounterfieldsused = (
                    False  # set this here so that we don't increment flawed fields
                )
                messagebox.showwarning(
                    "Invalid Value for Counter Field",
                    f"Warning: The Value of info field {i+1} is incompatible with being a counter. Counter field values must be integers. Fields have not been applied.",
                )
                editinfo_windows[0].lift()

    if proceedwithapplying:
        infofieldprintstr = ""
        infofieldsmsg = '<Configure parameter="Edit Fields"><FieldList>'
        for i in range(6):
            fieldmsgsegment = ""
            namemsgsegment = f"<Name>{editinfo_fieldnames[i].get()}</Name>"
            valuemsgsegment = f"<Value>{editinfo_fieldvalues[i].get()}</Value>"
            fieldtype = "Fixed"
            if editinfo_fieldcounters[i].get() == True:
                fieldtype = "Counter"
            if editinfo_fieldnames[i].get() == "":
                # Use XML tag for null if value is null
                namemsgsegment = "<Name/>"
            if editinfo_fieldvalues[i].get() == "":
                # Use XML tag for null if value is null
                valuemsgsegment = "<Value/>"

            fieldmsgsegment = (
                f'<Field type="{fieldtype}">{namemsgsegment}{valuemsgsegment}</Field>'
            )

            if fieldmsgsegment != '<Field type="Fixed"><Name/><Value/></Field>':
                # if is not an Empty field, append to msg for sending
                infofieldsmsg = infofieldsmsg + fieldmsgsegment
                # also append to str for printing to log later
                infofieldprintstr += f"{editinfo_fieldnames[i].get()}/{editinfo_fieldvalues[i].get()}/{'<Counter>' if editinfo_fieldcounters[i].get() else '<Fixed>'} "

        infofieldsmsg = infofieldsmsg + "</FieldList></Configure>"
        sendCommand(xrf, infofieldsmsg)
        printAndLog(f"Info-Fields Set: {infofieldprintstr}")

        editInfoOnClosing()


def resetEditFields_clicked():
    if messagebox.askyesno(
        "Reset All Fields and Values on Instrument?",
        "This will reset all field names and values on the instrument to a default placeholder. It will not affect assays that have already been taken. \n\nWould you like to proceed?",
    ):
        # instrument_ResetInfoFields() # Bugged, does not behave as expected.
        # instrument_QueryEditFields()    # Pull blank fields from instrument
        for i in range(6):
            if i == 0:
                editinfo_fieldnames[i].set("Sample ID")
                editinfo_fieldvalues[i].set("123")
                editinfo_fieldcounters[i].set(False)
            elif i == 1:
                editinfo_fieldnames[i].set("Sample Name")
                editinfo_fieldvalues[i].set("ABC")
                editinfo_fieldcounters[i].set(False)
            else:
                editinfo_fieldnames[i].set("")
                editinfo_fieldvalues[i].set("")
                editinfo_fieldcounters[i].set(False)
        instrument_ApplyInfoFields()
        # printAndLog('Info-Fields Reset.')
    editinfo_windows[0].lift()


def incrementInfoFieldCounterValues():
    """This will only update the values that have been marked as counters, and ONLY IN THE UI. not on the instrument. it checks editinfo_counterfieldsused == True to check that counter fields are valid and are being used"""
    if editinfo_validcounterfieldsused:
        for i in range(len(editinfo_fieldcounters)):
            if editinfo_fieldcounters[i].get() == True:
                # increment only counter fields, the same way the instrument would.
                editinfo_fieldvalues[i].set(int(editinfo_fieldvalues[i].get()) + 1)


def toggleResultsFrameVisible(_):
    if resultsframe.winfo_ismapped():
        resultsframe.pack_forget()
        printAndLog("Results Section Hidden. Ctrl+Shift+R to restore.", "WARNING")
    else:
        resultsframe.pack(
            side=tk.BOTTOM,
            fill="both",
            anchor=tk.SW,
            expand=True,
            padx=8,
            pady=[0, 8],
            ipadx=4,
            ipady=4,
        )


def toggleSpectraFrameVisible(_):
    if spectraframe.winfo_ismapped():
        spectraframe.pack_forget()
        printAndLog("Spectra Section Hidden. Ctrl+Shift+S to restore.", "WARNING")
    else:
        spectraframe.pack(
            side=tk.TOP,
            fill="both",
            anchor=tk.N,
            expand=True,
            padx=8,
            pady=[8, 8],
            ipadx=4,
            ipady=4,
        )


def toggleVitalsDisplayVisibility():
    if doDisplayVitals_var.get():
        vitalsframe.pack(
            side=tk.BOTTOM, anchor=tk.S, fill="x", expand=False, padx=8, pady=[4, 4]
        )
    else:
        vitalsframe.pack_forget()


def queryEditFields_clicked():
    if messagebox.askyesno(
        "Retrieve Info-Fields from Instrument?",
        "PLEASE BE AWARE: \nDue to an oversight in Bruker's OEM Protocol, retreiving the instrument's current info-fields will cause any 'Counter' fields to increment their value by 1 (this is only supposed to happen when an assay is started).\n\nAdditionally, the OEM Protocol does not provide a way to check if the fields are counters - only a way to set them as counters. \n\nFor these reasons, it is recommended to double check the field values and counter checkboxes are correct once retrieved. It is also reccommended to not regularly query the current field values if using counters as it will result in inconsistent incrementation. \n\nWould you like to proceed?",
    ):
        instrument_QueryEditFields()
    editinfo_windows[0].lift()


def queryXraySettings_clicked():
    sendCommand(xrf, '<Query parameter="XRay Settings"/>')


if __name__ == "__main__":
    # get args if any
    # lightweight mode defaults to false
    lightweight_mode_requested = False
    logFileName = ""
    if len(sys.argv) > 1:
        # print(f'Running S1Control with argument: {sys.argv[1]}')
        if sys.argv[1] in ["lightweight", "l", "L", "lite"]:
            lightweight_mode_requested = True

    # GUI
    thread_halt = False
    SERIALNUMBERRECV = False

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

    gui = ctk.CTk()
    # gui.bind("<Configure>", window_on_configure)
    gui.title("S1Control")
    gui.geometry("+5+5")
    printAndLog("asdasd")
    # print(f"scaling={ctk.ScalingTracker.get_window_scaling(gui)}")
    # # trying to scale ttk widgets properly with dpi changes in windows
    # if sys.platform.startswith("win"):
    #     ctypes.windll.shcore.SetProcessDpiAwareness(0)
    #     ctypes.windll.user32.SetProcessDPIAware()
    #     gui.tk.call("tk", "scaling", ctk.ScalingTracker.get_window_scaling(gui))

    # gui.geometry('1380x855')

    # APPEARANCE MODE DEFAULT AND STRVAR FOR TOGGLE - THESE TWO MUST MATCH ################################################################################
    ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
    # ctk.deactivate_automatic_dpi_awareness()
    enabledarkmode = tk.StringVar(value="light")
    # The default state of this variable must be changed to match the default setting of ctk appearancemode.

    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

    # Icons and Resources
    iconpath = resource_path("icons/pss_lb.ico")
    iconpath_linux = f'{resource_path("icons/pss_lb.png")}'
    iconphoto_linux = tk.PhotoImage(file=iconpath_linux)
    energiescsvpath = resource_path("energies.csv")
    # psslogo = ctk.CTkImage(
    #     light_image=Image.open(resource_path("pss-logo2-med.png")), size=(233, 96)
    # )
    psslogo = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/pss-logo2-med-b.png")),
        dark_image=Image.open(resource_path("icons/pss-logo2-med-w.png")),
        size=(233, 96),
    )

    icon_consecutive = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/repeat-2-b.png")),
        dark_image=Image.open(resource_path("icons/repeat-2-w.png")),
        size=(24, 24),
    )
    icon_startassay = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/play-fill.png")), size=(22, 22)
    )
    icon_stopassay = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/stop-fill.png")), size=(22, 22)
    )
    icon_identifypeak = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/crosshairpeak.png")), size=(22, 22)
    )
    icon_configureemissionlines = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/atom.png")), size=(22, 22)
    )
    icon_systemtime = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/clock.png")), size=(22, 22)
    )
    icon_apply = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/check.png")), size=(22, 22)
    )
    icon_applysmall = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/check.png")), size=(22, 22)
    )
    icon_s1version = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/binary.png")), size=(22, 22)
    )
    icon_temperature = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/temp-cold-line.png")), size=(22, 22)
    )
    icon_editinfo = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/pen-square.png")), size=(22, 22)
    )
    icon_getinfofields = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/list-restart.png")), size=(22, 22)
    )
    icon_resetinfofields = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/trash-2.png")), size=(22, 22)
    )
    icon_sensoron = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/sensor-fill.png")), size=(22, 22)
    )
    icon_sensoroff = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/sensor-line.png")), size=(22, 22)
    )
    icon_pressure = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/temp-hot-line.png")), size=(22, 22)
    )

    icon_softwaredev = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/code-2-b.png")),
        dark_image=Image.open(resource_path("icons/code-2-w.png")),
        size=(28, 28),
    )
    icon_plot_home = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/home.png")), size=(22, 22)
    )
    icon_plot_back = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/undo.png")), size=(22, 22)
    )
    icon_plot_forward = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/redo.png")), size=(22, 22)
    )
    icon_plot_saveimg = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/image-down.png")), size=(22, 22)
    )
    icon_plot_crop = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/crop.png")), size=(22, 22)
    )
    icon_plot_move = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/move.png")), size=(22, 22)
    )
    icon_plot_configure = ctk.CTkImage(
        light_image=Image.open(resource_path("icons/sliders-horizontal.png")),
        size=(22, 22),
    )
    # icon_sendinfofields = ctk.CTkImage(light_image=Image.open(resource_path("icons/install-fill.png")), size=(18, 18))
    # use correct method of setting window icon bitmap based on platform
    if sys.platform.startswith("win"):
        gui.iconbitmap(default=iconpath)
    else:
        gui.iconphoto(False, iconphoto_linux)
        # gui.call('wm', 'iconphoto', gui._w, iconpath_linux)

    # Fonts
    jbm24 = font.Font(family="JetBrains Mono", size=24)
    jbm20 = font.Font(family="JetBrains Mono", size=20)
    jbm18 = font.Font(family="JetBrains Mono", size=18)
    jbm18B = font.Font(family="JetBrains Mono", size=18, weight="bold")
    jbm16 = font.Font(family="JetBrains Mono", size=16)
    jbm13 = font.Font(family="JetBrains Mono", size=13)
    jbm12 = font.Font(family="JetBrains Mono", size=12)
    jbm10 = font.Font(family="JetBrains Mono", size=10)
    jbm10B = font.Font(family="JetBrains Mono", size=10, weight="bold")
    jbm09 = font.Font(family="JetBrains Mono", size=9)
    jbm09B = font.Font(family="JetBrains Mono", size=9, weight="bold")
    jbm08 = font.Font(family="JetBrains Mono", size=8)
    jbm08B = font.Font(family="JetBrains Mono", size=8, weight="bold")
    jbm07 = font.Font(family="JetBrains Mono", size=7)
    roboto09 = font.Font(family="Roboto", size=9)
    plotfont = {"fontname": "JetBrains Mono"}
    ctk_jbm08 = ctk.CTkFont(family="JetBrains Mono", size=8)
    ctk_jbm10 = ctk.CTkFont(family="JetBrains Mono", size=10)
    ctk_jbm11 = ctk.CTkFont(family="JetBrains Mono", size=11)
    ctk_jbm12 = ctk.CTkFont(family="JetBrains Mono", size=12)
    ctk_jbm12B = ctk.CTkFont(family="JetBrains Mono", size=12, weight="bold")
    ctk_jbm13 = ctk.CTkFont(family="JetBrains Mono", size=13)
    ctk_jbm14B = ctk.CTkFont(family="JetBrains Mono", size=14, weight="bold")
    ctk_jbm15B = ctk.CTkFont(family="JetBrains Mono", size=15, weight="bold")
    ctk_jbm18B = ctk.CTkFont(family="JetBrains Mono", size=18, weight="bold")
    ctk_jbm20B = ctk.CTkFont(family="JetBrains Mono", size=20, weight="bold")
    ctk_default_largeB = ctk.CTkFont(weight="bold")

    # Styles
    guiStyle = ttk.Style()
    guiStyle.theme_use("default")
    # Modify the font of the body
    guiStyle.configure("Treeview", highlightthickness=0, bd=0, font=jbm09)
    # Modify the font of the headings
    guiStyle.configure("Treeview.Heading", font=jbm09B)

    plotCTKColour = ("#dbdbdb", "#333333")  # ("#dbdbdb", "#4a4a4a")

    match ctk.get_appearance_mode():
        case "Dark":
            plottoolbarColour = "#333333"  # "#4a4a4a"
            treeviewColour_bg = "#333333"  # "#4a4a4a"
            plotbgColour = "#414141"
            plottextColour = WHITEISH
            plotgridColour = "#666666"

            guiStyle.configure(
                "Treeview",
                background="#3d3d3d",
                foreground=WHITEISH,
                rowheight=20,
                fieldbackground="#3d3d3d",
                bordercolor="#3d3d3d",
                borderwidth=0,
            )
            guiStyle.map("Treeview", background=[("selected", "#144870")])
            guiStyle.configure(
                "Treeview.Heading",
                background="#333333",
                foreground="white",
                relief="flat",
            )
            guiStyle.map("Treeview.Heading", background=[("active", "#1f6aa5")])

        case "Light":
            plottoolbarColour = "#dbdbdb"
            treeviewColour_bg = "#FFFFFF"
            plotbgColour = "#F5F5F5"
            plottextColour = CHARCOAL
            plotgridColour = "#DCDCDC"

            guiStyle.configure(
                "Treeview",
                background="#ebebeb",
                foreground=CHARCOAL,
                rowheight=20,
                fieldbackground="#ebebeb",
                bordercolor="#ebebeb",
                borderwidth=0,
            )
            guiStyle.map("Treeview", background=[("selected", "#36719f")])
            guiStyle.configure(
                "Treeview.Heading",
                background="#dbdbdb",
                foreground="black",
                relief="flat",
            )
            guiStyle.map("Treeview.Heading", background=[("active", "#3b8ed0")])
        case _:
            plottoolbarColour = "#dbdbdb"
            treeviewColour_bg = "#FFFFFF"
            plotbgColour = "#F5F5F5"
            plottextColour = CHARCOAL
            plotgridColour = "#DCDCDC"

            guiStyle.configure(
                "Treeview",
                background="#ebebeb",
                foreground=CHARCOAL,
                rowheight=20,
                fieldbackground="#ebebeb",
                bordercolor="#ebebeb",
                borderwidth=0,
            )
            guiStyle.map("Treeview", background=[("selected", "#36719f")])
            guiStyle.configure(
                "Treeview.Heading",
                background="#dbdbdb",
                foreground="black",
                relief="flat",
            )
            guiStyle.map("Treeview.Heading", background=[("active", "#3b8ed0")])

    instr_isarmed: bool = False
    instr_isloggedin: bool = False
    instr_assayisrunning: bool = False
    instr_assayrepeatsleft: int = 1
    instr_assayrepeatsselected: int = 1  # initial set
    instr_assayrepeatschosenforcurrentrun: int = 1
    instr_illuminations: list[Illumination] = []

    all_lines = [
        ["Be", "Be Kα", 0.108],
        ["B", "B Kα", 0.183],
        ["C", "C Kα", 0.277],
        ["N", "N Kα", 0.392],
        ["O", "O Kα", 0.525],
        ["F", "F Kα", 0.677],
        ["Ne", "Ne Kα", 0.849],
        ["Na", "Na Kα", 1.04],
        ["Mg", "Mg Kα", 1.254],
        ["Mg", "Mg Kβ", 1.302],
        ["Al", "Al Kα", 1.486],
        ["Al", "Al Kβ", 1.557],
        ["Si", "Si Kα", 1.74],
        ["Si", "Si Kβ", 1.837],
        ["P", "P Kα", 2.01],
        ["P", "P Kβ", 2.139],
        ["S", "S Kα", 2.309],
        ["S", "S Kβ", 2.465],
        ["Cl", "Cl Kα", 2.622],
        ["Cl", "Cl Kβ", 2.812],
        ["Ar", "Ar Kα", 2.958],
        ["Ar", "Ar Kβ", 3.19],
        ["K", "K Kα", 3.314],
        ["K", "K Kβ", 3.59],
        ["Ca", "Ca Kα", 3.692],
        ["Ca", "Ca Kβ", 4.013],
        ["Sc", "Sc Kα", 4.093],
        ["Sc", "Sc Kβ", 4.464],
        ["Ti", "Ti Kα", 4.512],
        ["Ti", "Ti Kβ", 4.933],
        ["Ti", "Ti Lβ", 0.458],
        ["Ti", "Ti Lα", 0.452],
        ["V", "V Kα", 4.953],
        ["V", "V Kβ", 5.428],
        ["V", "V Lβ", 0.518],
        ["V", "V Lα", 0.51],
        ["Cr", "Cr Kα", 5.415],
        ["Cr", "Cr Kβ", 5.947],
        ["Cr", "Cr Lβ", 0.582],
        ["Cr", "Cr Lα", 0.572],
        ["Mn", "Mn Kα", 5.9],
        ["Mn", "Mn Kβ", 6.492],
        ["Mn", "Mn Lβ", 0.648],
        ["Mn", "Mn Lα", 0.637],
        ["Fe", "Fe Kα", 6.405],
        ["Fe", "Fe Kβ", 7.059],
        ["Fe", "Fe Lβ", 0.718],
        ["Fe", "Fe Lα", 0.705],
        ["Co", "Co Kα", 6.931],
        ["Co", "Co Kβ", 7.649],
        ["Co", "Co Lβ", 0.79],
        ["Co", "Co Lα", 0.775],
        ["Ni", "Ni Kα", 7.48],
        ["Ni", "Ni Kβ", 8.267],
        ["Ni", "Ni Lβ", 0.866],
        ["Ni", "Ni Lα", 0.849],
        ["Cu", "Cu Kα", 8.046],
        ["Cu", "Cu Kβ", 8.904],
        ["Cu", "Cu Lβ", 0.947],
        ["Cu", "Cu Lα", 0.928],
        ["Zn", "Zn Kα", 8.637],
        ["Zn", "Zn Kβ", 9.57],
        ["Zn", "Zn Lβ", 1.035],
        ["Zn", "Zn Lα", 1.012],
        ["Ga", "Ga Kα", 9.251],
        ["Ga", "Ga Kβ", 10.267],
        ["Ga", "Ga Lβ", 1.125],
        ["Ga", "Ga Lα", 1.098],
        ["Ge", "Ge Kα", 9.886],
        ["Ge", "Ge Kβ", 10.982],
        ["Ge", "Ge Lβ", 1.218],
        ["Ge", "Ge Lα", 1.188],
        ["As", "As Kα", 10.543],
        ["As", "As Kβ", 11.726],
        ["As", "As Lβ", 1.317],
        ["As", "As Lα", 1.282],
        ["Se", "Se Kα", 11.224],
        ["Se", "Se Kβ", 12.497],
        ["Se", "Se Lβ", 1.419],
        ["Se", "Se Lα", 1.379],
        ["Br", "Br Kα", 11.924],
        ["Br", "Br Kβ", 13.292],
        ["Br", "Br Lβ", 1.526],
        ["Br", "Br Lα", 1.481],
        ["Kr", "Kr Kα", 12.648],
        ["Kr", "Kr Kβ", 14.112],
        ["Kr", "Kr Lβ", 1.636],
        ["Kr", "Kr Lα", 1.585],
        ["Rb", "Rb Kα", 13.396],
        ["Rb", "Rb Kβ", 14.961],
        ["Rb", "Rb Lβ", 1.751],
        ["Rb", "Rb Lα", 1.692],
        ["Sr", "Sr Kα", 14.165],
        ["Sr", "Sr Kβ", 15.835],
        ["Sr", "Sr Lβ", 1.871],
        ["Sr", "Sr Lα", 1.806],
        ["Y", "Y Kα", 14.958],
        ["Y", "Y Kβ", 16.739],
        ["Y", "Y Lβ", 1.998],
        ["Y", "Y Lα", 1.924],
        ["Zr", "Zr Kα", 15.775],
        ["Zr", "Zr Kβ", 17.668],
        ["Zr", "Zr Lβ", 2.126],
        ["Zr", "Zr Lα", 2.044],
        ["Nb", "Nb Kα", 16.615],
        ["Nb", "Nb Kβ", 18.625],
        ["Nb", "Nb Lβ", 2.26],
        ["Nb", "Nb Lα", 2.169],
        ["Mo", "Mo Kα", 17.48],
        ["Mo", "Mo Kβ", 19.606],
        ["Mo", "Mo Lβ", 2.394],
        ["Mo", "Mo Lα", 2.292],
        ["Tc", "Tc Kα", 18.367],
        ["Tc", "Tc Kβ", 20.626],
        ["Tc", "Tc Lβ", 2.535],
        ["Tc", "Tc Lα", 2.423],
        ["Ru", "Ru Kα", 19.279],
        ["Ru", "Ru Kβ", 21.655],
        ["Ru", "Ru Lβ", 2.683],
        ["Ru", "Ru Lα", 2.558],
        ["Rh", "Rh Kα", 20.216],
        ["Rh", "Rh Kβ", 22.724],
        ["Rh", "Rh Lβ", 2.834],
        ["Rh", "Rh Lα", 2.697],
        ["Pd", "Pd Kα", 21.177],
        ["Pd", "Pd Kβ", 23.818],
        ["Pd", "Pd Lβ", 2.99],
        ["Pd", "Pd Lα", 2.838],
        ["Ag", "Ag Kα", 22.163],
        ["Ag", "Ag Kβ", 24.941],
        ["Ag", "Ag Lβ", 3.15],
        ["Ag", "Ag Lα", 2.983],
        ["Cd", "Cd Kα", 23.173],
        ["Cd", "Cd Kβ", 26.093],
        ["Cd", "Cd Lβ", 3.315],
        ["Cd", "Cd Lα", 3.133],
        ["In", "In Kα", 24.21],
        ["In", "In Kβ", 27.275],
        ["In", "In Lβ", 3.487],
        ["In", "In Lα", 3.286],
        ["Sn", "Sn Kα", 25.271],
        ["Sn", "Sn Kβ", 28.485],
        ["Sn", "Sn Lβ", 3.663],
        ["Sn", "Sn Lα", 3.444],
        ["Sb", "Sb Kα", 26.359],
        ["Sb", "Sb Kβ", 29.725],
        ["Sb", "Sb Lβ", 3.842],
        ["Sb", "Sb Lα", 3.604],
        ["Te", "Te Kα", 27.473],
        ["Te", "Te Kβ", 30.993],
        ["Te", "Te Lβ", 4.029],
        ["Te", "Te Lα", 3.768],
        ["I", "I Kα", 28.612],
        ["I", "I Kβ", 32.294],
        ["I", "I Lβ", 4.221],
        ["I", "I Lα", 3.938],
        ["Xe", "Xe Kα", 29.775],
        ["Xe", "Xe Kβ", 33.62],
        ["Xe", "Xe Lβ", 4.418],
        ["Xe", "Xe Lα", 4.11],
        ["Cs", "Cs Kα", 30.973],
        ["Cs", "Cs Kβ", 34.982],
        ["Cs", "Cs Lβ", 4.619],
        ["Cs", "Cs Lα", 4.285],
        ["Ba", "Ba Kα", 32.194],
        ["Ba", "Ba Kβ", 36.378],
        ["Ba", "Ba Lβ", 4.828],
        ["Ba", "Ba Lα", 4.466],
        ["La", "La Kα", 33.442],
        ["La", "La Kβ", 37.797],
        ["La", "La Lβ", 5.038],
        ["La", "La Lα", 4.647],
        ["Ce", "Ce Kα", 34.72],
        ["Ce", "Ce Kβ", 39.256],
        ["Ce", "Ce Lβ", 5.262],
        ["Ce", "Ce Lα", 4.839],
        ["Pr", "Pr Kα", 36.027],
        ["Pr", "Pr Kβ", 40.749],
        ["Pr", "Pr Lβ", 5.492],
        ["Pr", "Pr Lα", 5.035],
        ["Nd", "Nd Kα", 37.361],
        ["Nd", "Nd Kβ", 42.272],
        ["Nd", "Nd Lβ", 5.719],
        ["Nd", "Nd Lα", 5.228],
        ["Pm", "Pm Kα", 38.725],
        ["Pm", "Pm Kβ", 43.827],
        ["Pm", "Pm Lβ", 5.961],
        ["Pm", "Pm Lα", 5.432],
        ["Sm", "Sm Kα", 40.118],
        ["Sm", "Sm Kβ", 45.414],
        ["Sm", "Sm Lβ", 6.201],
        ["Sm", "Sm Lα", 5.633],
        ["Eu", "Eu Kα", 41.542],
        ["Eu", "Eu Kβ", 47.038],
        ["Eu", "Eu Lβ", 6.458],
        ["Eu", "Eu Lα", 5.849],
        ["Gd", "Gd Kα", 42.996],
        ["Gd", "Gd Kβ", 48.695],
        ["Gd", "Gd Lβ", 6.708],
        ["Gd", "Gd Lα", 6.053],
        ["Tb", "Tb Kα", 44.482],
        ["Tb", "Tb Kβ", 50.385],
        ["Tb", "Tb Lβ", 6.975],
        ["Tb", "Tb Lα", 6.273],
        ["Dy", "Dy Kα", 45.999],
        ["Dy", "Dy Kβ", 52.113],
        ["Dy", "Dy Lβ", 7.248],
        ["Dy", "Dy Lα", 6.498],
        ["Ho", "Ho Kα", 47.547],
        ["Ho", "Ho Kβ", 53.877],
        ["Ho", "Ho Lβ", 7.526],
        ["Ho", "Ho Lα", 6.72],
        ["Er", "Er Kα", 49.128],
        ["Er", "Er Kβ", 55.674],
        ["Er", "Er Lβ", 7.811],
        ["Er", "Er Lα", 6.949],
        ["Tm", "Tm Kα", 50.742],
        ["Tm", "Tm Kβ", 57.505],
        ["Tm", "Tm Lβ", 8.102],
        ["Tm", "Tm Lα", 7.18],
        ["Yb", "Yb Kα", 52.388],
        ["Yb", "Yb Kβ", 59.382],
        ["Yb", "Yb Lβ", 8.402],
        ["Yb", "Yb Lα", 7.416],
        ["Lu", "Lu Kα", 54.07],
        ["Lu", "Lu Kβ", 61.29],
        ["Lu", "Lu Lβ", 8.71],
        ["Lu", "Lu Lα", 7.655],
        ["Hf", "Hf Kα", 55.79],
        ["Hf", "Hf Kβ", 63.244],
        ["Hf", "Hf Lβ", 9.023],
        ["Hf", "Hf Lα", 7.899],
        ["Ta", "Ta Kα", 57.535],
        ["Ta", "Ta Kβ", 65.222],
        ["Ta", "Ta Lβ", 9.343],
        ["Ta", "Ta Lα", 8.146],
        ["W", "W Kα", 59.318],
        ["W", "W Kβ", 67.244],
        ["W", "W Lβ", 9.672],
        ["W", "W Lα", 8.398],
        ["Re", "Re Kα", 61.141],
        ["Re", "Re Kβ", 69.309],
        ["Re", "Re Lβ", 10.01],
        ["Re", "Re Lα", 8.652],
        ["Os", "Os Kα", 63.0],
        ["Os", "Os Kβ", 71.414],
        ["Os", "Os Lβ", 10.354],
        ["Os", "Os Lα", 8.911],
        ["Ir", "Ir Kα", 64.896],
        ["Ir", "Ir Kβ", 73.56],
        ["Ir", "Ir Lβ", 10.708],
        ["Ir", "Ir Lα", 9.175],
        ["Pt", "Pt Kα", 66.831],
        ["Pt", "Pt Kβ", 75.75],
        ["Pt", "Pt Lβ", 11.071],
        ["Pt", "Pt Lα", 9.442],
        ["Au", "Au Kα", 68.806],
        ["Au", "Au Kβ", 77.982],
        ["Au", "Au Lβ", 11.443],
        ["Au", "Au Lα", 9.713],
        ["Hg", "Hg Kα", 70.818],
        ["Hg", "Hg Kβ", 80.255],
        ["Hg", "Hg Lβ", 11.824],
        ["Hg", "Hg Lα", 9.989],
        ["Tl", "Tl Kα", 72.872],
        ["Tl", "Tl Kβ", 82.573],
        ["Tl", "Tl Lβ", 12.213],
        ["Tl", "Tl Lα", 10.269],
        ["Pb", "Pb Kα", 74.97],
        ["Pb", "Pb Kβ", 84.939],
        ["Pb", "Pb Lβ", 12.614],
        ["Pb", "Pb Lα", 10.551],
        ["Bi", "Bi Kα", 77.107],
        ["Bi", "Bi Kβ", 87.349],
        ["Bi", "Bi Lβ", 13.023],
        ["Bi", "Bi Lα", 10.839],
        ["Po", "Po Kα", 79.291],
        ["Po", "Po Kβ", 89.803],
        ["Po", "Po Lβ", 13.446],
        ["Po", "Po Lα", 11.131],
        ["At", "At Kα", 81.516],
        ["At", "At Kβ", 92.304],
        ["At", "At Lβ", 13.876],
        ["At", "At Lα", 11.427],
        ["Rn", "Rn Kα", 83.785],
        ["Rn", "Rn Kβ", 94.866],
        ["Rn", "Rn Lβ", 14.315],
        ["Rn", "Rn Lα", 11.727],
        ["Fr", "Fr Kα", 86.106],
        ["Fr", "Fr Kβ", 97.474],
        ["Fr", "Fr Lβ", 14.771],
        ["Fr", "Fr Lα", 12.031],
        ["Ra", "Ra Kα", 88.478],
        ["Ra", "Ra Kβ", 100.13],
        ["Ra", "Ra Lβ", 15.236],
        ["Ra", "Ra Lα", 12.339],
        ["Ac", "Ac Kα", 90.884],
        ["Ac", "Ac Kβ", 102.846],
        ["Ac", "Ac Lβ", 15.713],
        ["Ac", "Ac Lα", 12.652],
        ["Th", "Th Kα", 93.351],
        ["Th", "Th Kβ", 105.605],
        ["Th", "Th Lβ", 16.202],
        ["Th", "Th Lα", 12.968],
        ["Pa", "Pa Kα", 95.868],
        ["Pa", "Pa Kβ", 108.427],
        ["Pa", "Pa Lβ", 16.703],
        ["Pa", "Pa Lα", 13.291],
        ["U", "U Kα", 98.44],
        ["U", "U Kβ", 111.303],
        ["U", "U Lβ", 17.22],
        ["U", "U Lα", 13.614],
        ["Np", "Np Kα", 101.059],
        ["Np", "Np Kβ", 114.234],
        ["Np", "Np Lβ", 17.751],
        ["Np", "Np Lα", 13.946],
        ["Pu", "Pu Kα", 103.734],
        ["Pu", "Pu Kβ", 117.228],
        ["Pu", "Pu Lβ", 18.296],
        ["Pu", "Pu Lα", 14.282],
        ["Am", "Am Kα", 106.472],
        ["Am", "Am Kβ", 120.284],
        ["Am", "Am Lβ", 18.856],
        ["Am", "Am Lα", 14.62],
        ["Cm", "Cm Kα", 109.271],
        ["Cm", "Cm Kβ", 123.403],
        ["Cm", "Cm Lβ", 19.427],
        ["Cm", "Cm Lα", 14.961],
        ["Bk", "Bk Kα", 112.121],
        ["Bk", "Bk Kβ", 126.58],
        ["Bk", "Bk Lβ", 20.018],
        ["Bk", "Bk Lα", 15.308],
        ["Cf", "Cf Kα", 115.032],
        ["Cf", "Cf Kβ", 129.823],
        ["Cf", "Cf Lβ", 20.624],
        ["Cf", "Cf Lα", 15.66],
    ]
    emissionLineElementButtonIDs = []
    emissionLinesElementslist = []
    linecfg_firsttime = True
    editinfo_firsttime = True
    linecfgwindows = []
    editinfo_windows = []
    editinfo_fieldnames = (
        []
    )  # Stores entrybox strvar objects for editinfo window field names for ref elsewhere
    editinfo_fieldvalues = (
        []
    )  # Stores entrybox strvar objects for editinfo window field vals for ref elsewhere
    editinfo_fieldcounters = (
        []
    )  # Stores checkbox boolvar objects for editinfo window counter checkbox for ref elsewhere
    editinfo_validcounterfieldsused = False

    phasetimelabels = []
    phasetimeentries = []
    phasetime1_stringvar = ctk.StringVar()
    phasetime2_stringvar = ctk.StringVar()
    phasetime3_stringvar = ctk.StringVar()
    phasename1_stringvar = ctk.StringVar()
    phasename2_stringvar = ctk.StringVar()
    phasename3_stringvar = ctk.StringVar()

    field1_name_strvar = ctk.StringVar()
    field2_name_strvar = ctk.StringVar()
    field3_name_strvar = ctk.StringVar()
    field4_name_strvar = ctk.StringVar()
    field5_name_strvar = ctk.StringVar()
    field6_name_strvar = ctk.StringVar()

    field1_val_strvar = ctk.StringVar()
    field2_val_strvar = ctk.StringVar()
    field3_val_strvar = ctk.StringVar()
    field4_val_strvar = ctk.StringVar()
    field5_val_strvar = ctk.StringVar()
    field6_val_strvar = ctk.StringVar()

    field1_iscounter_boolvar = ctk.BooleanVar()
    field2_iscounter_boolvar = ctk.BooleanVar()
    field3_iscounter_boolvar = ctk.BooleanVar()
    field4_iscounter_boolvar = ctk.BooleanVar()
    field5_iscounter_boolvar = ctk.BooleanVar()
    field6_iscounter_boolvar = ctk.BooleanVar()

    ui_firsttime = 1

    energiesfirsttime = True

    emission_lines_to_plot = []
    extraticks = []
    extraticklabels = []

    total_spec_channels = 2048
    spec_channels = np.array(list(range(0, total_spec_channels)))

    # plotphasecolours = ['blue', 'green', 'pink', 'orange', 'purple', 'pink', 'yellow']
    plotphasecolours = [
        "#5BB5F1",
        "#53bf47",
        "#F15BB5",
        "#f58700",
        "#9B5DE5",
        "#de1b2e",
        "#f5d000",
        "#143fc7",
        "#1b401e",
        "#c10f5d",
        "#00bf7f",
        "#6295a6",
        "#964726",
    ]
    plottedspectra = []
    plottedemissionlineslist = []
    assay_catalogue = []
    assay_catalogue_num = 1

    spectra = []
    specenergies = []
    instr_currentassayspectra = []
    instr_currentassayspecenergies = []
    instr_currentassaylegends = []
    # instr_currentassayresults =
    instr_currentambtemp = ""
    instr_currentdettemp = ""
    instr_serialnumber = "UNKNOWN"

    # CONNECTION DETAILS FOR TCP/IP VIA USB (Recommended)
    XRF_IP_USB = "192.168.137.139"
    XRF_PORT_USB = 55204  # 55204

    # CONNECTION STUFF FOR GeRDA CNC
    gerdaCNC: GerdaCNCController = None
    gerda_sample_list = None

    # CONNECTION DETAILS FOR WIFI  (Not Recommended - Also, DHCP will cause IP to change. Port may change as well?) Wifi is unreliable and prone to massive packet loss and delayed commands/info transmit.
    XRF_IP_WIFI = "192.168.153.167"  # '192.168.153.167:55101' found to work for ruffo when on phone hotspot network. both values may change depending on network settings?
    XRF_PORT_WIFI = 55101

    XRF_IP_USB_ALTERNATE = "190.168.137.139"  # In some VERY UNUSUAL cases, I have seen instuments come back from Bruker servicing with this IP changed to 190 instead of 192. Worth checking if it breaks.

    xrf = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # BRUKER API COMMANDS to be used with sendCommand
    bruker_query_loginstate = '<Query parameter="Login State"/>'
    bruker_query_armedstate = '<Query parameter="Armed State"/>'
    bruker_query_instdef = '<Query parameter="Instrument Definition"/>'
    bruker_query_allapplications = '<Query parameter="Applications"/>'
    bruker_query_currentapplicationinclmethods = (
        '<Query parameter="ActiveApplication">Include Methods</Query>'
    )
    bruker_query_methodsforcurrentapplication = '<Query parameter="Method"></Query>'
    bruker_query_currentapplicationprefs = (
        '<Query parameter="User Preferences"></Query>'
    )
    # UAP - incl everything
    bruker_query_currentapplicationphasetimes = '<Query parameter="Phase Times"/>'
    bruker_query_softwareversion = '<Query parameter="Version"/>'
    # S1 version, eg 2.7.58.392
    bruker_query_nosetemp = '<Query parameter="Nose Temperature"/>'
    bruker_query_nosepressure = '<Query parameter="Nose Pressure"/>'
    bruker_query_editfields = '<Query parameter="Edit Fields"/>'
    bruker_query_proximityrequired = '<Query parameter="Proximity Required"/>'
    bruker_query_storeresults = '<Query parameter="Store Results"/>'
    bruker_query_storespectra = '<Query parameter="Store Spectra"/>'

    bruker_configure_transmitstatusenable = '<Configure parameter="Transmit Statusmsg">Yes</Configure>'  # Enable transmission of trigger pull/release and assay start/stop status messages
    bruker_configure_transmitelementalresultsenable = '<Configure parameter="Transmit Results" grades="Yes" elements="Yes">Yes</Configure>'  # Enable transmission of elemental results, disables transmission of grade ID / passfail results
    bruker_configure_transmitspectraenable = (
        '<Configure parameter="Transmit Spectra">Yes</Configure>'
    )
    bruker_configure_transmitspectradisable = (
        '<Configure parameter="Transmit Spectra">No</Configure>'
    )
    bruker_configure_transmitstatusmessagesenable = (
        '<Configure parameter="Transmit Statusmsg">Yes</Configure>'
    )
    bruker_configure_proximityenable = (
        '<Configure parameter="Proximity Required">Yes</Configure>'
    )
    bruker_configure_proximitydisable = (
        '<Configure parameter="Proximity Required">No</Configure>'
    )
    bruker_configure_storeresultsenable = (
        '<Configure parameter="Store Results">Yes</Configure>'
    )
    bruker_configure_storeresultsdisable = (
        '<Configure parameter="Store Results">No</Configure>'
    )
    bruker_configure_storespectraenable = (
        '<Configure parameter="Store Spectra">Yes</Configure>'
    )
    bruker_configure_storespectradisable = (
        '<Configure parameter="Store Spectra">No</Configure>'
    )
    bruker_configure_resetinfofields = (
        '<Configure parameter="Edit Fields">Reset</Configure>'
    )

    bruker_command_login = "<Command>Login</Command>"
    bruker_command_assaystart = '<Command parameter="Assay">Start</Command>'
    bruker_command_assaystop = '<Command parameter="Assay">Stop</Command>'

    instr_currentphase = 0
    assay_phase_spectrumpacketcounter = 0
    instr_currentphaselength_s = 0
    instr_approxsingleassaytime = 0

    # set mpl log level to prevent console spam about missing fonts
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    driveFolderStr = ""
    s1vermanuallyrequested = False

    # Consts for datatypes on recv
    COOKED_SPECTRUM = "1"
    RESULTS_SET = "2"
    RAW_SPECTRUM = "3"
    PDZ_FILENAME = "4"
    XML_PACKET = "5"
    XML_SUCCESS_RESPONSE = "5a"
    XML_APPS_PRESENT_RESPONSE = "5b"
    XML_ACTIVE_APP_RESPONSE = "5c"
    STATUS_CHANGE = "6"
    SPECTRUM_ENERGY_PACKET = "7"
    UNKNOWN_DATA = "0"

    # COLOURS FOR ELEMENT GROUPS
    ALKALI_METALS = "#FC8B12"  #'goldenrod1'
    ALKALINE_EARTH_METALS = "#FAA23E"  #'DarkOrange1'
    TRANSITION_METALS = "#0084FF"  #'RoyalBlue1'
    OTHER_METALS = "#5F8DFF"  #'SteelBlue1'487BFA
    METALLOIDS = "#9778FE"  #'light slate gray'
    NON_METALS = "#FD81FF"  #'light goldenrod'
    HALOGENS = "#FF3CD0"  #'plum1'
    NOBLE_GASES = "#972EB4"  #'MediumOrchid1'
    LANTHANIDES = "#e84f51"  #'firebrick1'
    ACTINIDES = "#1BCA66"  #'spring green'

    # ELEMENT LIST FOR BUTTONS - FORMAT IS (ATOMIC NUMBER, SYMBOL, NAME, PERIODIC TABLE ROW, PERIODIC TABLE COLUMN, CLASS for bg colour)
    element_info = [
        (1, "H", "Hydrogen", 1, 1, NON_METALS),
        (2, "He", "Helium", 1, 18, NOBLE_GASES),
        (3, "Li", "Lithium", 2, 1, ALKALI_METALS),
        (4, "Be", "Beryllium", 2, 2, ALKALINE_EARTH_METALS),
        (5, "B", "Boron", 2, 13, METALLOIDS),
        (6, "C", "Carbon", 2, 14, NON_METALS),
        (7, "N", "Nitrogen", 2, 15, NON_METALS),
        (8, "O", "Oxygen", 2, 16, NON_METALS),
        (9, "F", "Fluorine", 2, 17, HALOGENS),
        (10, "Ne", "Neon", 2, 18, NOBLE_GASES),
        (11, "Na", "Sodium", 3, 1, ALKALI_METALS),
        (12, "Mg", "Magnesium", 3, 2, ALKALINE_EARTH_METALS),
        (13, "Al", "Aluminium", 3, 13, OTHER_METALS),
        (14, "Si", "Silicon", 3, 14, METALLOIDS),
        (15, "P", "Phosphorus", 3, 15, NON_METALS),
        (16, "S", "Sulfur", 3, 16, NON_METALS),
        (17, "Cl", "Chlorine", 3, 17, HALOGENS),
        (18, "Ar", "Argon", 3, 18, NOBLE_GASES),
        (19, "K", "Potassium", 4, 1, ALKALI_METALS),
        (20, "Ca", "Calcium", 4, 2, ALKALINE_EARTH_METALS),
        (21, "Sc", "Scandium", 4, 3, TRANSITION_METALS),
        (22, "Ti", "Titanium", 4, 4, TRANSITION_METALS),
        (23, "V", "Vanadium", 4, 5, TRANSITION_METALS),
        (24, "Cr", "Chromium", 4, 6, TRANSITION_METALS),
        (25, "Mn", "Manganese", 4, 7, TRANSITION_METALS),
        (26, "Fe", "Iron", 4, 8, TRANSITION_METALS),
        (27, "Co", "Cobalt", 4, 9, TRANSITION_METALS),
        (28, "Ni", "Nickel", 4, 10, TRANSITION_METALS),
        (29, "Cu", "Copper", 4, 11, TRANSITION_METALS),
        (30, "Zn", "Zinc", 4, 12, TRANSITION_METALS),
        (31, "Ga", "Gallium", 4, 13, OTHER_METALS),
        (32, "Ge", "Germanium", 4, 14, METALLOIDS),
        (33, "As", "Arsenic", 4, 15, METALLOIDS),
        (34, "Se", "Selenium", 4, 16, NON_METALS),
        (35, "Br", "Bromine", 4, 17, HALOGENS),
        (36, "Kr", "Krypton", 4, 18, NOBLE_GASES),
        (37, "Rb", "Rubidium", 5, 1, ALKALI_METALS),
        (38, "Sr", "Strontium", 5, 2, ALKALINE_EARTH_METALS),
        (39, "Y", "Yttrium", 5, 3, TRANSITION_METALS),
        (40, "Zr", "Zirconium", 5, 4, TRANSITION_METALS),
        (41, "Nb", "Niobium", 5, 5, TRANSITION_METALS),
        (42, "Mo", "Molybdenum", 5, 6, TRANSITION_METALS),
        (43, "Tc", "Technetium", 5, 7, TRANSITION_METALS),
        (44, "Ru", "Ruthenium", 5, 8, TRANSITION_METALS),
        (45, "Rh", "Rhodium", 5, 9, TRANSITION_METALS),
        (46, "Pd", "Palladium", 5, 10, TRANSITION_METALS),
        (47, "Ag", "Silver", 5, 11, TRANSITION_METALS),
        (48, "Cd", "Cadmium", 5, 12, TRANSITION_METALS),
        (49, "In", "Indium", 5, 13, OTHER_METALS),
        (50, "Sn", "Tin", 5, 14, OTHER_METALS),
        (51, "Sb", "Antimony", 5, 15, METALLOIDS),
        (52, "Te", "Tellurium", 5, 16, METALLOIDS),
        (53, "I", "Iodine", 5, 17, HALOGENS),
        (54, "Xe", "Xenon", 5, 18, NOBLE_GASES),
        (55, "Cs", "Caesium", 6, 1, ALKALI_METALS),
        (56, "Ba", "Barium", 6, 2, ALKALINE_EARTH_METALS),
        (57, "La", "Lanthanum", 6, 3, LANTHANIDES),
        (58, "Ce", "Cerium", 9, 4, LANTHANIDES),
        (59, "Pr", "Praseodymium", 9, 5, LANTHANIDES),
        (60, "Nd", "Neodymium", 9, 6, LANTHANIDES),
        (61, "Pm", "Promethium", 9, 7, LANTHANIDES),
        (62, "Sm", "Samarium", 9, 8, LANTHANIDES),
        (63, "Eu", "Europium", 9, 9, LANTHANIDES),
        (64, "Gd", "Gadolinium", 9, 10, LANTHANIDES),
        (65, "Tb", "Terbium", 9, 11, LANTHANIDES),
        (66, "Dy", "Dysprosium", 9, 12, LANTHANIDES),
        (67, "Ho", "Holmium", 9, 13, LANTHANIDES),
        (68, "Er", "Erbium", 9, 14, LANTHANIDES),
        (69, "Tm", "Thulium", 9, 15, LANTHANIDES),
        (70, "Yb", "Ytterbium", 9, 16, LANTHANIDES),
        (71, "Lu", "Lutetium", 9, 17, LANTHANIDES),
        (72, "Hf", "Hafnium", 6, 4, TRANSITION_METALS),
        (73, "Ta", "Tantalum", 6, 5, TRANSITION_METALS),
        (74, "W", "Tungsten", 6, 6, TRANSITION_METALS),
        (75, "Re", "Rhenium", 6, 7, TRANSITION_METALS),
        (76, "Os", "Osmium", 6, 8, TRANSITION_METALS),
        (77, "Ir", "Iridium", 6, 9, TRANSITION_METALS),
        (78, "Pt", "Platinum", 6, 10, TRANSITION_METALS),
        (79, "Au", "Gold", 6, 11, TRANSITION_METALS),
        (80, "Hg", "Mercury", 6, 12, TRANSITION_METALS),
        (81, "Tl", "Thallium", 6, 13, OTHER_METALS),
        (82, "Pb", "Lead", 6, 14, OTHER_METALS),
        (83, "Bi", "Bismuth", 6, 15, OTHER_METALS),
        (84, "Po", "Polonium", 6, 16, METALLOIDS),
        (85, "At", "Astatine", 6, 17, HALOGENS),
        (86, "Rn", "Radon", 6, 18, NOBLE_GASES),
        (87, "Fr", "Francium", 7, 1, ALKALI_METALS),
        (88, "Ra", "Radium", 7, 2, ALKALINE_EARTH_METALS),
        (89, "Ac", "Actinium", 7, 3, ACTINIDES),
        (90, "Th", "Thorium", 10, 4, ACTINIDES),
        (91, "Pa", "Protactinium", 10, 5, ACTINIDES),
        (92, "U", "Uranium", 10, 6, ACTINIDES),
        (93, "Np", "Neptunium", 10, 7, ACTINIDES),
        (94, "Pu", "Plutonium", 10, 8, ACTINIDES),
        (95, "Am", "Americium", 10, 9, ACTINIDES),
        (96, "Cm", "Curium", 10, 10, ACTINIDES),
        (97, "Bk", "Berkelium", 10, 11, ACTINIDES),
        (98, "Cf", "Californium", 10, 12, ACTINIDES),
        (99, "Es", "Einsteinium", 10, 13, ACTINIDES),
        (100, "Fm", "Fermium", 10, 14, ACTINIDES),
        (101, "Md", "Mendelevium", 10, 15, ACTINIDES),
        (102, "No", "Nobelium", 10, 16, ACTINIDES),
        (103, "Lr", "Lawrencium", 10, 17, ACTINIDES),
        (104, "Rf", "Rutherfordium", 7, 4, TRANSITION_METALS),
        (105, "Db", "Dubnium", 7, 5, TRANSITION_METALS),
        (106, "Sg", "Seaborgium", 7, 6, TRANSITION_METALS),
        (107, "Bh", "Bohrium", 7, 7, TRANSITION_METALS),
        (108, "Hs", "Hassium", 7, 8, TRANSITION_METALS),
        (109, "Mt", "Meitnerium", 7, 9, TRANSITION_METALS),
        (110, "Ds", "Darmstadtium", 7, 10, TRANSITION_METALS),
        (111, "Rg", "Roentgenium", 7, 11, TRANSITION_METALS),
        (112, "Cn", "Copernicium", 7, 12, TRANSITION_METALS),
        (113, "Nh", "Nihonium", 7, 13, OTHER_METALS),
        (114, "Fl", "Flerovium", 7, 14, OTHER_METALS),
        (115, "Mc", "Moscovium", 7, 15, OTHER_METALS),
        (116, "Lv", "Livermorium", 7, 16, OTHER_METALS),
        (117, "Ts", "Tennessine", 7, 17, HALOGENS),
        (118, "Og", "Oganesson", 7, 18, NOBLE_GASES),
    ]

    # TESTING, REMOVE THIS FOR SPEED PROBABLY
    # global element_colour_dict
    # element_colour_dict = {}
    # for e in element_info:
    #     element_colour_dict[e[1]]=e[5]

    # print(element_colour_dict)

    # Default DF to use in case no results provided.
    default_assay_results_df = pd.DataFrame.from_dict(
        {"Z": [0], "Compound": ["No Results"], "Concentration": [0], "Error(1SD)": [0]}
    )

    current_session_results_df = pd.DataFrame()

    # Frames
    LHSframe = ctk.CTkFrame(gui, width=340, corner_radius=0)
    LHSframe.pack(
        side=tk.LEFT, anchor=tk.W, fill="y", expand=False, padx=0, pady=0, ipadx=0
    )

    RHSframe = ctk.CTkFrame(gui, corner_radius=0, fg_color="transparent")
    RHSframe.pack(
        side=tk.RIGHT, anchor=tk.W, fill="both", expand=True, padx=0, pady=0, ipadx=0
    )

    spectraframe = ctk.CTkFrame(
        RHSframe, width=700, height=50, corner_radius=5, fg_color=plotCTKColour
    )
    spectraframe.pack(
        side=tk.TOP,
        fill="both",
        anchor=tk.N,
        expand=True,
        padx=8,
        pady=[8, 8],
        ipadx=4,
        ipady=4,
    )

    resultsframe = ctk.CTkFrame(
        RHSframe, width=700, height=300, fg_color=("#dbdbdb", "#333333")
    )
    resultsframe.pack(
        side=tk.BOTTOM,
        fill="both",
        anchor=tk.SW,
        expand=True,
        padx=8,
        pady=[0, 8],
        ipadx=4,
        ipady=4,
    )

    assaytableframe = tk.Frame(resultsframe, width=600, height=300)  # 450
    assaytableframe.pack(
        side=tk.LEFT,
        fill="both",
        anchor=tk.SW,
        expand=True,
        padx=[8, 0],
        pady=8,
        ipadx=0,
        ipady=0,
    )
    assaytableframe.pack_propagate(0)

    # Status Frame stuff

    statusframe = ctk.CTkFrame(LHSframe, width=50, height=30, corner_radius=5)
    statusframe.pack(
        side=tk.BOTTOM, anchor=tk.S, fill="x", expand=False, padx=8, pady=[4, 8]
    )
    # Status text display warningxrays/ready/not armed etc
    instr_DANGER_stringvar = tk.StringVar()
    status_label = ctk.CTkLabel(
        statusframe, textvariable=instr_DANGER_stringvar, font=ctk_jbm18B
    )
    status_label.pack(
        side=tk.TOP, fill="both", anchor=tk.N, expand=True, padx=2, pady=2
    )

    # vitals - Count rate and dead time widget stuff

    vitalsframe = ctk.CTkFrame(LHSframe, width=50, height=30, corner_radius=5)
    vitalsframe.pack(
        side=tk.BOTTOM, anchor=tk.S, fill="x", expand=False, padx=8, pady=[4, 4]
    )

    instr_countrate_stringvar = tk.StringVar(value="0cps")
    instr_deadtime_stringvar = tk.StringVar(value="0%dead")
    instr_tubevoltagecurrent_stringvar = tk.StringVar(value="0kV / 0\u03bcA")
    countrate_label = ctk.CTkLabel(
        vitalsframe, textvariable=instr_countrate_stringvar, font=ctk_jbm12B
    )
    countrate_label.pack(
        side=tk.RIGHT, fill="both", anchor=tk.N, expand=True, padx=2, pady=2
    )
    deadtime_label = ctk.CTkLabel(
        vitalsframe, textvariable=instr_deadtime_stringvar, font=ctk_jbm12B
    )
    deadtime_label.pack(
        side=tk.RIGHT, fill="both", anchor=tk.N, expand=True, padx=2, pady=2
    )
    voltagecurrent_label = ctk.CTkLabel(
        vitalsframe, textvariable=instr_tubevoltagecurrent_stringvar, font=ctk_jbm12B
    )
    voltagecurrent_label.pack(
        side=tk.LEFT, fill="both", anchor=tk.N, expand=True, padx=2, pady=2
    )

    # loading bar stuff
    xraysonbar = ctk.CTkProgressBar(LHSframe, width=50, mode="indeterminate")
    xraysonbar.pack(
        side=tk.BOTTOM, anchor=tk.S, fill="x", expand=False, padx=8, pady=[4, 4]
    )

    assayprogressbar = ctk.CTkProgressBar(LHSframe, width=50, mode="determinate")
    assayprogressbar.pack(
        side=tk.BOTTOM, anchor=tk.S, fill="x", expand=False, padx=8, pady=[8, 4]
    )
    assayprogressbar.set(0)

    # Tabview for controls LHS
    ctrltabview = ctk.CTkTabview(LHSframe, height=320)
    # was height=358
    ctrltabview.pack(
        side=tk.TOP, anchor=tk.N, fill="x", expand=False, padx=8, pady=[0, 4]
    )
    ctrltabview._segmented_button.configure(font=ctk_jbm12)
    ctrltabview.add("Assay Controls")
    ctrltabview.add("Instrument")
    ctrltabview.add("Options")
    ctrltabview.add("GeRDA")
    ctrltabview.add("About")
    ctrltabview.tab("Assay Controls").grid_columnconfigure(0, weight=1)
    ctrltabview.tab("Instrument").grid_columnconfigure(0, weight=1)
    ctrltabview.tab("Options").grid_columnconfigure(1, weight=1)
    ctrltabview.tab("About").grid_columnconfigure(0, weight=1)

    appmethodframe = ctk.CTkFrame(
        ctrltabview.tab("Assay Controls"), fg_color=("#c5c5c5", "#444444")
    )
    appmethodframe.grid(
        row=2, column=0, columnspan=3, rowspan=2, padx=4, pady=4, sticky=tk.NSEW
    )

    phaseframe = ctk.CTkFrame(
        ctrltabview.tab("Assay Controls"), fg_color=("#c5c5c5", "#444444")
    )
    phaseframe.grid(
        row=4, column=0, columnspan=3, rowspan=2, padx=4, pady=4, sticky=tk.NSEW
    )

    customspectrumconfigframe = ctk.CTkFrame(
        ctrltabview.tab("Assay Controls"), fg_color=("#c5c5c5", "#444444")
    )
    customspectrumconfigframe.grid(
        row=6, column=0, columnspan=3, rowspan=2, padx=4, pady=4, sticky=tk.NSEW
    )
    customspectrumconfigframe.columnconfigure(1, weight=1)

    # custom spectrum config frame stuff

    customspectrum_illumination_dropdown = ctk.CTkOptionMenu(
        customspectrumconfigframe,
        width=210,
        values=[""],
        command=customSpectrumIlluminationChosen,
        dynamic_resizing=True,
        font=ctk_jbm12B,
        dropdown_font=ctk_jbm12,
    )
    customspectrum_illumination_dropdown.grid(
        row=0, column=0, columnspan=3, padx=[4, 4], pady=4, sticky=tk.EW
    )
    customspectrum_illumination_dropdown.set("Illuminations")

    customspectrum_voltage_label = ctk.CTkLabel(
        customspectrumconfigframe,
        text="Voltage",
        anchor="w",
        font=ctk_jbm12,
    )

    customspectrum_voltage_entry = ctk.CTkEntry(
        customspectrumconfigframe,
        width=40,
        justify="right",
        border_width=1,
        font=ctk_jbm12,
    )

    customspectrum_voltage_units = ctk.CTkLabel(
        customspectrumconfigframe, width=2, text="kV", anchor="w", font=ctk_jbm12
    )
    customspectrum_voltage_entry.insert(0, "50")

    customspectrum_voltage_label.grid(
        row=1, column=0, padx=[8, 0], pady=4, sticky=tk.EW
    )
    customspectrum_voltage_entry.grid(
        row=1, column=1, padx=[4, 4], pady=4, sticky=tk.EW
    )
    customspectrum_voltage_units.grid(
        row=1, column=2, padx=[0, 8], pady=4, sticky=tk.EW
    )

    customspectrum_current_label = ctk.CTkLabel(
        customspectrumconfigframe,
        text="Current",
        anchor="w",
        font=ctk_jbm12,
    )

    customspectrum_current_entry = ctk.CTkEntry(
        customspectrumconfigframe,
        width=40,
        justify="right",
        border_width=1,
        font=ctk_jbm12,
    )

    customspectrum_current_units = ctk.CTkLabel(
        customspectrumconfigframe, width=2, text="uA", anchor="w", font=ctk_jbm12
    )
    customspectrum_current_entry.insert(0, "15")

    customspectrum_current_label.grid(
        row=2, column=0, padx=[8, 0], pady=4, sticky=tk.EW
    )
    customspectrum_current_entry.grid(
        row=2, column=1, padx=[4, 4], pady=4, sticky=tk.EW
    )
    customspectrum_current_units.grid(
        row=2, column=2, padx=[0, 8], pady=4, sticky=tk.EW
    )

    customspectrum_duration_label = ctk.CTkLabel(
        customspectrumconfigframe,
        text="Duration",
        anchor="w",
        font=ctk_jbm12,
    )

    customspectrum_duration_entry = ctk.CTkEntry(
        customspectrumconfigframe,
        width=40,
        justify="right",
        border_width=1,
        font=ctk_jbm12,
    )

    customspectrum_duration_units = ctk.CTkLabel(
        customspectrumconfigframe, width=2, text="s", anchor="w", font=ctk_jbm12
    )
    customspectrum_duration_entry.insert(0, "30")

    customspectrum_duration_label.grid(
        row=3, column=0, padx=[8, 0], pady=4, sticky=tk.EW
    )
    customspectrum_duration_entry.grid(
        row=3, column=1, padx=[4, 4], pady=4, sticky=tk.EW
    )
    customspectrum_duration_units.grid(
        row=3, column=2, padx=[0, 8], pady=4, sticky=tk.EW
    )

    customspectrum_filter_label = ctk.CTkLabel(
        customspectrumconfigframe,
        text="Filter",
        anchor="w",
        font=ctk_jbm12,
    )
    customspectrum_filter_dropdown = ctk.CTkOptionMenu(
        customspectrumconfigframe,
        width=210,
        values=[""],
        dynamic_resizing=True,
        font=ctk_jbm12B,
        dropdown_font=ctk_jbm12,
    )
    customspectrum_filter_label.grid(row=4, column=0, padx=[8, 0], pady=4, sticky=tk.EW)
    customspectrum_filter_dropdown.grid(
        row=4, column=1, columnspan=2, padx=[4, 4], pady=4, sticky=tk.EW
    )

    customspectrumconfigframe.grid_remove()

    # GeRDA Section
    button_gerda_initialise = ctk.CTkButton(
        ctrltabview.tab("GeRDA"),
        text="Connect to GeRDA CNC Controller",
        command=gerdaCNC_InitialiseConnectionIfPossible,
        font=ctk_jbm12B,
    )
    button_gerda_initialise.grid(
        row=0, column=0, columnspan=1, padx=4, pady=4, sticky=tk.NSEW
    )
    button_gerda_home = ctk.CTkButton(
        ctrltabview.tab("GeRDA"),
        text="CNC: Home",
        command=gerdaCNC_Home_clicked,
        font=ctk_jbm12B,
    )
    button_gerda_home.grid(
        row=1, column=0, columnspan=1, padx=4, pady=4, sticky=tk.NSEW
    )
    button_gerda_getcurrentpos = ctk.CTkButton(
        ctrltabview.tab("GeRDA"),
        text="CNC: Get Current Position",
        command=gerdaCNC_GetCurrentPosition_clicked,
        font=ctk_jbm12B,
    )
    button_gerda_getcurrentpos.grid(
        row=2, column=0, columnspan=1, padx=4, pady=4, sticky=tk.NSEW
    )
    button_gerda_helpme = ctk.CTkButton(
        ctrltabview.tab("GeRDA"),
        text="HELP",
        command=gerdaCNC_HelpMe_clicked,
        font=ctk_jbm12B,
    )
    button_gerda_helpme.grid(
        row=3, column=0, columnspan=1, padx=4, pady=4, sticky=tk.NSEW
    )

    # About Section
    about_blurb1 = ctk.CTkLabel(
        ctrltabview.tab("About"),
        text=f"S1Control {versionNum} ({versionDate})\nCreated by Zeb Hall for PSS\nContact: zhall@portaspecs.com\n",
        image=icon_softwaredev,
        justify="center",
        compound="top",
        font=ctk_jbm12,
    )
    about_blurb1.grid(
        row=3, column=0, columnspan=2, rowspan=2, padx=4, pady=4, sticky=tk.NSEW
    )

    about_imageframe = ctk.CTkFrame(
        ctrltabview.tab("About"), fg_color=("#c5c5c5", "#444444")
    )
    about_imageframe.grid(
        row=0, column=0, columnspan=2, rowspan=2, padx=4, pady=4, sticky=tk.NSEW
    )

    about_imagelabel = ctk.CTkLabel(about_imageframe, text=" ", image=psslogo)
    about_imagelabel.pack(
        side=tk.TOP, anchor=tk.N, fill="both", expand=True, padx=2, pady=2, ipady=8
    )

    # about_blurb_copyright_header = ctk.CTkLabel(ctrltabview.tab('About'), text=f'Acknowledgements:', justify = tk.LEFT, font=ctk_jbm10, text_color=plottextColour)
    # about_blurb_copyright_header.grid(row=2, column=0, columnspan = 2, rowspan = 2, padx=4, pady=4, sticky=tk.NSEW)
    # about_blurb_copyrights = ctk.CTkLabel(ctrltabview.tab('About'), text=f'MATPLOTLIB: Copyright (c) 2012-2023 Matplotlib Development Team; All Rights Reserved\n', justify = tk.LEFT, font=ctk_jbm08, text_color=plottextColour)
    # about_blurb_copyrights.grid(row=3, column=0, columnspan = 2, rowspan = 2, padx=4, pady=4, sticky=tk.NSEW)

    # Buttons
    # button_assay_text = ctk.StringVar()
    # button_assay_text.set('\u2BC8 Start Assay')
    # button_assay_text.set('\u2715 Stop Assay')
    # \u2BC0
    button_assay = ctk.CTkButton(
        ctrltabview.tab("Assay Controls"),
        width=110,
        command=startAssayClicked,
        text="Start Assay",
        fg_color="#33AF56",
        hover_color="#237A3C",
        image=icon_startassay,
        font=ctk_jbm14B,
    )  # , font = ctk_default_largeB,)
    button_assay.grid(row=1, column=0, padx=4, pady=4, sticky=tk.NSEW)

    # Consecutive Tests Section
    label_repeat_icon = ctk.CTkLabel(
        ctrltabview.tab("Assay Controls"), text="", image=icon_consecutive
    )
    label_repeat_icon.grid(row=1, column=1, padx=4, pady=4, sticky=tk.NSEW)

    # repeats_choice_var = ctk.StringVar(value='\u2B6F Consecutive')
    repeats_choice_var = ctk.StringVar(value="1")
    repeats_choice_list = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "15",
        "20",
        "50",
        "100",
        "150",
        "200",
        "300",
        "500",
        "1000",
    ]
    dropdown_repeattests = ctk.CTkOptionMenu(
        ctrltabview.tab("Assay Controls"),
        width=70,
        variable=repeats_choice_var,
        values=repeats_choice_list,
        command=repeatsChoiceMade,
        dynamic_resizing=True,
        font=ctk_jbm12B,
        dropdown_font=ctk_jbm12,
    )
    dropdown_repeattests.grid(row=1, column=2, padx=4, pady=4, sticky=tk.NSEW)

    button_editinfofields = ctk.CTkButton(
        ctrltabview.tab("Assay Controls"),
        image=icon_editinfo,
        text="Edit Info-Fields",
        command=editInfoFieldsClicked,
        font=ctk_jbm12B,
    )
    button_editinfofields.grid(
        row=8, column=0, columnspan=3, padx=4, pady=4, sticky=tk.NSEW
    )

    # button_startlistener = tk.Button(width = 15, text = "start listen", font = jbm10, fg = buttonfg3, bg = buttonbg3, command = lambda:xrfListenLoop_Start(None)).pack(ipadx=8,ipady=2)

    # button_getinstdef = tk.Button(width = 15, text = "get instdef", font = jbm10, fg = buttonfg3, bg = buttonbg3, command = getInfoClicked).pack(ipadx=8,ipady=2)

    # button_enablespectra = ctk.CTkButton(ctrltabview.tab("Instrument"), width = 13, text = "Enable Spectra Transmit", command = instrument_ConfigureTransmitSpectraEnable)
    # button_enablespectra.grid(row=1, column=0, padx=4, pady=4, sticky=tk.NSEW)

    # button_disablespectra = ctk.CTkButton(ctrltabview.tab("Instrument"), width = 13, text = "Disable Spectra Transmit", command = instrument_ConfigureTransmitSpectraDisable)
    # button_disablespectra.grid(row=2, column=0, padx=4, pady=4, sticky=tk.NSEW)

    button_gets1softwareversion = ctk.CTkButton(
        ctrltabview.tab("Instrument"),
        width=13,
        image=icon_s1version,
        text="Check Instrument Software Version",
        command=getS1verClicked,
        font=ctk_jbm12B,
    )
    button_gets1softwareversion.grid(
        row=1, column=0, columnspan=1, padx=4, pady=4, sticky=tk.NSEW
    )

    button_getnosetemp = ctk.CTkButton(
        ctrltabview.tab("Instrument"),
        width=13,
        image=icon_temperature,
        text="Check Nose Temperature",
        command=instrument_QueryNoseTemp,
        font=ctk_jbm12B,
    )
    button_getnosetemp.grid(
        row=2, column=0, columnspan=1, padx=4, pady=4, sticky=tk.NSEW
    )

    button_getnosepressure = ctk.CTkButton(
        ctrltabview.tab("Instrument"),
        width=13,
        image=icon_pressure,
        text="Check Nose Pressure",
        command=instrument_QueryNosePressure,
        font=ctk_jbm12B,
    )
    button_getnosepressure.grid(
        row=3, column=0, columnspan=1, padx=4, pady=4, sticky=tk.NSEW
    )

    button_setsystemtime = ctk.CTkButton(
        ctrltabview.tab("Instrument"),
        width=13,
        image=icon_systemtime,
        text="Sync Instrument Clock",
        command=instrument_ConfigureSystemTime,
        font=ctk_jbm12B,
    )
    button_setsystemtime.grid(
        row=4, column=0, columnspan=1, padx=4, pady=4, sticky=tk.NSEW
    )

    proximitysensor_var = ctk.BooleanVar(value=False)
    checkbox_proximitysensor = ctk.CTkCheckBox(
        ctrltabview.tab("Instrument"),
        text="Safety: Enable Proximity Sensor",
        variable=proximitysensor_var,
        onvalue=True,
        offvalue=False,
        command=lambda: instrument_toggleProximity(proximitysensor_var.get()),
        font=ctk_jbm12,
    )
    checkbox_proximitysensor.grid(row=5, column=0, padx=4, pady=4, sticky=tk.NSEW)

    storeresultsoninstrument_var = ctk.BooleanVar(value=True)
    checkbox_storeresultsoninstrument = ctk.CTkCheckBox(
        ctrltabview.tab("Instrument"),
        text="Output Result Files (.csv/.tsv)",
        variable=storeresultsoninstrument_var,
        onvalue=True,
        offvalue=False,
        command=lambda: instrument_toggleStoreResultFiles(
            storeresultsoninstrument_var.get()
        ),
        font=ctk_jbm12,
    )
    checkbox_storeresultsoninstrument.grid(
        row=6, column=0, padx=4, pady=4, sticky=tk.NSEW
    )

    storespectraoninstrument_var = ctk.BooleanVar(value=True)
    checkbox_storespectraoninstrument = ctk.CTkCheckBox(
        ctrltabview.tab("Instrument"),
        text="Output Spectra Files (.pdz)",
        variable=storespectraoninstrument_var,
        onvalue=True,
        offvalue=False,
        command=lambda: instrument_toggleStoreSpectraFiles(
            storespectraoninstrument_var.get()
        ),
        font=ctk_jbm12,
    )
    checkbox_storespectraoninstrument.grid(
        row=7, column=0, padx=4, pady=4, sticky=tk.NSEW
    )

    button_queryxraysettings = ctk.CTkButton(
        ctrltabview.tab("Instrument"),
        width=13,
        image=icon_systemtime,
        text="Query Xray Settings",
        command=queryXraySettings_clicked,
        font=ctk_jbm12B,
    )
    # button_queryxraysettings.grid(
    #     row=8, column=0, columnspan=1, padx=4, pady=4, sticky=tk.NSEW
    # )

    # button_proximityenable = ctk.CTkButton(ctrltabview.tab("Instrument"), width = 13, image=icon_sensoron, text = "Enable Proximity", command = instrument_ConfigureProximityEnable)
    # button_proximityenable.grid(row=4, column=0, padx=4, pady=4, sticky=tk.NSEW)

    # button_proximitydisable = ctk.CTkButton(ctrltabview.tab("Instrument"), width = 13, image=icon_sensoroff, text = "Disable Proximity", command = instrument_ConfigureProximityDisable)
    # button_proximitydisable.grid(row=4, column=1, padx=4, pady=4, sticky=tk.NSEW)

    # button_geteditfields = ctk.CTkButton(ctrltabview.tab("Instrument"), width = 13 ,text = "Get Current Info Fields", command = instrument_QueryEditFields)
    # button_geteditfields.grid(row=4, column=0, padx=4, pady=4, sticky=tk.NSEW)

    # button_getapplicationprefs = tk.Button(configframe, width = 25, text = "get current app prefs", font = jbm10, fg = buttonfg3, bg = buttonbg3, command = instrument_QueryCurrentApplicationPreferences)
    # button_getapplicationprefs.grid(row=7, column=1, padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)

    # button_getapplicationphasetimes = ctk.CTkButton(ctrltabview.tab("Instrument"), width = 13, text = "Get Phase Times", command = instrument_QueryCurrentApplicationPhaseTimes)
    # button_getapplicationphasetimes.grid(row=2, column=1, padx=4, pady=4, sticky=tk.NSEW)

    displayunits_label = ctk.CTkLabel(
        ctrltabview.tab("Options"), text="Units:", font=ctk_jbm12
    )
    displayunits_label.grid(row=1, column=0, padx=[4, 0], pady=4, sticky=tk.NSEW)

    displayunits_var = ctk.StringVar(value="ppm")
    displayunits_list = ["%", "ppm", "ppb"]
    dropdown_displayunits = ctk.CTkOptionMenu(
        ctrltabview.tab("Options"),
        variable=displayunits_var,
        values=displayunits_list,
        command=None,
        dynamic_resizing=False,
        font=ctk_jbm12B,
        dropdown_font=ctk_jbm12,
    )
    dropdown_displayunits.grid(row=1, column=1, padx=4, pady=4, sticky=tk.NSEW)

    # FLAG TO CONTROL AUTOMATIC SPECTRA PLOTTING ON PHASE/ASSAY COMPLETION
    doAutoPlotSpectra_var = ctk.BooleanVar(value=True)
    checkbox_doAutoPlotSpectra = ctk.CTkCheckBox(
        ctrltabview.tab("Options"),
        text="Automatically Plot Spectra",
        variable=doAutoPlotSpectra_var,
        onvalue=True,
        offvalue=False,
        font=ctk_jbm12,
    )
    checkbox_doAutoPlotSpectra.grid(
        row=2, column=0, padx=4, pady=4, columnspan=2, sticky=tk.NSEW
    )

    # FLAG TO CONTROL NORMALISATION OF SPECTRA VIA AREA-AND-TIME-NORMALISATION
    doNormaliseSpectra_var = ctk.BooleanVar(value=False)
    checkbox_doNormaliseSpectra = ctk.CTkCheckBox(
        ctrltabview.tab("Options"),
        text="Normalise Spectra, Time & Total Counts",
        variable=doNormaliseSpectra_var,
        onvalue=True,
        offvalue=False,
        font=ctk_jbm12,
    )
    checkbox_doNormaliseSpectra.grid(
        row=3, column=0, padx=4, pady=4, columnspan=2, sticky=tk.NSEW
    )
    checkbox_doNormaliseSpectra.deselect()

    # FLAG TO CONTROL DISPLAY OF COUNTS PER SEC AND DEAD TIME %
    doDisplayVitals_var = ctk.BooleanVar(value=True)
    checkbox_doDisplayVitals = ctk.CTkCheckBox(
        ctrltabview.tab("Options"),
        text="Display Counts/Second and Dead Time %",
        variable=doDisplayVitals_var,
        onvalue=True,
        offvalue=False,
        command=toggleVitalsDisplayVisibility,
        font=ctk_jbm12,
    )
    checkbox_doDisplayVitals.grid(
        row=4, column=0, padx=4, pady=4, columnspan=2, sticky=tk.NSEW
    )
    # checkbox_doDisplayVitals.deselect()

    enableautoassayCSV_var = ctk.StringVar(value="off")
    checkbox_enableautoassayCSV = ctk.CTkCheckBox(
        ctrltabview.tab("Options"),
        text="Auto Save Results to Individual CSVs",
        variable=enableautoassayCSV_var,
        onvalue="on",
        offvalue="off",
        font=ctk_jbm12,
    )
    checkbox_enableautoassayCSV.grid(
        row=5, column=0, padx=4, pady=4, columnspan=2, sticky=tk.NSEW
    )

    enableresultsCSV_var = ctk.StringVar(value="on")
    checkbox_enableresultsCSV = ctk.CTkCheckBox(
        ctrltabview.tab("Options"),
        text="Auto Save Results to Combined CSV",
        variable=enableresultsCSV_var,
        onvalue="on",
        offvalue="off",
        font=ctk_jbm12,
    )
    checkbox_enableresultsCSV.grid(
        row=6, column=0, padx=4, pady=4, columnspan=2, sticky=tk.NSEW
    )

    # FLAG TO CONTROL DISPLAY OF COUNTS PER SEC AND DEAD TIME %
    doSanityCheckSpectra_var = ctk.BooleanVar(value=True)
    checkbox_doSanityCheckSpectra = ctk.CTkCheckBox(
        ctrltabview.tab("Options"),
        text="Sanity-check Spectra on Assay Complete",
        variable=doSanityCheckSpectra_var,
        onvalue=True,
        offvalue=False,
        font=ctk_jbm12,
    )
    checkbox_doSanityCheckSpectra.grid(
        row=7, column=0, padx=4, pady=4, columnspan=2, sticky=tk.NSEW
    )

    enableendofassaynotifications_var = ctk.StringVar(value="on")
    checkbox_enableendofassaynotifications = ctk.CTkCheckBox(
        ctrltabview.tab("Options"),
        text="Desktop Notification on Assay Complete",
        variable=enableendofassaynotifications_var,
        onvalue="on",
        offvalue="off",
        font=ctk_jbm12,
    )
    checkbox_enableendofassaynotifications.grid(
        row=8, column=0, padx=4, pady=4, columnspan=2, sticky=tk.NSEW
    )

    checkbox_enabledarkmode = ctk.CTkCheckBox(
        ctrltabview.tab("Options"),
        text="Dark Mode UI (Ctrl+Shift+L)",
        variable=enabledarkmode,
        onvalue="dark",
        offvalue="light",
        command=lambda: ctk_change_appearance_mode_event(enabledarkmode.get()),
        font=ctk_jbm12,
    )
    checkbox_enabledarkmode.grid(
        row=9, column=0, padx=4, pady=4, columnspan=2, sticky=tk.NSEW
    )

    # Current Instrument Info stuff
    # label_currentapplication_text = ctk.StringVar()
    applicationselected_stringvar = ctk.StringVar(value="Application")
    methodselected_stringvar = ctk.StringVar(value="Method")
    instr_applicationspresent = []
    instr_methodsforcurrentapplication = []
    instr_filterspresent = []

    # Log Box

    # logbox_xscroll = tk.Scrollbar(infoframe, orient = 'horizontal')
    # logbox_xscroll.grid(row = 3, column = 1, columnspan = 2, sticky = tk.NSEW)
    # logbox_yscroll = tk.Scrollbar(infoframe, orient = 'vertical')
    # logbox_yscroll.grid(row = 1, column = 3, columnspan = 1, rowspan= 2, sticky = tk.NSEW)
    logbox = ctk.CTkTextbox(
        LHSframe,
        corner_radius=5,
        height=250,
        width=320,
        font=ctk_jbm10,
        text_color=WHITEISH,
        fg_color=CHARCOAL,
        wrap=tk.NONE,
    )
    logbox.pack(side=tk.TOP, anchor=tk.N, fill="both", expand=True, padx=8, pady=[4, 4])
    logbox.tag_config("ERROR", foreground="#d62d43")
    logbox.tag_config("WARNING", foreground="#e09c26")
    logbox.tag_config("INFO", foreground="#3B8ED0")  # 2783d9
    logbox.tag_config("BASIC", foreground=WHITEISH)
    logbox.configure(state="disabled")
    # logbox_xscroll.config(command = logbox.xview)
    # logbox_yscroll.config(command = logbox.yview)

    # Spectraframe Stuff
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams["font.family"] = "monospace"
    plt.rcParams["font.monospace"] = "JetBrains Mono"
    plt.rcParams["font.size"] = 9
    plt.rcParams["text.color"] = CHARCOAL
    plt.rcParams["axes.labelcolor"] = plottextColour
    plt.rcParams["xtick.color"] = plottextColour
    plt.rcParams["ytick.color"] = plottextColour
    plt.rcParams["path.simplify"] = False
    plt.rcParams["path.simplify_threshold"] = 0.1
    # 0.0 no simplification, 1.0 full simplification. 0.111111 is def. 0.0 supposed to be faster, but did not see significant performance improvement.
    # ylabel = plt.ylabel('Counts')
    # xlabel = plt.xlabel('Energy (keV)')

    fig = Figure(figsize=(10, 4), dpi=100, frameon=True)
    fig.set_tight_layout(True)

    spectra_ax = fig.add_subplot(111)
    spectra_ax.set_xlabel("Energy (keV)")
    spectra_ax.set_ylabel("Counts (Total)")
    spectra_ax.format_coord = lambda x, y: "{:.4f} keV / {:.0f} Counts".format(x, y)

    spectra_ax.set_xlim(xmin=0, xmax=40)
    spectra_ax.set_ylim(ymin=0, ymax=10000)
    # spectra_ax.autoscale_view()
    spectra_ax.autoscale(enable=True, tight=False)
    spectra_ax.locator_params(axis="x", nbins=23)
    spectra_ax.locator_params(axis="y", nbins=10)
    spectra_ax.margins(y=0.05, x=0.05)
    # spectra_ax.axhline(y=0, color='k')
    # spectra_ax.axvline(x=0, color='k')
    spectracanvas = FigureCanvasTkAgg(fig, master=spectraframe)
    spectracanvas.mpl_connect("motion_notify_event", onPlotCanvasMotion)

    spectracanvas.draw_idle()

    spectratoolbar = NavigationToolbar2Tk(
        spectracanvas, spectraframe, pack_toolbar=False
    )

    spectratoolbar.config(background=plottoolbarColour)
    spectratoolbar._message_label.config(background=plottoolbarColour, font=jbm09)
    spectracanvas.get_tk_widget().pack(
        side=tk.TOP, fill="both", expand=True, padx=8, pady=[8, 0]
    )
    # spectratoolbar.pack(side=tk.LEFT, fill="x", padx=8, pady=4, ipadx=5)
    for child in spectratoolbar.winfo_children():
        child.config(background=plottoolbarColour)

    spectratoolbar_button_home = ctk.CTkButton(
        spectraframe,
        text="",
        width=5,
        image=icon_plot_home,
        command=fig.canvas.toolbar.home,
    )
    spectratoolbar_button_home.pack(
        side=tk.LEFT, fill=None, padx=[8, 2], pady=[0, 8], ipadx=0
    )

    spectratoolbar_button_back = ctk.CTkButton(
        spectraframe,
        text="",
        width=5,
        image=icon_plot_back,
        command=fig.canvas.toolbar.back,
    )
    spectratoolbar_button_back.pack(
        side=tk.LEFT, fill=None, padx=[2, 2], pady=[0, 8], ipadx=0
    )

    spectratoolbar_button_forward = ctk.CTkButton(
        spectraframe,
        text="",
        width=5,
        image=icon_plot_forward,
        command=fig.canvas.toolbar.forward,
    )
    spectratoolbar_button_forward.pack(
        side=tk.LEFT, fill=None, padx=[2, 2], pady=[0, 8], ipadx=0
    )

    spectratoolbar_button_move = ctk.CTkButton(
        spectraframe,
        text="",
        width=5,
        image=icon_plot_move,
        command=fig.canvas.toolbar.pan,
    )
    spectratoolbar_button_move.pack(
        side=tk.LEFT, fill=None, padx=[2, 2], pady=[0, 8], ipadx=0
    )

    spectratoolbar_button_crop = ctk.CTkButton(
        spectraframe,
        text="",
        width=5,
        image=icon_plot_crop,
        command=fig.canvas.toolbar.zoom,
    )
    spectratoolbar_button_crop.pack(
        side=tk.LEFT, fill=None, padx=[2, 2], pady=[0, 8], ipadx=0
    )

    # spectratoolbar_button_configure = ctk.CTkButton(
    #     spectraframe,
    #     text="",
    #     width=5,
    #     image=icon_plot_configure,
    #     command=fig.canvas.toolbar.configure_subplots,
    # )
    # spectratoolbar_button_configure.pack(side=tk.LEFT, fill=None, padx=8, pady=[0,8], ipadx=0)

    spectratoolbar_button_save = ctk.CTkButton(
        spectraframe,
        text="",
        width=5,
        image=icon_plot_saveimg,
        command=fig.canvas.toolbar.save_figure,
    )
    spectratoolbar_button_save.pack(
        side=tk.LEFT, fill=None, padx=[2, 2], pady=[0, 8], ipadx=0
    )

    plot_coords_strvar = ctk.StringVar(value="")
    label_plot_coords = ctk.CTkLabel(
        spectraframe, textvariable=plot_coords_strvar, font=ctk_jbm12
    )
    label_plot_coords.pack(side=tk.LEFT, fill=None, padx=8, pady=[0, 8], ipadx=0)

    setPlotColours()

    # Other Toolbar widgets
    button_configureemissionlines = ctk.CTkButton(
        spectraframe,
        width=13,
        image=icon_configureemissionlines,
        text="Configure Emission Lines",
        command=configureEmissionLinesClicked,
        font=ctk_jbm12B,
    )
    button_configureemissionlines.pack(
        side=tk.RIGHT, fill="x", padx=[8, 8], pady=[0, 8]
    )

    # button_clearemissionlines = ctk.CTkButton(spectraframe, width = 13, text = "Clear Emission Lines", command = clearEmissionLinesClicked)
    # button_clearemissionlines.pack(side=tk.RIGHT, fill = 'x', padx = 0, pady = 4)

    button_analysepeak = ctk.CTkButton(
        spectraframe,
        width=13,
        image=icon_identifypeak,
        text="Identify Peak ",
        command=startPlotClickListener,
        font=ctk_jbm12B,
    )
    button_analysepeak.pack(side=tk.RIGHT, fill="x", padx=0, pady=[0, 8])

    # Assays Frame Stuff
    assaysColumns = (
        "t_num",
        "t_app",
        "t_time",
        "t_timeelapsed",
        "t_sanitycheck",
        "t_notes",
    )
    assaysTable = Treeview(
        assaytableframe, columns=assaysColumns, height="14", selectmode="extended"
    )
    assaysTable.pack(side="top", fill="both", expand=True)

    assaysTable.heading(
        "t_num",
        text="Assay",
        anchor=tk.W,
        command=lambda _col="t_num": treeview_sort_column(assaysTable, _col, False),
    )
    assaysTable.heading(
        "t_app",
        text="Application",
        anchor=tk.W,
        command=lambda _col="t_app": treeview_sort_column(assaysTable, _col, False),
    )
    assaysTable.heading(
        "t_time",
        text="Time",
        anchor=tk.W,
        command=lambda _col="t_time": treeview_sort_column(assaysTable, _col, False),
    )
    assaysTable.heading(
        "t_timeelapsed",
        text="Elapsed",
        anchor=tk.W,
        command=lambda _col="t_timeelapsed": treeview_sort_column(
            assaysTable, _col, False
        ),
    )
    assaysTable.heading(
        "t_sanitycheck",
        text="Sanity Check",
        anchor=tk.W,
        command=lambda _col="t_sanitycheck": treeview_sort_column(
            assaysTable, _col, False
        ),
    )
    assaysTable.heading(
        "t_notes",
        text="Info Fields",
        anchor=tk.W,
        command=lambda _col="t_notes": treeview_sort_column(assaysTable, _col, False),
    )

    assaysTable.column("t_num", minwidth=50, width=60, stretch=0, anchor=tk.W)
    assaysTable.column("t_app", minwidth=125, width=130, stretch=0, anchor=tk.W)
    assaysTable.column("t_time", minwidth=70, width=75, stretch=0, anchor=tk.W)
    assaysTable.column("t_timeelapsed", minwidth=60, width=65, stretch=0, anchor=tk.W)
    assaysTable.column("t_sanitycheck", minwidth=90, width=100, stretch=0, anchor=tk.W)
    assaysTable.column("t_notes", minwidth=130, width=150, stretch=1, anchor=tk.W)

    assaysTableScrollbarY = ctk.CTkScrollbar(resultsframe, command=assaysTable.yview)
    assaysTableScrollbarY.pack(
        side=tk.LEFT, fill="y", expand=False, padx=[0, 8], pady=8
    )

    assaysTable.configure(yscrollcommand=assaysTableScrollbarY.set)
    # assaysTable.configure(xscrollcommand=resultsTableScrollbarX.set)

    assaysTable.bind("<<TreeviewSelect>>", assaySelected)
    assaysTable.configure(show="headings")

    tables = []
    tables.append(assaysTable)

    # Resultsbox stuff

    # resultsbox = ctk.CTkTextbox(resultsframe, corner_radius=5, height = 250, width = 150, font = ctk_jbm11, wrap = tk.NONE)
    # resultsbox.pack(side = tk.RIGHT, fill = 'both', expand = True, padx=8, pady=8)
    # resultsbox.configure(state = 'disabled')

    resultsColumns = (
        "results_Z",
        "results_Compound",
        "results_Concentration",
        "results_Error",
    )
    resultsTable = Treeview(
        resultsframe, columns=resultsColumns, height="14", selectmode="browse"
    )
    resultsTable.pack(side=tk.LEFT, fill="both", expand=True, padx=[8, 0], pady=8)

    resultsTable.heading(
        "results_Z",
        text="Z",
        anchor=tk.W,
        command=lambda _col="results_Z": treeview_sort_column(
            resultsTable, _col, False
        ),
    )
    resultsTable.heading(
        "results_Compound",
        text="Compound",
        anchor=tk.W,
        command=lambda _col="results_Compound": treeview_sort_column(
            resultsTable, _col, False
        ),
    )
    resultsTable.heading(
        "results_Concentration",
        text=f"Concentration",
        anchor=tk.W,
        command=lambda _col="results_Concentration": treeview_sort_column(
            resultsTable, _col, False
        ),
    )
    resultsTable.heading(
        "results_Error",
        text="Error (1\u03C3)",
        anchor=tk.W,
        command=lambda _col="results_Error": treeview_sort_column(
            resultsTable, _col, False
        ),
    )

    resultsTable.column("results_Z", minwidth=25, width=30, stretch=0, anchor=tk.W)
    resultsTable.column(
        "results_Compound", minwidth=70, width=70, stretch=0, anchor=tk.W
    )
    resultsTable.column(
        "results_Concentration", minwidth=120, width=120, stretch=0, anchor=tk.E
    )
    resultsTable.column("results_Error", minwidth=110, width=120, anchor=tk.W)

    resultsTableScrollbarY = ctk.CTkScrollbar(resultsframe, command=resultsTable.yview)
    resultsTableScrollbarY.pack(
        side=tk.LEFT, fill="y", expand=False, padx=[0, 8], pady=8
    )
    # resultsTable.bind('<<TreeviewSelect>>', resultCompoundSelected)
    resultsTable.configure(show="headings")
    resultsTable.configure(yscrollcommand=resultsTableScrollbarY.set)

    tables.append(resultsTable)

    # Misc Keybindings a
    gui.bind("<Control-Shift-L>", checkbox_enabledarkmode.toggle)
    gui.bind("<Control-Shift-R>", toggleResultsFrameVisible)
    gui.bind("<Control-Shift-S>", toggleSpectraFrameVisible)

    # toggle settings that should be off IF lightweight mode was requested at runtime
    if lightweight_mode_requested:
        checkbox_doAutoPlotSpectra.deselect()
        spectraframe.pack_forget()
        print("S1CONTROL Launched in Lightweight-Mode.")

    # Begin Instrument Connection

    instrument_Connect()
    time.sleep(0.2)
    xrfListenLoopThread_Start(None)
    # xrfListenLoopProcess_Start()
    time.sleep(0.1)
    instrument_GetStates()
    time.sleep(0.1)
    instrument_GetInfo()  # Get info from IDF for log file NAMING purposes
    time.sleep(0.5)
    initialiseLogFile()  # Must be called after instrument and listen loop are connected and started, and getinfo has been called once, and time has been allowed for loop to read all info into vars
    time.sleep(0.2)
    # Get info to add to Log file
    instrument_GetInfo()

    statusUpdateCheckerLoop_Start(None)

    try:
        gui.title(f"S1Control - {driveFolderStr}")
    except:
        print("Unable To Set Window Title Using driveFolderStr")
        pass

    if instr_isloggedin == False:
        instrument_Login()

    time.sleep(0.05)
    instrument_SetImportantStartupConfigurables()
    time.sleep(0.05)
    instrument_QueryCurrentApplicationPhaseTimes()

    gui.protocol("WM_DELETE_WINDOW", onClosing)

    gui.mainloop()

    closeAllThreads()  # call after gui mainloop has ended
