# S1Control Changelog 

## v1.1.0 - 2024/06/20
 - Massive refactor complete!
 - Improved data structures to improve readability and maintainability, and make flet rewrite easier.
	 - All specific instrument information variables are now attributes of the BrukerInstrument class.
	 - Streamlined TCP connection logic to improve startup speed
	 - Cleared up some fringe variable type issues and improved typing and docstrings.
	 - Improved some unclear variable names (still need to do more of this) 
	 - Removed unnecessary global variables
 - Fixed a UI colour scheme bug introduced in v1.0.8 that resulted in white text on a light grey background on the spectra plot.

## v1.0.8 - 2024/06/10
 - Fixed a memory leak caused by matplotlib spectra plotting implementation when using the **automatically plot spectra** option.
	 - Memory leak still occurs when repeatedly adding and removing *many* elemental indicator lines to the plot. This is a fringe case and will be fixed soon.

## v1.0.7 - 2024/04/22
 - Implemented correct XMS instrument offsets for GeRDA usage.
 - Modified webhook notification behaviour to allow for usage of Teams webhooks, not just Slack. txt file containing webhook should now be named `notification-channel-webhook.txt`.
 - Minor adjustments to UI geometry to account for alternate scaling factors <100%

## v1.0.6 - 2024/03/25
 - Log backup location switched to PSS NAS (Y:\Service\pXRF\Automatic Instrument Logs (S1Control)) for PSS local network users (internal) (was previously GDrive)
 - Added catch for RuntimeError caused by UI Race condition on startup
 - Implemented correct Tracer 5 XYZ offsets for GeRDA.

## v1.0.5 - 2024/03/18
 - Exception handling improved.
 - Tweaks made to timing for gerda sample sequences and info-fields to improve consistency
 - "Results_" prefix for csv results output changed to "S1Control_Results_" to be consistent with log files. 

## v1.0.4 - 2024/02/19
 - Fixed several bugs related to estimated assay time readouts and progress bar logic that were causing custom spectrum mode assays to not estimate/track time correctly.
 - Fixed a bug that caused the custom spectrum duration entrybox to duplicate it's contents when an assay was started. No more scanning for 303030303030303030s.
 - removed a few unnecessary terminal debug printouts.

