ip_address = "lab.songli.io/uniquemachine"
function send_to_utils(command) {
  res = ""
  $.ajax({
    url: "http://" + ip_address + "/utils",
    type: 'POST',
    async: false,
    data: {
      key: command
    },
    success: function(data) {
      res = data;
    },
    error: function(xhr, ajaxOptions, thrownError) {
    }
  });
  return res; 
}

function deleteGroup() {
  groups = send_to_utils("get_groups");
  groups = groups.split('~');
  for (var i in groups) {
    var id = groups[i].split('$')[0];
    var name = groups[i].split('$')[1];
    $('<div id=' + id + '>' + name + '</div>').appendTo('body');
  }
  console.log(groups)
}
