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
    location = input("Location : ")
    if location == '':
        location = 'Stockcross, UK'

    sql = """SELECT pressure, wind_deg, temp FROM %s WHERE location = %s AND id >= %s AND id <= %s"""
    sql = "SELECT id, pressure, wind_deg, temp, rain, humidity FROM " + table_name.__str__() + " WHERE location = '" + location + "' AND id >= " + low_id.__str__() + " AND id <= " + high_id.__str__()
    print("SQL : " + sql)
    mycursor.execute(sql)
    records = mycursor.fetchall()
    print("Number of records retrieved : " + len(records).__str__())

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
    header = "id\tpressure\twind_deg\trainx100\twind_deg_diff\ttemp\thumidity\n"
    fp_out.write(header)
    for row in records:
        id = row[0]
        pressure = (row[1] - 950) * 4   # multiplication to make visible in graph only
        wind_deg = row[2]
        temp = row[3]
        rain = row[4] * 100 # make it appear in the graph
        humidity = row[5]

        wind_deg_diff = wind_deg - last_wind_deg
        csv_rec = id.__str__() + "\t" + pressure.__str__() + "\t" + wind_deg.__str__() + "\t" + rain.__str__()  + "\t" + wind_deg_diff.__str__() + "\t" + temp.__str__() + "\t" + humidity.__str__() + "\n"
        fp_out.write(csv_rec)
        last_wind_deg = wind_deg
        print(csv_rec)

    fp_out.close()

    print("Finished")


if __name__ == '__main__':
    main()
