// console.log("current_airing_data", current_airing_data);
let current_data = "";
let current_airing_data = "";
let current_screen_movie_data = null;
let code = "";
let div_visible = false;
let page = 1;
let next_page = Number;
let current_cate = "";
let total_page = "";
let spinner_loading = document.getElementById("spinner");

$("#anime_category").on("click", function (e) {
    // console.log($(this))
    // console.log(e)

    switch (e.target.id) {
        case "ing":
            console.log("ing.....")

            spinner_loading.style.display = "block";
            current_cate = "ing";
            get_anime_list(1, "ing");
            break;
        case "movie":
            console.log("movie")
            current_cate = "movie";
            get_anime_screen_movie(1);
            break;
        case "complete_anilist":
            console.log("complete")
            current_cate = "complete";
            get_complete_anilist(1);
            break;
        case "top_view":
            console.log("top_view")
            current_cate = "top_view";
            get_anime_list(1, "top_view");
            break;
        default:
            console.log("default")
            spinner_loading.style.display = "block";
            current_cate = "ing";
            get_anime_list(1, "ing");
            break;

    }
});


$("body").on("click", "#btn_search", function (e) {
    e.preventDefault();
    let query = $("#input_search").val();
    // console.log(query);

    if ($("#input_search").val() === "") {
        console.log("search keyword nothing");
        return false;
    }

    $.ajax({
        url: "/" + package_name + "/ajax/search",
        type: "POST",
        cache: false,
        data: {query: query},
        // dataType: "json",
        contentType: "application/x-www-form-urlencoded; charset=UTF-8",
        success: function (ret) {
            if (ret.ret) {
                make_screen_movie_list(ret);
            } else {
                $.notify("<strong>분석 실패</strong><br>" + ret.log, {
                    type: "warning",
                });
            }
        },
    });
});

const get_airing_list = () => {
    let spinner = document.getElementById("spinner");
    spinner.style.display = "block";
    $.ajax({
        url: "/" + package_name + "/ajax/airing_list",
        type: "GET",
        cache: false,
        dataType: "json",
        success: (ret) => {
            current_airing_data = ret;
            // console.log("ret::>", ret);
            if (current_airing_data !== "") {
                make_airing_list(ret);
                div_visible = true;
                spinner.style.display = "none";
                // console.log(div_visible);
            }
        },
    });

    if (div_visible) {
        //   {#$('#airing_list').toggle()#}
    }
};

const get_anime_list = (page, type) => {
    let url = "";
    let data = {page: page, type: type};

    switch (type) {
        case "ing":
            url = "/" + package_name + "/ajax/anime_list";
            current_cate = "ing";
            break;
        case "movie":
            url = "/" + package_name + "/ajax/screen_movie_list";
            current_cate = "movie";
            break;
        case "complete":
            url = "/" + package_name + "/ajax/screen_movie_list";
            current_cate = "complete";
            break;
        case "top_view":
            url = "/" + package_name + "/ajax/anime_list";
            current_cate = "complete";
            break;
        default:
            break;
    }

    $.ajax({
        url: url,
        type: "POST",
        data: data,
        cache: false,
        dataType: "json",
        success: (ret) => {
            //console.log("ret::>", ret);
            current_screen_movie_data = ret;
            total_page = ret.total_page;

            if (current_screen_movie_data !== "") {
                make_screen_movie_list(ret, page);
                div_visible = true;
                // console.log(div_visible);
                // $("img.lazyload").lazyload({
                //   threshold : 400,
                //   effect : "fadeIn",
                // });
            }
            next_page = page + 1;
        },
    });
};

const get_anime_screen_movie = (page) => {
    let data = {page: page};
    $.ajax({
        url: "/" + package_name + "/ajax/screen_movie_list",
        type: "POST",
        data: data,
        cache: false,
        dataType: "json",
        success: (ret) => {
            current_screen_movie_data = ret;
            total_page = ret.total_page;
            // console.log("ret::>", ret);

            if (current_screen_movie_data !== "") {
                make_screen_movie_list(ret, page);
                $("img.lazyload").lazyload({
                    threshold: 100,
                    effect: "fadeIn",
                });
                div_visible = true;
            }
            next_page = page + 1;
        },
    });
};

const get_complete_anilist = (page) => {
    let data = {page: page};
    $.ajax({
        url: "/" + package_name + "/ajax/complete_anilist",
        type: "POST",
        data: data,
        cache: false,
        dataType: "json",
        success: (ret) => {
            current_screen_movie_data = ret;
            console.log("get_complete_anilist():ret >", ret);
            total_page = ret.total_page;

            if (current_screen_movie_data !== "") {
                make_screen_movie_list(ret, page);
                $("img.lazyload").lazyload({
                    threshold: 100,
                    effect: "fadeIn",
                });
                div_visible = true;
            }
            next_page = page + 1;
        },
    });
};

