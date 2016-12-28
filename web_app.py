from flask import Flask, redirect, request, jsonify, make_response
from flask import render_template
import os
import json
from datetime import datetime
from models.Database import Database
from models.Intern import Intern 
from models.Staff import Staff
from models.Unregistered import Unregistered
from models.PCLocations import PCLocations 
from models.Log import Log
from requests import HTTPError
from punchin_utils import Utils
from utils.fcm import FCM_HTTP, FCM_XMPP

from pprint import pprint

web_app = Flask(__name__)
database = Database()
# xmpp = FCM_XMPP()
# xmpp.connect()
# xmpp.process(block=False)
fcm_http = FCM_HTTP()

# Contstants
#   User Types
INTERN = 90
STAFF = 10 
ADMIN = 40
UNREGISTERED = 99
#   State Types
BEGIN = 0 
PUNCHED_IN = 2
LUNCH_START = 4
LUNCH_END = 5
#   Confirm State
NO_CONFIRM = "NORESP"

#   Error Type
ERROR_NO_TOKEN = 'NOTOKEN'
ERROR_NO_USERINFO = 'NOUSERINFO'
ERROR_USER_INDETERMINATE = 'NOTVALIDUSER'
# --Error responses--
ERROR_NOT_ADMIN = "NOTADMIN"


# Decorators 
from functools import wraps

def signin_required(f):
    @wraps(f)
    def is_signed_in(*args, **kwargs):
        if request.method == "POST":
            if 'userTokenId' in request.form:
                # This person has signed in and has sent us their token
                # for us to validate
                data = validate_token(request.form['userTokenId'])
                database.set_token(request.form['fTokenId'])
                return f(data, *args, **kwargs)
            else:
                generate_error_template(ERROR_NO_TOKEN, *args, **kwargs)
    return is_signed_in

def login_required(f):
    @wraps(f)
    def is_logged_in(*args, **kwargs):
        if 'userId' in request.cookies :
            return f(*args, **kwargs)
        else: 
            # Send user to the login page
            return login()
    return is_logged_in
    
def initializeModels():
    if 'userId' in request.cookies:
        # Initialize the Database base instance 
        # with the token derived from the user 
        # ID token that was sent 
        pass
    pass
        
def admin_required(f):
    @wraps(f)
    def has_admin_cred(*args, **kwargs):
        data = validate_token(request.cookies['token'])
        email = data['googleUserObject']['email']
        if is_admin(email, data):
            return f(*args, **kwargs)    
        else:
            return error_response(ERROR_NOT_ADMIN, *args, **kwargs)
            # Return admin is required status to frontend
    return has_admin_cred




# Error views and methods
@web_app.route('/ooops')    
def generate_error_template(error_type=None):
    return render_template('error.html', error_type=error_type)
    
def error_response(error_type=None):
    from flask import jsonify
    
    error_message = {'error': ''}
    if error_type == ERROR_NOT_ADMIN:
        error_message['error'] = 'Lack of administrative privileges detected'
    else:
        error_message['error'] = 'Undefined Error'
    
    return jsonify(error_message)
        
# END
    
# User Facing Web Routes
@web_app.route('/')
def login():
    return render_template("index.html")

@web_app.route('/', methods=['POST'])    
def store_uuid():
    # Checks to see if the permanent cookie has 
    # already been set if not, check if a UUID 
    # has been sent and submit it to our DBs 
    # for further checks
    generated_uuid = request.form['pc_id']
    fbt = request.form['fbt']
    result = database.query('/pc_locations', 
                            generated_uuid, 
                            token=fbt)
    if result == None: 
        # Since the user hasn't ever registered 
        # this computer, lets go ahead and 
        # register it
        data_ts = dict(UREG=[generated_uuid])
        if database.query('/pc_locations', token=fbt) == None: 
            # pc_locations section doesn't exist
            database.insert('/', {'pc_locations': data_ts}, token=fbt)
        else: 
            undefined_list = database.query('/pc_locations', token=fbt)
            
            
            pprint( "Undefined PC Location List" + str(undefined_list))
            
            print "Retreieved of undefined systems" + str(undefined_list)
            if undefined_list == None: 
                database.put('/pc_locations', 'UDEF', data_ts['UDEF'])
            else: 
                undefined_list.append(generated_uuid)
                database.put('/pc_locations','UDEF', undefined_list)
    else: 
        return jsonify(True)
    
    return jsonify(True)
    
