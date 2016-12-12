// Handles the behaviour related 
// to the navigation around both 
// the staff and intern dashboard 

var STAFF_DASHBOARD = 20 
var INTERN_DASHBOARD = 22

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
            antiContentIndices = [2, 3, 4, 5, 6, 7]
            showContentView(contentIndices);
            hideContentView(antiContentIndices);
            break;
        case "Staff":
            contentIndices = [4, 5];
            antiContentIndices = [0, 1, 2, 3, 6, 7];
            showContentView(contentIndices);
            hideContentView(antiContentIndices);
            break;
        case "Intern":
            contentIndices = [2, 3]
            antiContentIndices = [0, 1, 4, 5, 6, 7]
            showContentView(contentIndices);
            hideContentView(antiContentIndices);
            break;
        case "Unregistered":
            contentIndices = [6, 7]
            antiContentIndices = [0, 1, 2, 3, 4, 5]
            showContentView(contentIndices);
            hideContentView(antiContentIndices);
            break;
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
  
  var dataRow = $('td:not(td:nth-of-type(3))', $(button).parents('tr'));
  var email = dataRow[0].innerText
  var name = dataRow[1].innerText.split(' ');
 
  var modal = $('#add_unregistered');
  modal.find('#inputEmail').val(email);
  modal.find('#inputFirstName').val(name[0]);
  modal.find('#inputLastName').val(name[1]);
  
  $('#inputEmail, #inputFirstName, #inputLastName').attr('readonly', true);
})  
