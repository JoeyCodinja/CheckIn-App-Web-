from flask import Flask, redirect, request, jsonify
from flask import render_template
import os
import json
from models.Database import Database
from models.Intern import Intern 
from models.Staff import Staff
from models.Unregistered import Unregistered
from models.PCLocations import PCLocations 
from requests import HTTPError
from punchin_utils import Utils

web_app = Flask(__name__)
database = Database()

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
        data_ts = dict(undefined=[generated_uuid])
        if database.query('/pc_locations', token=fbt) == None: 
            # pc_locations section doesn't exist
            database.insert('/', {'pc_locations': data_ts}, token=fbt)
        else: 
            undefined_list = database.query('/pc_locations/undefined', token=fbt)
            print "Retreieved of undefined systems" + str(undefined_list)
            if undefined_list == None: 
                database.insert('/pc_locations', data_ts)
            else: 
                undefined_list.append(generated_uuid)
                database.put('/pc_locations','undefined', undefined_list)
    else: 
        # Return an 'error' screen; system already sent its UUID
        pass
    
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
            intern_dash = redirect('/dashboard/intern')
            response = web_app.make_response(intern_dash)
            response.set_cookie('userId', value=cookie_user_id)
            response.set_cookie('token', value=data['token'])
            
            return response
        elif is_staff(email, data):
            if is_preregistered(email):
                validate_user(email)
            staff_dash = redirect('/dashboard/staff')
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
    location = request.form['location']
    uuid = request.form['uuid']
    
    
    pc_locations_exist = database.query('/pc_locations')
    if pc_locations_exist is None: 
        database.insert('/pc_locations', {location:[uuid]})
        return jsonify(uuid)
    
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
        
        
    return jsonify(uuid)
    
@web_app.route('/dashboard/unassign_location', methods=['POST'])
@signin_required
def unassign_system():
    # We should only receive the UUID as this point, 
    # we will employ a search to find where it is
    uuid = request.form['uuid']

    pc_locations = database.query('/pc_location')
    for location in pc_locations:
        if location == 'undefined':
            # Disregard because PC is already unregistered 
            return jsonify(False)
        
        if uuid in pc_locations[location]:
            pc_locations[location].remove(uuid)
            break
    
    database.insert('/pc_location', pc_locations)
    
    return jsonify(True)
    
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
    
    return_data['userId'] = id_info['sub']
    return_data['token'] = g_token
    return_data['googleUserObject']\
        .update(email=id_info['email'], 
                name=id_info['name'], 
                picture=id_info['picture'])
    
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
    
def submit_unregistered_user(data, user_data=None):
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
        database.insert('/unregistered', structure)

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