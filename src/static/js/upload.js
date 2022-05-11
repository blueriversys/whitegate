function onLoadAction() {
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
