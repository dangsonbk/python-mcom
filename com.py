import serial
import serial.tools.list_ports
import msvcrt
import time
import sys

EXCEPT_LIST = ["RIM"]
OPENNING = ""
SPEED = 115200
ser = serial.Serial(None, SPEED, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, None, False, False, None, False, None)

def kbfunc():
    if msvcrt.kbhit():
        return msvcrt.getch()
    else:
        return False

def serial_ports():
    result = []
    ports = serial.tools.list_ports.comports()

    for port in ports:
        for except_port in EXCEPT_LIST:
            if except_port not in port[1]:
                if "OSBDM/OSJTAG" in port[1]:
                    result.append([port[0],"OSBDM/OSJTAG"])
                else:
                    result.append([port[0],port[1]])
    return result

def do_command(command):
    global OPENNING
    global SPEED
    if "open" in command:
        com_port = command[5:].upper()
        try:
            ser.port = com_port
            ser.open()
            OPENNING = com_port
            print com_port, "opened successfully"
            ser.flushInput()    #flush input buffer, discarding all its contents
            ser.flushOutput()   #flush output buffer, aborting current output
            print "Serial port buffers cleared"
            print "--------------------------------------------------"
            try:
                while True:
                    # Shell
                    key = kbfunc();
                    if key!=False:
                        ser.write(key)
                    if ser.inWaiting() > 0:
                        sys.stdout.write(ser.read(1))
            except KeyboardInterrupt:
                ser.close()
                print ""
                print "CLI terminated"
        except Exception as inst:
            print inst

    if "c" == command:
        if OPENNING!="":
            try:
                ser.port = OPENNING
                ser.close()
                print OPENNING, "closed successfully"
                OPENNING = ""
            except Exception as inst:
                print inst

    if "l" == command:
        print "-------------------COM list-----------------------"
        ports = serial_ports()
        for port in ports:
            print port
        print "--------------------------------------------------"
        if OPENNING!="":
            print "-------------------COM opening--------------------"
            print OPENNING
            print "--------------------------------------------------"

    if "s" in command:
        if command[2:] != "":
            SPEED = command[2:]
            ser.baudrate = int(SPEED)
        print "Current baudrate:", str(ser.baudrate)

    if "h" == command:
        print "Command list:"
        print "open [com port] : open com port"
        print "c               : close currently openning com port"
        print "l               : list all com ports"
        print "s [com speed]   : set speed"
        print "s               : get speed"

if __name__ == '__main__':
    print "-------------------COM list-----------------------"
    ports = serial_ports()
    for port in ports:
        print port
    print "--------------------------------------------------"
    while(True):
        print ">",
        command = raw_input();
        if command == "q":
            print "exit minicom"
            exit()
        else:
            do_command(command)