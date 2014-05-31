'''modulo che riunisce le funzioni di lettura\scrittura dei files
linea programmazione:  ora,onoff,orainizio,minutoinizio,oredurata,minutidurata,giorni..
'''

import time as tm
import sys
from datetime import datetime, timedelta, time
from fcntl import flock, LOCK_EX, LOCK_UN, LOCK_SH, LOCK_NB
import logging

import conf


def openprogramlines(hour_pgm):
    '''legge file di programmazione e restituisce un insieme di liste
    richiede come argomento un oggetto di tipo datetime, restituisce
    una matrice le cui righe si riferiscono alle valvole, e le colonne
    si riferiscono alla programmazione della valvola corrispondente'''
    with open(conf.file_program, 'r') as f:
        try:
            flock(f, LOCK_SH | LOCK_NB) #non blocking lock
            line_p = f.read().splitlines()
            flock(f, LOCK_UN)
        except IOError:
            logging.info('%s utilizzato da un altro script'%conf.file_program)
            return 1
    if len(line_p) != conf.numerozone:
        logging.info('errore nella lettura: le righe sono diverse da %s'
                     %conf.numerozone)
        return 1
    progm = [line_p[i].split(',') for i in range(conf.numerozone)]
    return progm

def file_log(all_valve):
    '''legge lo stato di tutte le zone e lo inserisce in un file di log.
    in caso positivo resituisce l'epoch attuale, in caso negativo
    restituisce 1
    '''
    tm.sleep(0.05)
    value_list = [datetime.now().strftime('%a %d-%m-%y %H:%M:%S')]
    for i in range(conf.numerozone):
        value_list.append(str(all_valve[i].read('switch')))
    for i in range(conf.numerozone):
        value_list.append(str(all_valve[i].read('pushbutton')))
    for i in range(conf.numerozone):
        value_list.append(str(all_valve[i].read('valve')))
    log_str = ','.join(value_list)
    with open(conf.filelog, 'a') as fl:
        try:
            flock(fl, LOCK_EX | LOCK_NB)
            fl.write(log_str)
            fl.write('\n')
            flock(fl, LOCK_UN)
            logging.info('file log aggiornato')
        except IOError:
            logging.info('file %s utilizzato da un altro script'%conf.filelog)
            return 1
    utime = tm.time()
    return utime

def store_last_conf(all_valve):
    '''salva una linea separata da virgole, contenente l'epoch e lo
    stato delle sole valvole. In caso negativo restituisce 1
    '''
    lst_to_store = [str(tm.time())]
    for i in range(conf.numerozone):
        lst_to_store.append(str(all_valve[i].read('valve')))
    str_to_store = ','.join(lst_to_store)
    with open(conf.file_lastconf, 'w') as fts:
        try:
            flock(fts, LOCK_EX | LOCK_NB)
            fts.write(str_to_store)
            fts.write('\n')
            flock(fts, LOCK_UN)
            logging.info('scritta ultima configurazione su %s'
                         %conf.file_lastconf)
        except IOError:
            logging.info('file %s utilizzato da un altro script'
                         %conf.file_lastconf)
            return 1
    return 0

def read_last_conf():
    '''legge lo stato delle valvole dal file e lo inserisce in una lista
    il primo elemento della lista e' l'epoch in cui e' stata scritta
    gli altri sono gli stati in quell'istante
    '''
    with open(conf.file_lastconf, 'r') as flc:
        try:
            flock(flc, LOCK_SH | LOCK_NB) #non blocking lock
            line_last_con = flc.read().splitlines()
            flock(flc, LOCK_UN)
        except IOError:
            logging.info('file %s utilizzato da un altro script'
                         %conf.file_lastconf)
            return 1
    last_con = [line_last_con[0].split(',')]
    if len(last_con[0]) != (conf.numerozone + 1):
        logging.info('errore nella lettura: i termini sono diversi da %s'
                     %conf.numerozone)
        return 1
    return last_con[0]
