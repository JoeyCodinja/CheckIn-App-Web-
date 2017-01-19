// Handles the behaviour related 
// to the navigation around both 
// the staff and intern dashboard 

var STAFF_DASHBOARD = 10
var INTERN_DASHBOARD = 90

var contentViewLinks = $('.sidebar-menu :not(.treeview) a'); 

var contentContainers = $('.content .content, .content .content-header');

contentViewLinks.click(switchContentView);

function whichDashboard(){
    if (window.location.pathname.match('intern') != null )
        return INTERN_DASHBOARD;
    else if (window.location.pathname.match('staff') != null)
        return STAFF_DASHBOARD;
    else
        return Error('unrecognized dashboard');
}

function switchContentView(contentView){
    var contentIndices;
    var antiContentIndices;
    switch(contentView.target.innerText){
        // Show the content list click on, remove all the rest
        case "Intern CheckIn":
            contentIndices = [0, 1]
            antiContentIndices = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            showContentView(contentIndices);
            hideContentView(antiContentIndices);
            break;
        case "Staff":
            contentIndices = [4, 5];
            antiContentIndices = [0, 1, 2, 3, 6, 7, 8, 9, 10, 11];
            showContentView(contentIndices);
            hideContentView(antiContentIndices);
            break;
        case "Intern":
            contentIndices = [2, 3]
            antiContentIndices = [0, 1, 4, 5, 6, 7, 8, 9, 10, 11]
            showContentView(contentIndices);
            hideContentView(antiContentIndices);
            break;
        case "Unregistered":
            contentIndices = [6, 7]
            antiContentIndices = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11]
            showContentView(contentIndices);
            hideContentView(antiContentIndices);
            break;
        case "System Location Management":
            contentIndicies = [8, 9];
            antiContentIndicies = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11];
            showContentView(contentIndicies);
            hideContentView(antiContentIndicies);
        case "Intern Timetable":
            contentIndicies = [10, 11];
            antiContentIndicies = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            showContentView(contentIndicies);
            hideContentView(antiContentIndicies);
        default:
            break;
    }
}

function hideContentView(indicies){
    for (var candidate=0; candidate < indicies.length; candidate++){
        contentContainers[indicies[candidate]].classList.add('hidden');
    }
}

function showContentView(indicies){
    for (var candidate=0; candidate < indicies.length; candidate++){
        contentContainers[indicies[candidate]].classList.remove('hidden');
    }
}

// Gets the day and time from the Intern Timetable
function getDayAndTime(area){
    function removeEmptySpaces(array){
        new_array = []
        
        for (var item=0;item<array.length;item++){
            if (array[item] == "")
                continue
            new_array.push(array[item])
        }
        return new_array;
    }

    if (area.hasOwnProperty('target'))
        area = $(area.target).attr('data-grid');
    else
        area = $(area).attr('data-grid');
    
    var coordsFilter = new RegExp(/(\d)\,*/g)
    
    var coords = Array(2);
    coords[0] = coordsFilter.exec(area)[1];
    coords[1] = coordsFilter.exec(area)[1];
    
    var days = $('th:not(.table-responsive table tr th:first-child)')
                .text()
                .split(/(?:\s)*\s(?=\w)|\s/g);
    times= $('.content .content:last-of-type tbody tr td:first-child')
                .text()
                .split(/(?:\s)*\s(?=\d)|\s/g);
    
    days = removeEmptySpaces(days);
    times = removeEmptySpaces(times);
    
    day = days[Number(coords[1])];
    time = times[Number(coords[0])];
    
    return {'day': day, 'time': time} 
}

$('.btn[data-target*=delete_user]').click(function(){
    var button = $(this);
    
    var dataRow = $('td:not(td:nth-of-type(4))', $(button).parents('tr'));
    
    var passId = dataRow[0];
    var name = dataRow[1];
    var email = dataRow[2];
    
    var modal = $('#delete_user');
    var text = modal.find('.modal-body p')[0].innerText
    text = text.replace('--user-name--', name.innerText + ' ('+email.innerText+')');
    modal.find('.modal-body p')[0].innerText = text;
})

$('.btn[data-target*=add_user]').click(function(){
    
})

$('.btn[data-target*=add_unregistered]').click(function(){
  var button = $(this);
  
  var dataRow = $('td:not(td:nth-of-type(3), td:nth-of-type(4))', $(button).parents('tr'));
  var email = dataRow[0].innerText
  var name = dataRow[1].innerText.split(' ');
 
  var modal = $('#add_unregistered');
  modal.find('#inputEmail').val(email);
  modal.find('#inputFirstName').val(name[0]);
  modal.find('#inputLastName').val(name[1]);
  
  $('#inputEmail, #inputFirstName, #inputLastName').attr('readonly', true);
})  

$('.btn[data-target*=assign_location]').click(function(){
    var button = $(this);
    
    var dataRow = $('td:not(td:nth-of-type(3))', $(button).parents('tr')); 
    var uuid = dataRow[0].innerText;
    
    var modal = $('#assign_location');
    modal.find('#pc_id').val(uuid);
    $(modal.find('#pc_id')).attr('readonly',true);
})

$('i[data-target*=time_table]').click(function(){
    var dayAndTime = getDayAndTime($(this))
    
    $('#time_table input[name=day]').each(function(){
        if ($(this).val() == dayAndTime.day){
            $(this).attr('checked', true)
        }
    });
        
    $('option', '#time_table select[name=start_time]').each(function(){
            if ($(this).val() == dayAndTime.time){
                $(this).attr('selected', true)
                    .parent()
                    .attr('readonly', true);
            }
        });
    
})