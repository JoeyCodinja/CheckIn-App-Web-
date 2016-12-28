// Gives the service worker access to the firebase libraries
importScripts('https://www.gstatic.com/firebasejs/3.5.2/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/3.5.2/firebase-messaging.js');

//Initialize Firebase App

firebase.initializeApp({'messagingSenderId': '188380223415'})

const messaging = firebase.messaging();

payloadDescriptions = new Map([['CIR', 'Check-In Confirmation Requested'],
                               ['UEN', 'Unregistered Entry'],
                               ['CIC', 'Check-In Confirmed']])


// Handles messages that may occur
// when the application is in the background
messaging.setBackgroundMessageHandler(function(payload) {
    console.log(payload);
    var notificationInfo = getPayloadType(payload);
    const notificationTitle = "MITS Punch In -- " + notificationInfo['title'] 
    const notificationOptions = { 
        body: notificationInfo['body'],
        icon: '/static/ico/favicon.ico'
    };
    
    return self.registration.showNotification(notificationTitle, notificationOptions);
    
})


function getPayloadType(payload){
    
}