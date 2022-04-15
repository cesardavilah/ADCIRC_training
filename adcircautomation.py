import os
import time
import pexpect as px

import sys
import subprocess
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/cesar/PycharmProjects/CMPautomation/')
from MASTERController.Utilities import environment
from datetime import datetime
from uuid import uuid4
import os
from distutils.dir_util import copy_tree
from pathlib import Path
import pexpect as px
import pandas as pd
import errno


def create_id_adcirc():
    return datetime.now().strftime('%Y%m%d%H%M%S--') + str(uuid4())

def create_token_id_adcirc(eventid, extension:str):
    #.created, .prepped, .complete+exitcode, .extracted, .ras(temp), delete id ras, .runcomplete
    Path(environment.env_ADCIRCID()+eventid+'.'+extension).touch()

def check_eventid_complete(eventid):
    return os.path.isfile(environment.env_ADCIRCID()+eventid+'.complete0')

def prepare_simulation_adcprep(directory, cores):


    try:
        os.path.isfile(directory + "fort.14")
        os.path.isfile(directory + "fort.22")
        os.path.isfile(directory + "fort.15")
        os.path.isfile(directory + "adcprep")
        os.path.isfile(directory + "padcirc")
    except:
        IOError
        return

    # projectloc = environment.env_ADCIRCWORKING() + eventid + '/'
    # print(projectloc)
    child = px.spawn(directory+"adcprep", cwd=os.path.dirname(directory))

    index = child.expect([".*error.*", ".*ADCPREP.*"])

    if (index == 0):
        print("An error has been encountered")
        print(child.after)
        child.interact()
        return False
    else:
        child.expect(".*")
        child.sendline(str(cores))
        child.expect(".*")
        child.sendline("1")
        child.expect(".*")
        child.sendline("fort.14")
        child.expect(px.EOF)

        child2 = px.spawn(directory+"adcprep", cwd=os.path.dirname(directory))
        child2.expect(".*")
        child2.sendline(str(cores))
        child2.expect(".*")
        child2.sendline("2")
        child2.expect(px.EOF)
        print("Finished adcprep")
        # create_token_id_adcirc(directory, 'prepped')
        return True


def prepare_simulation(eventid, cores):
    inputloc = environment.env_ADCIRCINPUT()
    # eventid = datetime.now().strftime('%Y%m%d%H%M%S--') + str(uuid4())

    workloc = environment.env_ADCIRCWORKING()
    execloc = environment.env_ADCIRC()

    print(inputloc,eventid,workloc)
    try:
        os.path.isfile(inputloc + "fort.14")
        os.path.isfile(inputloc + "fort.22")
        os.path.isfile(inputloc + "fort.15")
        os.path.isfile(execloc + "adcprep")
        os.path.isfile(execloc + "padcirc")
    except:
        IOError
        return
    os.mkdir(workloc+eventid)
    copy_tree(inputloc, workloc+eventid)
    # print("copy"+execloc+" to "+workloc+eventid)
    copy_tree(execloc, workloc+eventid)

    create_token_id_adcirc(eventid, 'created')
    prepare_simulation_adcprep(eventid, cores)



def execute_simulation(directory, cores, SWAN=False):
    if SWAN:
        execute = "padcswan"
    else :
        execute = "padcirc"
    workloc = environment.env_ADCIRCWORKING()

    # executionpath = workloc+eventid+"/"+execute
    # print(executionpath)

    print("Simulating: "+ directory)

    os.chdir(directory)
    returns = os.system("time mpiexec -n " + str(cores) +" "+ directory+execute+' >> log.txt')
    # with open(directory+'log.txt', 'w') as out:
    #     returns = subprocess.call("mpiexec -n " + str(cores) +" "+ directory+execute, stdout=out)
    #TESTING COMMENT OUT WHEN NOT TESTING
    # returns = 0
    #END OF TESTING
    print("Simulation: "+directory+" finished with exit code "+str(returns))
    # create_token_id_adcirc(eventid, 'complete'+str(returns))
    return returns

def extract_simulation(eventid, node = 9390, file="fort.63"):
    if not check_eventid_complete(eventid):
        print("Simulation finished on a non 0 exit code, results can not be extracted.")

    workloc = environment.env_ADCIRCWORKING()
    path = workloc+eventid+'/'
    print(path)


    try:
        if (os.path.exists(path + 'fort_63_result.csv')):
            raise OSError
        with open(path + 'fort_63_result.csv', 'w') as out:
            try:
                with open(path + 'fort.63', 'r') as file:
                    cols = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
                    arr = pd.read_csv(path + 'fort.63', header=None, names=cols, delim_whitespace=True, dtype=str)

                    newarr = arr.loc[arr['a'] == str(node)]  # Same as observation point from NOAA in the laguna madre

                    towrite = ''
                    for index, row in newarr.iterrows():
                        # towrite += '%s, %s \n' % (row['a'], row['b'])
                        towrite += '%s \n' % (meter_to_foot(row['b']))
                        # print(towrite)
                    # print(towrite)
                    out.write(towrite)
            except IOError as e:
                print('Missing file fort.63')

    except OSError:
        print('Csv already exists. No overwrite enabled. Ignoring fort.63 file. ')

    try:
        if (os.path.exists(path + 'swan_HS_63_result.csv')):
            raise OSError
        try:
            with open(path + 'swan_HS.63', 'r') as file:
                cols = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
                arr = pd.read_csv(path + 'swan_HS.63', header=None, names=cols, delim_whitespace=True, dtype=str)

                newarr = arr.loc[arr['a'] == str(node)]  # Same as observation point from NOAA in the laguna madre

                with open(path + 'swan_HS_63_result.csv', 'w') as out:
                    towrite = ''
                    for index, row in newarr.iterrows():
                        towrite += '%s, %s \n' % (row['a'], row['b'])
                        # print(towrite)
                    # print(towrite)
                    out.write(towrite)
        except IOError as e:
            print('Missing file swan_HS.63')
    except OSError:
        print('Csv already exists. No overwrite enabled. Ignoring swan_HS.63 file. ')

    create_token_id_adcirc(eventid, 'extracted')
    #TESTING COMMENT OUT WHEN NOT TESTING
    eventid = '20191202183518--0e177f88-6ac4-48a4-b56f-b53a5c635469'
    #END OF TESTING

    create_token_id_adcirc(eventid, 'ras')

def meter_to_foot(meter:str):
    feet = 3.28084
    return str(round(float(meter) * feet, 8))







#
# cores = 4
# # #
# eventid = create_id_adcirc()
# prepare_simulation(eventid, cores)
# execute_simulation(eventid, cores)
#
# # eventid = '20191202183518--0e177f88-6ac4-48a4-b56f-b53a5c635469'
#
# extract_simulation(eventid, node=9390)