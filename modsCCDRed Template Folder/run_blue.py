#from __future__ import print_function, division

import subprocess
import os
from astropy.io import fits

'''flats = raw_input('Please enter flats data directory: ')
science = raw_input('Please enter science data directory: ')
calib = raw_input('Please enter calibration data directory: ')
stand = raw_input('Please enter standards data directory: ')'''

#########################################################################
flats = 'Flats/Dome'
specflats = 'Flats/Spectral'
science = 'Science'
calib = 'Calibration'
stand = 'Standards'
#########################################################################

def remove_reds(directory):
	for item in directory[:]:
		if ( (item[:6] == 'mods1r') or (item[8:] == 'm1r.fits') or (item[:1] == 'r') or (item[12:] == 'm1r_otf.fits') ):
			directory.remove(item)
	return(directory)

flats_dir = os.listdir(flats)
science_dir = os.listdir(science)
calib_dir = os.listdir(calib)
stand_dir = os.listdir(stand)
spec_dir = os.listdir(specflats)

flats_dir = remove_reds(flats_dir)
science_dir = remove_reds(science_dir)
calib_dir = remove_reds(calib_dir)
stand_dir = remove_reds(stand_dir)
spec_dir = remove_reds(spec_dir)

print('-> Running modsCCDRed for blue data...')

# Spectral flats
os.chdir(specflats)
curdir = os.getcwd()
print('Directory changed to %s' % curdir)

print('-> Bias correcting spectral flats...')

for files in spec_dir:
	subprocess.call(['modsBias.py', files])

print('-> Median combining spectral flats')

spec_files = ['modsMedian.py']
spec_dir = os.listdir(os.getcwd()) # Updating directory with new files
spec_dir = remove_reds(spec_dir)

for files in spec_dir:
	if (files[20:23] == '_ot'):
		spec_files.append(files)

spec_files.append('bspec_med.fits')

subprocess.call(spec_files)
print('Created bspec_med.fits !')

print('-> Fixing bad pixels...')

subprocess.call(['modsFixPix.py', 'bspec_med.fits', 'bspec_fix.fits'])

print('-> Flattening the image...')

subprocess.call(['modsPixFlat.py', 'bspec_fix.fits', 'specflat_m1b.fits'])

# Dome flats
print('-> Creating normalized color-free pixel flats...')

os.chdir('..')
os.chdir('..')
os.chdir(flats)
curdir = os.getcwd()
print('Directory changed to %s' % curdir)

print('-> Bias correcting flats...')

for files in flats_dir:
	subprocess.call(['modsBias.py', files])

print('-> Median combining flats...')

ug5_files = ['modsMedian.py']
clr_files = ['modsMedian.py']
flats_dir = os.listdir(os.getcwd()) # Updating directory with new files
flats_dir = remove_reds(flats_dir)

for files in flats_dir:
	fits_file = fits.open(files)
	color = fits_file[0].header['FILTNAME']
	if (color == 'Clear'):
		if (files[20:23] == '_ot'):
			clr_files.append(files)
	else:
		if (files[20:23] == '_ot'):
			ug5_files.append(files)

ug5_files.append('bug5_med.fits')
clr_files.append('bclr_med.fits')

subprocess.call(clr_files)
print('Created bclr_med.fits !')
subprocess.call(ug5_files)
print('Created bug5_med.fits !')

print('-> Adding Clear and UG5 channels...')

subprocess.call(['modsAdd.py', 'bclr_med.fits', 'bug5_med.fits', 'bflat_med.fits'])

print('-> Fixing bad pixels...')

subprocess.call(['modsFixPix.py', 'bflat_med.fits', 'bflat_fix.fits'])

print('-> Flattening the image...')

subprocess.call(['modsPixFlat.py', 'bflat_fix.fits', 'pixflat_m1b.fits'])

# Now we're done with processing the flats
# Move on to applying them to the data

subprocess.call(['cp', 'pixflat_m1b.fits', '../../Science'])
subprocess.call(['cp', 'pixflat_m1b.fits', '../../Calibration'])
subprocess.call(['cp', 'pixflat_m1b.fits', '../../Standards'])

#Changing to science directory

os.chdir('..')
os.chdir('..')
os.chdir(science)
curdir = os.getcwd()
print('Directory changed to %s' % curdir)

print('-> Applying flats to science data...')

for files in science_dir:
	subprocess.call(['modsProc.py', '-b', files, 'pixflat_m1b.fits'])

#Changing to standards directory

os.chdir('..')
os.chdir(stand)
curdir = os.getcwd()
print('Directory changed to %s' % curdir)

print('-> Applying flats to standards data...')

for files in stand_dir:
	subprocess.call(['modsProc.py', '-b', files, 'pixflat_m1b.fits'])

