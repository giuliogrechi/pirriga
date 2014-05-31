'''modulo che definisce le variabili da impostare
GPIO_b sono gli switch
GPIO_p sono i pulsanti
GPIO_r sono i rele'
dataPin, clockPin, latchPin si riferiscono allo shift register
'''

file_program = '/var/www/files_test/program.txt'
filelog = '/home/pi/pirrigami/current/log.txt'
filestdout = '/home/pi/pirrigami/current/stdout.txt'
filestderr = '/home/pi/pirrigami/current/stderr.txt'
file_lastconf = '/home/pi/pirrigami/current/lastconf.txt'
numerozone = 4
GPIO_b = 6, 14, 10, 11
GPIO_p = 0, 1, 2, 3
GPIO_r = 4, 5, 12, 13
dataPin, clockPin, latchPin = 7, 16, 15


import sys
import wiringpi2 as wpi
from datetime import datetime
import logging
import Queue
if ((len(GPIO_r) != len(GPIO_p)) or (len(GPIO_r) != len(GPIO_b)) or
                 (len(GPIO_b) != len(GPIO_p)) or (len(GPIO_r) != numerozone)):
    '''controllo impostazione GPIO'''
    logging.critical("errore nell'assegnazione delle gpio " +
          '(pulsanti e interruttori sono in numero diverso)')
    sys.exit(0)

'''parametri preimpostati all'avvio, da non modificare'''
start = [datetime(year=2000,month=01,day=01) for i in range(numerozone)]
end   = [datetime(year=2000,month=01,day=02) for i in range(numerozone)]
days  = ['lunedi','martedi','mercoledi',
         'giovedi','venerdi','sabato','domenica']
'''assegnazione numeri ai pin dello shift register (dal 100 in su)'''
pinBase = 100
RS  = pinBase + 0
E   = RS  + 1
DB4 = E + 1
DB5 = DB4 + 1
DB6 = DB5 + 1
DB7 = DB6 + 1
'''setup iniziale wiringpi'''
wpi.wiringPiSetup()
wpi.pinMode(dataPin, 1)
wpi.pinMode(clockPin, 1)
wpi.pinMode(latchPin, 1)
'''inizializzazione shift register e lcd -- da testare'''
wpi.sr595Setup(pinBase, 6, dataPin, clockPin, latchPin)
lcd = wpi.lcdInit(
    4, 16, 4,
    RS, E, DB4, DB5, DB6, DB7,
    0,0,0,0
    )
logtime = Queue.Queue()
lcdput = Queue.Queue()
