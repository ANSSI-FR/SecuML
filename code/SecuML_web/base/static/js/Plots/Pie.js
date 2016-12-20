function drawPie(div_name, get_path, int_prop) {

  if (typeof int_prop === 'undefined') {
    int_prop = '75%'
  }
 
  cleanDiv(div_name); 

  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open('GET', get_path(), false);
  xmlHttp.send(null);

  var pie_data = JSON.parse(xmlHttp.responseText);
  
  var pie = new d3pie(div_name, {
  	'size': {
  		'canvasWidth': 500,
  		'pieOuterRadius': int_prop
  	},
  	'data': {
  		'sortOrder': 'value-desc',
      'smallSegmentGrouping': {
        'enabled': true,
        'value' : 1
      },
  		'content': pie_data
  	},
  	'labels': {
  		'outer': {
  			'pieDistance': 8
  		},
  		'inner': {
  			'hideWhenLessThanPercentage': 3
  		},
  		'mainLabel': {
  			'fontSize': 12
  		},
  		'percentage': {
  			'color': '#ffffff',
  			'decimalPlaces': 0
  		},
  		'value': {
  			'color': '#adadad',
  			'fontSize': 11
  		},
  		'lines': {
  			'enabled': true
  		},
  		'truncation': {
  			'enabled': false
  		}
  	},
  	'misc': {
  		'gradient': {
  			'enabled': true,
  			'percentage': 100
  		}
  	}
  });
}

function addCallBackOnPieSelectList(div_name, get_path, 
    select_list_names, int_prop) {
  for (i in select_list_names) {
    select_list_name = select_list_names[i]
    var select_list = $('#' + select_list_name)[0];
    select_list.addEventListener('change', function() {
      drawPie(div_name, get_path, int_prop);
    });
  }
  drawPie(div_name, get_path, int_prop);
}
