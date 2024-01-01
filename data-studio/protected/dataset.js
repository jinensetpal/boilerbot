let pageSize = 30;
let currentPage = 1;
let totalItem = 0;
let pageResult = [];
let LabelAndUser = {};

function AutoPagination(total_item, item_per_page, max_button, container_id, cur_page, change_page_func){
    let total_page = Math.ceil (total_item / item_per_page)

    let pagination_container = document.getElementById(container_id)

    pagination_container.innerHTML = '<nav><ul class="pagination" id="'+container_id+'_inner_container"></ul></nav>'

    let child_container = document.getElementById(container_id+'_inner_container')

    let prev = cur_page - 1
    let next = cur_page + 1

    if(prev == 0){
        child_container.innerHTML += '<li class="page-item disabled"><span class="page-link"><i class="fa-solid fa-arrow-left"></i></span></li>'
    }else{
        child_container.innerHTML += '<li class="page-item"><a class="page-link" href="#" onclick="'+change_page_func+'('+prev.toString()+')"><i class="fa-solid fa-arrow-left"></i></a></li>'
    }

    if(total_page==1){
        child_container.innerHTML += '<li class="page-item active"><span class="page-link">1</span></li>'
    }else if(total_page <= max_button){

        let page_num = 1
        while(total_page >= page_num){
            if(page_num == cur_page){
                child_container.innerHTML += '<li class="page-item active"><span class="page-link">'+page_num.toString()+'</span></li>'
            }else{
                child_container.innerHTML += '<li class="page-item"><a class="page-link" href="#" onclick="'+change_page_func+'('+page_num.toString()+')">'+page_num.toString()+'</a></li>'
            }
            page_num+=1
        }

    }else{
        let render_list = [1,total_page]

        if(render_list.includes(cur_page-1) == false && cur_page-1 > 0){
            render_list.push(cur_page-1)
        }
        if(render_list.includes(cur_page) == false){
            render_list.push(cur_page)
        }
        if(render_list.includes(cur_page+1) == false && cur_page+1 <= total_page){
            render_list.push(cur_page+1)
        }

        render_list = render_list.sort(function (a, b) {return a-b})

        for(let i=0;i<render_list.length;i++){
            if(i>0 && render_list[i]>render_list[i-1]+1){
                child_container.innerHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>'
            }
            let page_num = render_list[i]
            if(page_num == cur_page){
                child_container.innerHTML += '<li class="page-item active"><span class="page-link">'+page_num.toString()+'</span></li>'
            }else{
                child_container.innerHTML += '<li class="page-item"><a class="page-link" href="#" onclick="'+change_page_func+'('+page_num.toString()+')">'+page_num.toString()+'</a></li>'
            }
        }
    }

    if(next > total_page){
        child_container.innerHTML += '<li class="page-item disabled"><span class="page-link"><i class="fa-solid fa-arrow-right"></i></span></li>'
    }else{
        child_container.innerHTML += '<li class="page-item"><a class="page-link" href="#" onclick="'+change_page_func+'('+next.toString()+')"><i class="fa-solid fa-arrow-right"></i></a></li>'
    }
}

function renderPagination(page) {
    if(totalItem == 0){
        // get total item
        let url = "http://3.141.44.228:8001/get_wikihow_total_count"
        let data = {
            "security_key": very_very_secure_key
        }

        $.ajax({
            url: url,
            type: "POST",
            dataType : "json",
            contentType: "application/json; charset=utf-8",
            data : JSON.stringify(data),
            success: function(result){
                totalItem = result

                AutoPagination(totalItem, pageSize, 8, "pagination", page, "getDataset")
            }
        })
    }else{
        AutoPagination(totalItem, pageSize, 8, "pagination", page, "getDataset")
    }
}

function jumpToPage(){
    let page = $("#jump-to-page-input").val()
    getDataset(parseInt(page))
}

function jumpToPageKeyword(){
    $("#search-keyword-deep").val("")
    // disable deep search and keyword search button
    $("#deep-search-btn").prop('disabled', true);
    $("#keyword-search-btn").prop('disabled', true);

    // set button html to spinner
    $("#keyword-search-btn").html('Searching <i class="fa-solid fa-circle-notch fa-spin"></i>')

    getDataset(1)
}

function jumpToPageDeep(){
    $("#search-keyword").val("")
    // disable deep search and keyword search button
    $("#deep-search-btn").prop('disabled', true);
    $("#keyword-search-btn").prop('disabled', true);

    // set button html to spinner
    $("#deep-search-btn").html('Searching <i class="fa-solid fa-circle-notch fa-spin"></i>')
    getDataset(1)
}

function resetFilter(){
    $("#search-keyword").val("")
    $("#search-keyword-deep").val("")
    getDataset(1)
}

