import sys
import getopt
import configparser
import os
import glob
import subprocess
import time


def __main__(argv):
    __init__()

    getParameters(argv)

    readSettings()

    readTheme(settings.get('settings', 'theme'))
    
    if rom == '':
        fillParametersForDebug()

    getSaveDirectories()

    getSaveFiles(system, rom)

    printDebug()

    createNotification('up', 'GoogleDrive', 'sync')
    showNotification('/dev/shm/cloud-sync.png', '10000')
    
    time.sleep(3)
    
    createNotification('up', 'GoogleDrive', 'ok')
    showNotification('/dev/shm/cloud-sync.png', '10000')


# initalize the script
def __init__():
    global configBasePath
    global scriptBasePath

    configBasePath = '/opt/retropie/configs/'
    scriptBasePath = '/home/pi/RetroPie/scripts/cloud-sync/'


# extract given RetroArch parameters into global variables
def getParameters(argv):
    global system
    global emulator
    global rom
    global command

    system = ''
    emulator = ''
    rom = ''
    command = ''

    try:
        opts, args = getopt.getopt(argv, 'hs:e:r:c:', ['system=', 'emulator=', 'rom=', 'command='])
    except getopt.GetoptError:
        print('FEHLER')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('Usage')
            print('   cloud-sync.py -s <system> -e <emulator> -r <rom> -c <command>')
            print('   cloud-sync.py --system <system> --emulator <emulator> --rom <rom> --command <command>')
            sys.exit()
        elif opt in ('-s', '--system'):
            system = arg
        elif opt in ('-e', '--emulator'):
            emulator = arg
        elif opt in ('-r', '--rom'):
            rom = arg
        elif opt in ('-c', '--command'):
            command = arg


# fill variables if no RetroArch parameters given for DEBUG purposes
def fillParametersForDebug():
    global system
    global emulator
    global rom
    global command

    system = 'gb'
    emulator = 'lr-gambatte'
    rom = '/home/pi/RetroPie/roms/gb/Mystic Quest (Germany).zip'
    command = '/opt/retropie/emulators/retroarch/bin/retroarch -L /opt/retropie/libretrocores/lr-gambatte/gambatte_libretro.so --config /opt/retropie/configs/gb/retroarch.cfg "/home/pi/RetroPie/roms/gb/Mystic Quest (Germany).zip'


# read the settings file
def readSettings():
    global settings
    global scriptBasePath

    settings = configparser.ConfigParser()
    settings.read(scriptBasePath + 'settings.ini')


# read RetroArch configuration parameters from several files (first hit counts): Content, System, All
def getParameterFromConfig(system, parameter):
    config = configparser.ConfigParser()

    # Content
    # TODO get parameter from content override

    # Core
    # TODO get parameter from core override

    # System
    try: 
        f = open(configBasePath + system + '/retroarch.cfg')
        c = '[dummy]\n' + f.read()

        config.read_string(c)
        retVal = config.get('dummy', parameter)

        return retVal
    except configparser.NoOptionError:
        print('No system specific parameter found')

    # All
    try: 
        f = open(configBasePath + 'all/retroarch.cfg')
        c = '[dummy]\n' + f.read()

        config.read_string(c)
        retVal = config.get('dummy', parameter)

        return retVal
    except configparser.NoOptionError:
        print('No default parameter found')

    return 'n/a'


# get the save directories from RetroArch configuration
def getSaveDirectories():
    global savefile_directory
    global savestate_directory

    savefile_directory = getParameterFromConfig(system, 'savefile_directory')
    if savefile_directory in ('n/a', '"default"'):
        savefile_directory = os.path.dirname(rom)

    savestate_directory = getParameterFromConfig(system, 'savestate_directory')
    if savestate_directory in ('n/a', '"default"'):
        savestate_directory = os.path.dirname(rom)


# get a list of battery saves, save states and screenshots
def getSaveFiles(system, rom):
    config = configparser.ConfigParser()
    config.read(scriptBasePath + 'systems.ini')

    global savefile_extensions
    global savestate_extensions

    savefile_extensions = config.get(system, 'savefile')
    savestate_extensions = config.get(system, 'savestate')

    game = os.path.basename(rom)
    game = game.rsplit('.', 1)[0]
    
    global savefiles 
    savefiles = set(glob.glob(savefile_directory + '/' + game + '.' + savefile_extensions))

    global savestates
    savestates = set(glob.glob(savestate_directory + '/' + game + '.' + savestate_extensions))

    global savestates_images
    savestates_images = set(glob.glob(savestate_directory + '/' + game + '.' + savestate_extensions + '.png'))

    savestates = set(savestates) - set(savestates_images)


