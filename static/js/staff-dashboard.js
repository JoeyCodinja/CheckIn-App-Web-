$(document).ready(function(){
    $('#add_unregistered .modal-footer .btn-success').click(formTransmitData)

    $('#add_user .modal-footer .btn-success').click(formTransmitData);

    $('#delete_user .modal-footer .btn-success').click(formTransmitData);
    
    $('.register_cancel').click(formTransmitData);
});

// Time Management functions
var timerIntervalId = null; 

function getStringTime(){
    return moment().format('LTS');
}

function displayTime(){
    var element = document.querySelector('.time-display');
    element.innerText = getStringTime();
}

function startDisplayTimer(){
    timerIntervalId = window.setInterval(displayTime, 250);
}

startDisplayTimer();


// User Submitted Data Functions

function formTransmitData(){
    if ($(this).parents('.modal').length == 0)
        var modalSelector = '#cancel_unregistered'
    else
        var modalSelector = "#" + $(this).parents('.modal').attr('id');
    
    var data; 
    var action; 
    
    switch(modalSelector){
        case '#delete-user':
            // This modal has no form attached, so we have to provide it with data
            action = window.location.origin + '/'; 
            email = $(this).parents('.modal').find('.modal-body p')[0].innerText
            email_regex = /(\w+)@(\w+)(.com|.edu|.co|.net|.org)/;
            regex_result = email_regex.exec(email);
            if (regex_result != null)
                data = regex_result[0]
            else
                errorOccurred();
            break;
        case '#cancel_unregistered':
            // This modal also has no form attached so we have to provide it with data
            action = window.location.origin + '/dashboard/unregistered/cancel'
            data = {'email': 
                        $(this)
                            .parents('tr')
                            .find('td:first-of-type')[0].innerText};
            break;
        case '#add_user':
        case '#add_unregistered':
            action = $(modalSelector + ' form').attr('action');
            data = $(modalSelector + ' form').serializeArray();
            break;
        default:
            break;
    }
    $.post(action, data, null, 'json').done(updateTableWithNewResults).fail(errorOccurred);
}

function removeResultFromTable(email, userType){
    // find the email in the table and remove it 
    var INTERN = 90
    var STAFF = 10
    var ADMINSTAFF = 8 
    var UNREGISTERED = 99 
    switch(userType){
        case INTERN:
            email_selector = '.content section:nth-child(4)' +
                             ' table tr:not(tr:nth-of-type(1))' + 
                             ' td:nth-of-type(3)'
            var emails = $(email_selector);
            break;
        case STAFF:
            email_selector = '.content section:nth-child(6)' +
                             ' table tr:not(tr:nth-of-type(1))' + 
                             ' td:nth-of-type(3)'
        case ADMINSTAFF:    
            break;
        case UNREGISTERED: 
            email_selector = '.content section:nth-child(8)' + 
                             ' table tr:not(tr:nth-of-type(1))' + 
                             ' td:first-of-type'
        default:
            break;
    }
    var emails = $(email_selector);
    for (var item=0; item<emails.length; item++){
        if(emails[item].innerText == email){
            $(emails[item]).parents('tr').remove();
        }
    }
}

function addResultToTable(data){
    // Add the result to the respective table based on userType result
    var INTERN = 90
    var STAFF = 10
    var ADMINSTAFF = 8 
    
    var dataSet = $('<tr>');
    switch(data['userType']){
        case INTERN:
            var activeContentSelector = '.content .content-header:not(.content-header.hidden)'
            var contentActive = $(activeContentSelector)[0].innerText.match('Intern');
            if ( contentActive != null ){
                var activeTableSelector = '.content .content:not(.hidden) table tbody';
                
            } else{
                var activeTableSelector = '.content .content h1:not(.time-display)';
                for (var items=0; items < activeTableSelector.length; items){
                    if (activeTableSelector[items].innerText.match('Intern')){
                        activeTableSelector = $(activeTableSelector[items]);
                        items = 99;
                    }
                }
            }
            
            for (var items=0; items < Object.keys(data).length; items++){
                    var tableData = $('<td>');
                    console.log(Object.keys(data)[items]);
                    tableData.text(data[Object.keys(data)[items]])
                    dataSet.append(tableData);
            }
            $(activeTableSelector).append(dataSet);
            break;
            
        case STAFF:
        case ADMINSTAFF: 
            var activeContentSelector = '.content .content-header:not(.content-header.hidden)'
            var contentActive = $(activeContentSelector)[0].innerText.match('Staff');
            if ( contentActive != null ){
                var activeTableSelector = '.content .content:not(.content-header.hidden table tbody';
                
            } else{
                var activeTableSelector = '.content .content h1:not(.time-display)';
                for (var items=0; items < activeTableSelector.length; items){
                    if (activeTableSelector[items].innerText.match('Staff')){
                        activeTableSelector = $(activeTableSelector[items]);
                        items = 99;
                    }
                }
            }
            
            for (var items=0; items < Object.keys(data).length; items++){
                    var tableData = $('<td>');
                    console.log(Object.keys(data)[items]);
                    tableData.text(data[Object.keys(data)[items]])
                    dataSet.append(tableData);
            }
            $(activeTableSelector).append(dataSet);
            
            break;
        default:
            break;
    }
}

function updateTableWithNewResults(data){
    if (Object.keys(data).includes('register')){
        addResultToTable(data['register'])
    } else if(Object.keys(data).includes('delete')){
        removeResultFromTable(
            data['delete']['email'], 
            data['delete']['userType'])
    } else if(Object.keys(data).includes('error')){
        // Display an error modal that shows 
    }
    
}

function errorOccurred(){
    
}
