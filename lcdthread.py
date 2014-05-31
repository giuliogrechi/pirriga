import threading
import time as tm
import sys
import conf
import wiringpi2 as wpi
from datetime import datetime
import logging
import time as tm

'''Lcd  processo va avanti in modo indefinito fino a quando un altra
funzione non portera' la varibile stoplcd su True. Questo deve essere fatto
tutte le volte che si esce dal programma, quindi prima di ogni sys.exit, e
ogni qual volta si presentera' un eccezione che chiude il programma
'''


class Lcd_Thread(threading.Thread):
    def __init__(self, lcd_ob, valve_ob):
        self.lcd_ob = lcd_ob
        self.valve_ob = valve_ob
        self.timeclear = tm.time()
        logging.info('inizializzato thread lcd')
        super(Lcd_Thread, self).__init__()

    def run(self):
        while True:
            # tm.sleep(0.5)
            self.printlcd()

    def printlcd(self):
        if conf.lcdput.empty() == True:
            strstatus = ['off' for i in range(len(self.valve_ob))]
            for r in range(len(self.valve_ob)):
                if int(self.valve_ob[r].read('valve')) == 1:
                    strstatus[r] = 'on '
                else:
                    strstatus[r] = 'off'
            stringLCD0 = ''.join(['1-', strstatus[0], ' 2-', strstatus[1]])
            stringLCD1 = ''.join(['3-', strstatus[2], ' 4-', strstatus[3]])
            stringLCD2 = ''
            stringLCD3 = datetime.now().strftime('%H:%M:%S %d-%m')
            if (tm.time() - self.timeclear) > 10:
                wpi.lcdHome(self.lcd_ob)
                tm.sleep(0.005)
                wpi.lcdClear(self.lcd_ob)
                tm.sleep(0.005)
                self.timeclear = tm.time()
                # conf.lcd = wpi.lcdInit(
                #     4, 16, 4,
                #     conf.RS, conf.E, conf.DB4, conf.DB5, conf.DB6, conf.DB7,
                #     0,0,0,0
                #     )
                # self.lcd_ob = conf.lcd
            wpi.lcdPosition(self.lcd_ob, 0, 0)
            tm.sleep(0.005)
            wpi.lcdPuts(self.lcd_ob, stringLCD0)
            tm.sleep(0.005)
            wpi.lcdPosition(self.lcd_ob, 0, 1)
            tm.sleep(0.005)
            wpi.lcdPuts(self.lcd_ob, stringLCD1)
            tm.sleep(0.005)
            wpi.lcdPosition(self.lcd_ob, -4, 2)
            tm.sleep(0.005)
            wpi.lcdPuts(self.lcd_ob, stringLCD2)
            tm.sleep(0.005)
            wpi.lcdPosition(self.lcd_ob, -4, 3)
            tm.sleep(0.005)
            wpi.lcdPuts(self.lcd_ob, stringLCD3)
            tm.sleep(0.005)
        elif conf.lcdput.get() == 'restart':
            wpi.lcdHome(self.lcd_ob)
            tm.sleep(0.005)
            wpi.lcdClear(self.lcd_ob)
            tm.sleep(0.005)
            wpi.lcdPosition(self.lcd_ob, 0, 0)
            tm.sleep(0.005)
            wpi.lcdPuts(self.lcd_ob, 'RIAVVIO')
            tm.sleep(0.005)
            wpi.lcdPosition(self.lcd_ob, 0, 1)
            while True:
                wpi.lcdPuts(self.lcd_ob, '*')
                tm.sleep(0.5)
        else:
            pass

    def clearlcd(self):
        wpi.lcdHome(self.lcd_ob)
        tm.sleep(0.005)
        wpi.lcdClear(self.lcd_ob)
        tm.sleep(0.005)

