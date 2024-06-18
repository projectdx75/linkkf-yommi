let current_data = "";
let current_airing_data = "";
let code = "";
let div_visible = false;
let total_page = "";


const params = new Proxy(new URLSearchParams(window.location.search), {
  get: (searchParams, prop) => searchParams.get(prop),
});

// console.log('current_airing_data', current_airing_data);

const get_airing_list = () => {
  $.ajax({
    url: "/" + package_name + "/ajax/airing_list",
    type: "GET",
    cache: false,
    dataType: "json",
    success: (ret) => {
      if (ret.ret == "success" && ret.episode != null) {
        current_airing_data = ret;
        total_page = ret.total_page;
        // console.log(ret)
        if (current_airing_data !== "") {
          make_airing_list(ret);
          div_visible = true;
          // console.log(div_visible)
        }
      } else {
        $.notify("<strong>분석 실패</strong><br>" + ret.log, {
          type: "warning",
        });
        div_visible = true;
      }
    },
  });

  if (div_visible) {
    // {#$('#airing_list').toggle()#}
  }
};

// console.log(div_visible)

$(document).on("click", "button.code-button", function (e) {
  e.preventDefault();
  // console.log('click')
  // console.log('code to click:' + $(this).data("code"))
  document.getElementById("code").value = $(this).data("code");
  $("#code").val($(this).data("code"));
  $("#airing_list").toggle();
  code = document.getElementById("code").value;
  document.getElementById("analysis_btn").click();
});
$(".code-button").tooltip();

$("body").on("click", "#analysis_btn", function (e) {
  e.preventDefault();
  if (document.getElementById("code").value !== "") {
    code = document.getElementById("code").value;
  }
  // console.log('#analysis_btn >>> code::', code)
  if (code === "") {
    console.log("code 값을 입력해주세요.");
    $.notify("<strong>code 값을 입력해주세요.</strong><br>");
    return;
  }

  $.ajax({
    url: "/" + package_name + "/ajax/analysis",
    type: "POST",
    cache: false,
    data: { code: code },
    dataType: "json",
    success: function (ret) {
      if (ret.ret == "success" && ret.data != null) {
        // console.log(ret.data)
        make_program(ret.data);
        dismissLoadingScreen()
      } else {
        $.notify("<strong>분석 실패</strong><br>" + ret.log, {
          type: "warning",
        });
      }
    },
  });
});

$("body").on("click", "#go_linkkf_btn", function (e) {
  e.preventDefault();
  window.open(linkkf_url, "_blank");
});

function make_airing_list(data) {
  let str = "";
  let tmp = "";

  tmp =
    '<div id="exModal" class="form-inline" role="dialog" aria-hidden="true">';
  tmp += "</div>";
  str += m_hr_black();
  // {#str += m_row_start(0);#}
  // {##}
  // {#str += m_row_end();#}
  // {#str += m_hr_black();#}
  str +=
    '<div id="inner_airing" class="d-flex align-content-between flex-wrapd-flex align-content-between flex-wrap">';
  for (let i in data.episode) {
    // {#str += m_row_start();#}
    // {#tmp = '<div class="col-sm"><strong>' + data.episode[i].title+ '</strong>';#}
    //
    // {#tmp += '<br />'#}
    // {#tmp += '' + data.episode[i].code + '</div>';#}
    // {#str += m_col(12, tmp)#}
    tmp =
      '<div class="mx-1 mb-1"><button id="code_button" data-code="' +
      data.episode[i].code +
      '" type="button" class="btn btn-primary code-button bootstrap-tooltip" data-toggle="button" data-tooltip="true" aria-pressed="true" autocomplete="off" data-placement="top">' +
      '<span data-tooltip-text="' +
      data.episode[i].title +
      '">' +
      data.episode[i].code +
      "</span></button></div>";
    // {#if (i === 10) {#}
    // {#    tmp += '<div class="w-100"></div>'#}
    str += tmp;
  }
  str += "</div>";
  str += m_hr_black();

  document.getElementById("airing_list").innerHTML = str;
}

