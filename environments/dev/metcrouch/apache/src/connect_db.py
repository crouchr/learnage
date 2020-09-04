import mysql.connector

def connect_database():
    """

    :return:
    """
    mydb = mysql.connector.connect(
        host="erminserver.localdomain",
        database="metminidb",
        user="metmini",
        password="metmini"
    )

    mycursor = mydb.cursor()

    return (mydb, mycursor)
