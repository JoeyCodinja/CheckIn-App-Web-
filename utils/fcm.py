# Contains code for use to use XMPP to communicate with FCM 

fcm_xmpp_endpoint = {'production':"fcm-xmpp.googleapis.com:5235", 
                     'development': "fcm-xmpp.googleapis.com:5236"}
                     

# App server FCM messaging credentials
user = '188380223415@gcm.googleapis.com'
      
api_key = 'AAAAK9xWF7c:APA91bFqVM8vjFxDZzL' +\
          'OQ50fGkS77FaRMAS7IpB6xAb92lKuHS' +\
          '4-HykFEEknooob6oED5ZVhdvyviK0fm' +\
          'CwbyWVLoYdEYcJ-y98I01Y_zTFauSIE' +\
          'wW6mjVcffurdAnF7dKPzFqwOpqMkgkz' +\
          'EM-dP4sc_lndc_OaHJQ'

import logging 
import urllib2 
import json
import requests

from sleekxmpp import ClientXMPP 
from sleekxmpp.exceptions import IqError, IqTimeout

INTERN = 90 
STAFF = 10 
ADMIN = 40 

class FCM_XMPP(ClientXMPP):
    def __init__(self, jid=user, password=api_key):
        ClientXMPP.__init__(self, jid, password, {'default_port':5326})
        
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        
    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        
        
    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply('Thanks for sending\n%(body)s' % msg).send()
            
            
class FCM_HTTP(object):
    AUTH_KEY = api_key
    DOWNSTREAM_MESSAGE = "HTTPS://fcm.googleapis.com/fcm/send"
    
    def __init__(self, key=AUTH_KEY): 
        self.key = key
    
    def send_topic_message(self, topic, data):
        # Sends an HTTP POST message via FCM and 
        # returns the message ID for the message 
        # which serves as the identifier for 
        # that message
        data = {'to': '/topics/%s' % topic, 
                'data': data}
        
        response = self.build_request(FCM_HTTP.DOWNSTREAM_MESSAGE,
                                      'POST',
                                      self.key,
                                      json.dumps(data)).json()
        try: 
            return response['message_id']
        except (TypeError, IndexError):
            return ValueError('No message id received in response')
        
        
    def send_message(self, to, data):
        data = {'to': to, 
                'data': data}
                
        response = self.build_request(FCM_HTTP.DOWNSTREAM_MESSAGE, 
                                      'POST',
                                      self.key, 
                                      json.dumps(data))
                                      
        if response.status_code == 200: 
            return response.json()['results'][0]['message_id']
        else: 
            return False
        
    def build_request(self, endpoint, method, key, data=None, host_url=None, json=None):
        args = {'url': endpoint, 
                'headers':{'Authorization': 'key=%s' % key,
                           'Content-Type': 'application/json'}
                }
                
        if host_url is not None: 
            args.update({'origin_req_host': host_url})
        if json is not None:
            args.update({'json': json})
        if data is not None : 
            args.update({'data': data})
        
        if method == 'POST': 
            return requests.post(**args)
        elif method == 'GET': 
            return requests.get(**args)
                               
    def topic_subscribe(self, fcm_iid, user_type):
        
        topic_subscription_url = "https://iid.googleapis.com/iid/v1/%s/rel/topics/%s"
        
        if int(user_type) == INTERN:
            # Register the user for the 'confirm' topic
            topic = ['confirm',]
        elif int(user_type) == STAFF: 
            # Register the user for the 'arrive' topic
            topic = ['arrive', 'unregistered', 'lunch', 'confirm']
        else: 
            raise ValueError("No topics available for subscription for user specified")
        
        # Only add topics that aren't subscribed for
        subscribed_topics = self._check_topics(fcm_iid)
        for topics in subscribed_topics: 
            if topics in topic:
                try:
                    del topic[topic.index(topics)]
                except ValueError:
                    #Topic subscribed to that we don't know about --shrugs--
                    continue 
                    
        responseObject = [] 
        
        if len(topic) == 0:
            return True
        
        for t in topic:
            url_placeholders = (fcm_iid, t)
            response = self.build_request(topic_subscription_url % url_placeholders,
                                          'POST',
                                          self.key)
            if response.status_code == 200:
                responseObject.append(True)
            else: 
                responseObject.append(False)
        return responseObject
        
    def _check_topics(self, fcm_iid):
        # Returns a list of the topics subscribed to
        
        checkTopicsURL = "https://iid.googleapis.com/iid/info/%s?details=true"
        
        response = self.build_request(checkTopicsURL % fcm_iid,
                                      'GET', 
                                      self.key).json()
                                      
        print response 
        try:
            topics = response['rel']['topics'].keys()
        except KeyError:
            return []
        except TypeError:
            pass 
        
        return map(lambda x: str(x), topics)
    
            
            
        
        
        