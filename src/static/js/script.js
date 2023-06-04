$(document).ready(function() {
	$(".photo").on('click', function() {
		var url = $(this).attr('src');
		$("#modal-image").attr('src', url);
		$("#myModal").modal("show");
	});
/*
  $("#sidebar").mCustomScrollbar({
      theme: "minimal"
  });
*/
  $('#menuButtonOpen, #menuButtonClose').on('click', function () {
      $('#sidebar, #content').toggleClass('active');
      $('.collapse.in').toggleClass('in');
      $('a[aria-expanded=true]').attr('aria-expanded', 'false');
  });
/*
  $('#sidebarClose').on('click', function () {
    $('#sidebar, #content').toggleClass('active');
    $('.collapse.in').toggleClass('in');
    $('a[aria-expanded=true]').attr('aria-expanded', 'false');
  });
*/
});


//SERVER = 'localhost'
//PORT   = 9999


function sendEmail(json) {
  var userid = json.response.resident.userid;
  var passw = json.response.resident.password;
  var email = json.response.resident.email;

  // here we make a request to "sendsinglemail"
  var request = new XMLHttpRequest();
  request.open('POST', '/sendsinglemail', true)
  
  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);
    
    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'error') {
            alert('error sending email to user');
        }
        else {
            alert('Email sent to user');
        }
    } 
    else {
        alert('Error sending email');
    }

    return;
  }    

  var requestObj = new Object();
  requestObj.emailto = email;
  requestObj.subject = 'Your whitegatecondo.com info';
  requestObj.body = 'Your credential to access whitegatecondo.com:\n\nusername: ' + userid + "\npassword: " + passw ;

  // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
  jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);
}


// here we make a request to "sendmail"
function sendBulkEmail() {
  var request = new XMLHttpRequest();
  request.open('POST', '/sendmail', true)
  
  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);
    
    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'error') {
            alert('Error sending email to all users');
        }
        else {
            alert('Email sent to all users');
        }
    } 
    else {
        alert('Error sending email to all users');
    }

    return;
  }    

  var requestObj = new Object();
  requestObj.subject = document.getElementById('titlefield_id').value;
  requestObj.body = document.getElementById('emailtextfield_id').value;

  if ( requestObj.subject.trim().length == 0 || requestObj.body.trim().length == 0 ) {
      alert("Title and Body of the message are required");
      return;
  }

  jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);
}


// we retrieve the user data from the database first
// then we use that data to send him an email.
function startSendEmail() {
  var userid = document.getElementById("userid").value;
  var request = new XMLHttpRequest();
  request.open('POST', '/getresident', true)

  var requestObj = new Object();
  requestObj.type = 'user';
  requestObj.id = userid;
  jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);
  
  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);
    
    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'not_found') {
            alert('Record not found for User Id '+userid);
            return;
        }

        if (json.response.resident.email.trim().length == 0) {
            alert("User doesn't have an email address on file");
            return;
        }
              
        sendEmail(json);
    } 
    else {
        alert('Error retrieving user');
        return;
    }
  }    

}

function saveAnnouncs() {
  var announcs = document.getElementById("announctextfield_id").value;
  var request = new XMLHttpRequest();
  request.open('POST', '/saveannouncs', true)

  var requestObj = new Object();
  requestObj.lines = announcs;
  jsonStr = '{ "announc": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);

  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);

    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'success') {
            alert('Announcements have been saved.');
            return;
        }
        else {
            alert('There was a problem trying to save the announcements.');
            return;
        }
    }
    else {
        alert('Error saving the announcements.');
        return;
    }
  }

}





function retrieveUsers() {
  var request = new XMLHttpRequest()
  request.open('GET', '/getresidents', true)
  
  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);
    
    if (request.status >= 200 && request.status < 400) {
//        if (json.user.status == 'loggedout') {
//            document.location.href = '/login';
//            return;
//        }
        
        // populate table
        populateTable(json);
    } 
    else {
        alert('Error retrieving residents list')
    }
      
  }    

  request.send();
}

function retrieveUserByUnit() {
  var unit = document.getElementById("maint_unit").value;
  retrieveUser('unit', unit);
}

