import helpers_adcirc as ha
import parsenam as pnam
import datetime
import shutil
import adcircautomation as aauto
import schedule
import time


def ADCIRC_SIM_AT_00():
    #MVP. Needs to catch er`rors still
    CORES = 14 #NUMBER OF CORES TO USE FOR COMPUTATION OF ADCIRC
    TEMPDIR = r'/media/sf_SHARED_FOLDER_VM/temp_adcirc/'
    ADCIRC_SIM_DIRECTORY = '/media/sf_SHARED_FOLDER_VM/automated_input/'
    ADCIRC_EXEC_DIRECTORY = '/media/sf_SHARED_FOLDER_VM/execution_files/'

    # ha.flush(TEMPDIR)
    # #Get date
    #
    cur_date = ha.get_current_date()
    # cur_date = '20220318'
    print(cur_date)
    forecast_production_hr = '00'
    ADCIRC_SIM_CURDATE = ADCIRC_SIM_DIRECTORY + cur_date



    #Download most recent NAM data
    ha.download_latest_NAM(searchString=":(U|V)GRD:10 m|PRES:surface:", SAVEDIR= TEMPDIR, date=cur_date)
    # Turn nam data into fort.22
    pnam.grab_fcst(date=cur_date, forecast_production_hr=forecast_production_hr, path=TEMPDIR, extension='.grib2')
    #Put nam data into corresponding folder
    shutil.move(TEMPDIR+'fort.22', ADCIRC_SIM_CURDATE+ '/fort.22')
    shutil.copy(ADCIRC_EXEC_DIRECTORY+'adcprep', ADCIRC_SIM_CURDATE+'/adcprep')
    shutil.copy(ADCIRC_EXEC_DIRECTORY+'padcirc', ADCIRC_SIM_CURDATE+'/padcirc')
    shutil.copy(ADCIRC_EXEC_DIRECTORY+'dem.vrt', ADCIRC_SIM_CURDATE+'/dem.vrt')




    #Prep
    aauto.prepare_simulation_adcprep(ADCIRC_SIM_CURDATE+'/', cores=CORES)


    #Execute
    aauto.execute_simulation(ADCIRC_SIM_CURDATE+'/', cores=CORES, SWAN=False)

    ha.prep_for_vcore(ADCIRC_SIM_DIRECTORY + cur_date, [ADCIRC_SIM_DIRECTORY + cur_date, '83', '-1'])


schedule.every().day.at("15:26").do(ADCIRC_SIM_AT_00)

def test_upload():
    import requests
    url = "https://vcore.utrgv.edu/adcirc"
    key = "3c6448c6-ef30-4046-878a-6acf0d8a9226"

    files = {'adcirc': ('dem.tiff', open('/media/sf_SHARED_FOLDER_VM/automated_input/20220329/dem.tiff', 'rb'))}
    r = requests.post(url, headers={'key': key}, files=files)
    print(r.content)


# ADCIRC_SIM_AT_00()

test_upload()




# while(True):
#     # schedule.run_pending()
#     test_upload()
#
#     time.sleep(20)
#     now = datetime.datetime.now()
#     print("Current date and time : ")
#     print(now.strftime("%Y-%m-%d %H:%M:%S"))