@web_app.route('/dashboard', methods=["POST"])   
@signin_required
def dashboard(data):
    # used to redirect based on indenity of the person who logged in
    # staff or interns
    if data is not None:
        email = data['googleUserObject']['email']
        cookie_user_id = data['userId']
        
        if is_intern(email, data):
            if is_preregistered(email): 
                validate_user(email)
            intern_dash = redirect('https://checkin-appuwi-codeinja.c9users.io/dashboard/intern')
            response = web_app.make_response(intern_dash)
            response.set_cookie('userId', value=cookie_user_id)
            response.set_cookie('token', value=data['token'])
            
            return response
        elif is_staff(email, data):
            if is_preregistered(email):
                validate_user(email)
            staff_dash = redirect('https://checkin-appuwi-codeinja.c9users.io/dashboard/staff')
            response = web_app.make_response(staff_dash)
            response.set_cookie('userId', value=cookie_user_id)
            response.set_cookie('token', value=data['token'])
            return response
        else:
            submit_unregistered_user(data)
            return generate_error_template(ERROR_USER_INDETERMINATE)

    return generate_error_template(ERROR_NO_USERINFO)
        
@web_app.route('/dashboard/intern')
def intern_dashboard():
    return render_template("intern.html")

@web_app.route('/dashboard/staff')
def staff_dashboard():
    user_listing = {'staff': [], 'intern': []}
    unregistered_listing = []
    pc_locations = []
    
    user_listing['staff'] = Staff.from_db(database)
    user_listing['intern'] = Intern.from_db(database)
    unregistered_listing =  Unregistered.from_db(database)
    pc_locations = PCLocations.from_db(database)
    
    
    return render_template("staff.html", 
                           valid_locations = PCLocations.valid_locations,
                           user_listing=user_listing , 
                           unregistered_listing=unregistered_listing,
                           pc_locations=pc_locations)
    
@web_app.route('/dashboard/intern/update')
def intern_update():
    # Updates intern information by 
    # recieving json requests with 
    # the key name of the value to 
    # be updated as well as the new 
    # value we are replacing the old 
    # value with. The user email id 
    # is also end 
    # TODO: Move to API
    data = json.loads(request.form['data'])
    key = data.keys()
    key.remove('emailId')
    key = key[0]
    database.put('/users/'+data['emailId'], key, data[key])
    
    return jsonify(database.query('/user', data['emailId']))
    
@web_app.route('/dashboard/staff/update')
def staff_update():
    # Updates staff information by 
    # recieving json requests with 
    # the key name of the value to 
    # be updated as well as the new 
    # value we are replacing the old 
    # value with 
    # TODO: Move to API
    data = json.loads(request.form['data'])
    key = data.keys()
    key.remove('emailId')
    key = key[0]
    database.put('/users', data['emailId'], key, data[key])
    
    return jsonify(database.query('/user', data['emailId']))

@web_app.route('/dashboard/assign_location', methods=["POST"])
@signin_required
def assign_system():
    # UUIDs for a particular location are added based on user request
    
    import pdb; pdb.set_trace()
    
    location = request.form['location']
    uuid = request.form['uuid']
    
    
    pc_locations_exist = database.query('/pc_locations')
    if pc_locations_exist is None: 
        database.insert('/pc_locations', {location:[uuid]})
        return jsonify({'location_assigned': 
                            {'location': location, 
                             'uuid': uuid}})
    
    created_previously = database.query('/pc_locations/'+ str(location))
    
    if created_previously != None:
        # If location created previously then it should return
        # a list of the UUIDs assigned to this location
        created_previously.append(uuid)
        database.put('/pc_locations', location, created_previously)
    else:
        # We have to create the location given to us as well as input the uuid 
        # for this specific location
        database.put('/pc_locations', location, [uuid])
        
        
    return jsonify({'location_assigned': 
                        {'uuid': uuid,
                         'location': location}})
    
@web_app.route('/dashboard/unassign_location', methods=['POST'])
@signin_required
def unassign_system():
    # We should only receive the UUID as this point, 
    # we will employ a search to find where it is
    uuid = request.form['uuid']

    pc_locations = database.query('/pc_location')
    for location in pc_locations:
        location_member = uuid in pc_locations[location]
        unregistered_section = location == PCLocations.Unregistered
        if location_member and not unregistered_section:
            # Remove the UUID of the PC from the 
            # previously assigned location and 
            # append it to the unaassigned list
            pc_locations[location].remove(uuid)
            pc_locations[PCLocations.Unregistered].append(uuid)
            return jsonify({'location_unassigned': {'uuid': uuid}})
        elif location_member and unregistered_section:
            # Wasn't unassigned because it was already unassigned
            return jsonify(False)
        else: 
            continue
    
    return jsonify({'error': 'uuid was not found'})
    
