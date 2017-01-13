$(document).ready(function(){
    $('#add_unregistered .modal-footer .btn-success').click(formTransmitData)

    $('#add_user .modal-footer .btn-success').click(formTransmitData);

    $('#delete_user .modal-footer .btn-success').click(formTransmitData);
    
    $('#assign_location .modal-footer .btn-success').click(formTransmitData);
    
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
        default: 
            action = $(modalSelector + ' form').attr('action');
            data = $(modalSelector + ' form').serializeArray();
            break;
    }
    
    console.log("Data being sent" + data);
    
    $.post(action, data, null, 'json')
        .done(updateTableWithNewResults)
        .fail(errorOccurred)
        .always(removeModal);
}

function removeModal(){
    $('.modal.in').modal('hide');
}

function removeResultFromTable(id, section){
    id_selector = null
    switch(section){
        case 'INTERN':
            id_selector = '.content section:nth-child(4)' +
                          ' table tr:not(tr:nth-of-type(1))' + 
                          ' td:nth-of-type(3)';
            break; 
        case 'STAFF': 
            id_selector = '.content section:nth-child(6)' + 
                          ' table tr:not(tr:nth-of-type(1))' +
                          ' td:nth-of-type(3)';
            break;
        case 'UNREGISTERED': 
            id_selector = '.content section:nth-child(8)' + 
                          ' table tr:not(tr:nth-of-type(1))' + 
                          ' td:first-of-type';
            break; 
        case 'PC':
            id_selector = '.content section:nth-child(10)' +
                          ' table tr:not(tr:nth-of-type(1))' + 
                          ' td:first-of-type';
            break;
        default:
            break;
    }
    
    if (id_selector == null || id_selector == undefined)
        window.alert("Can't retrieve rows for updated on " + section + "tables");
    
    var rows = $(id_selector);
    for (var item=0; item<rows.length; item++){
        if (rows[item].innerText == id)
            $(rows).parents('tr').remove();
    }
}

function addResultToTable(data, section){
    switch(section){
        case 'UNREGISTERED':
            break;
        case 'INTERN': 
            activeContent = getContentToUpdate(section);
            activeContent.append(generateResultForTable(data));
            break;
        case 'STAFF':
        case 'STAFFADMIN':
            activeContent = getContentToUpdate(section);
            activeContent.append(generateResultForTable(data));
            break;
        case 'PC': 
            break;
            activeContent = getContentToUpdate(section);
            activeContent.append(generateResultForTable(data));
        default:
            break;
    }
}

function getContentToUpdate(section){
    var activeContentSelector = 
        $('.content .content-header:not(.content-header.hidden)');
    
    isContentActive = $(activeContentSelector)[0].innerText;
    matchArgument = null; 
    switch(section){
        case 'INTERN':
            matchArgument = 'Intern';
            break;
        case 'STAFF':
        case 'STAFFADMIN':
            matchArgument = 'Staff';
            break;
        case 'PC':
            matchArgument = "PC"; 
        default:
            break;
    }
    isContentActive = $(activeContentSelector)[0]
                        .innerText.match(matchArgument) != null;
    var activeTable;
    if (isContentActive)
        activeTable = $('.content .content:not(.content.hidden) tbody');
    else{
        activeTable = $('.content.content h1:not(.time-display)');
        for (var items=0; items < activeTable.length; items){
            if (activeTable[items].innerText.match(matchArgument)){
                activeTable = $(activeTable[items]).parent()
                activeTable = activeTable.find('+ .content.content tbody');
                items = 99;
            }
        }
    }
    
    return activeTable;
}

function generateResultForTable(data){
    var dataset = $('<tr>');
    
    for (var items=0; items < Object.keys(data).length; items++){
        var tableData = $('<td>');
        console.log(Object.keys(data)[items]);
        tableData.text(data[Object.keys(data)[items]])
        dataSet.append(tableData);
    }
    
    return dataset; 
}

