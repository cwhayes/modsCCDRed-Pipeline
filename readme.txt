LAST UPDATED: 5/20/19 by CONOR HAYES

Automated pipeline for running MODS1 spectral data through modsCCDRed reduction. Raw data will need to be moved into the appropriate folders, and the program will only work for one object at a time. Horribly optimized, might fix if I have time.

==KNOWN BUGS==
-Sometimes consumes all available resources on a computer.
-Doesn't correctly identify the Finals folders. Final files are in with the raw files, so it's more of an inconvenience than a fatal error.
-Does drop a few errors along the way, as I haven't fully fixed the code to remove files we don't want to process. Again, not a fatal error, doesn't seem to cause issues, but is annoying.
-Red channel data doesn't always seem to flip correctly.
-Doesn't include a cosmic ray removal program. Currently working on implementing one.

