$('.checkin-btn:not(.checkin-btn.pressed) svg, .checkout-btn:not(.checkout-btn.pressed) svg').click(depress);
$('.checkin-btn:not(.checkin-btn.pressed) svg, .checkout-btn:not(.checkout-btn-pressed) svg').click(log_event);
$('.loglunch-btn').click(log_event);
$('.loglunch-btn').click
$('.logendlunch-btn').click(log_event);

var timerID; 

// Log Methods 
var CHECKIN = 'checkin';
var CHECKOUT= 'checkout';
var LUNCHIN = 'lunchstart'; 
var LUNCHOUT= 'lunchend';
var UNKNOWN = 'unknown';

// Transition State
var TO_PENDING = 'checkin->'; 
var TO_CHECKOUT = 'pending->';
var TO_CHECKIN = '<-checkin';
var TO_LUNCH = '<-checkout'; 
var FROM_LUNCH = 'checkout->';

var LogMapping = new Map([[CHECKIN, TO_PENDING],
                      [CHECKOUT, TO_CHECKIN],
                      [LUNCHIN, TO_LUNCH],
                      [LUNCHOUT, TO_CHECKOUT]])

// UI Functions 
    // Button UI changes
function depress(){
    // Depress the buttons that are clicked
    // Only works for check-n and check-out 
    // buttons 
    var btn = $(this).parents('[class$=-btn]'); 
    var btn_pressed = $('.' + btn[0].className + '.pressed');
    
    btn.css('display','none');
    btn_pressed.css('display','block');
    
    setTimeout(release, 500, btn);
}

function release(btn){
    var btn_pressed = $('.' + btn[0].className + '.pressed');
    
    btn.css('display', 'block');
    btn_pressed.css('display', 'none');
}

function transitionState(to){
    var pending_btn = $('.pending-btn');
    var checkin_btn = $('.checkin-btn');
    var checkout_btn = $('.checkout-btn');
    var lunch_btn = $('.loglunch-btn');
    switch(to){
        case TO_PENDING:
            // Hide the check-in button and show 
            // the pending button
            pending_btn.removeClass('hidden');
            checkin_btn.addClass('hidden');
            break;
        case TO_CHECKOUT:
            // Hide the pending button and show
            // the checkout button
            checkout_btn.removeClass('hidden');
            pending_btn.addClass('hidden');
            break;
        case TO_CHECKIN:
            // Hide the checkout button and 
            // show the checkin button
            checkin_btn.removeClass('hidden');
            checkout_btn.addClass('hidden');
            break;
        case TO_LUNCH:
            // Hide the checkout button and 
            // show the lunch controls 
            checkout_btn.addClass('hidden');
            lunch_btn.removeClass('hidden');
            break;
        case FROM_LUNCH:
            // Hide the lunch controls and 
            // show the checkout button
            checkout_btn.removeClass('hidden');
            break;
        default:
            window.alert('Transition Error');
            break;
    }
}

    // Time display
function initTimer(duration){
    // Given the duration in ms the timer 
    // should countdown second by second
    
    // Calculate hours from duration 
    duration = calculateDuration(duration); 

    var timeAfterDuration = new Date();
    
    timeAfterDuration.setHours(duration[0] + timeAfterDuration.getHours());
    
    timeAfterDuration.setMinutes(duration[1] + timeAfterDuration.getMinutes());
    
    timeAfterDuration.setSeconds(duration[2] + timeAfterDuration.getSeconds());
    
    timerID = setInterval(timeRemaining, 900, timeAfterDuration)
}

function calculateDuration(duration){
    // Takes a duration of time in milliseconds
    // and returns an array of the form 
    // [<hours>, <minutes>, <seconds>]
    
    var hours = Math.floor(duration / 3600000)  
    duration = duration - (hours * 3600000) 
    
    var minutes = Math.floor(duration / 60000)
    duration = duration - (minutes * 60000)
    
    var seconds = Math.floor(duration / 1000)
    duration = duration - (seconds * 1000)
    
    return [hours, minutes, seconds]
}

function timeRemaining(endTime){
    // At call time will return the 
    // remaining time till endTime
    var duration = calculateDuration(endTime.getTime() - new Date().getTime())
    console.log("".concat(duration[0], ":", duration[1], ':', duration[2]));
    
    if (duration[0] == 0 && duration[1] == 0 && duration[2] == 0){
        clearInterval(timerID);
    }
    
    return "".concat(duration[0], ':', duration[1], ':', duration[2])
}

    
// Log Functions 
function log_event(event){
    
    var eventBtn = $(event.target).parents('[class$=-btn]');
    
    cases = {'checkin-btn'    : CHECKIN,
             'checkout_btn'   : CHECKOUT,
             'loglunch-btn'   : LUNCHIN,
             'logendlunch-btn': LUNCHOUT}
    caseEntries = Object.entries(cases);
    for(var caSe=0; caSe < caseEntries.length; caSe++)
    {
        if (eventBtn.hasClass(caseEntries[caSe][0]))
            var eventType = caseEntries[caSe][1];
    }
    if (eventType == undefined)
        eventType = UNKNOWN
    
    var eventURL = window.location.origin + '/dashboard/messaging/web';
    
    var logTime = new Date().toLocaleTimeString();
    
    var logParams = {'time': logTime,
                     'method': eventType} 
    
    var eventTransition = transitionState;
                 
    $.post(eventURL, logParams)
        .always(transitionState(LogMapping.get(eventType)))
        .done(transitionState(TO_CHECKOUT))
        .fail(transitionState(TO_CHECKIN));
}
