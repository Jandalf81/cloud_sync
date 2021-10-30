import sys
import getopt
import configparser
import os
import glob


def __main__(argv):
    __init__()

    getParameters(argv)
    
    if rom == '':
        fillParametersForDebug()

    getSaveDirectories()

    getSaveFiles(system, savefile_directory, rom)

    printDebug()


def __init__():
    global configBasePath

    configBasePath = '/opt/retropie/configs/'


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


def fillParametersForDebug():
    global system
    global emulator
    global rom
    global command

    system = 'gb'
    emulator = 'lr-gambatte'
    rom = '/home/pi/RetroPie/roms/gb/Mystic Quest (Germany).zip'
    command = '/opt/retropie/emulators/retroarch/bin/retroarch -L /opt/retropie/libretrocores/lr-gambatte/gambatte_libretro.so --config /opt/retropie/configs/gb/retroarch.cfg "/home/pi/RetroPie/roms/gb/Mystic Quest (Germany).zip'


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


def getSaveDirectories():
    global savefile_directory
    global savestate_directory

    savefile_directory = getParameterFromConfig(system, 'savefile_directory')
    if savefile_directory in ('n/a', '"default"'):
        savefile_directory = os.path.dirname(rom)

    savestate_directory = getParameterFromConfig(system, 'savestate_directory')
    if savestate_directory in ('n/a', '"default"'):
        savestate_directory = os.path.dirname(rom)


def getSaveFiles(system, directory, rom):
    config = configparser.ConfigParser()
    config.read('/home/pi/RetroPie/scripts/cloud-sync/systems.ini')

    global savefile_extensions
    global savestate_extensions

    savefile_extensions = config.get(system, 'savefile')
    savestate_extensions = config.get(system, 'savestate')

    romWithoutExt = rom.rsplit('.', 1)[0]
    
    global savefiles 
    savefiles = set(glob.glob(romWithoutExt + '.' + savefile_extensions))

    global savestates
    savestates = set(glob.glob(romWithoutExt + '.' + savestate_extensions))

    global savestates_images
    savestates_images = set(glob.glob(romWithoutExt + '.' + savestate_extensions + '.png'))

    savestates = set(savestates) - set(savestates_images)


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