# log to TSV file
import time


def log_metmini_data_tsv(metmini_data):
    """

    :param metmini_data:
    :return:
    """
    metmini_data_rec = time.ctime() + '\t' +\
        metmini_data['pressure'].__str__() + '\t' +\
        metmini_data['ptrend'] + '\t' +\
        metmini_data['wind_dir'] + '\t' +\
        metmini_data['wind_strength'] + '\t' +\
        metmini_data['forecast'] + '\t' +\
        metmini_data['bforecast'] + '\t' +\
        metmini_data['oforecast']

    fpOut = open("/tmp/metmini_data.tsv", "a")
    print >> fpOut, metmini_data_rec
    fpOut.flush()
    fpOut.close()