#Changing to calibration directory

os.chdir('..')
os.chdir(calib)
curdir = os.getcwd()
print('Directory changed to %s' % curdir)

print('-> Applying flats to calibration data...')

for files in calib_dir:
	subprocess.call(['modsProc.py', '-b', files, 'pixflat_m1b.fits'])

#Combining calibration spectra

calib_dir = os.listdir(os.getcwd()) # Updating directory with new files
calib_dir = remove_reds(calib_dir)
calib_tocombine = ['modsAdd.py']

for files in calib_dir:
	if (files[-9:] == '_otf.fits'):
		calib_tocombine.append(files)

calib_tocombine.append('comp_m1b_ls.fits')

print('-> Combining calibration spectra...')
subprocess.call(calib_tocombine)

#Combining science data (if desired)

combine_science = raw_input('Would you like to combine your science data? (y/n) ')

if (combine_science == 'y'):
	os.chdir('..')
	os.chdir(science)
	curdir = os.getcwd()
	print('Directory changed to %s' % curdir)
	science_dir = os.listdir(os.getcwd()) # Updating directory with new files
	science_dir = remove_reds(science_dir)

	target_name = raw_input('What is your target name? (no spaces) ')
	combine_method = raw_input('What method would you like to use? (median/sum) ')
	
	if (combine_method == 'median'):
		sci_tocombine = ['modsMedian.py']
		for files in science_dir:
			if (files[-9:] == '_otf.fits'):
				sci_tocombine.append(files)

		sci_tocombine.append(target_name + '_m1b_ls.fits')

	elif (combine_method == 'sum'):
		sci_tocombine = ['modsAdd.py']
		for files in science_dir:
			if (files[-9:] == '_otf.fits'):
				sci_tocombine.append(files)

		sci_tocombine.append(target_name + '_m1b_ls.fits')

	print('-> Combining science spectra...')
	subprocess.call(sci_tocombine)

#Combining standards data (if desired)

combine_stand = raw_input('Would you like to combine your standards data? (y/n) ')

if (combine_stand == 'y'):
	os.chdir('..')
	os.chdir(stand)
	curdir = os.getcwd()
	print('Directory changed to %s' % curdir)
	stand_dir = os.listdir(os.getcwd()) # Updating directory with new files
	stand_dir = remove_reds(stand_dir)

	star_name = raw_input('What is your standard star name? (no spaces) ')
	combine_method = raw_input('What method would you like to use? (median/sum) ')
	
	if (combine_method == 'median'):
		stand_tocombine = ['modsMedian.py']
		for files in stand_dir:
			if (files[-9:] == '_otf.fits'):
				stand_tocombine.append(files)

		stand_tocombine.append(star_name + '_m1b.fits')

	elif (combine_method == 'sum'):
		stand_tocombine = ['modsAdd.py']
		for files in stand_dir:
			if (files[-9:] == '_otf.fits'):
				stand_tocombine.append(files)

		stand_tocombine.append(star_name + '_m1b_ls.fits')

	print('-> Combining standards spectra...')
	subprocess.call(stand_tocombine)

#Moving the final files to the Finals folder

print('-> Moving all the final files to the Finals folder...')

os.chdir('..')
curdir = os.getcwd()
print('Directory changed to %s' % curdir)
flats_dir = os.listdir(flats)
science_dir = os.listdir(science)
calib_dir = os.listdir(calib)
stand_dir = os.listdir(stand)
spec_dir = os.listdir(specflats)

flats_dir = remove_reds(flats_dir)
science_dir = remove_reds(science_dir)
calib_dir = remove_reds(calib_dir)
stand_dir = remove_reds(stand_dir)
spec_dir = remove_reds(spec_dir)

os.chdir(flats)
subprocess.call(['cp', 'pixflat_m1b.fits', '../../Finals/Flats'])

os.chdir(science)
for files in science_dir:
	if (files[-9:] == '_otf.fits'):
		subprocess.call(['cp', files, '../Finals/Science/Uncombined'])
	elif (files[-8:] == '_ls.fits'):
		subprocess.call(['cp', files, '../Finals/Science/Combined'])


os.chdir('..')
os.chdir(stand)
for files in stand_dir:
	if (files[-9:] == '_otf.fits'):
		subprocess.call(['cp', files, '../Finals/Standards/Uncombined'])
	elif (files[-9:] == '_m1b.fits'):
		subprocess.call(['cp', files, '../Finals/Standards/Combined'])

os.chdir('..')
os.chdir(calib)
subprocess.call(['cp', 'comp_m1b_ls.fits', '../Finals/Calibration'])

os.chdir('..')
os.chdir(specflats)
subprocess.call(['cp', 'specflat_m1b.fits', '../../Finals/Flats'])

print('-> Blue data processing complete!')
