function onLoadAction() {
    loadResident();
}

function loadResident() {
  var request = new XMLHttpRequest();
  request.open('GET', '/getloggedinuser', true);
  request.send();

  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);

    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'not_found') {
            alert('Error trying to retrieve logged in user.');
            return;
        }

        retrieveLoggedinResident(json.response.resident.unit);
    }
    else {
        alert('Error retrieving user')
    }
  }
}

function retrieveLoggedinResident(residentUnit) {
  var request = new XMLHttpRequest();
  request.open('POST', '/getresident', true)

  var requestObj = new Object();
  requestObj.type = 'unit';
  requestObj.id = residentUnit;
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

        document.getElementById('unit').innerHTML = json.response.resident.unit;
        document.getElementById('user_id').innerHTML = json.response.resident.userid;
        document.getElementById('name').value = json.response.resident.name;
        document.getElementById('email').value = json.response.resident.email;
        document.getElementById('phone').value = json.response.resident.phone;
        document.getElementById('ownername').value = json.response.resident.ownername;
        document.getElementById('owneremail').value = json.response.resident.owneremail;
        document.getElementById('ownerphone').value = json.response.resident.ownerphone;

        document.getElementById('startdt_month').value = json.response.resident.startdt.month;
        document.getElementById('startdt_year').value  = json.response.resident.startdt.year;

        if ( json.response.resident.occupants.length != 0) {
            document.getElementById('occup1_name').value = json.response.resident.occupants[0].name;
            document.getElementById('occup1_email').value = json.response.resident.occupants[0].email;
            document.getElementById('occup1_cc').checked = json.response.resident.occupants[0].cc;
            document.getElementById('occup1_phone').value = json.response.resident.occupants[0].phone;

            document.getElementById('occup2_name').value = json.response.resident.occupants[1].name;
            document.getElementById('occup2_email').value = json.response.resident.occupants[1].email;
            document.getElementById('occup2_cc').checked = json.response.resident.occupants[1].cc;
            document.getElementById('occup2_phone').value = json.response.resident.occupants[1].phone;

            document.getElementById('occup3_name').value = json.response.resident.occupants[2].name;
            document.getElementById('occup3_email').value = json.response.resident.occupants[2].email;
            document.getElementById('occup3_cc').checked = json.response.resident.occupants[2].cc;
            document.getElementById('occup3_phone').value = json.response.resident.occupants[2].phone;

            document.getElementById('occup4_name').value = json.response.resident.occupants[3].name;
            document.getElementById('occup4_email').value = json.response.resident.occupants[3].email;
            document.getElementById('occup4_cc').checked = json.response.resident.occupants[3].cc;
            document.getElementById('occup4_phone').value = json.response.resident.occupants[3].phone;

            document.getElementById('occup5_name').value = json.response.resident.occupants[4].name;
            document.getElementById('occup5_email').value = json.response.resident.occupants[4].email;
            document.getElementById('occup5_cc').checked = json.response.resident.occupants[4].cc;
            document.getElementById('occup5_phone').value = json.response.resident.occupants[4].phone;
        }

        document.getElementById('curr_password').value = '';
        document.getElementById('new_password').value = '';
        document.getElementById('repeat_password').value = '';

        // set the change id panel fields to blank
        document.getElementById('changeid_panel_password').value = '';
        document.getElementById('new_userid').value = json.response.resident.userid;
    }
    else {
        alert('Error retrieving user');
        return;
    }
  }
}


function saveResident() {
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
  requestObj.unit = document.getElementById('unit').innerHTML;
  requestObj.userid = document.getElementById('user_id').innerHTML;
  requestObj.name = document.getElementById('name').value;
  requestObj.email = document.getElementById('email').value;
  requestObj.phone = document.getElementById('phone').value;
  requestObj.ownername = document.getElementById('ownername').value;
  requestObj.owneremail = document.getElementById('owneremail').value;
  requestObj.ownerphone = document.getElementById('ownerphone').value;

  const occupants = [];
  occupants[0]= new Object();
  occupants[1]= new Object();
  occupants[2]= new Object();
  occupants[3]= new Object();
  occupants[4]= new Object();

  startdt = new Object();
  startdt.month = document.getElementById('startdt_month').value;
  startdt.year = document.getElementById('startdt_year').value;
  requestObj.startdt = startdt;

  occupants[0].name = document.getElementById('occup1_name').value;
  occupants[0].email = document.getElementById('occup1_email').value;
  occupants[0].cc = document.getElementById('occup1_cc').checked;
  occupants[0].phone = document.getElementById('occup1_phone').value;

  occupants[1].name = document.getElementById('occup2_name').value;
  occupants[1].email = document.getElementById('occup2_email').value;
  occupants[1].cc = document.getElementById('occup2_cc').checked;
  occupants[1].phone = document.getElementById('occup2_phone').value;

  occupants[2].name = document.getElementById('occup3_name').value;
  occupants[2].email = document.getElementById('occup3_email').value;
  occupants[2].cc = document.getElementById('occup3_cc').checked;
  occupants[2].phone = document.getElementById('occup3_phone').value;

  occupants[3].name = document.getElementById('occup4_name').value;
  occupants[3].email = document.getElementById('occup4_email').value;
  occupants[3].cc = document.getElementById('occup4_cc').checked;
  occupants[3].phone = document.getElementById('occup4_phone').value;

  occupants[4].name = document.getElementById('occup5_name').value;
  occupants[4].email = document.getElementById('occup5_email').value;
  occupants[4].cc = document.getElementById('occup5_cc').checked;
  occupants[4].phone = document.getElementById('occup5_phone').value;

  requestObj.occupants = occupants;

  if (requestObj.userid === '') {
    alert('User Id is a required field');
    return;
  }

  if (requestObj.headname === '') {
    alert('Head of household name is a required field');
    return;
  }

  // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
  jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);
}

