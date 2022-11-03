var package_name = "{{arg['package_name']}}";
var sub = "{{arg['sub']}}";
var current_data = null;

$(document).ready(function(){
  global_sub_request_search('1');
});

$("#search").click(function(e) {
  e.preventDefault();
  global_sub_request_search('1');
});

$("body").on('click', '#page', function(e){
  e.preventDefault();
  global_sub_request_search($(this).data('page'));
});

$("#reset_btn").click(function(e) {
  e.preventDefault();
  document.getElementById("order").value = 'desc';
  document.getElementById("option").value = 'all';
  document.getElementById("search_word").value = '';
  global_sub_request_search('1')
});


$("body").on('click', '#json_btn', function(e){
  e.preventDefault();
  var id = $(this).data('id');
  for (i in current_data.list) {
    if (current_data.list[i].id == id) {
      m_modal(current_data.list[i])
    }
  }
});

$("body").on('click', '#self_search_btn', function(e){
  e.preventDefault();
  var search_word = $(this).data('title');
  document.getElementById("search_word").value = search_word;
  global_sub_request_search('1')
});

$("body").on('click', '#remove_btn', function(e) {
  e.preventDefault();
  id = $(this).data('id');
  $.ajax({
    url: '/'+package_name+'/ajax/'+sub+ '/db_remove',
    type: "POST", 
    cache: false,
    data: {id:id},
    dataType: "json",
    success: function (data) {
      if (data) {
        $.notify('<strong>삭제되었습니다.</strong>', {
          type: 'success'
        });
        global_sub_request_search(current_data.paging.current_page, false)
      } else {
        $.notify('<strong>삭제 실패</strong>', {
          type: 'warning'
        });
      }
    }
  });
});

$("body").on('click', '#request_btn', function(e){
  e.preventDefault();
  var content_code = $(this).data('content_code');
  $(location).attr('href', '/' + package_name + '/' + sub + '/request?content_code=' + content_code)
});



function make_list(data) {
  //console.log(data)
  str = '';
  for (i in data) {
    //console.log(data[i])
    str += m_row_start();
    str += m_col(1, data[i].id);
    tmp = (data[i].status == 'completed') ? '완료' : '미완료';
    str += m_col(1, tmp);
    tmp = data[i].created_time + '(추가)';
    if (data[i].completed_time != null)
      tmp += data[i].completed_time + '(완료)';
    str += m_col(3, tmp)
    tmp = data[i].savepath + '<br>' + data[i].filename + '<br><br>';
    tmp2 = m_button('json_btn', 'JSON', [{'key':'id', 'value':data[i].id}]);
    tmp2 += m_button('request_btn', '작품 검색', [{'key':'content_code', 'value':data[i].content_code}]);
    tmp2 += m_button('self_search_btn', '목록 검색', [{'key':'title', 'value':data[i].title}]);
    tmp2 += m_button('remove_btn', '삭제', [{'key':'id', 'value':data[i].id}]);
    tmp += m_button_group(tmp2)
    str += m_col(7, tmp)
    str += m_row_end();
    if (i != data.length -1) str += m_hr();
  }
  document.getElementById("list_div").innerHTML = str;
}