const messaging = firebase.messaging();

// Requests persmission for the browser
// to receive notifications
messaging.requestPermission().then(
    function(){}, 
    function(err){
        // Show modal that states that 
        // the user will be unable to ue the 
        // application properly without this 
        //enabled with the option to opt-in
    }
);

function sendMessagingToken(fBaseMsgToken){
    registerMessagingTokenURI = window.location.origin + '/'
    post()
}