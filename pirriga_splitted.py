#!/usr/bin/python
# https://projects.drogon.net/raspberry-pi/wiringpi/pins/    numerazione pins
#linea programmazione:  ora,onoff,orainizio,minutoinizio,oredurata,minutidurata,giorni..

import sys
import subprocess
import signal
import wiringpi2 as wpi
import time as tm
from datetime import datetime, timedelta, time
from fcntl import flock, LOCK_EX, LOCK_UN, LOCK_SH, LOCK_NB
import logging

import conf
import inout
import valve
from valve import Zone, alloff #setup wiringpi all'interno
import lcdthread
import swbutt
import argparse


"""redirect standard e error output in un file prima di importare i moduli
personali
"""
# old_stdout = sys.stdout
# old_stderr = sys.stderr
# sys.stdout = open(conf.filestdout, 'a')
# sys.stderr = open(conf.filestderr, 'a')

numerozone = conf.numerozone

"""cattura dei segnali per la corretta terminazione
del programma anche in caso di riavvio
"""
def handler(signum=None, frame=None):
    quit()
for sig in [signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT]:
    signal.signal(sig, handler)

"""GPIO numerate con il metodo wiringpi"""
#wpi.wiringPiSetup() inserito in conf.py da testare se funziona


def hour_prog(alloff, pgm, valve_hp, fst_time):
    """controlla e gestisce lo stato della valvola k data la programmazione
    oraria contenuta nella lista pgm
    """
    hournow = datetime.now()
    gg = hournow.weekday()
    if valve_hp.read('switch') == 1:
         #RIPORTARE SU 0!********************************************
        logging.debug("valvola %s impostata su manuale"%str(valve_hp.position))
        pass
    elif pgm[1] == 'on':
        if conf.days[gg] in pgm:
            """ricalcola l'ora di inizio e fine solo se le la valvola e' spenta,
            (o e' la prima chiamata) e se siamo in un giorno corrispondente
            a quelli impostati.
            Se e' accesa deve prima essere spenta per ricalcolare.
            """
            logging.debug("oggi parte la valvola %s"%str(valve_hp.position))
            if valve_hp.read('valve') == 0 or fst_time == True:
                logging.debug("calcolo orario valvola %s"%valve_hp.position)
                conf.start[valve_hp.position] = datetime(
                                     year = int(hournow.strftime("%Y")),
                                     month = int(hournow.strftime("%m")),
                                     day = int(hournow.strftime("%d")),
                                     hour = int(pgm[2]),
                                     minute = int(pgm[3])
                                     )
                conf.end[valve_hp.position] = (
                                        conf.start[valve_hp.position] +
                                        timedelta(hours=int(pgm[4]),
                                                  minutes=int(pgm[5]))
                                        )
                logging.debug("start valvola %s: %s"
                      %(valve_hp.position,conf.start[valve_hp.position]))
                logging.debug("end valvola %s: %s"
                      %(valve_hp.position,conf.end[valve_hp.position]))
            if ((hournow > conf.start[valve_hp.position]) and
                    (hournow < conf.end[valve_hp.position])):
                """l'istruzione e' chiamata all'interno dell'if sui giorni
                la valvola viene accesa solo se e' un giorno impostato in pgm
                """
                if alloff:
                    valve_hp.on()
                    logging.warning("valvola %s accesa tramite programmazione"
                          %valve_hp.position)
                    return 1
                elif valve_hp.read('valve') == 1:
                    logging.debug("valvola %s gia' accesa"%valve_hp.position)
                    pass
                else:
                    logging.debug("si doveva accendere valvola %s\
                    ma un'altra valvola accesa"%valve_hp.position)
                    pass
        if ((valve_hp.read('valve') == 1) and
                (hournow > conf.end[valve_hp.position])):
            """controllo fatto anche se il giorno non e' corrispondente a
            quello impostato: nel caso end[k] sara' l'ultimo calcolato,
            necessariamente nel giorno passato
            """
            valve_hp.off()
            logging.warning("valvola %s spenta tramite programmazione"
                  %valve_hp.position)
            return 1
    elif (valve_hp.read('valve') == 1) and (pgm[1] != 'on'):
        """valvola impostata su off e accesa
        da spegnere; siamo sempre nel caso switch su automatico
        """
        valve_hp.off()
        logging.warning("valvola %s era accesa ma e' stata portata off -->spenta"
              %valve_hp.position)
        return 1
    else:
        pass
    return 0



def restart(all_valve_rst):
    """invia un comando di riavvio al terminale. successivamente esce;
    in ogni caso il programma riconosce il segnale sigterm e si chiude
    in modo soft se il lo spegnimento o il riavvio della macchina sono morbidi
    """
    inout.store_last_conf(all_valve_rst)
    command = "/sbin/shutdown -r now"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    logging.warning("%s"%output)
    quit()

