#!python3
import pyodbc
import time
from datetime import datetime

conn = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=s_bobl;pwd=347brrhr6TG2LfAQ;database=bobl354')
#  ^^^ 2 values must be change for your own program.

#  Since the CSIL SQL Server has configured a default database for each user, there is no need to specify it (<username>354)

cur = conn.cursor()

# to validate the connection, there is no need to change the following line

notDone=True
while notDone:
    choice=input("What would you like to do? Insert New passenger = 1, view Passenger list = 2, Booking = 3 : ")
    if choice=='1':
        #Inserting new Passenger
        cur.execute("SELECT MAX(passenger_id) FROM dbo.Passenger")
        row = cur.fetchone()
        sid=row[0]+1
        firstname = input("Enter your firstname: ")
        lastname = input("Enter your lastname: ")
        miles = 0

        sql = "INSERT INTO Passenger VALUES(?,?,?,?)"
        values = [sid,firstname,lastname,miles]
        cur.execute(sql,values)
        conn.commit()

        print("The profile for passenger '"+str(sid)+"' '"+firstname+"' '"+lastname+"' was created.")

        cur.execute('SELECT * from dbo.Passenger')
        row = cur.fetchone()
        while row:
            print (str(row[0]) + ' ' + str(row[1]) + ' '+ str(row[2]) + ' ' + str(row[3])  )
            row = cur.fetchone()
        

    elif choice=='2':
        #view Passenger list from input
        #check Flight_Instance table if it exists
        checkFI=True
        while checkFI:
            flightcode= input('Enter flight_code : ')
            departdate = input('Enter depart_date : ')
            sql = "SELECT * FROM Flight_Instance I WHERE I.flight_code LIKE '%s' AND I.depart_date= '%s' " % (flightcode,departdate)
            cur.execute(sql)
            row = cur.fetchone()
            if row==None:
                print("The inputted flight instance does not exist, please try again")
                checkFI=True
            else:
                sql = """SELECT P.passenger_id,P.first_name,P.last_name,P.miles,B.flight_code,B.depart_date,available_seats
                FROM Passenger P INNER JOIN Booking B ON P.passenger_id=B.passenger_id
                INNER JOIN Flight_instance F ON B.flight_code=F.flight_code
                AND B.depart_date=F.depart_date
                WHERE B.flight_code LIKE '%s' AND B.depart_date= '%s' """ % (flightcode,departdate)
            cur.execute(sql)
            row = cur.fetchone()
        
            print("")
            while row:
                print (str(row[0]) + ' ' + str(row[1]) + ' '+ str(row[2]) + ' ' + str(row[3])  + ' ' + str(row[4])+ ' ' + str(row[5])+ ' ' + str(row[6]) )
                avail=row[6]
                row = cur.fetchone()
            print("")    
            print("For flight_code "+flightcode+" and depart_date "+ departdate+", there are "+ str(avail)+" available seats.")
            print("")
            checkFI=False

    elif choice=='3':
        
        #checking if passenger id exists
        checkP=True
        #checking instance if it exists
        checkFI=True
        #checking trip if S or M, if neither then redo
        checkTrip=True

        while checkP:
            passengerid=input("Enter passenger_id for booking: ")
            sql="SELECT * FROM Passenger P WHERE P.passenger_id= '%s' " % (passengerid)
            cur.execute(sql)
            row = cur.fetchone()
            if row==None:
                print("The inputted passenger_id does not exist, please try again")
                checkP=True
            else:
                checkP=False
                #checking trip if S or M, if neither then redo
                while checkTrip:
                    trip=input("Is this a single or multi-city trip, type S or M?")
                    if trip=="S" or trip=="s":
                        checkTrip=False
                        while checkFI:
                            flightcode=input('Enter flight_code for Booking: ')
                            departdate = input('Enter depart_date for Booking: ')
                            sql = "SELECT * FROM Flight_Instance I WHERE I.flight_code LIKE '%s' AND I.depart_date= '%s' " % (flightcode,departdate)
                            cur.execute(sql)
                            row = cur.fetchone()
                            if row==None:
                                print("The inputted flight instance does not exist, please try again")
                                checkFI=True
                            elif row[4]<1:
                                checkFI=True
                                print("The inputted flight instance is FULL, there are no available seats. Please try again")
                            else:
                                sql = "INSERT INTO Booking VALUES ('%s','%s','%s')" % (flightcode,departdate,passengerid)
                                cur.execute(sql)
                                conn.commit()
                                print("Single trip booking has been completed.")
                                checkFI=False
                    elif trip=="M" or trip=="m":
                        checkTrip=False
                        while checkFI:
                            flightcode1=input('Enter flight_code for First Booking: ')
                            departdate1=input('Enter depart_date for First Booking: ')
                            flightcode2=input('Enter flight_code for Second Booking: ')
                            departdate2=input('Enter depart_date for Second Booking: ')

                            sql1 = "SELECT * FROM Flight_Instance I WHERE I.flight_code LIKE '%s' AND I.depart_date= '%s' " % (flightcode1,departdate1)
                            cur.execute(sql1)
                            row1 = cur.fetchone()
                            conn.commit()
                
                            sql2 = "SELECT * FROM Flight_Instance I WHERE I.flight_code LIKE '%s' AND I.depart_date= '%s' " % (flightcode2,departdate2)
                            cur.execute(sql2)
                            row2 = cur.fetchone()
                            conn.commit()
                    
                            #converting departdates into python dates
                            newdate1=time.strptime(departdate1, "%Y-%m-%d")
                            newdate2=time.strptime(departdate2, "%Y-%m-%d")

                            if row1==None:
                                print("The first inputted flight instance does not exist, please try again")
                                checkFI=True
                            elif row2==None:
                                print("The second inputted flight instance does not exist, please try again")
                                checkFI=True
                            elif newdate2 < newdate1:
                                print("The second inputted flight instance is earlier than the first inputted flight instance. Please try again")
                                checkFI=True
                            elif row1[4]<1:
                                checkFI=True
                                print("The first inputted flight instance is FULL, there are no available seats. Please try again")
                            elif row2[4]<1:
                                checkFI=True
                                print("The second inputted flight instance is FULL, there are no available seats. Please try again")
                            else:
                                checkFI=False
                                sql = "INSERT INTO Booking VALUES ('%s','%s','%s')" % (flightcode1,departdate1,passengerid)
                                cur.execute(sql)
                                conn.commit()
                                sql = "INSERT INTO Booking VALUES ('%s','%s','%s')" % (flightcode2,departdate2,passengerid)
                                cur.execute(sql)
                                conn.commit()
                                print("Multi-trip booking has been completed.")
                    else:
                        checkTrip=True
    else:
        notDone=True

    
#k=input("press close to exit")
conn.close()