function retrieveUserByUserId() {
  var userid = document.getElementById('maint_userid').value;
  if (userid === '') {
    alert('Must enter a User Id for this search.');
    return;
  }

  retrieveUser('user', userid);
}

function retrieveUser(type, argValue) {
  var request = new XMLHttpRequest();
  request.open('POST', '/getresident', true)
  
  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);
    
    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'not_found') {
            if (type === 'unit') {
              alert('Record not found for unit '+argValue);
            }
            else {
              alert('Record not found for User Id '+argValue);
            }
        
            cleanScreen();
            return;
        }
        
        // populate table
        populateScreen(json);
    } 
    else {
        alert('Error retrieving user')
    }
      
  }    

  var requestObj = new Object();
  requestObj.type = type;
  requestObj.id = argValue;

  // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
  jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);
}

function saveUser() {
  var request = new XMLHttpRequest();
  request.open('POST', '/saveresidentpartial', true)
  
  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);
    
    if (request.status >= 200 && request.status < 400) {
        alert('Record saved to database');
    } 
    else {
        alert('Error saving record to database')
    }
  }    

  var requestObj = new Object();
  requestObj.unit = document.getElementById('maint_unit').value;
  requestObj.userid = document.getElementById('maint_userid').value;
  requestObj.password = document.getElementById('maint_password').value;
  requestObj.name = document.getElementById('maint_name').value;
  requestObj.email = document.getElementById('maint_email').value;
  requestObj.phone = document.getElementById('maint_phone').value;
  requestObj.ownername = document.getElementById('maint_ownername').value;
  requestObj.owneremail = document.getElementById('maint_owneremail').value;
  requestObj.ownerphone = document.getElementById('maint_ownerphone').value;

  startdt = new Object();
  startdt.month = document.getElementById('maint_startdt_month').value;
  startdt.year = document.getElementById('maint_startdt_year').value;
  requestObj.startdt = startdt;
  requestObj.type = document.getElementById('maint_type').value;

  const occupants = [];
  occupants[0]= new Object();
  occupants[1]= new Object();
  occupants[2]= new Object();
  occupants[3]= new Object();
  occupants[4]= new Object();
  occupants[0].name = document.getElementById('maint_occup1_name').value;
  occupants[0].email = document.getElementById('maint_occup1_email').value;
  occupants[0].cc = document.getElementById('maint_occup1_cc').checked;
  occupants[0].phone = document.getElementById('maint_occup1_phone').value;
  occupants[1].name = document.getElementById('maint_occup2_name').value;
  occupants[1].email = document.getElementById('maint_occup2_email').value;
  occupants[1].cc = document.getElementById('maint_occup2_cc').checked;
  occupants[1].phone = document.getElementById('maint_occup2_phone').value;
  occupants[2].name = document.getElementById('maint_occup3_name').value;
  occupants[2].email = document.getElementById('maint_occup3_email').value;
  occupants[2].cc = document.getElementById('maint_occup3_cc').checked;
  occupants[2].phone = document.getElementById('maint_occup3_phone').value;
  occupants[3].name = document.getElementById('maint_occup4_name').value;
  occupants[3].email = document.getElementById('maint_occup4_email').value;
  occupants[3].cc = document.getElementById('maint_occup4_cc').checked;
  occupants[3].phone = document.getElementById('maint_occup4_phone').value;
  occupants[4].name = document.getElementById('maint_occup5_name').value;
  occupants[4].email = document.getElementById('maint_occup5_email').value;
  occupants[4].cc = document.getElementById('maint_occup5_cc').checked;
  occupants[4].phone = document.getElementById('maint_occup5_phone').value;
  requestObj.occupants = occupants;

  if (requestObj.userid === '') {
    alert('User Id is a required field');
    return;
  }

  if (requestObj.name === '') {
    alert('Name is a required field');
    return;
  }

/*  
  if (requestObj.email === '') {
    alert('Email is a required field');
    return;
  }
*/

  if (requestObj.type === '') {
    alert('Type of resident must be selected');
    return;
  }

  if (requestObj.password === '') {
    alert('Password must be filled out');
    return;
  }

  // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
  jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);
}