function make_program(data) {
  current_data = data;
  // console.log('current_data:: ', data)
  str = "";
  tmp = '<div class="form-inline w-100">';
  tmp += m_button("check_download_btn", "선택 다운로드 추가", []);
  tmp += m_button("all_check_on_btn", "전체 선택", []);
  tmp += m_button("all_check_off_btn", "전체 해제", []);
  tmp += m_button("down_subtitle_btn", "자막만 전체 받기", [])
  tmp +=
    '&nbsp;&nbsp;&nbsp;<input id="new_title" name="new_title" class="form-control form-control-sm" value="' +
    data.title +
    '">';
  tmp += "</div>";
  tmp += '<div class="form-inline">';
  tmp += m_button("apply_new_title_btn", "저장폴더명 변경", []);
  tmp +=
    '&nbsp;&nbsp;&nbsp;<input id="new_season" name="new_season" class="form-control form-control-sm" value="' +
    data.season +
    '">';
  tmp += m_button("apply_new_season_btn", "시즌 변경 (숫자만 가능)", []);
  tmp += m_button("search_tvdb_btn", "TVDB", []);
  tmp += m_button("add_whitelist", "스케쥴링 추가", []);

  tmp += "</div>";
  tmp = m_button_group(tmp);
  str += tmp;
  // program
  // str += m_hr_black();
  str += "<div class='card p-lg-5 mt-md-3 p-md-3 border-light'>"

  str += m_row_start(0);
  tmp = "";
  if (data.poster_url != null)
    tmp = '<img src="' + data.poster_url + '" class="img-fluid">';
  str += m_col(3, tmp);
  tmp = "";
  tmp += m_row_start(0);
  tmp += m_col(3, "제목", "right");
  tmp += m_col(9, data.title);
  tmp += m_row_end();
  tmp += m_row_start(0);
  tmp += m_col(3, "시즌", "right");
  tmp += m_col(9, data.season);
  tmp += m_row_end();
  for (i in data.detail) {
    tmp += m_row_start(0);
    key = Object.keys(data.detail[i])[0];
    value = data.detail[i][key];
    tmp += m_col(3, key, "right");
    tmp += m_col(9, value);
    tmp += m_row_end();
  }

  str += m_col(9, tmp);
  str += m_row_end();

  // str += m_hr_black();
  str += "</div>"
  for (i in data.episode) {
    str += m_row_start();
    // tmp = '<img src="' + data.episode[i].image + '" class="img-fluid">'
    // str += m_col(3, tmp)
    tmp = "<strong>" + data.episode[i].title + "</strong>";
    tmp += "<br>";
    tmp += data.episode[i].filename + "<br><p></p>";

    tmp += '<div class="form-inline">';
    tmp +=
      '<input id="checkbox_' +
      data.episode[i].code +
      '" name="checkbox_' +
      data.episode[i].code +
      '" type="checkbox" checked data-toggle="toggle" data-on="선 택" data-off="-" data-onstyle="success" data-offstyle="danger" data-size="small">&nbsp;&nbsp;&nbsp;&nbsp;';
    // tmp += m_button('add_queue_btn', '다운로드 추가', [{'key': 'code', 'value': data.episode[i].code}])
    tmp += m_button("add_queue_btn", "다운로드 추가", [
      { key: "idx", value: i },
    ]);
   // tmp += '<button id="play_video" name="play_video" class="btn btn-sm btn-outline-primary" data-idx="'+i+'">바로보기</button>';
    tmp += "</div>";
    str += m_col(12, tmp);
    str += m_row_end();
    if (i != data.length - 1) str += m_hr(0);
  }
  document.getElementById("episode_list").innerHTML = str;
  $('input[id^="checkbox_"]').bootstrapToggle();
}

$("body").on("click", "#all_check_on_btn", function (e) {
  e.preventDefault();
  $('input[id^="checkbox_"]').bootstrapToggle("on");
});

$("body").on("click", "#all_check_off_btn", function (e) {
  e.preventDefault();
  $('input[id^="checkbox_"]').bootstrapToggle("off");
});

$("body").on("click", "#search_tvdb_btn", function (e) {
  e.preventDefault();
  new_title = document.getElementById("new_title").value;
  url = "https://www.thetvdb.com/search?query=" + new_title;
  window.open(url, "_blank");
});

$("body").on("click", "#add_whitelist", function (e) {
  e.preventDefault();
  $.ajax({
    url: "/" + package_name + "/ajax/add_whitelist",
    type: "POST",
    cache: false,
    dataType: "json",
    success: function (ret) {
      if (ret.ret) {
        $.notify("<strong>추가하였습니다.</strong><br>", {
          type: "success",
        });
        make_program(ret);
      } else {
        $.notify("<strong>추가 실패</strong><br>" + ret.log, {
          type: "warning",
        });
      }
    },
  });
});


$("body").on('click', '#down_subtitle_btn', function(e) {
  e.preventDefault();
  console.log('자막 전체 받기')

  const all = $('input[id^="checkbox_"]');
  let str = "";
  for (let i in all) {
    if (all[i].checked) {
      code = all[i].id.split("_")[1];
      str += code + ",";
    }
  }
  if (str === "") {
    $.notify("<strong>선택하세요.</strong>", {
      type: "warning",
    });
    return;
  }
  $.ajax({
    url: "/" + package_name + "/ajax/down_subtitle_list",
    type: "POST",
    cache: false,
    data: { code: str },
    dataType: "json",
    success: function (data) {
      if (data.ret == "success") {
        $.notify("<strong>" + data.log + "개를 추가하였습니다.</strong>", {
          type: "success",
        });
      } else {
        $.notify("<strong>" + data.log + "</strong>", {
          type: "warning",
        });
      }
    },
  });

});