function getDataset(page) {
    let url = "http://3.141.44.228:8001/get_all_wikihow"
    let data = {
        "skip": (page-1)*pageSize,
        "limit": pageSize,
        "security_key": very_very_secure_key
    }

    let keyword = $("#search-keyword").val()
    if(keyword != "" && keyword != null){
        url = "http://3.141.44.228:8001/get_wikihow_with_keyword"
        data['keyword'] = keyword
        console.log("normal keyword search")
    }

    let keyword_deep = $("#search-keyword-deep").val()
    if(keyword_deep != "" && keyword_deep != null){
        url = "http://3.141.44.228:8001/get_wikihow_deep_search"
        data['keyword'] = keyword_deep
        console.log("deep keyword search")
    }
    
    console.log(data)

    $.ajax({
        url: url,
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data),
        success: function(result){
            console.log(result)
            
            $("#wikihow-list").html("");

            pageResult = result[0]

            for (let i=0; i<pageResult.length; i++){
                let labels = ""
                for(let j=0; j<pageResult[i]['labels'].length; j++){
                    // 1: auto labeled
                    // 2: manual labeled danger
                    // 3: manual labeled safe
                    let labelUser = pageResult[i]['labels'][j]['user']

                    LabelAndUser[pageResult[i]['labels'][j]['id']] = labelUser

                    let onclick = "alert('You can only delete your own labels!')"

                    if(labelUser == $("#user-name").text()){
                        onclick = "deleteLabel("+pageResult[i]['labels'][j]['id']+")"
                    }

                    if(pageResult[i]['labels'][j]['label'] == '1'){
                        labels += '<span class="badge bg-warning">Danger ('+pageResult[i]['labels'][j]['user']+')</span>'
                    }else if(pageResult[i]['labels'][j]['label'] == '2'){
                        labels += '<span class="badge bg-danger" onclick="'+ onclick +'">Danger ('+pageResult[i]['labels'][j]['user']+')</span>'
                    }else{
                        labels += '<span class="badge bg-success" onclick="'+ onclick +'">Safe ('+pageResult[i]['labels'][j]['user']+')</span>'
                    }
                }

                if(labels == ""){
                    labels = '<span class="badge bg-info">Safe? (Unlabeled)</span>'
                }

                let buttons = '<button class="btn btn-outline-danger btn-sm" onclick="labelDataset('+pageResult[i]['id']+', 2)">Danger</button> <button class="btn btn-outline-success btn-sm" onclick="labelDataset('+pageResult[i]['id']+', 3)">Safe</button>'

                let one_row = '<tr><td onclick="getWikihow('+i+')">'+pageResult[i]['title']+'</td><td id="wikihow-item-'+pageResult[i]['id']+'">'+labels+'</td><td>'+buttons+'</td></tr>'

                $("#wikihow-list").append(one_row)
            }

            totalItem = result[1]

            // enable deep search and keyword search button
            $("#deep-search-btn").prop('disabled', false);
            $("#keyword-search-btn").prop('disabled', false);

            // set button html to normal
            $("#deep-search-btn").html('Search +')
            $("#keyword-search-btn").html('Search')

            currentPage = page

            AutoPagination(totalItem, pageSize, 8, "pagination", page, "getDataset")
        },
        error: function(error){
            console.log(error)
        }
    })
}

function deleteLabel(id){
    // check if user is the one who labeled it
    let username = $("#user-name").text()
    if(LabelAndUser[id] != username){
        alert("You can only delete the label you labeled")
        return
    }

    // use confirm to make sure user want to delete
    let r = confirm(username + ", are you sure you want to delete this label?")
    if(!r){
        return
    }

    let url = "http://3.141.44.228:8001/delete_wikihow_label_by_id"
    let data = {"id": parseInt(id), "security_key": very_very_secure_key}

    $.ajax({
        url: url,
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data),
        success: function(result){
            getDataset(currentPage)
        }
    })
}


function labelDataset(id, label) {
    let username = $("#user-name").text()
    // remove spaces before and after
    let data = {
        "label": label,
        "user": username,
        "wikihow_id": parseInt(id),
        "security_key": very_very_secure_key
    }

    console.log(data)

    let url = "http://3.141.44.228:8001/add_to_wikihowlabel"

    $.ajax({
        url: url,
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data),
        success: function(result){
            console.log(result)

            if(result == true){
                // refresh the page
                getDataset(currentPage)
            }
        }
    })
}

function getWikihow(idx) {
    let url = "http://3.141.44.228:8001/get_wikihow_file"
    let data = {
        "file_name": pageResult[idx]['file_name'],
        "security_key": very_very_secure_key
    }

    $.ajax({
        url: url,
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data),
        success: function(result){
            console.log(result['data'])

            $("#wikihow-article-view").html("")
            
            $("#article-title").text(result['data']["articleTitle"])

            let collapse_text = ""

            let hasParts = result['data']["hasParts"];
            let indexText = "Part #"

            if(hasParts){
                if(result['data']["methods"].length > 1){
                    collapse_text += '<div class="text-primary my-2">This article has multiple <strong>PARTs</strong></div>'
                }else{
                    collapse_text += '<div class="text-primary my-2">This article has only <strong>ONE PART</strong></div>'
                }
                indexText = "Part #"
            }else{
                if(result['data']["methods"].length > 1){
                    collapse_text += '<div class="text-success my-2">This article has multiple <strong>METHODs</strong></div>'
                }else{
                    collapse_text += '<div class="text-success my-2">This article has only <strong>ONE METHOD</strong></div>'
                }
                indexText = "Method #"
            }

            for(let j=0; j<result['data']["methods"].length; j++){
                collapse_text += '<div class="wiki-part-title"><strong>'+indexText+(j+1)+':</strong> '+result['data']["methodsNames"][j]+'</div><ol class="wiki-part-steps">'

                let steps = result['data']["methods"][j];
                for(let k=0; k<steps.length; k++){
                    collapse_text += '<li>'+steps[k]+'</li>'
                }

                collapse_text += '</ol>'

                collapse_text += '<hr>'
            }

            let collapse = '<div>' + collapse_text + '</div>';

            $("#wikihow-article-view").append(collapse);

            // show #article-detail-model modal
            $("#article-detail-model").modal('show');
        }
    })
}

getDataset(currentPage)