function cleanScreen() {
    document.getElementById('maint_userid').value = '';
    document.getElementById('maint_password').value = '';
    document.getElementById('maint_name').value = '';
    document.getElementById('maint_email').value = '';
    document.getElementById('maint_phone').value = '';
    document.getElementById('maint_ownername').value = '';
    document.getElementById('maint_owneremail').value = '';
    document.getElementById('maint_ownerphone').value = '';
    document.getElementById('maint_startdt_month').value = '';
    document.getElementById('maint_startdt_year').value = '';
    document.getElementById('maint_type').value = '';

    document.getElementById('maint_occup1_name').value = '';
    document.getElementById('maint_occup1_email').value = '';
    document.getElementById('maint_occup1_cc').checked = false;
    document.getElementById('maint_occup1_phone').value = '';
    document.getElementById('maint_occup2_name').value = '';
    document.getElementById('maint_occup2_email').value = '';
    document.getElementById('maint_occup2_cc').checked = false;
    document.getElementById('maint_occup2_phone').value = '';
    document.getElementById('maint_occup3_name').value = '';
    document.getElementById('maint_occup3_email').value = '';
    document.getElementById('maint_occup3_cc').checked = false;
    document.getElementById('maint_occup3_phone').value = '';
    document.getElementById('maint_occup4_name').value = '';
    document.getElementById('maint_occup4_email').value = '';
    document.getElementById('maint_occup4_cc').checked = false;
    document.getElementById('maint_occup4_phone').value = '';
    document.getElementById('maint_occup5_name').value = '';
    document.getElementById('maint_occup5_email').value = '';
    document.getElementById('maint_occup5_cc').checked = false;
    document.getElementById('maint_occup5_phone').value = '';
}

function populateScreen(json) {
    var unit = json.response.resident.unit;
    var userid = json.response.resident.userid;
    var password = json.response.resident.password;
    var name = json.response.resident.name;
    var email = json.response.resident.email;
    var phone = json.response.resident.phone;
    var ownername = json.response.resident.ownername;
    var owneremail = json.response.resident.owneremail;
    var ownerphone = json.response.resident.ownerphone;
    var startdtMonth = json.response.resident.startdt.month;
    var startdtYear = json.response.resident.startdt.year;
    var type = json.response.resident.type;

    document.getElementById('maint_unit').value = unit;
    document.getElementById('maint_userid').value = userid;
    document.getElementById('maint_password').value = password;
    document.getElementById('maint_name').value = name;
    document.getElementById('maint_email').value = email;
    document.getElementById('maint_phone').value = phone;
    document.getElementById('maint_ownername').value = ownername;
    document.getElementById('maint_owneremail').value = owneremail;
    document.getElementById('maint_ownerphone').value = ownerphone;
    document.getElementById('maint_startdt_month').value = startdtMonth;
    document.getElementById('maint_startdt_year').value  = startdtYear;
    document.getElementById('maint_type').value = type;

    if ( json.response.resident.occupants.length != 0) {
        document.getElementById('maint_occup1_name').value = json.response.resident.occupants[0].name;
        document.getElementById('maint_occup1_email').value = json.response.resident.occupants[0].email;
        document.getElementById('maint_occup1_cc').checked = json.response.resident.occupants[0].cc;
        document.getElementById('maint_occup1_phone').value = json.response.resident.occupants[0].phone;
        document.getElementById('maint_occup2_name').value = json.response.resident.occupants[1].name;
        document.getElementById('maint_occup2_email').value = json.response.resident.occupants[1].email;
        document.getElementById('maint_occup2_cc').checked = json.response.resident.occupants[1].cc;
        document.getElementById('maint_occup2_phone').value = json.response.resident.occupants[1].phone;
        document.getElementById('maint_occup3_name').value = json.response.resident.occupants[2].name;
        document.getElementById('maint_occup3_email').value = json.response.resident.occupants[2].email;
        document.getElementById('maint_occup3_cc').checked = json.response.resident.occupants[2].cc;
        document.getElementById('maint_occup3_phone').value = json.response.resident.occupants[2].phone;
        document.getElementById('maint_occup4_name').value = json.response.resident.occupants[3].name;
        document.getElementById('maint_occup4_email').value = json.response.resident.occupants[3].email;
        document.getElementById('maint_occup4_cc').checked = json.response.resident.occupants[3].cc;
        document.getElementById('maint_occup4_phone').value = json.response.resident.occupants[3].phone;
        document.getElementById('maint_occup5_name').value = json.response.resident.occupants[4].name;
        document.getElementById('maint_occup5_email').value = json.response.resident.occupants[4].email;
        document.getElementById('maint_occup5_cc').checked = json.response.resident.occupants[4].cc;
        document.getElementById('maint_occup5_phone').value = json.response.resident.occupants[4].phone;
    }
    else {
        document.getElementById('maint_occup1_name').value = '';
        document.getElementById('maint_occup1_email').value = '';
        document.getElementById('maint_occup1_cc').checked = '';
        document.getElementById('maint_occup1_phone').value = '';
        document.getElementById('maint_occup2_name').value = '';
        document.getElementById('maint_occup2_email').value = '';
        document.getElementById('maint_occup2_cc').checked = '';
        document.getElementById('maint_occup2_phone').value = '';
        document.getElementById('maint_occup3_name').value = '';
        document.getElementById('maint_occup3_email').value = '';
        document.getElementById('maint_occup3_cc').checked = '';
        document.getElementById('maint_occup3_phone').value = '';
        document.getElementById('maint_occup4_name').value = '';
        document.getElementById('maint_occup4_email').value = '';
        document.getElementById('maint_occup4_cc').checked = '';
        document.getElementById('maint_occup4_phone').value = '';
        document.getElementById('maint_occup5_name').value = '';
        document.getElementById('maint_occup5_email').value = '';
        document.getElementById('maint_occup5_cc').checked = '';
        document.getElementById('maint_occup5_phone').value = '';
    }
}

