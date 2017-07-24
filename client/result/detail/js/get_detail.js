ip_address = "lab.songli.us/uniquemachine"
details_global = [];

function get_details_by_id(column, id) {
  var command = "get_details," + id;
  details = send_to_utils(command);
  return details
}

function get_details(column) {
  var id = $("select[id=select_" + column + "]").val();
  input_id = (document.getElementById('input_' + column).value);
  if (input_id != "") id = parseInt(input_id);
  $('#table_' + column).empty();
  var details = get_details_by_id(column, id);
  details_global[column - 1] = details;
  getDetails(details, column);
}

// subtract all the imgs
function subtract() {
  // clear the res div
  $('#table_3').empty();
  // here we only have 28 pictures
  for (var i in details_global[0]) {
    if (details_global[0][i] == details_global[1][i]) continue;
    g_0 = details_global[0][i];
    g_1 = details_global[1][i];
    console.log(i, g_0);
    try {
      $('#table_3').append('<tr><td>' + i + '</td><td>' + g_0.substring(0, 32) + '</td><td>' + g_1.substring(0, 32) + '</td></tr>');
    } catch (e) {
      console.error(e);
    }
    //Only GOD knows where 'gpu_hashes' comes from
    //use it and figure it later....
    if (i == 'gpu_hashes') {
      for (var j in g_0) {
        if (g_0[j] != g_1[j]) {
          $('#table_3').append('<tr><td>' + j + '</td><td>' + g_0[j].substring(0, 4) + '</td><td>' + g_1[j].substring(0, 4) + '</td></tr>');
        }
      }
    } else if (i == "fonts") {
      /*
      var str_0 = details_global[0][i];
      var str_1 = details_global[1][i];
      var font_res = [];
      for (var j in str_0) {
        if (str_0[j] != str_1[j]) {
          font_res.push(font_list[j]);
        }
      }
      for (var j = 0;j < font_res.length;j += 3) {
        $('#table_3').append('<tr><td>' + font_res[j] + '</td><td>' + font_res[j + 1]
          + '</td><td>' + font_res[j + 2] + '</td></tr>');
      }
      */
    }
  }
}

// this function is used to clear all the data
function clear_all_data() {
  var password = prompt("Input your password to clear data: ");
  res = send_to_utils("clear," + password);
  alert(res);
}
