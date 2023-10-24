import mysql.connector


def connect_database(db_name):
    """

    :return:
    """
    mydb = mysql.connector.connect(
        host="erminserver.localdomain",
        database=db_name,
        user="metmini",
        password="metmini"
    )

    mycursor = mydb.cursor()

    return (mydb, mycursor)
