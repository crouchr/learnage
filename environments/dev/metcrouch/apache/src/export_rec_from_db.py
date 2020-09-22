# prototyping utility script to be used to export records from metminidb Table suitable for graphing in Excel
import connect_db




def main():
    database_name = "metminidb"
    table_name = "actual"
    export_file = "metmini-actual.tsv"
    mydb, mycursor = connect_db.connect_database(database_name)

    low_id  = input("Lowest ID  (to export) : ")
    high_id = input("Highest ID (to export) : ")

    sql = "SELECT pressure, wind_deg, temp FROM " + table_name.lower() + " WHERE location='Stockcross, UK' AND id >= " + low_id.__str__() + " AND id <= " + high_id.__str__()
    print(sql)

    mycursor.execute(sql)
    records = mycursor.fetchall()

    fp_out = open(export_file , "w")
    for row in records:
        pressure = row[0]
        wind_deg = row[1]
        temp = row[2]
        csv_rec = pressure.__str__() + "\t" + wind_deg.__str__() + "\t" + temp.__str__() + "\n"
        print(csv_rec)
        fp_out.write(csv_rec)

    fp_out.close()


if __name__ == '__main__':
    main()
