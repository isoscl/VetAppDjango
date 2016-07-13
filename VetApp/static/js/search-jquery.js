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


function delete_row(e){
  console.log("event is:" +e);
}

/*
  table_name should be in format "type_whrite_anything_here"
  i.e animal_table_1, because table_name is used to determine link address
  object_list [<object_in_json>, ...]
  header_list [str, ...] in correct order, allways should start with pk!
  insert_top, set True if want to set new items in top of list
  link, if true makes link to address that object
*/
function insertObjectToTable(table_name, object, link){
  var table = document.getElementById(table_name);
  var row = table.insertRow(-1);

  get_header_list(object['type'], function(header_list){
    console.log("got header_list: " + header_list)
    //make hidden pk column
    var cell = row.insertCell(0);
    cell.innerHTML = object['pk'];
    cell.style = 'display:none'
    //make link to object if wanted
    var i = 1;
    if(link){ //make
      row.insertCell(i).innerHTML = '<a target="_blank" href="/'+ table_name.split('_')[0] +'/?id='+object['pk']+'">' + object[header_list[i]] + '</a>'
      i++;
    }
    //insert data to row
    for(; i < header_list.length; i++){
      row.insertCell(i).innerHTML = object[header_list[i]]
    }
    row.insertCell(i).innerHTML = '<button onclick="$(this).closest(\'tr\').remove()";>X</button>'
  });
}



function insertObjectsToTable(table_name, object_list, link){
  for(var key in object_list){
    console.log("inserting object to table")
    insertObjectToTable(table_name, object_list[key], link);
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

function make_ajax_path(_type){
  return '/ajax_'+_type.toLowerCase()+'/';
}

function get_header_list(_type, return_func){
  var header_list = JSON.parse(localStorage.getItem(_type+"-header-list"));
  console.log("local header list is: " + header_list)
  if(header_list === null){
    console.log("no locale found, making query");
    make_ajax_query(make_ajax_path('header'), 'GET', {type:_type}, function(response2){
      //Store header-list to localdatabase
      console.log("got: "+ response2);
      localStorage.setItem(_type+"-header-list", JSON.stringify(response2.header_list));
      return_func(response2.header_list);
    });
  }else{
    console.log("Found local list");
    return_func(header_list)
  }
}

function queryObjects(_type, search_string, start, _max, return_func){
  var payload = {start:start, max:_max, search_string:search_string};
  //make query to get objects
  console.log("making call to get objects")
  make_ajax_query(make_ajax_path(_type), 'POST', payload, function(response){
    //check if we allready have loaded header-lists for this object type
    console.log("Got objects, responce is: " + response);
    //check that related headel-list is loaded from server
    if(localStorage.getItem(_type+"-header-list") === null){
      make_ajax_query(make_ajax_path('header'), 'GET', {type:_type}, function(response2){
        //Store header-list to localdatabase
        localStorage.setItem(_type+"-header-list", JSON.stringify(response2.header_list));
        return_func(response.objects);
      });
    }else{
      return_func(response.objects);
    }
  });
}



function object_query(request, response, _type){
  console.log(request.term);

  queryObjects(_type,request.term,0,-1, function(_objects){
    console.log('queryObjects returned: ' + _objects);
    objects = []
    for(var i in _objects){
      objects.push({"label":_objects[i].name, "data":_objects[i]})
    }
    response(objects)
  });
}

function animal_query(request, response){
  object_query(request, response, 'Animal');
}

$(document).ready(function() {
  // $('#mytable tbody').on( 'click', 'tr', function () {
  //     console.log($(this));
  //
  //     // if ( $(this).hasClass('highlight') ) {
  //     //     $(this).removeClass('highlight');
  //     // }
  //     // else {
  //     //     table.$('tr.selected').removeClass('highlight');
  //     //     $(this).addClass('highlight');
  //     // }
  // } );


  $("#about-btn2").click( function(event){
      //You have to get in this code the values you need to work with, for example:
      // var my_json = {start:0,
      // max:-1,
      // search_string:"",}
      queryObjects('Animal', "", 0, -1, function(objects){
          console.log("got objects: " + objects);
          insertObjectsToTable('animal_table',objects);
      });

      // make_ajax_query(make_ajax_path('animal'), 'POST', my_json, function(response){
      //   insertObjectsToTable('animal_table',response.objects)
      // });
    });



  $( "#animal-tags" ).autocomplete({
    source: animal_query,
    select: function(event, ui){
      console.log("event ", event);
      console.log("ui: ", ui);

      localStorage.setItem("animal-tags-selected-object", JSON.stringify(ui.item.data))
      delete ui.item.data

    },
  });

  $("#add-btn").click( function(event){
      //You have to get in this code the values you need to work with, for example:
      insertObjectToTable('animal_table',JSON.parse(localStorage.getItem("animal-tags-selected-object")));
  });

});
