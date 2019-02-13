function addShortcuts(){
  $(document).keypress(function (e) {
     var key = e.keyCode;
     if(key == 13){
        $('#ok_button').click();
        return false;
     } else if(key == 39){
        $('#next_button').click();
        return false;
     } else if(key == 37){
        $('#prev_button').click();
        return false;
     }
  });
}

function getCurrentInstance() {
  return instances_list[current_instance_index];
}

function displayAnnotationDivision(suggestions) {
  var main = $('#main')[0];
  // Selected instance - data and annotation
  var row = createDivWithClass(null,  'row', parent_div = main);
  displayInstancePanel(row);
  displayInstanceInformationStructure();
  displayAnnotationDiv(suggestions, conf.interactive);
}
