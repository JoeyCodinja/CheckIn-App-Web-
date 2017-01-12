const messaging = firebase.messaging();
var isSubscribed = false; 
payloadDescriptions = new Map([['arrive', 'Check-In Confirmation Requested'],
                               ['UEN', 'Unregistered Entry'],
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
 
messaging.onMessage(function(payload){
    var activeDashboard = whichDashboard(); 
    
    payload = payload.data
    
    if (payloadDescriptions.has(payload.method)){
        if (activeDashboard == STAFF_DASHBOARD){
            switch(payload.method){
                case 'arrive':
                    addBox(createBox(payload), TO_ARRIVE);
                    break;
                case 'lunch':
                    var found = false;
                    box = $('.box.box-success .small-box');
                    for(var i=0; i < box.length; i++){
                        var uid = $('.inner p', box[i]).text();
                        if (uid == payload.u_id){
                            found = true;
                            moveBoxArgs = {'to':TO_LUNCH, 
                                           'box':box[i]};
                            moveBox.call(moveBoxArgs)
                            break;
                        }
                    }
                    if (found == false){
                        box = $('.box.box-danger .small-box'); 
                        for (var i=0; i < box.length; i++){
                            var uid = $('.inner p', box[i]).text();
                            if (uid == payload.u_id){
                                moveBoxArgs = {'to':TO_PRESENT,
                                               'box':box[i]}
                                moveBox.call(moveBoxArgs);
                                break;
                            }
                        }
                    }
                    break;
                case 'leave':
                    box = $('.box.box-success .small-box');
                    for(var i=0; i < box.length; i++){
                        var uid = $('.inner p', box[i]).text();
                        if (uid == payload.u_id){
                            moveBoxArgs = {'to' : TO_LEAVE, 
                                           'box': box[i]};
                            moveBox.call(moveBoxArgs);
                            break;
                        }
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
})

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