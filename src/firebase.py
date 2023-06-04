import sys
import pyrebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

'''
     prod: https://whitegate-fc568-default-rtdb.firebaseio.com
     test: https://whitegatetest-default-rtdb.firebaseio.com
'''
class Firebase:
    def __init__(self, account_file_name, database_url):
        self.cred = credentials.Certificate(account_file_name)
        firebase_admin.initialize_app(self.cred, {'databaseURL': database_url})
        self.ref = db.reference("/ResidentsDB/residents")

    def insert_or_update_resident(self, resident):
        unit = resident['unit']
        self.ref = db.reference("/ResidentsDB/residents")
        self.ref.child(unit).set(resident)

    def retrieve_all_residents(self):
        self.ref = db.reference("/ResidentsDB")
        all_residents = self.ref.get()
        return all_residents

    def get_number_of_records(self):
        residents = self.retrieve_all_residents()
        return len(residents['residents'])

    def retrieve_by_user_id(self, userid):
        self.ref = db.reference("/ResidentsDB/residents")
        resident = self.ref.order_by_child("userid").equal_to(userid).get()
        return resident

    def delete_by_unit(self, unit):
        self.ref = db.reference("/ResidentsDB/residents")
        self.ref.child(unit).set({})

    def retrieve_by_unit(self, unit):
        self.ref = db.reference("/ResidentsDB/residents")
        resident = self.ref.child(unit).get()
        return resident

    def insert_or_update_all_residents(self, all_residents):
        residents = all_residents['residents']
        for res in residents:
            self.insert_or_update_resident(res)

    @staticmethod
    def print_one_resident(unit, residents):
        all_my_res = residents['residents']
        # print a single resident from the retrieved list
        for ares in all_my_res:
            if ares is None:
                continue
            if ares['unit'] == unit:
                print(f"unit 26 data: {ares['email']},  {ares['phone']}")
