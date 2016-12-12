var googleUserObject = null;

function onSignIn(googleUser){
    var profile = googleUser.getBasicProfile();
    console.log(profile.getEmail() + ' logged in');
    googleUserObject =  googleUser;
    generateSignOutButton(googleUser);
    firebaseLogin(googleUser);
}

function signIn(){
    // Forces reauthentication on each sign-in call
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signIn({'prompt': 'login'}).then(onSignIn); 
}

function signOut(){
    var redirectToLogin = false;
    if (window.location.pathname.match('dashboard') != null){
        // Move the user back to the log in screen when done
        redirectToLogin = true;
    }
    var auth2 = gapi.auth2.getAuthInstance();
    if (auth2.isSignedIn.get()){
        auth2.signOut().then(function(){
            // remove the Sign Out button
            document.querySelector('.btn').remove();
        });
        firebase.auth().signOut().then(function(){
            console.log("Sign out succcessful");
            if (redirectToLogin){
                window.location = window.location.origin;
            }
        }, function(){
            console.log("Sign out unsuccessful");
        })
    }
}

function reinitializeAuth(){
    gapi.load('auth2', function(){
        auth2 = gapi.auth2.init({
            client_id: '188380223415-ddaj7pcggh2jstsrgb3vin6pfbbbtjm2.apps.googleusercontent.com'
        }).then(function(){
            if (!gapi.auth2.getAuthInstance().isSignedIn.get()){
                window.location = window.location.origin;
            }
            loggedInUser = gapi.auth2.getAuthInstance().currentUser.get();
            console.log(loggedInUser.getBasicProfile().getEmail() + " auth regained");
        })
    });
}

function firebaseLogin(googleUser){
    var unsubscribe = firebase.auth().onAuthStateChanged(function (firebaseUser){
        unsubscribe();
        if (!isUserEqual(googleUser, firebaseUser)){
            var credential = firebase.auth.GoogleAuthProvider.credential(getTokenId())
            firebase.auth().signInWithCredential(credential)
                .then(redirectUser)
                .catch(function(error){
                window.alert('Cannot authenticate with firebase');
            })
        } else {
            console.log(googleUserObject.getBasicProfile().getEmail() + 
                ' already signed in');
            redirectUser();
        }
    });
}

function isUserEqual(googleUser, firebaseUser){
    if (firebaseUser){
        var providerData = firebaseUser.providerData; 
        for (var i=0; i < providerData.length; i++){
            var first_case = providerData[i].providerId === firebase.auth.GoogleAuthProvider.PROVIDER_ID;
            var second_case = providerData[i].uid === googleUser.getBasicProfile().getId();
            if(first_case && second_case){
                return true;
            }
        }
    }
    return false;
}

function generateSignOutButton(isSignedIn){
    if (isSignedIn.isSignedIn()){
        var signOutButton = document.createElement('div');
        signOutButton.innerHTML = "Sign out";
        signOutButton.className = 'btn';
        signOutButton.addEventListener('click', signOut, false);
        switch(window.location.href){
            case window.location.origin + '/':
                var loginElement = document.querySelector('.login');
                loginElement.insertAdjacentElement('beforeend', signOutButton)
                break;
            case window.location.origin + '/dashboard/intern':
            case window.location.origin + '/dashboard/staff':
                break;
            default:
                break;
        }
    }
    
}

function getTokenId(){
    if (googleUserObject != null){
        return googleUserObject.getAuthResponse().id_token;
    } else {
        throw new TypeError("User isn't logged in");
    }
}

function getFirebaseToken(){
    return firebase.auth().currentUser.getToken();
}

function redirectUser(){
    var dashboardDeterminant = window.location.origin + '/dashboard';
    getFirebaseToken().then(function(value){
        checkUUID()
        post(dashboardDeterminant, [getTokenId(), value])
    },
    function(error){
        window.alert('Can\'t retrieve Firebase token Id');
    });
}

function checkUUID(){
    // Checks for a pc_id cookie and verifies that
    // the UUID present is a valid UUID and checks 
    // with our DBs 
    if ( storageAvailable('localStorage') ){
        // LocalStorage is available hence we can continue
        pc_id = localStorage['pc_id']
        if (pc_id != undefined){
            if (testUUID(pc_id)){
               return true;
            }
                
        }else{
            // Generate and send this uuid to the 
            // server for submission
            localStorage['pc_id'] = generateUUID();
            submitUUID_URL = window.location.origin
            $.post(submitUUID_URL, {'pc_id': localStorage['pc_id'],
                                    'fbt': getFirebaseToken()})
                .done(function(data, status, jqXHR){
                    result = true; 
                })
                .error(function(){
                    window.alert('UUID issue occured');
                });
            return true;
        }
    } else {
        // Local storage isn't available
        // Can't identify this computer
        // Prompt to use a different browser
        window.alert('Please use an updated browser to continue.'); 
    }
     
}

function generateUUID(){
    // Generate the UUID and store it as a permanent 
    // cookie
    return uuid();
}