function changePassword() {
  var userid = document.getElementById("user_id").innerHTML;
  var unit = document.getElementById("unit").innerHTML;
  var curr_password = document.getElementById("curr_password").value;
  var new_password = document.getElementById("new_password").value;
  var repeat_password = document.getElementById("repeat_password").value;

  // check the quality of the new password
  new_password = new_password.trim();
  repeat_password = repeat_password.trim();

  if (new_password != repeat_password) {
      alert("New password and Repeat password fields don't match");
      return;
  }

  if ( new_password.length < 6) {
      alert("New password doesn't have a minimum of 6 characters");
      return;
  }

  // prepare structure to send to backend
  var request = new XMLHttpRequest();
  request.open('POST', '/getresident', true)
  var requestObj = new Object();
  requestObj.type = 'unit';
  requestObj.id = unit;
  jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);

  // invoke backend to check if the type current password matches current password
  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);

    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'not_found') {
            alert('Record not found for User Id '+userid);
            return;
        }

        db_password = json.response.resident.password;

        if (db_password != curr_password) {
            alert("The current password you entered doesn't match your current password on file");
            return;
        }


        // all is good, let's change the password
        change_db_password(json.response.resident.unit, new_password);
    }
    else {
        alert('Error retrieving user');
        return;
    }
  }
}

function change_db_password(unit, new_password) {
  var request = new XMLHttpRequest();
  request.open('POST', '/changepassword', true)

  // prepare structure to invoke backend
  var requestObj = new Object();
  requestObj.unit = unit;
  requestObj.password = new_password;
  jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);

  // load data obtained from backend
  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);

    if (request.status >= 200 && request.status < 400) {
        document.getElementById('curr_password').value = '';
        document.getElementById('new_password').value = '';
        document.getElementById('repeat_password').value = '';
        alert('New password saved to database');
    }
    else {
        alert('Error saving password to database')
    }
  }
}

function changeUserid() {
  var userid = document.getElementById("user_id").innerHTML;
  var unit = document.getElementById("unit").innerHTML;
  var new_userid = document.getElementById("new_userid").value;
  var curr_password = document.getElementById("changeid_panel_password").value;

  if ( new_userid.length < 1) {
      alert("New user id cannot be blank");
      return;
  }

  // prepare structure to send to backend
  var request = new XMLHttpRequest();
  request.open('POST', '/getresident', true)
  var requestObj = new Object();
  requestObj.type = 'unit';
  requestObj.id = unit;
  jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);

  // invoke backend to check if the current password typed in matches the current password
  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);

    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'not_found') {
            alert('Record not found for User Id '+userid);
            return;
        }

        db_password = json.response.resident.password;

        if (db_password != curr_password) {
            alert("The current password you entered doesn't match your password on file");
            return;
        }

        // all is good, let's change the password
        change_db_userid(json.response.resident.unit, new_userid);
    }
    else {
        alert('Error retrieving user');
        return;
    }
  }
}

function change_db_userid(unit, new_userid) {
  var request = new XMLHttpRequest();
  request.open('POST', '/changeuserid', true)

  // prepare structure to invoke backend
  var requestObj = new Object();
  requestObj.unit = unit;
  requestObj.userid = new_userid;
  jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);

  // load data obtained from backend
  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);

    if (request.status >= 200 && request.status < 400) {
        document.getElementById('changeid_panel_password').value = '';
        document.getElementById('user_id').innerHTML = new_userid;
        alert('New user id saved to database');
    }
    else {
        alert('Error saving user id to database')
    }
  }
}