## v1.0.3 - 2024/02/16
 - Added 'start-at-scan-#' entry box next to Sample Sequence Start button, allowing the sample sequence to be started at any scan.
 - Implemented GeRDA Event notification functionality for Slack.
    - Sends messages to a designated slack channel or user workspace on certain attention-worthy GeRDA events (major instrument errors, pre-emptive temperature warnings, sanity check failures, completion of all scans, etc)
    - include your slack webhook URL in 'slackwebhook.txt' in the same directory as the S1Control executable to use this functionality. (see: https://api.slack.com/apps/)
 - Fixed issue cased by race condition between CNC order of events and notification normal assay logic. 
 - Fixed inaccurate error message appearing when CNC attempts first move after Homing had already taken place (homing function was not correctly setting last_moved coords with offsets)
 - Added 'reason' field to CNC stop command, providing contrast between user-initiated stop and ERROR-stop. (e.g. in the case of a count-rate error)
 - Fixed some inconsistent logbox message importance colours
 - Fixed some incoherent onClosing logic


## v1.0.2 - 2024/02/15
 - Implemented increment/decrement buttons for Phase times, long overdue QOL feature.
 - Fixed a bug when omitting scan time in sample-sequence CSVs.
 - Fixed a logic error on quit when log backup location can't be found.

## v1.0.1 - 2024/02/14
 - Fixed various bugs left over in v1.0.0:
    - Attempted Re-initiation of XRF listen loop will no longer prevent the software from closing.
    - Fixed log files missing the last few lines when backed up prematurely
    - Adjusted listen loop logic to be more resilient

## v1.0.0 - 2024/02/13 - MAJOR UPDATE - GeRDA/CNC System Integration
 - Implemented GeRDA / CNC Platform functionality for Sample Sequences, Sampling Jobs, and Calibrations.
    - The GeRDA Controls can now be accessed on the 'GeRDA' tab of the action menu in the top-left of the UI.
    - The software can be used to control the CNC-based GeRDA system in conjunction with an instrument if both are connected.
    - At this point, this functionality is designed to run onboard the Raspberry Pi 3b microcomputer inside the GeRDA control box. It will be expanded in future to allow control from any computer connected to the CNC control board and Instrument. 
    - Currently, only the Titan's coordinate offsets are programmed in, so the Tracer is currently not supported for this mode.
    - To run samples with GeRDA using S1Control, First click on the 'Connect to CNC Controller' button. When connection is sucessful, the other functions become available.
    - The system is designed to take in a CSV-format 'Sample Sequence CSV'. This is a CSV File with the following Headers: ``"ScanNumber", "Name/Note", "XPosition(mm)", "YPosition(mm)", "Illumination(optional)", "Time(sec)(optional)"``. An example file is included for reference. The "Illumination" and "Time" columns can be left blank and the instrument will instead use the normal selected application for analysis. The Coordinates for standard sampling tray positions A->J are also included for reference in 'gerda_spacers_coords_for_sampling.csv'.
    - Additionally, about a million other things too lengthy to list here.
- The Sanity-checking functionality has been updated to include checks for 'null' spectra: i.e, spectra with only a zero-peak. This is to allow for error-checking during sample sequences.
- The software will now try to re-establish dropped connections for a moment before panicking.
- Improved handling of Custom Spectrum mode analyses to better integrate with system.
- Updated some status flag logic to better gauge when the instrument is busy scanning.
- X-ray lines data was shifted to the element_string_lists.py file for cleanliness' sake.
- Included script file 'Rename-PDZ-using-amended-S1Control-Results-csv.py' to allow for auto-renaming of PDZ files to their sample names. This will be updated in future to be integrated into S1Control.


## v0.9.6 - 2024/01/22
 - Implemented near-complete backend for GeRDA CNC System control for quasi-run-order and sample run functionality.
    - Class-based approaches for GerdaCNCController, GerdaSampleInfo, and GerdaSampleList (made up of GerdaSampleInfo instances).
    - Sample list scanning (for calibrations, etc) will use a threaded asynchronous approach to account for mechanical delay of gerda system.
    - Further implementation into UI will happen in the next update.
 - Fixed a bug causing instrument to continue trying to scan when set to multiple assays, when a count rate error occurs.
 - Fixed a bug related to instrument vitals readouts when an instrument error occurs, causing the program to crash. Errant values will now cause vitals to read 0 across the board.
 - Restructured some messier parts of code to separate py file (element string lists) to improve readability.
 - Modified log file printing function behaviour if no log file name has been determined yet. This should make debugging early crashes easier.
 - Fixed some colour issues on mpl canvas.

## v0.9.5 - 2024/01/10
 - Redesigned plot toolbar and improved info readouts.
    - This was necessary to prevent mpl incompatabilities with larger/smaller display scalings and to prevent cross-platform issues.

## v0.9.4 - 2024/01/08
 - Overhauled the spectrum 'sanity-checking' algorithm: 
    - Now finds the point where the spectrum 'drops off' by using a 98%/2% split of total spectrum counts, instead of the previous noise-standard-deviation method.
    - In testing, this completely removed false-positive sanity check failures on low-fluorescence samples like Silica, assays with unusually short/long phase times, and samples causing sum peaks on 15kV phases.
    - It also reliably detected all of the 7 different 'known fail' pdz files during testing.
    - Hopefully this is the last iteration of this algorithm! Famous last words.
    - New tester function is called sanityCheckSpectrum_SumMethod(), have left in previous (now unused) sanityCheckSpectrum() function for reference.
 - Slightly adjusted Assaytable column widths to fix mistake with minwidths and defaultwidths being incongruent.

## v0.9.3 - 2023/12/22
 - Added the option to select an Illumination from a dropdown in Custom Spectrum mode.
    - Did this by implementing an 'Illumination' dataclass to store illumination data from the IDF in a more sensible way. This should be scalable in future for runorder/tempcal purposes.
 - Fixed an issue with the repeat-assays logic that caused Custom spectrum settings to not be used for subsequent assays.
    - Repeat assays on Custom-spectrum mode should work correctly now.
 - Slightly adjusted threshold for spectrum sanity check, and added some text to the warning messasge explaining the shortcomings of the check:
    - "Note: This function has no way of checking for sum peaks or low-fluorescence samples, so false positives may occur."
 - Fixed method dropdown still being populated by previously selected application's methods when Custom spectrum is selected.


## v0.9.2 - 2023/12/18
 - Improved plotting logic, fixed several bugs related to emission line toggling and plot overlaying functionality. Should no longer leave partial phases of assays on the next plot sometimes after adding emission lines.
 - modified numpy/pandas row referencing in preparation for upcoming feature deprecation in module

## v0.9.1 - 2023/12/14
- Tweaked sensitivity of sanity check by increasing counts threshold from stddev/100 to stddev/50.

## v0.9.0 - 2023/12/14
- Implemented a 'spectrum sanity checker':
    - This function is on by default, and can be disabled in options.
    - some instruments and calibrations have been having issues where the correct voltage for the source is not set properly, despite all other beam parameters being set as normal. This manifests in  strange looking spectra (for instance, instead of the first phase of GeoExploration using 15kv/no filter/~40uA, it will use 30kV, no filter, ~40uA.)
    - This setting will check that the spectra being recieved by S1Control *'Make sense'*: it checks that the spectrum recieved is possible to be generated by the voltage reported by the instrument. A red **ERROR** message will be generated in the logbox on assay completion if it doesn't pass these checks.
- the 'Sanity Check' result and a combined info-field value string, now appear in the assay table and the results csv.
- adjusted the size / design of some UI elements to better suit the newly expanded assaytable.
- improved logic for counter edit-info fields, now will increment correctly in UI alongside instrument incrementation.
- clarified some error messages related to connection issues
- fixed cross-platform issues caused by invalid path escape sequences
- began implementation of logic for reconnection upon instrument connection dropout (not fully implemented yet)

## v0.8.4 - 2023/12/06
- implemented several changes to improve performance on low-spec hardware (raspberry pi 3b+ tested), including a 'lightweight' mode which can be launched into by running S1Control.py with  the argument 'l' or 'lightweight'. This mode hides the spectra plotting frame completely, and is replaced by expanded results and assay table views.
- added checkbox in options to disable automatic spectra plotting after phase completion and assay completion. auto plotting is enabled by default.
- removed duplicate printing of logbox/logfile messages to the system terminal to improve performance.
- changed instances of mpl .draw() to .draw_idle() to reduce freezes during plotting events.
- added keybinding for hiding spectra plot frame (CTRL+SHIFT+S)

## v0.8.3 - 2023/11/27
- Upgraded built python runtime to 3.12.0
- Corrected compatibility issues with linux version
- Rectified some scaling issues caused by windows dpi/scaling factor (100%/125% etc.) for (hopefully) better font readability
- Corrected f-string and r-string compat issues related to python version upgrade
- Changed 'Spectrum Only' mode into 'Custom Spectrum' mode to differentiate from inbuilt application on some older instruments.

## v0.8.2 - 2023/11/23
- Various visual and filesystem changes to improve compatibility with linux

## v0.8.1 - 2023/11/17
- added proper 'spectrum only' configuration mode.
- Added proper support for adjusting tube parameters (voltage, current, filters) a'la spectrometer mode.
- unfortunately it doesn't work under the spectrometer mode application, because bruker are incompetent.
- make sure to select 'SPECTRUM ONLY' at the bottom of the application menu to use it.

## v0.8.0 - 2023/11/09
- Counts per Second and Dead Time % checkbox is now 'Vitals' display - will also show requested tube voltage and current, in a widget near status bar.
- adjusted some scheduling/threading problems that could cause crashes
- fixed some places where the unified fonts weren't being used

## v0.7.4 - 2023/11/07
- added checkbox option for displaying the counts per second and dead time %. reports values every packet (~1/sec) in the logbox.

## v0.7.3 - 2023/10/26
- formatting adjusted to use 'black' pep 8 formatting style for readability.
- fixed some system ping and resource path issues.
- standardised font usage - all UI elements now use jetbrains mono. now need to manually install font file.
- altered bitmap icon code and added XBM file for linux/mac support

## v0.7.2 - 2023/10/25
- linux beta test version

## v0.7.1 - 2023/09/06
- added more quantity options for repeat testing for stability testing purposes. will add cutom field in future, this is a just a bandaid fix

## v0.7.0 - 2023/08/23
- fixed bugs causing crashes when using:
    - custom concentrations in calibrations
    - calibrations that only output one elemental concentration
    - grade library calibrations
- added support for grade library matching results. they will print in logbox now instead of being invisible.
- improved performance for completion of assay. now uses built-in select method of assayTable for plotting and displaying of results.

## v0.6.6 - 2023/07/27
- Implemented support for plotting multiple spectra/assays at once (overlaid). Can select multiple with ctrl+click or shift+click from the assay table. Colours will cycle.
- visual improvements for dark mode results table and assay table.

## v0.6.4 - 2023/07/14
Added keybindings for light/dark mode toggle (CTRL+SHIFT+L), and results section show/hide toggle (CTRL+SHIFT+M).

## v0.6.3 - 2023/06/30
- Properly implemented colour-coding for logbox.
- fixed some messy/vague error messages
- minor UI spacing issues

## v0.6.2 - 2023/06/29
- implemented logbox colour coding for error and warning messages

## v0.6.1 - 2023/06/22
- Implemented workarounds for ctk bugs: toplevel window icon and lift().

## v0.6.0 - 2023/06/22
- icon and button overhaul
- minor UI improvements
- ability to query nose pressure sensor reading
- fixes to start/stop assay button logic

## v0.5.9 - 2023/06/16
- fixed issues related to matplotlib 3.7.1 update. now uses latest version of mpl instead of 3.6.3.
- Fixed crashes occuring when expected values aren't found in idf information. This should improve compatibility for older instruments and ones with corrupted system files.
- fixed re-plot and odd behaviour when selecting assays in table before starting a new assay.
- fixed ui issue - software option checkboxes misalignment

## v0.5.8 - 2023/06/01
- adjusted units display and convention. PPM is now the default.
- fixed broken column sorting in results table introduced with switch to PPM default.
- removed unnecessary replot of last phase spectra on plot.
- added support for live (end of each phase) spectra plotting of normalised spectra if option is enabled. required changing when spectra counts are normalised to earlier in flow. final completeAssay function now checks for normalised data before normalising, to avoid reprocessing.
- added change of axes label based on normalisation selection.



> patchnotes prior to v0.5.8 can be found in github commits