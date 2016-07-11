// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

function make_ajax_query(url, type, data, response_func, error_func){
  $.ajax({  //Call ajax function sending the option loaded
    url: url,  //This is the url of the ajax view where you make the search
    type: type,
    data: data,
    success: function(response) {
      console.log(response)
      if (response.error) { // If the function fails
          if(error_func){
            error_func(response.error_text);
          }else{
            alert(response.error_text);
          }
      } else {  // Success
          response_func(response);
      }
    }
  });
}

$(document).ready(function() {

  $("#about-btn").click( function(event) {
    alert("You clicked the button using JQuery!");
  });

  $("#about-btn2").click( function(event){
      //You have to get in this code the values you need to work with, for example:
      var my_json = {start:0,
      max:10,
      search_string:"sadsad",}

      make_ajax_query("/ajax_url/", 'POST', my_json,
      console.log);
  });
});
