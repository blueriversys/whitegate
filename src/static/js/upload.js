function onLoadAction() {
    document.getElementById("email-progress-bar").style.display = "none";
    fillAnnouncs();
}

/*
   This is invoked by upload.html to fill the announcements text box.
   Unfortunately, this cannot be placed in announcs.js because
   doing so would force us to import announcs.js from upload.html,
   which would create a double "onLoadAction()" function
*/
function fillAnnouncs() {
    var request = new XMLHttpRequest()
    request.open('GET', '/getannouncs', true)

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          var announcs_text = '';
          for (var i=0; i<json.announcs.length; i++) {
              announcs_text += json.announcs[i] + '\n';
          }
          document.getElementById('announctextfield_id').innerHTML = announcs_text;
      }
      else {
          alert('Error retrieving announcements list')
      }

    }

    request.send();
}

/*
   This is invoked by upload.html to save announcements.
   Unfortunately, this cannot be placed in announcs.js because
   doing so would force us to import announcs.js from upload.html,
   which would create a double "onLoadAction()" function
*/
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

function uploadFileProgress(convname, fileControl, barControl) {
    // retrieve the file object from the DOM
    let file = document.getElementById(fileControl).files[0];

    // test to make sure the user chose a file
    if (file == undefined || file == "") {
        alert('Please select a file before clicking the upload button.');
        return;
    }

    //print file details
    console.log("File Name : ",file.name);
    console.log("File size : ",file.size);
    console.log("File type : ",file.type);

    // create form data to send via XHR request
    var formData = new FormData();
    formData.append("file", file);
    formData.append("filesize", ''+file.size); // append only takes string as 2nd arg
    formData.append("convname", convname);

    //create XHR object to send request
    var request = new XMLHttpRequest();

    var progressBar = document.getElementById(barControl);
    progressBar.value = 0;
    progressBar.style.display="inline";

    // add a progress event handler to the AJAX request
    request.upload.addEventListener('progress', event => {
        let totalSize = event.total; // total size of the file in bytes
        let loadedSize = event.loaded; // loaded size of the file in bytes
        // calculate percentage
        var percent = (event.loaded / event.total) * 100;
        progressBar.value = Math.round(percent);
    });

    // initializes a newly-created request
    request.open('POST', '/upload', true);

    // ask to be notified when the upload is finished
    request.onreadystatechange = () => {
        if (request.readyState == 4 && request.status == 200) {
            progressBar.value = 100;
            alert('File '+file.name + ' successfully uploaded');
            progressBar.style.display="none";
        }
    };

    // send request to the server
    request.send(formData);
}

function deleteFile(filepath, filename) {
    var request = new XMLHttpRequest()
    request.open('POST', '/deletefile', true)

    request.onload = function () {
        // Begin accessing JSON data here
        var json = JSON.parse(this.response);

        if (request.status >= 200 && request.status < 400) {
            if (json.status == 'success') {
                alert('File ' + filename + ' has been deleted.');
                location.reload(true);
            }
            else {
                alert("Some error occurred trying to delete file "+filename);
            }
        }
        else {
            alert('Error communicating with the server.');
        }
    }

    var requestObj = new Object();
    requestObj.filepath = filepath;
    requestObj.filename = filename;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}