@web_app.route('/dashboard/register', methods=["POST"])
@admin_required
def user_pre_registration():
    def register_user(request):
        # TODO: need to somehow get the email 
        # address of the person being input
        intern_information = dict(id=request.form['id'], 
                                  FCM_ID=dict(web_app=None), 
                                  APP_ID=None, 
                                  isValidated=False,
                                  name=' '.join([request.form['first-name'],
                                                 request.form['last-name']]),
                                  userType=INTERN, 
                                  lastState=BEGIN)
        
        email = escape_email_id(request.form['email'].split('@')[0])
        
        intern_information = {email: intern_information}
            
        database.put('/user', email, intern_information[email])
        
        return request.form
    
    print "Request Data" + str(request.form)
    insertedData = register_user(request)
    
    # TODO: getting a 
    
    return jsonify({'register':{'email':insertedData['email'], 
                                'name':' '.join([insertedData['first-name'], 
                                                 insertedData['last-name']]), 
                                'id': insertedData['id'],
                                'userType': insertedData['userType']
                    }})

@web_app.route('/dashboard/validate')
@signin_required
def user_validation():
    from flask.json import jsonify
    return jsonify(validate_user(request))
    
@web_app.route('/dashboard/unregistered/cancel', methods=["POST"])
def cancel_unregistered():
    email = escape_email_id(request.form['email'].split('@')[0])
    database.delete('/unregistered', email)
    return jsonify({'delete': {'email': request.form['email'],
                               'userType': UNREGISTERED }
                   })

@web_app.route('/dashboard/subscribe', methods=["POST"])
@login_required
def subscribe():
    params = request.form
    result = fcm_http.topic_subscribe(params['fcm_iid'], params['user'])
    
    # After subscription tag the registration key to this users information 
    user_email = validate_token(request.cookies['token'])
    user_email = user_email['googleUserObject']['email']
    user_email = escape_email_id(user_email)
    user_email = user_email.split('@')[0]
    
    data = {'web_app': params['fcm_iid']}
    
    database.put('/user/%s' % user_email, 'FCM_ID', data=data)

    
    return jsonify(result)

@web_app.route('/dashboard/messaging/android')
def message_android():
    pass 

@web_app.route('/dashboard/messaging/web', methods=["POST"])
@login_required
def message_web():
    INTERN_METHODS = ['checkin', 'checkout', 
                      'lunchstart', 'lunchend',]
    INTERN_MAPPING = {
        INTERN_METHODS[0] : Log.ARRIVE,
        INTERN_METHODS[1] : Log.LEAVE,
        INTERN_METHODS[2] : Log.LUNCH,
        INTERN_METHODS[3] : Log.LUNCH
    }
    
    STAFF_METHODS = ['confirm', 'registering',]
    
    STAFF_MAPPING = {
        STAFF_METHODS.index('confirm'): Log.CONFIRM
    }
    
    SYSTEM_METHODS = ['unregistered']
    
    message_info = request.form.to_dict()
    
    if str(message_info['method']) in INTERN_MAPPING:
        MAPPING = INTERN_MAPPING
    elif str(message_info['method']) in STAFF_MAPPING:
        MAPPING = STAFF_MAPPING
    elif str(message_info['method']) in SYSTEM_METHODS:
        MAPPING = dict(map(lambda x : (x, x), SYSTEM_METHODS))
    else:
        error = json.dumps({'error': 'invalid messaging method:%s' % request.form['method']})
        response = make_response(error, 400)
        return response 
        
    log_type = MAPPING[message_info['method']]
        
    del message_info['method']
    
    if log_type == Log.LUNCH: 
        fcm_http.send_topic_message(INTERN_MAPPING[message_info['method']], message_info)
         
    if log_type == Log.ARRIVE:
        # Get the user's ID; 
        # send the message out arrive topic;
        # Log to FDB
        user = get_uid(request.cookies['token'])
        message_info.update({'u_id': user})
        
        log_id = fcm_http.send_topic_message(log_type, message_info)
        log = Log(log_id, log_type, user)
        log.to_db(database)
        
    elif log_type == Log.CONFIRM:
        user_to_notify = database.query('/log', message_info['lid'])['from']
        user_to_notify = get_fcm_iids(INTERN, aux_id=user_to_notify)
        Log.from_db(database, message_info['lid'])
        
    elif log_type in SYSTEM_METHODS:
        pass 
    
    
    return jsonify(True)

@web_app.route('/dashboard/messaging/ios')
def message_ios():
    pass

def validate_user(email):
    # Users are validated on their first 
    # login after they have been granted 
    # access by being added to the table of
    # personnel
    email = escape_email_id(email)
    return database.put('/user', email.split('@')[0], {'isValidated': True});

