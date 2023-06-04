"""
   Defines classses and variables related to the handling of users.
"""

import os
import json
from flask_login import UserMixin
from werkzeug.utils import secure_filename

USER_TYPE_ADMIN = 0
USER_TYPE_BOARD = 1
USER_TYPE_SECRETARY = 2
USER_TYPE_RESIDENT = 3


class User(UserMixin):
    def __init__(self, id, unit, userid, password, name, email, startdt, phone, type, ownername, owneremail, ownerphone, occupants, active=True):
        self.id = id
        self.unit = unit
        self.userid = userid
        self.password = password
        self.name = name
        self.email = email
        self.startdt = startdt
        self.phone = phone
        self.type = type
        self.ownername = ownername
        self.owneremail = owneremail
        self.ownerphone = ownerphone
        self.occupants = occupants
        self.active = active

    def get_json_data(self):
        user = {
            'unit': self.unit,
            'userid': self.userid,
            'name': self.name,
            'password': self.password,
            'email': self.email,
            'startdt': self.startdt,
            'phone': self.phone,
            'type': self.type,
            'ownername': self.ownername,
            'owneremail': self.owneremail,
            'ownerphone': self.ownerphone,
            'occupants': self.occupants
        }
        return user

    def get_id(self):
        return self.id

    def get_unit(self):
        return self.unit

    def get_userid(self):
        return self.userid

    def get_password(self):
        return self.password

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def get_startdt(self):
        return self.startdt

    def get_phone(self):
        return self.phone

    def get_type(self):
        return self.type

    def get_ownername(self):
        return self.owner

    def get_owneremail(self):
        return self.owneremail

    def get_ownerphone(self):
        return self.ownerphone

    def get_occupants(self):
        return self.occupants

    def is_active(self):
        return self.active

    def get_auth_token(self):
        return make_secure_token(self.userid , key='secret_key')

class UsersRepository:
    def __init__(self):
        self.unit_dict = dict()
        self.identifier = 0
    
    def save_user(self, user):
        self.unit_dict.setdefault(user.unit, user)

    def add_user_to_dict(self, user):
        self.unit_dict.setdefault(user.unit, user)

    def get_user_by_userid(self, userid):
        for key in self.get_users():
            user = self.get_user_by_unit(key)
            if user.userid == userid:
                return user
        return None
    
    def get_user_by_id(self, id):
        for key in self.get_users():
            user = self.get_user_by_unit(key)
            if user.id == id:
                return user
        return None
    
    def get_user_by_unit(self, unit):
        return self.unit_dict.get(unit)
    
    def get_users(self):
        return self.unit_dict
    
    def delete_user(self, user):
        userObj = self.unit_dict.get(user.unit)
        if userObj == None:
            return
        del self.unit_dict[user.unit]

    def next_index(self):
        self.identifier += 1
        return self.identifier

    def save_users_to_file(self, filename):
        with open(filename, 'w') as f:
            userslist = []
            for user in self.unit_dict.values():
                record = {
                    'unit': user.unit,
                    'userid': user.userid,
                    'password': user.password,
                    'name': user.name,
                    'email': user.email,
                    'startdt': user.startdt,
                    'phone': user.phone,
                    'type': user.type,
                    'ownername': user.ownername,
                    'owneremail': user.owneremail,
                    'ownerphone': user.ownerphone,
                    'occupants': user.occupants
                }
                userslist.append(record)
            residents = {'residents': userslist}
            json_obj = json.dumps(residents)
            f.write(json_obj)


# define user repository
users_repository = UsersRepository()

# create a few users of different types
#user_admin = User('admin', 'admin@7394', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_ADMIN)

# board members
'''
user_jsilva = User('jsilva', 'joe@7394', 'info@whitegatecondo.com', users_repository.next_index(), USER_TYPE_BOARD)
user_dakins = User('dakins', 'dan@3443', 'nadsnika@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_cbusa = User('cbusa', 'chris@7575', 'mufflermannh@yahoo.com', users_repository.next_index(), USER_TYPE_BOARD)
user_wmann = User('wmann', 'wayne@1348', 'rookiemann57@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_mjohnson = User('mjohnson', 'mary@8765', 'mjculady@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
'''

# authorized secretaries and treasurer
'''
user_vbarrett = User('vbarrett', 'virginia@6465', 'ginnybarrett@comcast.net', users_repository.next_index(), USER_TYPE_SECRETARY)
user_dgilligan = User('dgilligan', 'donna@1331', 'dgilligan89@comcast.net', users_repository.next_index(), USER_TYPE_SECRETARY)
'''

# regular residents
# user_jresident = User('jresident', 'johnpass', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_RESIDENT)


#temporary email addresses
# create a few users of different types
'''
user_admin = User('admin', 'admin@7394', 'info@whitegatecondo.com', users_repository.next_index(), USER_TYPE_ADMIN)
user_jsilva = User('jsilva', 'joe@7394', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_dakins = User('dakins', 'dan@3443', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_cbusa = User('cbusa', 'chris@7575', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_wmann = User('wmann', 'wayne@1348', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_mjohnson = User('mjohnson', 'mary@8765', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_vbarrett = User('vbarrett', 'virginia@6465', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_SECRETARY)
user_dgilligan = User('dgilligan', 'donna@1331', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_SECRETARY)
user_jresident = User('jresident', 'johnpass', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_RESIDENT)
'''


# add users to repository
'''
users_repository.save_user(user_admin)
users_repository.save_user(user_jsilva)
users_repository.save_user(user_dakins)
users_repository.save_user(user_cbusa)
users_repository.save_user(user_wmann)
users_repository.save_user(user_mjohnson)
users_repository.save_user(user_vbarrett)
users_repository.save_user(user_dgilligan)
users_repository.save_user(user_jresident)
'''