def quit():
    '''ripristina lo stato iniziale delle GPIO e dello stdout/stderr'''
    valve.resetpins_exit()
    logging.warning("reset -----> uscita")
    # sys.stdout.flush()
    # sys.stdout.close()
    # sys.stderr.close()
    # sys.stdout = old_stdout
    # sys.stderr = old_stderr
    sys.exit(0)

def recall(sec, valve_rec):
    last_conf_list = inout.read_last_conf()
    if last_conf_list != 1:
        if ((tm.time() - (float)(last_conf_list[0])) < sec):
            #recupera l'ultima configurazione solo se e' stata salvata
            #meno di (sec) secondi prima
            logging.warning("ripristino ultima configurazione %s"
                            %last_conf_list)
            for i in range(numerozone):
                if int(last_conf_list[i + 1]) == 1: #RIPORTARE SU 0**********************************
                    valve_rec[i].on()
                    logging.warning("valvola %s accesa tramite configurazione"
                          %i)
                else:
                    pass
            return 0
        else:
            logging.info("ultima configurazione salvata piu' di %s sec fa"%sec)
            return 1

def main():
    try:
        logging.info("avvio script")
        lcd = lcdthread.Lcd_Thread(conf.lcd)
        lcd.setDaemon(True)
        lcd.start()
        logging.info("lcd avviato")
        #valve: inizializzazione di una lista di oggetti di tipo Zona

        valve = [Zone(conf.GPIO_b[r], conf.GPIO_p[r], conf.GPIO_r[r], r)
                 for r in range(numerozone)]
        recall(60.0, valve)

        """inizializzazione variabili di stato"""
        firstTime = True
        ttime = 0
        lcdtime = 0
        statusNow = [valve[r].read("all") for r in range(numerozone)]
        while True:
            #ricopia il vecchio status su status old
            statusOld = list(statusNow)
            statusNow = [valve[r].read("all") for r in range(numerozone)]
            #checking switches - da rivedere il debouncing
            for r in range(numerozone):
                if (statusOld[r]['switch'] +
                    statusNow[r]['switch']) == 1:
                    """se la somma e' 1, sono necessariamente
                    0 1 o vicevesa
                    """
                    tm.sleep(0.03)
                    if (statusOld[r]['switch'] +
                        valve[r].read('switch')) == 1:
                        """rilegge la configurazione, se e' rimasta stabile
                        dopo 30 millisecondi chiama la funzione apposita
                        """
                        if swbutt.switch_change(valve[r]):
                            ttime = inout.file_log(valve)
            #checking pushbuttons - da testare il debouncing
            for r in range(numerozone):
                if (statusOld[r]['pushbutton'] == 1 and
                    statusNow[r]['pushbutton'] == 0):
                    tm.sleep(1)
                    #TUTTI SU 0 !! ******************************************************************
                    if ((valve[0].read('pushbutton') == 1) and
                        (valve[1].read('pushbutton') == 1) and
                        (valve[2].read('pushbutton') == 1)):
                        """combinazione di pulsanti per riavviare
                        il sistema in modo morbido
                        """
                        logging.warning(
                            "premuti i pulsanti 0 1 2 - reboot system")
                        restart(valve)
                    if valve[r].read("pushbutton") == 0:
                        """se dopo un secondo lo stato del pulsante e' ancora
                        su 0, chiama la funzione apposita
                        """
                        if swbutt.buttonpress(alloff(valve), valve[r]):
                            ttime = inout.file_log(valve)
                    else:
                        pass

            #controllo file programmazione
            #scrittura log
            #scrittura lcd
            program_lines = inout.openprogramlines(datetime.now())
            if program_lines != 1:
                """se program_lines == 1 il file programmazione non e'
                consistente. non viene quindi invocata hour_prog().
                """
                for k in range(numerozone):
                    if hour_prog(
                        alloff(valve), program_lines[k],
                        valve[k], firstTime
                        ):
                        ttime = inout.file_log(valve)
            if (tm.time() - ttime) >  900:
                ttime = inout.file_log(valve)
            firstTime == False

    except KeyboardInterrupt:
        logging.warning("KeyboardInterrupt")
        inout.store_last_conf(valve)
        lcd.clearlcd()
        quit()

    except Exception, ex:
        logging.error('%s'%ex.__doc__)
        logging.error('%s'%ex.message)
        logging.error("Exception")
        inout.store_last_conf(valve)
        lcd.clearlcd()
        quit()

if __name__ == "__main__":

    opt = ['notset', 'debug', 'info', 'warning', 'error', 'critical']
    # OPT = [opt[i].upper() for i in range(len(opt))]
    # opt.extend(OPT)
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug",
                    help="specifica il livello di logging default WARNING",
                    choices=opt)

    args = parser.parse_args()
    if args.debug is None:
        loglevel = 'warning'
    else:
        loglevel = args.debug

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' %loglevel)
    logging.basicConfig(level=numeric_level,
                        filename='output.log',
                        format='[%(asctime)s][%(levelname)s](%(funcName)s)%(message)s')

    main()

