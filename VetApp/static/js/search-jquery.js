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


// <tr>
//     <th><a href="/animal?id=1" target="_blank">asd </a></th>
//     <th>fdhg</th>
//     <th class="text-center">3 </th>
//     <th class="text-center">3 </th>
//     <th class="text-center">3 </th>
//     <th class="text-center">3 </th>
// </tr>

/*
  table_name should be in format "type_whrite_anything_here"
  i.e animal_table_1, because table_name is used to determine link address

  object_list [<object_in_json>, ...]
  header_list [str, ...] in correct order, allways should start with pk!
  insert_top, set True if want to set new items in top of list
  link, if true makes link to address that object
*/
function insertRowToTable(table_name, object_list, header_list, link){
  var table = document.getElementById(table_name);

  for(var key in object_list){
    var obj = object_list[key];
    var row = table.insertRow(-1);

    //make hidden pk column
    var cell = row.insertCell(0);
    cell.innerHTML = obj[header_list[0]];
    cell.style = 'display:none'

    //make link to object if wanted
    var i = 1;
    if(link){ //make
      row.insertCell(i).innerHTML = '<a target="_blank" href="/'+ table_name.split('_')[0] +'/?id='+obj['pk']+'">' + obj[header_list[i]] + '</a>'
      i++;
    }

    //insert data to row
    for(; i < header_list.length; i++){
      row.insertCell(i).innerHTML = obj[header_list[i]]
    }

  }
}

function make_ajax_query(url, type, data, response_func, error_func){
  $.ajax({  //Call ajax function sending the option loaded
    url: url,  //This is the url of the ajax view where you make the search
    type: type,
    data: data,
    success: function(response) {
      console.log('make_ajax_query->response: ', response)
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

function test_query(request, response){
  console.log(request.term);

  var my_json = {start:0,
  max:-1,
  search_string:request.term,}

  make_ajax_query("/ajax_url/", 'POST', my_json, function(response2){
    objects = []
    for(var i in response2.objects){
      console.log("add object")
      objects.push({"label":response2.objects[i].name, "value":response2.objects[i]})
    }

    console.log("list", objects)

    response(objects)
  });
}

// make_ajax_query("/ajax_url/", 'POST', my_json,)

$(document).ready(function() {

  $("#about-btn").click( function(event) {
    alert("You clicked the button using JQuery!");
  });

  $('#mytable tbody').on( 'click', 'tr', function () {
      console.log($(this));

      // if ( $(this).hasClass('highlight') ) {
      //     $(this).removeClass('highlight');
      // }
      // else {
      //     table.$('tr.selected').removeClass('highlight');
      //     $(this).addClass('highlight');
      // }
  } );


  $("#about-btn2").click( function(event){
      //You have to get in this code the values you need to work with, for example:
      var my_json = {start:0,
      max:-1,
      search_string:"",}

      make_ajax_query("/ajax_url/", 'POST', my_json, function(response){
        insertRowToTable('animal_table',response.objects,response.header_list)
      });
  });


  var availableTags = ['a','b','asd','asdf']
  $( "#animal-tags" ).autocomplete({
    source: test_query,
    select: function(event, ui){
      console.log("event ", event);
      console.log("ui: ", ui);

      console.log($("#add-btn"))

      $("#add-btn").value = ui.value

    },
  });

  $("#add-btn").click( function(event){
      //You have to get in this code the values you need to work with, for example:
      console.log("Clicked")
  });

});
