let g_base_codes = [];
let g_index = 0;
let g_select_values = [];

$(document).ready(function () {
    getBaseCodes();
});

function getBaseCodes() {
    $.ajax({
        type: "GET",
        url: "/base/codes",
        data: {},
        success: function (response) {
            g_base_codes = response;
        }
    })
}

function getCode() {
    if ($("#btn-rec").is(":visible")) {
        $("#btn-rec").hide();
    }

    if (!$("#btn-next").is(":visible")) {
        $("#btn-next").show();
    }

    if (g_index > 0) {
        g_select_values.push($("input[name='checkType']:checked").val());
    }

    if (g_index == g_base_codes.length) {
        let data = {};
        g_base_codes.forEach(function (code, idx) {
            data[code] = g_select_values[idx];
        });
        $.ajax({
            type: "POST",
            url: '/stocks',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
            success: function (response) {
                $("#select-box").empty();
                response.forEach(function (code) {
                    makeStock(code);
                });
                $("#btn-next").hide();
                $("#btn-init").show();
            }
        })

    } else {
        $.ajax({
            type: "GET",
            url: `/codes?group=${g_base_codes[g_index]}`,
            data: {},
            success: function (response) {
                $("#select-box").empty();
                response.forEach(function (code) {
                    makeType(code);
                });
                g_index++;
            }
        })
    }
}

function getStockInfo(company_code) {
    $.ajax({
        type: "GET",
        url: `/stock?code=${company_code}`,
        data: {},
        success: function (response) {
            alert(`주가: ${response['price']}\n시총: ${response['amount']}\nPER: ${response['per']}`);
        }
    })
}

function setLike(company_code){
    $.ajax({
        type: "PUT",
        contentType: "application/json; charset=utf-8",
        url: `/stock/like`,
        data: JSON.stringify({'code':company_code}),
        success: function (response) {
            alert("수정되었습니다");
        }
    })
}

function setUnLike(company_code){
    $.ajax({
        type: "PUT",
        contentType: "application/json; charset=utf-8",
        url: `/stock/unlike`,
        data: JSON.stringify({'code':company_code}),
        success: function (response) {
            alert("수정되었습니다")
        }
    })
}

 function getListStocks(){
    $.ajax({
        type: "GET",
        url: `/stocks/like`,
        success: function (response) {
            response.forEach(function (stock, index) {
                makeListStock(stock, index);
            });
        }
    })
}

function makeType(code) {
    let tempHtml = `<div class="form-check">
                      <input class="form-check-input" type="radio" value="${code['code']}" name='checkType'>
                      <label class="form-check-label" for="defaultCheck1">
                        ${code['name']}
                      </label>
                    </div>`;
    $("#select-box").append(tempHtml);
}

function makeStock(stock) {
    let tempHtml = `<div class="form-check">
                      <label class="form-check-label" for="defaultCheck1">
                        ${stock['name']}
                      </label>`;

    if(stock['isLike']){
        tempHtml += `<button type="button" class="btn btn-danger" onclick="setUnLike('${stock['code']}')">취소</button>`;
    } else {
        tempHtml += `<button type="button" class="btn btn-warning" onclick="setLike('${stock['code']}')">즐겨찾기</button>`;
    }
    tempHtml += `<button type="button" class="btn btn-info" onclick="getStockInfo('${stock['code']}')">정보</button>
                 </div>`;

    $("#select-box").append(tempHtml);
}

function makeListStock(stock, index) {
    let tempHtml = ` <tr>
                      <th scope="row">${index + 1}</th>
                      <td>${stock['name']}</td>
                    `;

    if(stock['isLike']){
        tempHtml += `<td><button type="button" class="btn btn-danger" onclick="setUnLike('${stock['code']}')">취소</button></td>`;
    } else {
        tempHtml += `<td><button type="button" class="btn btn-warning" onclick="setLike('${stock['code']}')">즐겨찾기</button></td>`;
    }

    tempHtml += `<td><button type="button" class="btn btn-info" onclick="getStockInfo('${stock['code']}')">정보</button></td></tr>`
    $("#list-stock").append(tempHtml);
}

function changePart(part) {
    if(part == 'rec'){
        item = '#part-rec';
    } else {
        item = '#part-like';
        getListStocks();
    }
    $(item).closest("div").find("div").each(function (index) {
        if ($(this).is(":visible")) {
            $(this).hide();
        } else {
            $(this).show();
        }
    });

    $(item).closest("ul").find("li").each(function (index) {
        if ($(this).children("a").hasClass("active")) {
            $(this).children("a").removeClass("active");
            $(this).children("a").addClass("disabled");
        } else {
            $(this).children("a").addClass("active");
            $(this).children("a").removeClass("disabled");
        }
    });
}

function reset() {
    location.reload();
}