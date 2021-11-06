import sys
import getopt
import configparser
import os
import glob
import subprocess
import time
import logging


def __main__(argv):
    # initialization
    configBasePath, scriptBasePath = __init__()
    direction, system, emulator, rom, command = getParameters(argv)

    # read settings and theme
    settings = readSettings(scriptBasePath)
    theme = readTheme(scriptBasePath, settings.get('settings', 'theme'))
    
    # for DEBUG purposes
    if rom == '':
        direction, system, emulator, rom, command = fillParametersForDebug()

    # get game name from ROM path
    game = getGameFromROM(rom)

    # get allowed save file extensions
    savefile_extensions, savestate_extensions = getSaveExtensions(scriptBasePath, system)

    # get LOCAL saves
    localSavefile_directory, localSavestate_directory = getLocalSaveDirectories(configBasePath, system, rom)
    localSavefiles, localSavestates, localSavestates_images = getLocalSaveFiles(localSavefile_directory, localSavestate_directory, game, savefile_extensions, savestate_extensions)


    rCloneRemoteType = getRcloneRemoteType(settings.get('settings', 'remote'))


    # create notification PNG
    createNotification(scriptBasePath, settings, theme, direction, rCloneRemoteType, 'sync', system, game, localSavefiles, localSavestates, localSavestates_images)
    showNotification('/dev/shm/cloud-sync.png', settings.get('settings', 'notification_timeout'))
    time.sleep(3)
    createNotification(scriptBasePath, settings, theme, direction, rCloneRemoteType, 'ok', system, game, localSavefiles, localSavestates, localSavestates_images)
    showNotification('/dev/shm/cloud-sync.png', settings.get('settings', 'notification_timeout'))


