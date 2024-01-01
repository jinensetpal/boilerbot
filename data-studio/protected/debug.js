let currentPagination = 1
let allConv = []

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

function getAllConv(){
    let url = "http://3.141.44.228:8001/get_all_debug_conversation_id"
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
            console.log(result)

            // store all conv
            allConv = result

            // render conversation list. Default page is 1
            getConvByPage(1)
        },
        error: function(error){
            console.log(error)
        }
    })
}

function getConvByPage(page){
    // get the sub array of conv for the current page
    let pageItem = 40
    let start = (page-1) * pageItem
    let end = start + pageItem
    let conv = allConv.slice(start, end)

    // render the conv list. #conv-list is a table
    $("#conv-list").html('')

    // add tbody
    $("#conv-list").append('<tbody></tbody>')
    for(let i=0; i<conv.length; i++){
        let oneConv = conv[i]

        // render the row
        $("#conv-list tbody").append('<tr onclick="getConvById(\''+oneConv['conversation_id']+'\')" id="conv-list-item-'+oneConv['conversation_id']+'"> <td>'+oneConv['created_at'].substr(0, 10)+' '+oneConv['created_at'].substr(11, 8)+'</td> <td><span>'+oneConv["conversation_id"].substr(0,8)+'</span></td></tr>')
    }

    // render pagination
    AutoPagination(allConv.length, pageItem, 5, "conv-pagination", page, "getConvByPage")

    setHeight()
}

function getConvById(conv_id){
    let url = "http://3.141.44.228:8001/get_debug_info_by_conversation_id_str"
    let data = {
        "conversation_id": conv_id,
        "security_key": very_very_secure_key
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
            renderConversation(result)
        },
        error: function(error){
            console.log(error)
        }
    })
}

function renderConversation(conv){

    // add .selected class to tr
    $("#conv-list tbody tr").removeClass("selected")
    $("#conv-list-item-"+conv[0]['conversation_id']).addClass("selected")
                
    // render conversation meta data
    let totalTurns = conv.length

    $("#conv-metadata-id").text(conv[0]['conversation_id'])
    $("#conv-metadata-turns").text(totalTurns)

    $(".conv-metadata").css("display", "block")

    // render conversation line list
    $(".conv-lins").html("")
    for(let i=0; i<conv.length; i++){
        let oneLine = conv[i]

        // oneLine['debug_info'] should be split by |||
        // render each item as a list item
        // create the debug info list
        let debugInfoList = oneLine['debug_info'].split("|||")
        let renderedDebugInfoList = ""
        for(let j=0; j<debugInfoList.length; j++){
            renderedDebugInfoList += '<li>'+debugInfoList[j]+'</li>'
        }

        let renderedLine = '<div class="card mb-3"> <ul class="list-group list-group-flush"> <li class="list-group-item">User: '+oneLine['text']+'</li> <li class="list-group-item">Bot: '+oneLine['bot_response']+'</li> </ul> <div> <p class="card-text"><ul>'+ renderedDebugInfoList +'</ul></p> </div> </div>'

        $(".conv-lins").append(renderedLine)
    }
}

function setHeight(){
    // set the height of the conversation list: #conv-list-container
    // the height of the conversation list is the height of the window - the height of the navbar - the height of the #show-filter-button - the height of the #conv-pagination
    let height = $(window).height() - $("body>nav.navbar").height() - - $("#conv-pagination").height() - 90

    $("#conv-list-container").css("height", height+"px")

    // also set the max height and make it scroll when overflow
    $("#conv-list-container").css("max-height", height+"px")
    $("#conv-list-container").css("overflow-y", "auto")

}

getAllConv()