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
  if(table){
    var row = table.insertRow(-1);

    get_header_list(object['type'], function(header_list){
      console.log("got header_list: " + header_list)
      //make hidden pk column
      var cell = row.insertCell(0);
      cell.innerHTML = object['pk'];
      cell.style.display = 'none';

      //make link to object if wanted
      var i = 1;
      if(link){ //make
        row.insertCell(i).innerHTML = '<a target="_blank" href="/'+ table_name.split('_')[0] +'/?id='+object['pk']+'">' + object[header_list[i]] + '</a>'
        i++;
      }
      //insert data to row
      for(; i < header_list.length; i++){
        row.insertCell(i).innerHTML = object[header_list[i]];
      }
      row.insertCell(i).innerHTML = '<button onclick="$(this).closest(\'tr\').remove()";>X</button>'
    });
  }else{
    alert("insertObjectToTable-function can not find table named: "+ table_name);
  }
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
  var header_list = localStorage.getItem( _type+"-header-list");

  if(header_list == "undefined"){
    console.log("Header was not found at local storage. Making ajax query to fetch it.");
    make_ajax_query(make_ajax_path('header'), 'GET', {type:_type}, function(response2){
      //Store header-list to localdatabase
      console.log("got: "+ response2);
      localStorage.setItem(_type+"-header-list", JSON.stringify(response2.header_list));
      return_func(response2.header_list);
    });
  }else{
    console.log("found! header_list: " + JSON.parse(header_list))
    return_func(JSON.parse(header_list));
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

function getTableType(table_name){
  return table_name.split('_')[0];
}

function get_text_from_html_string(html_string){
  var parser = new DOMParser();
  var doc = parser.parseFromString(html_string, "text/xml");
  return doc.firstChild
}



function getTableObjects(table_name, return_func){
  var table = document.getElementById(table_name);
  if(table){
    get_header_list(getTableType(table_name), function(header_list){
      var objects = [];
      if(table.rows.length < 2){
        console.log("no rows to be parsed");
        return_func(objects);
      }else if(table.rows[1].cells.length < header_list.length){
        alert("Can not get objects from " + table_name + ", because it has less"+
        "rows than it should have. It has: " + table.rows[1].cells.length +
        ", it should have: " + header_list.length);
        return_func(objects);
      }else{
        console.log("looping")
        for(var i = 1; i < table.rows.length; i++){
          var object = {};
          for(var j = 0; j < header_list.length; j++){
            object[header_list[j]] = table.rows[i].cells[j].innerHTML;
          }
          objects.push(object);
        }
        console.log("Objects are: "+ objects);
        return_func(objects);
      }
    });
  }else{
    alert("getTableObjects-function did not find table named: " + table_name);
    return [];
  }
}

function create_table_name(_type, name){
  return _type + "_" + name + "_table";
}



function get_search_json(_type, table_name){
  function get_json(table_name, query){
    return {
      source: query,
      select: function(event, ui){
        localStorage.setItem(table_name+"-search-selected-object", JSON.stringify(ui.item.data))
        delete ui.item.data
      },
    }
  }

  if(_type === 'Animal'){
    return get_json(table_name, animal_query);
  }else{
    console.error("get_search_json, got un defined type: " + _type);
    return {};
  }
}

function initAutocomplete(_type, _name){
  var item = $( "#"+ name +"-search" );
  if(item){
    var name = create_table_name(_type, _name);
    item.autocomplete(get_search_json(_type, name));
  }
}

function initAddButton(_type, _name){
  var item = $("#" + name + "-add-btn");
  if(item){
    var name = create_table_name(_type, _name);
    localStorage.setItem(name+"-search-selected-object",undefined)
    item.click( function(event){
        json_string = localStorage.getItem(name+"-search-selected-object" );
        if(json_string !== 'undefined'){
          insertObjectToTable(name, JSON.parse(json_string));
        }else{
          console.log("No object to be added")
        }
    });
  }
}


$(document).ready(function() {

  initAutocomplete('Animal','');
  initAddButton('Animal','');

  // $("#about-btn2").click( function(event){
  //     queryObjects('Animal', "", 0, -1, function(objects){
  //         console.log("got objects: " + objects);
  //         insertObjectsToTable(create_table_name('Animal',""), objects);
  //     });
  //   });

  // $("#get-btn").click( function(event){
  //     getTableObjects(create_table_name('Animal', ''), function(objects){
  //       alert("Table contains: " + objects);
  //     });
  // });

});
