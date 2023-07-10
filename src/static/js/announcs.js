/*
   This is invoked by announcs.html to handle announcement related operations.
   Also used by announcs.html to load announcements, loadAnnouncs()
*/

/* invoked by announcs.html */
function onLoadAction() {
    loadAnnouncs();
}

function loadAnnouncs() {
    var request = new XMLHttpRequest()
    request.open('GET', '/getannouncs', true)
    
    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);
      
      if (request.status >= 200 && request.status < 400) {
          var ul = document.getElementById("announc-list");
          for (var i=0; i<json.announcs.length; i++) {
              var li = document.createElement("li");
              li.appendChild(document.createTextNode('example li'));
              ul.appendChild(li);
              li.innerHTML = json.announcs[i];
          }            
      } 
      else {
          alert('Error retrieving announcements list')
      }
        
    }    
  
    request.send();
}

