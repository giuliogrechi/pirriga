import logging
from datetime import datetime
import threading
import time as tm
import Queue
import subprocess
from copy import deepcopy

import inout
# from pirriga_threads import restart
from valve import alloff, Zone
import conf

class Button_Thread(threading.Thread):
    def __init__(self, all_valve):
        self.all_valve = all_valve
        self.numerozone = len(self.all_valve)
        self.statusNowBUTT = [self.all_valve[r].read('pushbutton')
                              for r in range(self.numerozone)]
        self.statusOldBUTT = deepcopy(self.statusNowBUTT)
        super(Button_Thread, self).__init__()
        logging.info('inizializzato thread pushbuttons')

    def run(self):
        while True:
            self.checkbutton()
            tm.sleep(0.02)

    def checkbutton(self):
        try:
            self.statusOldBUTT = deepcopy(self.statusNowBUTT)
            self.statusNowBUTT = [self.all_valve[r].read('pushbutton')
                                  for r in range(self.numerozone)]
            for r in range(self.numerozone):
                # logging.debug('entrato nel loop di controllo bottoni %s'%r)
                if (self.statusOldBUTT[r] == 1 and
                    self.statusNowBUTT[r] == 0):
                    logging.debug("identificato cambiamento bottone")
                    tm.sleep(0.3)
                    #TUTTI SU 0 !! ******************************************************************
                    if ((self.all_valve[0].read('pushbutton') == 0) and
                        (self.all_valve[1].read('pushbutton') == 0) and
                        (self.all_valve[2].read('pushbutton') == 0)):
                        '''combinazione di pulsanti per riavviare
                        il sistema in modo morbido
                        '''
                        logging.warning(
                            'premuti i pulsanti 0 1 2 - reboot system')
                        self.restart(self.all_valve)
                        conf.lcdput.put('restart')
                    if self.all_valve[r].read('pushbutton') == 0:
                        '''se dopo un secondo lo stato del pulsante e' ancora
                        su 0, chiama la funzione apposita
                        '''
                        logging.debug("identificato cambiamento switch")
                        if self.buttonpress(
                                            alloff(self.all_valve),
                                            self.all_valve[r]
                                            ):
                            ttime = inout.file_log(self.all_valve)
                            conf.logtime.put(ttime)
                    else:
                        pass
        except ValueError:
            logging.info('%s'%self.statusOld)
            logging.info('%s'%self.statusNowBUTT)
            logging.info('errore nella lettura del pulsante')
            pass

    def buttonpress(self, alloff, valve_bpress):
        logging.debug("funzione buttonpress avviata")
        if int(valve_bpress.read('switch')) == 1:
            #switch su automatico
            logging.info(
                'interruttore %s impostato su automatico nessuna azione'
                  %valve_bpress.position)
            return 0
        elif alloff == True:
            #switch e' su manuale e valvole sono tutte spente
            valve_bpress.on()
            logging.warning('interruttore %s impostato su manuale, tutte le altre valvole sono spente: ACCENSIONE'%valve_bpress.position)
        elif int(valve_bpress.read('valve')) == 1:
            #switch su manuale e valvola corrispondente e' accesa
            valve_bpress.off()
            logging.warning('interruttore %s impostato su manuale, e la valvola accesa: SPEGNIMENTO'%valve_bpress.position)
        else:
            logging.info('interruttore %s impostato su manuale, ma una delle altre valvole gia accesa.'%valve_bpress.position)
            return 0
        return 1

    def restart(self, all_valve):
        '''invia un comando di riavvio al terminale. successivamente esce;
        in ogni caso il programma riconosce il segnale sigterm e si chiude
        in modo soft se lo spegnimento o il riavvio della macchina sono morbidi
        '''
        inout.store_last_conf(all_valve)
        command = '/sbin/shutdown -r now'
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output = process.communicate()[0]
        logging.warning('%s'%output)


class Switch_Thread(threading.Thread):
    def __init__(self, all_valve):
        self.all_valve = all_valve
        self.numerozone = len(self.all_valve)
        self.statusNowSWI = [self.all_valve[r].read('switch')
                             for r in range(self.numerozone)]
        self.statusOld = deepcopy(self.statusNowSWI)
        super(Switch_Thread, self).__init__()
        logging.info('inizializzato thread switches')

    def run(self):
        while True:
            self.checkswitches()
            tm.sleep(0.02)

    def checkswitches(self):
        try:
            self.statusOld = deepcopy(self.statusNowSWI)
            logging.debug("ricopiato statusnow su statusOld")
            self.statusNowSWI = [self.all_valve[r].read('switch')
                                 for r in range(self.numerozone)]
            logging.debug("letto statusnow")
            logging.debug(self.statusNowSWI)
            for r in range(self.numerozone):
                logging.debug('entrato nel loop di controllo switch')
                logging.debug('STATUSOLD %s %s'%(r,self.statusOld[r]))
                logging.debug('STATUSNOW %s %s'%(r,self.statusNowSWI[r]))
                if (self.statusOld[r] +
                    self.statusNowSWI[r]) == 1:
                    '''se la somma e' 1, sono necessariamente
                    0 1 o vicevesa
                    '''
                    logging.debug('rilevato cambiamento switch')
                    tm.sleep(0.03)
                    if (self.statusOld[r] +
                        self.all_valve[r].read('switch')) == 1:
                        '''rilegge la configurazione, se e' rimasta stabile
                        dopo 30 millisecondi chiama la funzione apposita
                        '''
                        if self.switch_change(self.all_valve[r]):
                            ttime = inout.file_log(self.all_valve)
                            conf.logtime.put(ttime)
        except ValueError:
            logging.info('%s'%self.statusOld)
            logging.info('%s'%self.statusNowSWI)
            logging.info('errore nella lettura dello switch')
            pass

    def switch_change(self,valve_SWchange):
        '''se la valvola corrispondente era accesa la spegne altrimenti niente'''
        if valve_SWchange.read('valve') == 1:
            valve_SWchange.off()
            logging.warning(
                'interruttore variato: la valvola %s era accesa: SPEGNIMENTO'
                %valve_SWchange.position)
        else:
            logging.info(
                'interruttore variato: la valvola %s non era accesa: nessuna azione'
                %valve_SWchange.position)
            return 0
        return 1

