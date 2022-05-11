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


async function uploadFile(filename) {
  let formData = new FormData(); 
  var fileupload = document.getElementById(filename);

  if (fileupload.files[0] == undefined || fileupload.files[0] == "") {
  	  alert('Please select a document file before clicking the upload button.');
  	  return;
  }

  formData.append("file", fileupload.files[0]);
  formData.append("convname", filename);

  await fetch('/upload', {
    method: "POST", 
    body: formData
  }).then(response => {
      if (!response.ok) {
         throw new Error('The file upload has failed.');
      }
      else {
         alert('File upload was successful.');
      }
  });
}


function sendEmail(json) {
  var userid = json.response.resident.userid;
  var passw = json.response.resident.password;
  var email = json.response.resident.email;
  //alert('userid '+userid + '   pass '+passw);

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
  var unit = document.getElementById("unitid").value;
  retrieveUser('unit', unit);
}

function retrieveUserByUserId() {
  var userid = document.getElementById('userid').value;
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
  request.open('POST', '/saveresident', true)
  
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
  requestObj.unit = document.getElementById('unitid').value;
  requestObj.userid = document.getElementById('userid').value;
  requestObj.lastname = document.getElementById('lastname').value;
  requestObj.name = document.getElementById('name').value;
  requestObj.email = document.getElementById('email').value;
  requestObj.startdt = document.getElementById('startdt').value;
  requestObj.phone = document.getElementById('phone').value;
  requestObj.type = document.getElementById('type').value;

  if (requestObj.userid === '') {
    alert('User Id is a required field');
    return;
  }

  if (requestObj.lastname === '') {
    alert('Last Name is a required field');
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

  // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
  jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);
}

function cleanScreen() {
  document.getElementById('userid').value = '';
  document.getElementById('lastname').value = '';
  document.getElementById('name').value = '';
  document.getElementById('email').value = '';
  document.getElementById('startdt').value = '';
  document.getElementById('phone').value = '';
  document.getElementById('type').value = '';
}

function populateScreen(json) {
  var unit = json.response.resident.unit;
  var userid = json.response.resident.userid;
  var lastname = json.response.resident.lastname;
  var name = json.response.resident.name;
  var email = json.response.resident.email;
  var startdt = json.response.resident.startdt;
  var phone = json.response.resident.phone;
  var type = json.response.resident.type;

  document.getElementById('unitid').value = unit;
  document.getElementById('userid').value = userid;
  document.getElementById('lastname').value = lastname;
  document.getElementById('name').value = name;
  document.getElementById('email').value = email;
  document.getElementById('startdt').value = startdt;
  document.getElementById('phone').value = phone;
  document.getElementById('type').value = type;
}

function populateTable(json) {
  var table = document.getElementById('residentstableid');
  var rowCount = table.rows.length;
  
  for (var x=rowCount-1; x>0; x--) {
      table.deleteRow(x);
  }

  for (var i=0; i<json.residents.length; i++) {
      var row = table.insertRow( -1 ); // -1 is insert as last  
      var cell0 = row.insertCell( - 1 ); // -1 is insert as last            
      var cell1 = row.insertCell( - 1 ); // -1 is insert as last            
      var cell2 = row.insertCell( - 1 ); // -1 is insert as last   
      var cell3 = row.insertCell( - 1 ); // -1 is insert as last   
      var cell4 = row.insertCell( - 1 ); // -1 is insert as last   
      var cell5 = row.insertCell( - 1 ); // -1 is insert as last   
      var cell6 = row.insertCell( - 1 ); // -1 is insert as last   
      var cell7 = row.insertCell( - 1 ); // -1 is insert as last   
      var unit = json.residents[i].unit;
      var userid = json.residents[i].userid;
      var password = json.residents[i].password;
      var lastname = json.residents[i].lastname;
      var name = json.residents[i].name;
      var email = json.residents[i].email;
      var startdt = json.residents[i].startdt;
      var phone = json.residents[i].phone;
      cell0.innerHTML = unit;
      cell1.innerHTML = userid;
      cell2.innerHTML = password;
      cell3.innerHTML = lastname;
      cell4.innerHTML = name;
      cell5.innerHTML = email;
      cell6.innerHTML = startdt;
      cell7.innerHTML = phone;
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
