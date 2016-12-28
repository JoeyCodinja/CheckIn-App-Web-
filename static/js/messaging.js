const messaging = firebase.messaging();
var isSubscribed = false; 


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
    
})




function sendMessage(data){
     
}


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