# initalize the script
# returns configBasePath, scriptBasePath
def __init__():
    logging.basicConfig(filename='/dev/shm/cloud-sync.log', format='%(asctime)s: %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.info('Script started')

    configBasePath = '/opt/retropie/configs/'
    scriptBasePath = os.path.dirname(sys.argv[0]) + '/'

    return configBasePath, scriptBasePath


# extract given RetroArch parameters into global variables
# returns direction, system, emulator, rom, command
def getParameters(argv):
    logging.debug('getting parameters from call...')

    direction = ''
    system = ''
    emulator = ''
    rom = ''
    command = ''

    try:
        opts, args = getopt.getopt(argv, 'hd:s:e:r:c:', ['direction=', 'system=', 'emulator=', 'rom=', 'command='])
    except getopt.GetoptError:
        logging.error('wrong call to script')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('Usage')
            print('   cloud-sync.py -s <system> -e <emulator> -r <rom> -c <command>')
            print('   cloud-sync.py --system <system> --emulator <emulator> --rom <rom> --command <command>')
            sys.exit()
        elif opt in ('-d', '--direction'):
            direction = arg
            logging.debug('got parameter --direction: {0}'.format(arg))
        elif opt in ('-s', '--system'):
            system = arg
            logging.debug('got parameter --system: {0}'.format(arg))
        elif opt in ('-e', '--emulator'):
            emulator = arg
            logging.debug('got parameter --emulator: {0}'.format(arg))
        elif opt in ('-r', '--rom'):
            rom = arg
            logging.debug('got parameter --rom: {0}'.format(arg))
        elif opt in ('-c', '--command'):
            command = arg
            logging.debug('got parameter --command: {0}'.format(arg))

    return direction, system, emulator, rom, command


# fill variables if no RetroArch parameters given for DEBUG purposes
def fillParametersForDebug():
    direction = 'down'
    system = 'gb'
    emulator = 'lr-gambatte'
    rom = '/home/pi/RetroPie/roms/gb/Mystic Quest (Germany).zip'
    command = '/opt/retropie/emulators/retroarch/bin/retroarch -L /opt/retropie/libretrocores/lr-gambatte/gambatte_libretro.so --config /opt/retropie/configs/gb/retroarch.cfg "/home/pi/RetroPie/roms/gb/Mystic Quest (Germany).zip'

    logging.debug('DEBUG parameter --direction: {0}'.format(direction))
    logging.debug('DEBUG parameter --system: {0}'.format(system))
    logging.debug('DEBUG parameter --emulator: {0}'.format(emulator))
    logging.debug('DEBUG parameter --rom: {0}'.format(rom))
    logging.debug('DEBUG parameter --command: {0}'.format(command))

    return direction, system, emulator, rom, command


# read the settings file
# returns settings
def readSettings(scriptBasePath):
    logging.debug('reading settings.ini...')

    settings = configparser.ConfigParser()
    settings.read(scriptBasePath + 'settings.ini')

    return settings

# get extensions to savefiles and savestates
# returns savefile_extensions, savestate_extensions
def getSaveExtensions(scriptBasePath, system):
    logging.debug('getting save file extensions...')

    config = configparser.ConfigParser()
    config.read(scriptBasePath + 'systems.ini')

    savefile_extensions = config.get(system, 'savefile')
    savestate_extensions = config.get(system, 'savestate')

    return savefile_extensions, savestate_extensions


# get the game name from ROM path
# returns game
def getGameFromROM(rom):
    game = os.path.basename(rom)
    game = game.rsplit('.', 1)[0]

    return game


# read RetroArch configuration parameters from several files (first hit counts): Content, System, All
# returns retVal (containing parameter value from first hit)
def getParameterFromConfig(configBasePath, system, parameter):
    logging.debug('getting value of "{0}" from configuration file "{1}"...'.format(parameter, system))

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

        logging.debug('found value "{0}" in system specific configuration'.format(retVal))

        return retVal
    except configparser.NoOptionError:
        logging.debug('no value found in system specific configuration')

    # All
    try: 
        f = open(configBasePath + 'all/retroarch.cfg')
        c = '[dummy]\n' + f.read()

        config.read_string(c)
        retVal = config.get('dummy', parameter)

        logging.debug('found value "{0}" in default configuration'.format(retVal))

        return retVal
    except configparser.NoOptionError:
        logging.debug('no value found in any configuration file')

    return 'n/a'


# get the LOCAL save directories from RetroArch configuration
# returns localSavefile_directory, localSavestate_directory
def getLocalSaveDirectories(configBasePath, system, rom):
    logging.debug('getting Save directories...')

    localSavefile_directory = getParameterFromConfig(configBasePath, system, 'savefile_directory')
    if localSavefile_directory in ('n/a', '"default"'):
        localSavefile_directory = os.path.dirname(rom)
        logging.debug('set value to "{0}"'.format(localSavefile_directory))

    localSavestate_directory = getParameterFromConfig(configBasePath, system, 'savestate_directory')
    if localSavestate_directory in ('n/a', '"default"'):
        localSavestate_directory = os.path.dirname(rom)
        logging.debug('set value to "{0}"'.format(localSavestate_directory))

    logging.info('Local Savefile directory set to {0}'.format(localSavefile_directory))
    logging.info('Local Savestate directory set to {0}'.format(localSavestate_directory))

    return localSavefile_directory, localSavestate_directory


# get a list of LOCAL battery saves, save states and screenshots
# returns return localSavefiles, localSavestates, localSavestates_images
def getLocalSaveFiles(localSavefile_directory, localSavestate_directory, game, savefile_extensions, savestate_extensions):  
    logging.debug('getting local save files...')

    localSavefiles = set(glob.glob(localSavefile_directory + '/' + game + '.' + savefile_extensions))

    localSavestates_images = set(glob.glob(localSavestate_directory + '/' + game + '.' + savestate_extensions + '.png'))

    localSavestates = set(glob.glob(localSavestate_directory + '/' + game + '.' + savestate_extensions))
    localSavestates = set(localSavestates) - set(localSavestates_images)

    logging.info('found local savefiles: {0}'.format(localSavefiles))
    logging.info('found local savestates: {0}'.format(localSavestates))
    logging.info('found local savestate images: {0}'.format(localSavestates_images))

    return localSavefiles, localSavestates, localSavestates_images


def getRemoteSaveFiles(system, game, savefile_extensions, savestate_extensions):
    #print('rclone ls' + settings.get('settings', 'remote'))
    pass


# read theme file
# returns theme
def readTheme(scriptBasePath, name):
    logging.debug('reading themes/{0}/theme.ini'.format(name))

    theme = configparser.ConfigParser()
    theme.read(scriptBasePath + 'themes/' + name + '/theme.ini')

    return theme


def getRcloneRemoteType(remote):
    logging.debug('Getting type of RCLONE remote path {0}'.format(remote))

    try:
        stdoutBytes = subprocess.run(['rclone',  'config',  'file'], capture_output=True).stdout
        stdout = stdoutBytes.decode('utf-8')
        configFile = stdout.replace('Configuration file is stored at:\n', '')
        configFile = configFile.replace('\n', '')
    
        logging.debug('RCLONE configuration at {0}'.format(configFile))

        remoteName = remote[0:remote.index(':')]

        rCloneConfig = configparser.ConfigParser()
        rCloneConfig.read(configFile)
        rCloneRemoteType = rCloneConfig.get(remoteName, 'type')

        logging.debug('Got type of "{0}"'.format(rCloneRemoteType))

    except:
        logging.error('Error while getting type of RCLONE remote type')
        sys.exit(2)
    
    return rCloneRemoteType


# create a new notification using the theme and save it to /dev/shm/cloud-sync.png
def createNotification(scriptBasePath, settings, theme, direction, provider, status, system, game, localSavefiles, localSavestates, localSavestates_images):
    logging.debug('creating notification PNG...')
    
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
    if len(localSavefiles) > 0:
        command.append('-pointsize ' + theme.get('battery', 'fontsize') + ' -font ' + theme.get('battery', 'font') + ' -style ' + theme.get('battery', 'fontstyle') + ' -fill "' + theme.get('battery', 'fontcolor') + '" -draw "text ' + theme.get('battery', 'xy') + ' \'Battery Save found\'"')
    else:
        command.append('-pointsize ' + theme.get('battery', 'fontsize') + ' -font ' + theme.get('battery', 'font') + ' -style ' + theme.get('battery', 'fontstyle') + ' -fill "' + theme.get('battery', 'fontcolor') + '" -draw "text ' + theme.get('battery', 'xy') + ' \'No Battery Save found\'"')
    # Save States
    command.append('-pointsize ' + theme.get('savestate', 'fontsize') + ' -font ' + theme.get('savestate', 'font') + ' -style ' + theme.get('savestate', 'fontstyle') + ' -fill "' + theme.get('savestate', 'fontcolor') + '" -draw "text ' + theme.get('savestate', 'xy') + ' \'' + str(len(localSavestates)) + ' Savestate(s) and ' + str(len(localSavestates_images)) + ' Screenshot(s) found\'"')

    command.append(scriptBasePath + '/themes/' + settings.get('settings', 'theme') + '/direction_' + direction + '.png -geometry ' + theme.get('direction', 'geometry') + ' -composite')
    command.append(scriptBasePath + '/themes/' + settings.get('settings', 'theme') + '/provider_' + provider + '.png -geometry ' + theme.get('provider', 'geometry') + ' -composite')
    command.append(scriptBasePath + '/themes/' + settings.get('settings', 'theme') + '/status_' + status + '.png -geometry ' + theme.get('status', 'geometry') + ' -composite')

    # output file
    command.append('/dev/shm/cloud-sync.png')

    logging.debug(' '.join(command))

    os.system(' '.join(command))


# show a notification
def showNotification(image, timeout):
    logging.debug('show notification PNG...')
    
    command = ['nohup',  'pngview', image]
    command.append('-t ' + timeout)
    command.append('-b 0')
    command.append('-l 10000')
    command.append('-x 16')
    command.append('-y 16')
    command.append('&>/dev/null')
    command.append('&')
    subprocess.Popen(command)


if __name__ == '__main__':
    __main__(sys.argv[1:])