$("body").on("click", "#apply_new_title_btn", function (e) {
  e.preventDefault();
  new_title = document.getElementById("new_title").value;
  $.ajax({
    url: "/" + package_name + "/ajax/apply_new_title",
    type: "POST",
    cache: false,
    data: { new_title: new_title },
    dataType: "json",
    success: function (ret) {
      if (ret.ret) {
        $.notify("<strong>적용하였습니다.</strong><br>", {
          type: "success",
        });
        // console.log(ret)
        make_program(ret);
      } else {
        $.notify("<strong>적용 실패</strong><br>" + ret.log, {
          type: "warning",
        });
      }
    },
  });
});

$("body").on("click", "#apply_new_season_btn", function (e) {
  e.preventDefault();
  new_season = document.getElementById("new_season").value;
  if ($.isNumeric(new_season) == false) {
    $.notify("<strong>시즌은 숫자여야 합니다.</strong><br>" + ret.log, {
      type: "warning",
    });
  } else {
    $.ajax({
      url: "/" + package_name + "/ajax/apply_new_season",
      type: "POST",
      cache: false,
      data: { new_season: new_season },
      dataType: "json",
      success: function (ret) {
        if (ret.ret) {
          $.notify("<strong>적용하였습니다.</strong><br>", {
            type: "success",
          });
          make_program(ret);
        } else {
          $.notify("<strong>적용 실패</strong><br>" + ret.log, {
            type: "warning",
          });
        }
      },
    });
  }
});

// 하나씩 다운로드 추가
$("body").on("click", "#add_queue_btn", function (e) {
  e.preventDefault();
  // code = $(this).data('code');
  code = current_data.episode[$(this).data("idx")].code;
  // console.log('code:: ', code)
  let data = current_data.episode[$(this).data("idx")];
  // console.log('data:: ', data)
  $.ajax({
    url: "/" + package_name + "/ajax/add_queue",
    type: "POST",
    cache: false,
    data: { code: code, data: JSON.stringify(data) },
    dataType: "json",
    success: function (data) {
      // console.log('#add_queue_btn::data >>', data)
      if (data.ret === "enqueue_db_append") {
        $.notify("<strong>다운로드 작업을 추가 하였습니다.</strong>", {
          type: "success",
        });
      } else if (data.ret === "enqueue_db_exist") {
        $.notify("<strong>DB에 존재하는 에피소드입니다.</strong>", {
          type: "warning",
        });
      } else if (data.ret === "db_completed") {
        $.notify("<strong>DB에 완료 기록이 있습니다.</strong>", {
          type: "warning",
        });
      } else if (data.ret === "fail") {
        $.notify("<strong>이미 큐에 있습니다. 삭제 후 추가하세요.</strong>", {
          type: "warning",
        });
      } else if (data.ret === "no_data") {
        $.notify("<strong>잘못된 코드입니다.</strong>", {
          type: "warning",
        });
      } else if (data.ret === "Debugging") {
        $.notify("<strong>Debugging</strong>", {
          type: "warning",
        });
      } else {
        $.notify("<strong>추가 실패</strong><br>" + ret.log, {
          type: "warning",
        });
      }
    },
  });
});

$("body").on("click", "#check_download_btn", function (e) {
  e.preventDefault();
  all = $('input[id^="checkbox_"]');
  str = "";
  for (i in all) {
    if (all[i].checked) {
      code = all[i].id.split("_")[1];
      str += code + ",";
    }
  }
  if (str == "") {
    $.notify("<strong>선택하세요.</strong>", {
      type: "warning",
    });
    return;
  }
  $.ajax({
    url: "/" + package_name + "/ajax/add_queue_checked_list",
    type: "POST",
    cache: false,
    data: { code: str },
    dataType: "json",
    success: function (data) {
      if (data.ret == "success") {
        $.notify("<strong>" + data.log + "개를 추가하였습니다.</strong>", {
          type: "success",
        });
      } else {
        $.notify("<strong>" + data.log + "</strong>", {
          type: "warning",
        });
      }
    },
  });
});

$("#go_modal_airing").on("shown.bs.modal", function () {
  // {#get_airing_list()#}
  $("#exModal").trigger("focus");
});

$("#go_modal_airing").click(function (e) {
  e.preventDefault();
  // console.log('open modal')
  $("#exModal").bootstrapToggle();
  if (current_airing_data === "") {
    get_airing_list();
  }
  $("#inner_airing").toggle();
  $("#airing_list").toggle();
});

$("#go_modal_airing").attr("class", "btn btn-primary");