// console.log(div_visible);

$(document).on("click", "button.code-button", function (e) {
    e.preventDefault();
    // console.log("click");
    // console.log("code to click:" + $(this).data("code"));
    document.getElementById("code").value = $(this).data("code");
    $("#code").val($(this).data("code"));
    $("#airing_list").toggle();
    code = document.getElementById("code").value;
    document.getElementById("analysis_btn").click();
});
$(".code-button").tooltip();

$("body").on("click", "#analysis_btn", function (e) {
    e.preventDefault();
    code = document.getElementById("code").value;
    if (document.getElementById("code").value === "") {
        console.log("code 값을 입력 해주세요.");
        return;
    }

    $.ajax({
        url: "/" + package_name + "/ajax/analysis",
        type: "POST",
        cache: false,
        data: {code: code},
        dataType: "json",
        success: function (ret) {
            if (ret.ret) {
                make_program(ret);
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
    str +=
        '<div id="inner_airing" class="d-flex align-content-between flex-wrapd-flex align-content-between flex-wrap">';
    for (i in data.episode) {
        tmp =
            '<div class="mx-1 mb-1"><button id="code_button" data-code="' +
            data.episode[i].code +
            '" type="button" class="btn btn-primary code-button bootstrap-tooltip" data-toggle="button" data-tooltip="true" aria-pressed="true" autocomplete="off" data-placement="top">' +
            '<span data-tooltip-text="' +
            data.episode[i].title +
            '">' +
            data.episode[i].code +
            "</span></button></div>";

        str += tmp;
    }
    str += "</div>";
    str += m_hr_black();

    document.getElementById("airing_list").innerHTML = str;
    $("img.lazyload").lazyload({
        threshold: 100,
        effect: "fadeIn",
    });
}

function make_screen_movie_list(data, page) {
    let str = "";
    let tmp = "";
    let new_anime = true;
    let new_style = ''
    console.log('page: ', page)

    let page_elem = "";
    if (page === undefined) {
    } else {
        page_elem = '<span class="badge bg-warning">' + page + "</span>";
    }

    str += "<div id='page_caption' style='border-bottom: aqua 1px solid; margin-bottom: 5px'>";
    str +=
        '<button type="button" class="btn btn-info">Page ' +
        page_elem +
        "</button>";
    str += "</div>";
    str += '<div id="inner_screen_movie" class="row infinite-scroll">';
    for (let i in data.episode) {
        if ( data.episode[i].code === data.latest_anime_code) {
            new_anime = false
        }

        if (new_anime && page === '1') {
            new_style = 'new-anime';
        } else {
            new_style = '';
        }

        tmp = '<div class="col-6 col-sm-4 col-md-3">';
        tmp += '<div class="card '+ new_style +'">';
        // tmp += '<div class="card-header">';

        // tmp +=
        //   '<img class="card-img-top lazyload" src="./static/img_loader_x200.svg" data-original="' + data.episode[i].image_link + '" />';
        tmp +=
            '<img class="card-img-top lazy" src="./static/img_loader_x200.svg" data-lazy-src="' +
            data.episode[i].image_link +
            '" style="cursor: pointer" onclick="location.href=\'./request?code=' +
            data.episode[i].code +
            "'\"/>";
        if (current_cate === "ing") {
            tmp +=
                '<span class="badge badge-danger badge-on-image">' +
                data.episode[i].chapter +
                "</span>";
        }
        // tmp += '<div class="card-body '+ new_anime ? 'new-anime' : '' +'">';
        tmp += '<div class="card-body">';
        tmp += '<h5 class="card-title">' + data.episode[i].title + "</h5>";
        tmp +=
            '<button id="add_whitelist" name="add_whitelist" class="btn btn-sm btn-favorite mb-1" data-code="' +
            data.episode[i].code +
            '"><p class="card-text">' +
            data.episode[i].code +
            " <i class=\"bi bi-heart-fill\"></i></p></button>";
        tmp +=
            '<a href="./request?code=' +
            data.episode[i].code +
            '" class="btn btn-primary cut-text">' +
            data.episode[i].title +
            "</a>";
        tmp += "</div>";
        tmp += "</div>";
        // tmp += "</div>"
        tmp += "</div>";
        str += tmp;
    }
    str += "</div>";
    str += m_hr_black();

    if (page > 1) {
        const temp = document.createElement("div");
        temp.innerHTML = str;
        while (temp.firstChild) {
            document.getElementById("screen_movie_list").appendChild(temp.firstChild);
        }
        page++;
    } else {
        document.getElementById("screen_movie_list").innerHTML = str;
    }
    $("img.lazyload").lazyload({
        threshold: 100,
        effect: "fadeIn",
    });
}

const spinner = document.getElementById("spinner");
const imagesContainer = document.getElementById("inner_screen_movie");
const infiniteContainer = document.getElementById("screen_movie_list");

const loadNextAnimes = (cate, page) => {
    spinner.style.display = "block";
    const data = {type: cate, page: String(page)};
    let url = "";

    switch (cate) {
        case "ing":
            url = "/" + package_name + "/ajax/anime_list";
            current_cate = "ing";
            break;
        case "movie":
            url = "/" + package_name + "/ajax/screen_movie_list";
            current_cate = "movie";
            break;
        case "complete":
            url = "/" + package_name + "/ajax/anime_list";
            current_cate = "complete";
            break;
        default:
            break;
    }

    // console.log('fetch_url::>', url)
    console.log("cate::>", cate);
    console.log("current_cate::>", current_cate);

    if (page > total_page) {
        console.log("전체 페이지 초과");
        document.getElementById("spinner").style.display = "none";
        return false;
    }

    fetch(url, {
        method: "POST",
        cache: "no-cache",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams(data),
    })
        .then((res) => {
            document.getElementById("spinner").style.display = "block";
            return res.json();
        })
        .then((response) => {
            // console.log("return page:::> ", response.page);
            make_screen_movie_list(response, response.page);
            $("img.lazyload").lazyload({
                threshold: 100,
                effect: "fadeIn",
            });
            page++;
            next_page++;
        })
        .catch((error) => console.error("Error:", error));
};

const onScroll = (e) => {
    threshold = 50;
    console.dir(e.target.scrollingElement.scrollHeight);
    const {scrollTop, scrollHeight, clientHeight} = e.target.scrollingElement;
    // if (Math.round(clientHeight + scrollTop) >= scrollHeight + threshold) {
    if (clientHeight + scrollTop + threshold >= scrollHeight) {
        document.getElementById("spinner").style.display = "block";
        // setTimeout()
        console.log("loading");
        // console.log(current_cate)
        // console.log("now page::> ", page);
        // console.log("next_page::> ", next_page);
        setTimeout(loadNextAnimes(current_cate, next_page), 1500);
        $("img.lazyload").lazyload({
            threshold: 100,
            effect: "fadeIn",
        });
    }
};

const debounce = (func, delay) => {
    let timeoutId = null;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(func.bind(null, ...args), delay);
    };
};

document.addEventListener("scroll", debounce(onScroll, 300));

function make_program(data) {
    let str,
        tmp = "";

    tmp = '<div class="form-inline">';
    tmp += m_button("check_download_btn", "선택 다운로드 추가", []);
    tmp += m_button("all_check_on_btn", "전체 선택", []);
    tmp += m_button("all_check_off_btn", "전체 해제", []);
    tmp +=
        '&nbsp;&nbsp;&nbsp;&nbsp;<input id="new_title" name="new_title" class="form-control form-control-sm" value="' +
        data.title +
        '">';
    tmp += "</div>";
    tmp += '<div class="form-inline">';
    tmp += m_button("apply_new_title_btn", "저장폴더명 변경", []);
    tmp +=
        '&nbsp;&nbsp;&nbsp;&nbsp;<input id="new_season" name="new_season" class="form-control form-control-sm" value="' +
        data.season +
        '">';
    tmp += m_button("apply_new_season_btn", "시즌 변경 (숫자만 가능)", []);
    tmp += m_button("search_tvdb_btn", "TVDB", []);
    tmp += m_button("add_whitelist", "스케쥴링 추가", []);
    tmp += "</div>";
    tmp = m_button_group(tmp);
    str += tmp;
    // program
    str += m_hr_black();
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

    str += m_hr_black();
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
        tmp += m_button("add_queue_btn", "다운로드 추가", [
            {key: "code", value: data.episode[i].code},
        ]);
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
    let data_code = $(this).attr("data-code");
    //console.log(data_code);
    $.ajax({
        url: "/" + package_name + "/ajax/add_whitelist",
        type: "POST",
        cache: false,
        data: JSON.stringify({data_code: data_code}),
        contentType: "application/json;charset=UTF-8",
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

$("body").on("click", "#apply_new_title_btn", function (e) {
    e.preventDefault();
    new_title = document.getElementById("new_title").value;
    $.ajax({
        url: "/" + package_name + "/ajax/apply_new_title",
        type: "POST",
        cache: false,
        data: {new_title: new_title},
        dataType: "json",
        success: function (ret) {
            if (ret.ret) {
                $.notify("<strong>적용하였습니다.</strong><br>", {
                    type: "success",
                });
                // console.log(ret);
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
            data: {new_season: new_season},
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
    code = $(this).data("code");
    $.ajax({
        url: "/" + package_name + "/ajax/add_queue",
        type: "POST",
        cache: false,
        data: {code: code},
        dataType: "json",
        success: function (data) {
            if (data.ret === "success") {
                $.notify("<strong>다운로드 작업을 추가 하였습니다.</strong>", {
                    type: "success",
                });
            } else if (data.ret === "fail") {
                $.notify("<strong>이미 큐에 있습니다. 삭제 후 추가하세요.</strong>", {
                    type: "warning",
                });
            } else if (data.ret === "no_data") {
                $.notify("<strong>잘못된 코드입니다.</strong>", {
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
        data: {code: str},
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

// $("#go_modal_airing").on("shown.bs.modal", function () {
//   // {#get_airing_list()#}
//   $("#exModal").trigger("focus");
// });

// $("#go_modal_airing").click(function (e) {
//   e.preventDefault();
//   console.log("open modal");
//   // $("#exModal").bootstrapToggle();
//   if (current_airing_data === "") {
//     get_airing_list();
//   }
//   $("#inner_airing").toggle();
//   $("#airing_list").toggle();
// });

// $("#go_modal_airing").attr("class", "btn btn-primary");

$(document).ready(function () {
    $("#input_search").keydown(function (key) {
        if (key.keyCode === 13) {
            // alert("엔터키를 눌렀습니다.");
            $("#btn_search").trigger("click");
        }
    });
    let spinner = document.getElementById("spinner");
    spinner.style.display = "block";
    get_anime_list(1, "ing");
    // $("img.lazyload").lazyload({
    //   threshold : 200,
    //   effect : "fadeIn",
    // });
});

// <!--<script src="https://cdn.jsdelivr.net/npm/vanilla-lazyload@17.7.0/dist/lazyload.min.js"></script>-->

// <!--<script>-->
// <!--  lazyLoadInstance.update();-->
// <!--</script>-->
// <!--<script>-->
// <!--  const lazyLoadInstance = new LazyLoad({-->
// <!--  // Your custom settings go here-->
// <!--});-->
// <!--  lazyLoadInstance.update()-->
// <!--</script>-->
window.lazyLoadOptions = {
    elements_selector:
        "img[data-lazy-src],.rocket-lazyload,iframe[data-lazy-src]",
    data_src: "lazy-src",
    data_srcset: "lazy-srcset",
    data_sizes: "lazy-sizes",
    class_loading: "lazyloading",
    class_loaded: "lazyloaded",
    threshold: 50,
    callback_loaded: function (element) {
        if (
            element.tagName === "IFRAME" &&
            element.dataset.rocketLazyload == "fitvidscompatible"
        ) {
            if (element.classList.contains("lazyloaded")) {
                if (typeof window.jQuery != "undefined") {
                    if (jQuery.fn.fitVids) {
                        jQuery(element).parent().fitVids();
                    }
                }
            }
        }
    },
};
window.addEventListener(
    "LazyLoad::Initialized",
    function (e) {
        var lazyLoadInstance = e.detail.instance;
        if (window.MutationObserver) {
            var observer = new MutationObserver(function (mutations) {
                var image_count = 0;
                var iframe_count = 0;
                var rocketlazy_count = 0;
                mutations.forEach(function (mutation) {
                    for (var i = 0; i < mutation.addedNodes.length; i++) {
                        if (
                            typeof mutation.addedNodes[i].getElementsByTagName !== "function"
                        ) {
                            continue;
                        }
                        if (
                            typeof mutation.addedNodes[i].getElementsByClassName !==
                            "function"
                        ) {
                            continue;
                        }
                        images = mutation.addedNodes[i].getElementsByTagName("img");
                        is_image = mutation.addedNodes[i].tagName == "IMG";
                        iframes = mutation.addedNodes[i].getElementsByTagName("iframe");
                        is_iframe = mutation.addedNodes[i].tagName == "IFRAME";
                        rocket_lazy =
                            mutation.addedNodes[i].getElementsByClassName("rocket-lazyload");
                        image_count += images.length;
                        iframe_count += iframes.length;
                        rocketlazy_count += rocket_lazy.length;
                        if (is_image) {
                            image_count += 1;
                        }
                        if (is_iframe) {
                            iframe_count += 1;
                        }
                    }
                });
                if (image_count > 0 || iframe_count > 0 || rocketlazy_count > 0) {
                    lazyLoadInstance.update();
                }
            });
            var b = document.getElementsByTagName("body")[0];
            var config = {
                childList: !0,
                subtree: !0,
            };
            observer.observe(b, config);
        }
    },
    !1
);
