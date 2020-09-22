# prototyping utility script to be used to export records from metminidb Table suitable for graphing in Excel

import connect_db

import low_pass_filter


def main():
    database_name = "metminidb"
    table_name = "actual"
    export_file = "metmini-actual.tsv"
    last_wind_deg = 0
    wind_deg_raw = []
    window_size = 10

    mydb, mycursor = connect_db.connect_database(database_name)

    low_id  = input("Lowest ID  (to export) : ")
    high_id = input("Highest ID (to export) : ")

    sql = "SELECT pressure, wind_deg, temp FROM " + table_name.lower() + " WHERE location='Stockcross, UK' AND id >= " + low_id.__str__() + " AND id <= " + high_id.__str__()
    #print(sql)

    mycursor.execute(sql)
    records = mycursor.fetchall()

    # perform low pass filtering on wind_deg values
    for row in records:
        wind_deg_raw.append(row[1])
    wind_deg_filtered = low_pass_filter.low_pass(wind_deg_raw, window_size)

    # low-pass filter and add the differential values
    fp_out = open("filtered_wind_deg.tsv", "w")
    for wind_deg in wind_deg_filtered:
        wind_deg_diff = wind_deg - last_wind_deg
        csv_rec = wind_deg.__str__() + "\t" + wind_deg_diff.__str__() + "\n"
        fp_out.write(csv_rec)
        last_wind_deg = wind_deg
    fp_out.close()

    #
    fp_out = open(export_file, "w")
    header = "pressure\ttemp\twind_deg\twind_deg_diff\n"
    fp_out.write(header)
    for row in records:
        pressure = row[0]
        wind_deg = row[1]
        temp = row[2]
        wind_deg_diff = wind_deg - last_wind_deg
        csv_rec = pressure.__str__() + "\t" + temp.__str__() + "\t" + wind_deg.__str__() + "\t" + wind_deg_diff.__str__() + "\n"
        fp_out.write(csv_rec)
        last_wind_deg = wind_deg

    fp_out.close()

    print("Finished")


if __name__ == '__main__':
    main()
