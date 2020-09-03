# log to TSV file
import time


def log_metmini_data_tsv(utc, metmini_data):
    """

    :param metmini_data:
    :return:
    """
    metmini_data_rec = utc.__str__() + '\t' +\
        time.ctime() + '\t' +\
        metmini_data['pressure'].__str__() + '\t' +\
        metmini_data['ptrend'] + '\t' +\
        metmini_data['wind_dir'] + '\t' +\
        metmini_data['wind_strength'] + '\t' + \
        metmini_data['location'] + '\t' + \
        metmini_data['forecast'] + '\t' +\
        metmini_data['bforecast'] + '\t' +\
        metmini_data['oforecast'] + '\t' +\
        metmini_data['clouds'] + '\t' +\
        metmini_data['coverage'] + '\t' +\
        metmini_data['notes'] + '\t' +\
        metmini_data['yest_rain'] + '\t' +\
        metmini_data['yest_wind'] + '\t' +\
        metmini_data['yest_min_temp'] + '\t' +\
        metmini_data['yest_max_temp'] + '\t' +\
        metmini_data['yest_notes'] + '\t' +\
        metmini_data['data_type']

    fpOut = open("/tmp/metmini_data.tsv", "a")
    print >> fpOut, metmini_data_rec
    fpOut.flush()
    fpOut.close()
