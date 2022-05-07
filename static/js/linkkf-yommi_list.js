const sub = "";
let current_data = null;

const get_list = (page, move_top = true) => {
  let formData = get_formdata("#form_search");
  // console.log(formData)
  formData += "&page=" + page;
  $.ajax({
    url: "/" + package_name + "/ajax/web_list",
    type: "POST",
    cache: false,
    data: formData,
    dataType: "json",
    success: (data) => {
      current_data = data;
      if (data) {
        if (move_top) window.scrollTo(0, 0);
        make_list(data.list);
        // {#console.log(data)#}
        // {#console.log(ret.data)#}
      } else {
        $.notify("<strong>분석 실패</strong><br>" + ret.log, {
          type: "warning",
        });
      }
    },
  });
};

function sub_request_search(page, move_top = true) {
  let formData = get_formdata("#form_search");
  // console.log(formData)
  formData += "&page=" + page;
  console.log(formData)
  $.ajax({
    url: "/" + package_name + "/ajax/web_list",
    type: "POST",
    cache: false,
    data: formData,
    dataType: "json",
    success: function (data) {
      current_data = data;
      if (move_top) window.scrollTo(0, 0);
      make_list(data.list);
      make_page_html(data.paging);
    },
  });
}

function make_page_html(data) {
  str = ' \
    <div class="d-inline-block"></div> \
      <div class="row mb-3"> \
        <div class="col-sm-12"> \
          <div class="btn-toolbar" style="justify-content: center;" role="toolbar" aria-label="Toolbar with button groups" > \
            <div class="btn-group btn-group-sm mr-2" role="group" aria-label="First group">'
  if (data.prev_page) {
    str += '<button id="page" data-page="' + (data.start_page-1) + '" type="button" class="btn btn-secondary">&laquo;</button>'
  }

  for (var i = data.start_page ; i <= data.last_page ; i++) {
    str += '<button id="page" data-page="' + i +'" type="button" class="btn btn-secondary" ';
    if (i == data.current_page) {
      str += 'disabled';
    }
    str += '>'+i+'</button>';
  }
  if (data.next_page) {
    str += '<button id="page" data-page="' + (data.last_page+1) + '" type="button" class="btn btn-secondary">&raquo;</button>'
  }

  str += '</div> \
    </div> \
    </div> \
    </div> \
  '
  document.getElementById("page1").innerHTML = str;
  document.getElementById("page2").innerHTML = str;
}

// function global_sub_request_search(page, move_top=true) {
//   var formData = get_formdata('#form_search')
//   formData += '&page=' + page;
//   $.ajax({
//     url: '/' + package_name + '/ajax/' + sub + '/web_list',
//     type: "POST",
//     cache: false,
//     data: formData,
//     dataType: "json",
//     success: function (data) {
//       current_data = data;
//       if (move_top)
//         window.scrollTo(0,0);
//       make_list(data.list)
//       make_page_html(data.paging)
//     }
//   });
// }

$("body").on("click", "#remove_btn", function (e) {
  e.preventDefault();
  let id = $(this).data("id");
  $.ajax({
    url: "/" + package_name + "/ajax/db_remove",
    type: "POST",
    cache: false,
    data: { id: id },
    dataType: "json",
    success: function (data) {
      if (data) {
        $.notify("<strong>삭제되었습니다.</strong>", {
          type: "success",
        });
        sub_request_search(current_data.paging.current_page, false);
        // get_list()
      } else {
        $.notify("<strong>삭제 실패</strong>", {
          type: "warning",
        });
      }
    },
  });
});

$(document).ready(function () {
  // {#global_sub_request_search('1');#}
  get_list(1);
});

$("#search").click(function(e) {
  e.preventDefault();
  sub_request_search('1');
});

$("body").on("click", "#page", function (e) {
  e.preventDefault();
  sub_request_search($(this).data("page"));
});

$("body").on("click", "#json_btn", function (e) {
  e.preventDefault();
  var id = $(this).data("id");
  for (i in current_data.list) {
    if (current_data.list[i].id == id) {
      m_modal(current_data.list[i]);
    }
  }
});

$("body").on("click", "#self_search_btn", function (e) {
  e.preventDefault();
  let search_word = $(this).data("title");
  document.getElementById("search_word").value = search_word;
  sub_request_search("1");
});

$("body").on("click", "#request_btn", function (e) {
  e.preventDefault();
  var content_code = $(this).data("content_code");
  $(location).attr(
    "href",
    "/" + package_name + "/request?code=" + content_code
  );
});

function make_list(data) {
  //console.log(data)
  let tmp,
    tmp2 = "";
  // console.log(data)
  if (data.length > 0) {
    let str = "";
    for (let i in data) {
      // console.log(data[i]);
      str += m_row_start();
      str += m_col(1, data[i].id);
      tmp = data[i].status == "completed" ? "완료" : "미완료";
      str += m_col(1, tmp);
      tmp = data[i].created_time + "(추가)<br/>";
      if (data[i].completed_time != null)
        tmp += data[i].completed_time + "(완료)";
      str += m_col(3, tmp);
      tmp_save_path = data[i].contents_json.save_path
        ? data[i].contents_json.save_path
        : "";
      tmp =
        tmp_save_path +
        "<br />" +
        data[i].contents_json.filename +
        "<br /><br />";
      tmp2 = m_button("json_btn", "JSON", [{ key: "id", value: data[i].id }]);
      tmp2 += m_button("request_btn", "작품 검색", [
        { key: "content_code", value: data[i].contents_json.program_code },
      ]);
      tmp2 += m_button("self_search_btn", "목록 검색", [
        { key: "title", value: data[i].contents_json.program_title },
      ]);
      tmp2 += m_button("remove_btn", "삭제", [
        { key: "id", value: data[i].id },
      ]);
      tmp += m_button_group(tmp2);
      str += m_col(7, tmp);
      str += m_row_end();
      if (i != data.length - 1) str += m_hr();
    }
    document.getElementById("list_div").innerHTML = str;
  } else {
    console.log("목록없슴");
    return false;
  }
}