function populateTable(json) {
  var table = document.getElementById('residentstableid');
  var rowCount = table.rows.length;
  
  for (var x=rowCount-1; x>0; x--) {
      table.deleteRow(x);
  }

  for (var i=0; i<json.residents.length; i++) {
      var row = table.insertRow( -1 ); // -1 is insert as last  
      var unit_cell = row.insertCell( - 1 ); // -1 is insert as last
      var user_id_cell = row.insertCell( - 1 ); // -1 is insert as last
      var pass_cell = row.insertCell( - 1 ); // -1 is insert as last
      var name_cell = row.insertCell( - 1 ); // -1 is insert as last
      var email_cell = row.insertCell( - 1 ); // -1 is insert as last
      var phone_cell = row.insertCell( - 1 ); // -1 is insert as last
      var ownername_cell = row.insertCell( - 1 ); // -1 is insert as last
      var owneremail_cell = row.insertCell( - 1 ); // -1 is insert as last
      var ownerphone_cell = row.insertCell( - 1 ); // -1 is insert as last
      var startdate_cell = row.insertCell( - 1 ); // -1 is insert as last

      var unit = json.residents[i].unit;
      var userid = json.residents[i].userid;
      var password = json.residents[i].password;
      var name = json.residents[i].name;
      var email = json.residents[i].email;
      var phone = json.residents[i].phone;
      var ownername = json.residents[i].ownername;
      var owneremail = json.residents[i].owneremail;
      var ownerphone = json.residents[i].ownerphone;
      var startdtMonth = json.residents[i].startdt.month;
      var startdtYear = json.residents[i].startdt.year;

      unit_cell.innerHTML = unit;
      user_id_cell.innerHTML = userid;
      pass_cell.innerHTML = password;
      name_cell.innerHTML = name;
      email_cell.innerHTML = email;
      phone_cell.innerHTML = phone;
      ownername_cell.innerHTML = ownername;
      owneremail_cell.innerHTML = owneremail;
      ownerphone_cell.innerHTML = ownerphone;
      if (startdtMonth != '' && startdtYear != '') {
          startdate_cell.innerHTML = startdtMonth + "/" + startdtYear;
      }
  }
}

