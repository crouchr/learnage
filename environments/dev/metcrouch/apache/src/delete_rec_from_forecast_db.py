# utility script to be used to delete records from any metminidb Table
import connect_db


def main():
    database_name = "metminidb"

    mydb, mycursor = connect_db.connect_database(database_name)

    print("MySQL Tables")
    print(" actual*     - table of measured weather via OpenWeatherApi")
    print(" forecasts   - table of forecasts")
    print(" metminilogs - logs from Weather station(s)")
    print()

    table_name = input("SQL Table name : ")

    low_id  = input("Lowest ID  (to delete) : ")
    high_id = input("Highest ID (to delete) : ")

    sql = "DELETE FROM " + table_name.lower() + " WHERE id >= " + low_id.__str__() + " AND id <= " + high_id.__str__()
    print(sql)

    val = (id)

    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record(s) deleted from database")


if __name__ == '__main__':
    main()