function updateTableWithNewResults(data){
    switch(Object.keys(data)[0]){
        case 'register':
            var section = null
            if (data['register']['userType'] == 99) 
                section = "UNREGISTERED"
            else if (data['register']['userType'] == 90)
                section = "INTERN"
            else if (data['register']['userType'] == 10)
                section = "STAFF"
            else if (data['register']['userType'] == 8)
                section = "STAFFADMIN"
            
            addResultToTable(data['register'], section);
            break;
        case 'location_assigned':
            addResultToTable(data['location_assigned']['uuid'], 'PC')
            break;
        case 'delete':
            var userType = data['delete']['userType']
            var isIntern = userType == 90 
            var isStaff = userType == 10 || userType == 8 
            var isUnregistered = userType == 99 
            if (isIntern) 
                removeResultFromTable(data['delete']['email'], 'INTERN')
            else if (isStaff)
                removeResultFromTable(data['delete']['email'], 'STAFF')
            else if (isUnregistered)
                removeResultFromTable(data['delete']['email'], 'UNREGISTERED')
            else
                window.alert('Incompatible Type Found')
            break;
        case 'location_unassigned':
            removeResultFromTable(data['location_unassigned']['uuid'], 'PC')
            break; 
        default: 
            break;
    }
}

function errorOccurred(){
    window.alert("There seems to have been an error, please refresh your browser or report the problem");
}

function createBox(data){
    var box = '<div class="col-lg-3 col-xs-6">' +
            '<div class="small-box bg-aqua">' + 
            '<div class="inner">' +
            '<h3>..user_name..</h3>' + 
            '<p>..user_id..</p>'+ 
            '</div>' + 
            '<div class="icon">' + 
            '<i>..arrive_time..</i>' + 
            '</div>' + 
            '<a href="#" class="small-box-footer">Confirm <i class="fa fa-arrow-circle-right"></i></a>' + 
            '</div>' + 
            '</div>';
    
    var re = new RegExp(/\.\.\w*\.\./)
    var filler = re.exec(box);
    for (var i=0;i < 3;i++){
        switch(filler[0]){
            case '..user_name..':
                box = box.replace(filler[0], data.name);
                break;
            case '..user_id..': 
                box = box.replace(filler[0], data.u_id);
                break;
            case '..arrive_time..':
                box = box.replace(filler[0], data.time);
                break;
        }
        filler = re.exec(box);
    }
    
    return $(box);
}


function confirm_time(event, confirm_info){
    var box = $(event.target).parents('.small-box');
    
    var confirm_data = {'u_id': box.find('.inner p').text(), 
                        'method': 'confirm'}

    $.ajax({
        'url': window.location.origin + '/dashboard/messaging/web',
        'data': confirm_data,
        'method': 'POST', 
        'context': {'box': box, 'to': TO_PRESENT}
    }).always().done(moveBox).error(confirm_error)
}

function confirm_error(){
    // TODO Add pulse animation from red to color
    var box_footer = $('.small-box-footer', $(this.box));
    var revertColor = box_footer.css('background');
    box_footer.css('background', 'red');
    box_footer.text('Confirm Error ');
}

function indicate_lunch_start(){
    
}

function indicate_lunch_end(){
    
}

function decorateBox(box, confirm_info){
    var replaceables = $('.inner p', box);
    var confirm_button = $('.small-box-footer i ').click(confirm_time, confirm_info)
    
    replaceables.map(function(value, index ,array){
        $(value).text().replace(/\.\.\w*\.\./, confirm_info[index])
    })
    
    return box 
}

var TO_PRESENT = 'PRESENT'
var TO_ARRIVE = 'CHECKIN'
var TO_LUNCH = 'LUNCH'
var TO_LEAVE = 'CHECKOUT'

function moveBox(){
    var totalBox = $(this.box).parent('.col-lg-3.col-xs-6');
    removeBox(this.box);
    addBox(totalBox, this.to);
}

function removeBox(box){
    // Add animation 
    
    var box_parent = $(box).parent()
    $(box_parent).remove();
}

function addBox(box, where){
    var location = new Map([[TO_PRESENT, '.box-success'],
                        [TO_ARRIVE, '.box-warning'],
                        [TO_LUNCH, '.box-danger'],
                        [TO_LEAVE, '.box-primary']])
    
    var to = location.get(where);
    if (to == undefined){
        console.log('Error adding box');
    }else{
        var section = '.box' + location.get(where) + ' .box-body .row';
        $(box).appendTo(section);
        $('.small-box-footer').click(confirm_time);
    }
}

