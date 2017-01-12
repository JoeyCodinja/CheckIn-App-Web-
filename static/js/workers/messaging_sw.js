// Gives the service worker access to the firebase libraries
importScripts('https://www.gstatic.com/firebasejs/3.5.2/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/3.5.2/firebase-messaging.js');

//Initialize Firebase App
firebase.initializeApp({'messagingSenderId': '188380223415'})

const messaging = firebase.messaging();

payloadDescriptions = new Map([['arrive', 'Check-In Confirmation Requested'],
                               ['unregistered', 'Unregistered Entry'],
                               ['lunch', ['Lunch Start', 'Lunch End']],
                               ['confirm', 'Check-In Confirmed'],
                               ['leave' ,'Intern Checkout']])

var lunchStarted = false; 


var domains = ["https://checkin-appuwi-codeinja.c9users.io/dashboard/staff", 
               "https://checkin-appuwi-codeinja.c9users.io/dashboard/intern"]


// Handles messages that may occur
// when the application is in the background
messaging.setBackgroundMessageHandler(function(payload) {
    console.log(payload);
    var notificationInfo = getPayloadType(payload);
    
    if (notificationInfo == undefined){
        return {'error': "Malformed Payload"} 
    }
    const notificationTitle = "MITS Punch In -- " + notificationInfo['title'] 
    const notificationOptions = { 
        body: notificationInfo['body'],
        icon: '/static/ico/favicon.ico'
    };
    
    var bCastChannel = new BroadcastChannel('inactive_window_listener')
    bCastChannel.postMessage(payload);
    
    return self.registration
        .showNotification(notificationTitle, notificationOptions);
    
})


function getPayloadType(payload){
    payload = payload.data;
    var notificationObject = {title: payloadDescriptions.get(payload.method), 
                              body: undefined,
                              actions: undefined
                             } 
                              
    if ( notificationObject.title == undefined ){
        return notificationObject.title
    }
    
    var trailing_notif_message;
    var notification_actions; 
    
    switch(payload.method){
        case 'arrive': 
            trailing_notif_message = payload['uid'] + ""
            // notification_actions = {"view": undefined, "confirm": undefined} 
            // addBox(createBox(payload), TO_ARRIVE);
            break; 
        case 'lunch':
            if ( !lunchStarted ){
                lunchStarted = true;
                trailing_notif_message = " has gone for lunch.";
            }
            else{
                lunchStarted = false;
                trailing_notif_message = " has come back from lunch.";
            }
            notification_actions={"view": undefined} 
            break;
        case 'leave':
            trailing_notif_message = " has left the work area."
            notification_actions = {"view": undefined}
            break;
        case "confirm":
            trailing_notif_message = "Your arrival time has been confirmed";
            notification_actions = {"view": undefined}
            break;
        default:
            break;
    }
    if (payload['method'] == 'confirm'){
        notificationObject.body = trailing_notif_message;
    } else {
        notificationObject.body = payload['u_id'] + trailing_notif_message;
    }
    notificationObject.actions = notification_actions
    
    return notificationObject
}