def validate_token(g_token):
    from oauth2client import client, crypt
    
    CLIENT_ID = "188380223415-ddaj7pcggh2jstsrgb3vin6pfbbbtjm2" +\
                ".apps.googleusercontent.com"
    
    return_data = dict(userId=None, googleUserObject=dict(), token=None)
    id_info = None
    
    try: 
        id_info = client.verify_id_token(g_token, CLIENT_ID)
        if id_info['aud'] not in [CLIENT_ID]:
            raise crypt.AppIdentityError("Unrecognized client.")
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
    except crypt.AppIdentityError:
        # Invalid token
        pass
    
    try:
        return_data['userId'] = id_info['sub']
        return_data['token'] = g_token
        return_data['googleUserObject']\
            .update(email=id_info['email'], 
                    name=id_info['name'], 
                    picture=id_info['picture'])
    except (TypeError, IndexError):
        raise ValueError('Token passed is invalid')
        
    return return_data
    
def is_intern(email, data):
    query_result = None
    email = escape_email_id(email.split('@')[0])
    try:
        query = database.query('/user', email)
        print str(query)
        query_result = query['userType']
    except (HTTPError, KeyError, TypeError):
        # Put user in unregistered list
        return False
    return query_result == INTERN
    
def is_staff(email, data):
    query_result = None
    email = escape_email_id(email.split('@')[0])
    try:
        query = database.query('/user', email) 
        print str(query)
        query_result = query['userType']
    except (HTTPError, KeyError, TypeError):
        # Put user in unregistered list
        submit_unregistered_user(data)
        return False 
    return query_result == STAFF or query_result == STAFF & ADMIN 

def is_admin(email, data):
    email = escape_email_id(email.split('@')[0])
    try:
        userType = database.query('/user', email)['userType']
    except (HTTPError, KeyError, TypeError):
        # Do nothing. We can't go adding admin just so quite yet
        print "Incorrect User Type" + str(userType)
        return False
    return userType == ADMIN or userType == STAFF & ADMIN
    
def is_preregistered(email):
    email = escape_email_id(email.split('@')[0])
    try:
        result = database.query('/user', email)
        return not result['email']['isValidated']
    except (HTTPError, KeyError): 
        return False
    
def get_uid(token):
    user = validate_token(token)['googleUserObject']['email']
    user = user.split('@')[0]
    user = database.query('/user/%s' % escape_email_id(user))
    return user['id']

def submit_unregistered_user(data, user_data=None):
    # TODO send a 
    from datetime import datetime
    basicGoogleProfile = data['googleUserObject']
    
    basicGoogleProfile['email'] = escape_email_id(basicGoogleProfile['email'].split('@')[0])
        
    structure = {basicGoogleProfile['email']: 
                    {'date': Utils.display_time().isoformat(), 
                     'name': basicGoogleProfile['name']}}
                     
    if user_data is not None: 
        structure[basicGoogleProfile['email']]\
            .update(('proposedId', user_data['id']))
            
    print database.query(None)
    
    if database.query('/unregistered') == None:
        structure = {'unregistered': structure}
        database.insert(None, structure)
    else:
        database.put('/unregistered', 
                     basicGoogleProfile['email'],
                     structure[basicGoogleProfile['email']])

def get_fcm_iids(userType, user_id=None, aux_id=None):
        if user_id is not None:
            user = database.query('/user/%s' % user_id)
            try:
                return user['FCM_ID']['web_app']
            except IndexError:
                raise ValueError('User has not been registered with Firebase as yet')
        
        if aux_id is not None:
            users = database.query('/user')
            for user in users:
                if users[user]['id'] == aux_id:
                    return users[user]['FCM_ID']['web_app']
            
        users = database.query('/user').keys()
        personnel_ids = []
        for user in users:
            query_user = database.query('/user', user)
            fcm_iid_notnull = query_user['FCM_ID']['web_app'] != ' '
            isUserType = int(query_user['userType']) ==  userType
            
            if fcm_iid_notnull and isUserType: 
                personnel_ids.append(query_user['FCM_ID']['web_app'])
        return personnel_ids

def escape_email_id(email):
    import re 
    invalid_characters = r'[.$\[\]#/]'
    search_obj = re.search(invalid_characters, email) 
    
    while search_obj is not None:
        invalid_character = email[search_obj.start():search_obj.end()]
        print invalid_character
        email = email.replace(invalid_character, '!%03d!' % ord(invalid_character), 1)
        search_obj = re.search(invalid_characters, email)
    
    print email
    
    return email
    
def parse_email_id(escaped_email):
    import re
    escaped_character_match = r'!(\d{3})!'
    search_obj = re.search(escaped_character_match, escaped_email)
    
    while search_obj is not None:
       replace_chr = chr(int(search_obj.group(1)))
       escaped_chr = escaped_email[search_obj.start():search_obj.end()]
       escaped_email = escaped_email.replace(escaped_chr, replace_chr)
       search_obj = re.search(escaped_character_match, escaped_email)
    
    print escaped_email 
    
    return escaped_email
    

if __name__ == "__main__":
    web_app.config.debug = True
    
    web_app.run(os.getenv('IP', '0.0.0.0'), os.getenv('PORT', 8080))