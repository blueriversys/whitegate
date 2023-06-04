function onLoadAction() {
    loadAnnouncs();
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

function deleteFile(filepath, filename) {
    var request = new XMLHttpRequest()
    request.open('POST', '/deletefile', true)

    request.onload = function () {
        // Begin accessing JSON data here
        var json = JSON.parse(this.response);

        if (request.status >= 200 && request.status < 400) {
            if (json.status == 'success') {
                alert('File ' + filename + ' has been deleted.');
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

function loadAnnouncs() {
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

