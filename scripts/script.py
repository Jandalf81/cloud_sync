import sys
import getopt

def __main__(argv):
    global system
    global emulator
    global rom
    global command

    getParameters(argv)


def getParameters(argv):
    system = ''
    emulator = ''
    rom = ''
    command = ''

    try:
        opts, args = getopt.getopt(argv, 'hs:e:r:c:', ['system=', 'emulator=', 'rom=', 'command='])
    except getopt.GetoptError:
        print('FEHLER' + sys.stderr)
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

    print('System: ', system)
    print('Emulator: ', emulator)
    print('ROM: ', rom)
    print('Command: ', command)

    f = open('/dev/shm/py.txt', 'w')
    f.write('System: ' + system)
    f.write('Emulator: ' + emulator)
    f.write('ROM: ' + rom)
    f.write('Command: ' + command)
    f.close()


if __name__ == '__main__':
    __main__(sys.argv[1:])