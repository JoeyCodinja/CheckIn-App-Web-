const messaging = firebase.messaging();
var isSubscribed = false; 
payloadDescriptions = new Map([['arrive', 'Check-In Confirmation Requested'],
                               ['unregistered', 'Unregistered Entry'],
                               ['lunch', ['Lunch Start', 'Lunch End']],
                               ['confirm', 'Check-In Confirmed'],
                               ['leave', 'Intern Checkout']])


if ('serviceWorker' in navigator){
    navigator.serviceWorker
        .register(window.location.origin + '/static/js/workers/messaging_sw.js')
        .then(function(registration){
            messaging.useServiceWorker(registration);
            
            messaging.getToken().then(subscribeToTopics);
        })
}

function findUserMoveBox(id, where, to){
    LocationMapping = new Map([[TO_PRESENT, '.box-success'],
                               [TO_ARRIVE, '.box-warning'],
                               [TO_LUNCH, '.box-danger'],
                               [TO_LEAVE, '.box-primary']]);
                               
    box = $('.box'+LocationMapping.get(where)+' .small-box');
    for (var i=0; i< box.length; i++){
        var uid = $('.inner p', box[i]).text();
        if (uid == id){
            moveBoxArgs = {'to':to,
                           'box':box[i]}; 
            moveBox.call(moveBoxArgs);
            return true;
        }
    }
    return false;
}

function processPayload(payload){
    var activeDashboard = whichDashboard(); 
    
    payload = payload.data
    // Check if this is a MessageEvent
    if (payload.hasOwnProperty('data')){
        payload = payload.data
    }
    
    if (payloadDescriptions.has(payload.method)){
        if (activeDashboard == STAFF_DASHBOARD){
            switch(payload.method){
                case 'arrive':
                    var found = findUserMoveBox(payload.u_id, TO_LEAVE, TO_PRESENT);
                    if (!found){
                        addBox(createBox(payload), TO_ARRIVE);
                    }
                    break;
                case 'lunch':
                    var found = false;
                    box = $('.box.box-success .small-box');
                    
                    var found = findUserMoveBox(payload.u_id, TO_PRESENT, TO_LUNCH);
                    if (!found){
                        found = findUserMoveBox(payload.u_id, TO_LUNCH, TO_PRESENT)
                        if (!found){
                            // box is not where its supposed to be
                            // fire error
                            console.log('Unable to find info for ' + payload.u_id);
                        }
                    }
                    break;
                case 'leave':
                    var found = findUserMoveBox(payload.u_id, TO_PRESENT, TO_LEAVE);
                    if (found){
                        console.log('Unable to find info for ' + payload.u_id);
                    }
                    break;
                default: 
                    window.alert("Unrecognized method passed in message");
                    break;
            }
        }
        else if (activeDashboard == INTERN_DASHBOARD){
            switch(payload.method){
                case 'confirm':
                    transitionState(TO_CHECKOUT); 
                    break;
                default:
                    window.alert("Unrecognized method passed in message");
            }
        }
        else
            window.alert("Unknown dashboard");
    } else {
        window.alert('Method unknown')
    }
}


// Requests persmission for the browser
// to receive notifications
messaging.requestPermission().then(
    function(){}, 
    function(err){
        // Show modal that states that 
        // the user will be unable to ue the 
        // application properly without this 
        // enabled with the option to opt-in
    }
);
 
messaging.onMessage(processPayload);

var bCastChannel = new BroadcastChannel('inactive_window_listener');
bCastChannel.onmessage = processPayload;

function subscribeToTopics(token){
    var requestParameters = {'fcm_iid': token, 'user': whichDashboard() };
    var subscriptionURL = window.location.origin + '/dashboard/subscribe'; 
    $.post(subscriptionURL, requestParameters, null, 'json')
            .done(function(){
                isSubscribed = true;
            })
            .fail(function(){
                window.alert('System was unable to subscribe to notifications. Please report this error');
                // Implement Exponential Backoff retry subscribe 
            })
    
}

function createConfirmBox(){
    var confirm_box = $("<div>");
}