# read theme file
def readTheme(name):
    global theme

    theme = configparser.ConfigParser()
    theme.read(scriptBasePath + 'themes/' + name + '/theme.ini')


# create a new notification using the theme and save it to /dev/shm/cloud-sync.png
def createNotification(direction, provider, status):
    global theme

    game = os.path.basename(rom)
    game = game.rsplit('.', 1)[0]

    command = ['convert']
    # settings
    command.append('-gravity NorthWest')
    # size
    command.append('-size ' + theme.get('notification', 'size'))
    # background color
    command.append('canvas:"' + theme.get('notification', 'background') + '"')
    # Game System and Name
    command.append('-pointsize ' + theme.get('game', 'fontsize') + ' -font ' + theme.get('game', 'font') + ' -style ' + theme.get('game', 'fontstyle') + ' -fill "' + theme.get('game', 'fontcolor') + '" -draw "text ' + theme.get('game', 'xy') + ' \'[' + system + '] ' + game + '\'"')
    # Battery Save
    if len(savefiles) > 0:
        command.append('-pointsize ' + theme.get('battery', 'fontsize') + ' -font ' + theme.get('battery', 'font') + ' -style ' + theme.get('battery', 'fontstyle') + ' -fill "' + theme.get('battery', 'fontcolor') + '" -draw "text ' + theme.get('battery', 'xy') + ' \'Battery Save found\'"')
    else:
        command.append('-pointsize ' + theme.get('battery', 'fontsize') + ' -font ' + theme.get('battery', 'font') + ' -style ' + theme.get('battery', 'fontstyle') + ' -fill "' + theme.get('battery', 'fontcolor') + '" -draw "text ' + theme.get('battery', 'xy') + ' \'No Battery Save found\'"')
    # Save States
    command.append('-pointsize ' + theme.get('savestate', 'fontsize') + ' -font ' + theme.get('savestate', 'font') + ' -style ' + theme.get('savestate', 'fontstyle') + ' -fill "' + theme.get('savestate', 'fontcolor') + '" -draw "text ' + theme.get('savestate', 'xy') + ' \'' + str(len(savestates)) + ' Savestate(s) and ' + str(len(savestates_images)) + ' Screenshot(s) found\'"')

    command.append(scriptBasePath + '/themes/' + settings.get('settings', 'theme') + '/direction_' + direction + '.png -geometry ' + theme.get('direction', 'geometry') + ' -composite')
    command.append(scriptBasePath + '/themes/' + settings.get('settings', 'theme') + '/provider_' + provider + '.png -geometry ' + theme.get('provider', 'geometry') + ' -composite')
    command.append(scriptBasePath + '/themes/' + settings.get('settings', 'theme') + '/status_' + status + '.png -geometry ' + theme.get('status', 'geometry') + ' -composite')

    # output file
    command.append('/dev/shm/cloud-sync.png')

    print(' '.join(command))
    os.system(' '.join(command))


# show a notification
def showNotification(image, timeout):
    command = ['nohup',  'pngview', image]
    command.append('-t ' + timeout)
    command.append('-b 0')
    command.append('-l 10000')
    command.append('-x 16')
    command.append('-y 16')
    command.append('&>/dev/null')
    command.append('&')
    subprocess.Popen(command)


# print debug information
def printDebug():
    print('----------')
    print('System: ' + system)
    print('Emulator: ' + emulator)
    print('ROM: ' + rom)
    print('Command: ' + command)
    print('Savefile directory: ' + savefile_directory)
    print('Savefile extensions: ' + savefile_extensions)
    print('Savefiles:')
    print(savefiles)
    print('Savestate directory: ' + savestate_directory)
    print('Savestate extensions: ' + savestate_extensions)
    print('Savestates:')
    print(savestates)
    print('Savestate images:')
    print(savestates_images)


if __name__ == '__main__':
    __main__(sys.argv[1:])