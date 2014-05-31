import wiringpi2 as wpi
import sys
import logging
import time as tm
import conf


class Zone(object):
    '''crea oggetti di tipo zona, inizializzando rele' switch e pulsanti'''
    def __init__(self, pin_b, pin_p, pin_r, position):
        super(Zone, self).__init__()
        self.pin_b = pin_b
        self.pin_p = pin_p
        self.pin_r = pin_r
        self.position = position
        self.timeread = [0.0 for r in range(4)]
        self.switch = 0
        self.pushbutton = 0
        self.valve = 0
        self.state = {'switch':0, 'pushbutton':0, 'valve':0}
        wpi.pinMode(self.pin_b, 0)
        wpi.pinMode(self.pin_p, 0)
        wpi.pinMode(self.pin_r, 1)
        wpi.digitalWrite(self.pin_r, 0)
        logging.debug('inizializzata valvola numero %s'%position)

    def close(self):
        wpi.digitalWrite(self.pin_r,0)
        wpi.pinMode(self.pin_r,0)
        wpi.pinMode(self.pin_b,0)
        wpi.pinMode(self.pin_p,0)
        return 0

    def on(self):
        if wpi.digitalRead(self.pin_r) == 0:
            wpi.digitalWrite(self.pin_r, 1)
            return 0
        else:
            return 1

    def off(self):
        if wpi.digitalRead(self.pin_r) == 1:
            wpi.digitalWrite(self.pin_r, 0)
            return 0
        else:
            return 1

    def read(self, toread):
        if toread == 'switch':
            if (tm.time() - self.timeread[0]) > 0.01:
                self.timeread[0] = tm.time()
                self.switch = int(wpi.digitalRead(self.pin_b))
            return self.switch
        if toread == 'pushbutton':
            if (tm.time() - self.timeread[1]) > 0.01:
                self.timeread[1] = tm.time()
                self.pushbutton = int(wpi.digitalRead(self.pin_p))
            return self.pushbutton
        if toread == 'valve':
            if (tm.time() - self.timeread[2]) > 0.01:
                self.timeread[2] = tm.time()
                self.valve = int(wpi.digitalRead(self.pin_r))
            return self.valve
        # if toread == 'all':
        #     if (tm.time() - self.timeread[3]) > 0.01:
        #         self.timeread[3] = tm.time()
        #         self.state['switch'] = int(wpi.digitalRead(self.pin_b))
        #         self.state['pushbutton'] = int(wpi.digitalRead(self.pin_p))
        #         self.state['valve'] = int(wpi.digitalRead(self.pin_r))
        #         logging.debug('letta valvola numero %s'%self.position)
        #         logging.debug('%s'%self.state)
        #     return self.state


def resetpins_exit():
    '''funzione da chiamare prima di chiudere il programma
    riporta tutte le GPIO a 0 e le imposta come input
    '''
    for r in range(conf.numerozone):
        wpi.digitalWrite(conf.GPIO_r[r], 0)
        wpi.pinMode(conf.GPIO_r[r], 0)
        wpi.pinMode(conf.GPIO_b[r], 0)
        wpi.pinMode(conf.GPIO_p[r], 0)
    wpi.pinMode(conf.dataPin, 0)
    wpi.pinMode(conf.clockPin, 0)
    wpi.pinMode(conf.latchPin, 0)
    logging.info('Ho spento tutto e portato tutte le gpio come input')
    return 0

def alloff(all_valve):
    '''restituisce un valore booleano che indica
    se le valvole sono tutte spente
    '''
    result = True
    for i in range(len(all_valve)):
        result = result and (all_valve[i].read('valve') == 0)
    return result

