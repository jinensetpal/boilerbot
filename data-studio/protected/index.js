let currentPagination = 1
let allConv = []
let currentLines = {}
let currentConvId = null

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

function renderStars(){
    // foreach span with class list-conv-rating, extract the data-rating attribute and render the stars
    $(".list-conv-rating").each(function(){
        var rating = parseInt($(this).attr("data-rating"));
        var star = "";
        for(var i=0; i<rating; i++){
            star += '<i class="fa fa-star fa-xs yellow-star"></i>';
        }
        // add <i class="fa-regular fa-star"></i> for the remaining stars
        for(var i=rating; i<5; i++){
            star += '<i class="fa-regular fa-star fa-xs"></i>';
        }

        $(this).html(star);
    });
}

function getAllConv(){
    let url = "http://3.141.44.228:8001/get_all_rated_conversations"
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
            allConv = result['results']

            // render conversation list. Default page is 1
            getConvByPage(1)
        },
        error: function(error){
            console.log(error)
        }
    })
}

function getConvWithFilter(){
    let min_rating = parseInt($("#min-rating-filter").val())
    let max_rating = parseInt($("#max-rating-filter").val())
    let min_date = $("#start-date-filter").val()
    let max_date = $("#end-date-filter").val()

    let data = {
        "min_rating": min_rating,
        "max_rating": max_rating,
        "min_date": min_date,
        "max_date": max_date,
        "security_key": very_very_secure_key
    }

    console.log(data)

    $.ajax({
        url: "http://3.141.44.228:8001/get_conversation_with_filters",
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data),
        success: function(result){
            console.log(result)

            // store all conv
            allConv = result['results']

            // render conversation list. Default page is 1
            getConvByPage(1)
        },
        error: function(error){
            console.log(error)
        }
    })
}

function resetConvFilter(){
    $("#min-rating-filter").val() = 1
    $("#max-rating-filter").val() = 5
    $("#start-date-filter").val() = ""
    $("#end-date-filter").val() = ""
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
        $("#conv-list tbody").append('<tr onclick="getConvById('+oneConv['id']+')" id="conv-list-item-'+oneConv['id']+'"> <td>'+oneConv['start_at'].substr(0, 10)+' '+oneConv['start_at'].substr(11, 8)+'</td> <td><span class="list-conv-rating" data-rating="'+oneConv['rating']+'"></span></td></tr>')
    }

    renderStars()

    // render pagination
    AutoPagination(allConv.length, pageItem, 5, "conv-pagination", page, "getConvByPage")

    setHeight()
}

function getConvById(id){
    let url = "http://3.141.44.228:8001/get_conversation_by_id"
    let data = {
        "id": parseInt(id),
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

            currentConvId = id

            renderConversation(result['results'])
        },
        error: function(error){
            console.log(error)
        }
    })
}

function renderConversation(conv){

    // add .selected class to tr
    $("#conv-list tbody tr").removeClass("selected")
    $("#conv-list-item-"+conv['id']).addClass("selected")
                
    // render conversation meta data
    let totalTurns = conv['lines'].length
    
    let feedback = "N/A"

    if(conv['feedback'] != null || conv['feedback'] != undefined || conv['feedback'] != ""){
        feedback = conv['feedback']
    }

    $("#conv-metadata-id").text(conv['id_str'])
    $("#conv-metadata-turns").text(totalTurns)
    $("#conv-metadata-rating").text(conv['rating'])
    $("#conv-metadata-time").text(conv['start_at'].substr(0, 10)+' '+conv['start_at'].substr(11, 8))
    $("#conv-metadata-feedback").text(feedback)

    // add onclick event to view debug info button, the parameter is the conversation id
    $("#viewDebugInfo").attr("onclick", "viewDebugInfo(\'"+conv['id_str']+"\')")

    $(".conv-metadata").css("display", "block")

    // render conversation line list
    $(".conv-lins").html("")
    currentLines = {}

    $.ajax({
        url: "http://3.141.44.228:8001/get_instruction_by_conversation_id",
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify({"conversation_id": conv['id_str'], "security_key": very_very_secure_key}),
        success: function(result){
            console.log(result)

            let instructions = {}

            if(result != null || result != undefined){
                for(let i=0; i<result.length; i++){
                    let oneInstruction = result[i]
                    console.log(oneInstruction)

                    // check if oneInstruction['line_id'] is in the instructions
                    // if not, then add it to the instructions
                    if(!(oneInstruction['line_id'] in instructions)){
                        instructions[oneInstruction['line_id']] = [{
                            "user": oneInstruction['user'],
                            "text_response": oneInstruction['text_response']
                        }]
                    }else{
                        instructions[oneInstruction['line_id']].push({
                            "user": oneInstruction['user'],
                            "text_response": oneInstruction['text_response']
                        })
                    }
                }
            }

            console.log(instructions)
            
            for(let i=0; i<conv['lines'].length; i++){
                let oneLine = conv['lines'][i]
        
                currentLines[oneLine['id']] = oneLine['text']

                let userInput = oneLine['text']

                if(userInput == "N/A"){
                    console.log(oneLine['intent'])

                    let userEvent = oneLine['intent'].split("|||")

                    userInput = "Event: " + userEvent[0]

                    let eventDetails = JSON.parse(userEvent[1])
                    console.log(eventDetails['arguments'])

                    if(eventDetails['arguments']['L'].length > 0){
                        userInput += "<br>Paremeter: " + eventDetails['arguments']['L'][0]["S"]
                    }
                }

        
                // render the user part
                // if the line is in the instruction list, then render the line with different color
                if(oneLine['id'] in instructions){
                    $(".conv-lins").append('<div class="mb-3"> <div class="row g-0"> <div class="col-md-1"> <div class="line-from"> <i class="fa fa-user fa-xl"></i> </div> </div> <div class="col-md-11 align-left"> <div class="line-body" style="background-color: #198754;" onclick="showAddInstructionModal(\''+oneLine['id']+'\', \''+ conv['id_str'] +'\')"> <div class="card-text">'+ userInput +'</div> </div> </div> </div> </div>')
                    for(let j=0; j<instructions[oneLine['id']].length; j++){
                        $(".conv-lins").append('<div class="mb-3"> <div class="row g-0"> <div class="col-md-1"> <div class="line-from"> <i class="fa-solid fa-pen-to-square fa-xl"></i> </div> </div> <div class="col-md-11 align-left"> <div class="line-body" style="background-color: #198754;"> <div class="card-text">'+ instructions[oneLine['id']][j]['user'] + ": " + instructions[oneLine['id']][j]['text_response'] + '</div> </div> </div> </div> </div>')
                    }
                }else{
                    $(".conv-lins").append('<div class="mb-3"> <div class="row g-0"> <div class="col-md-1"> <div class="line-from"> <i class="fa fa-user fa-xl"></i> </div> </div> <div class="col-md-11 align-left"> <div class="line-body" onclick="showAddInstructionModal(\''+oneLine['id']+'\', \''+ conv['id_str'] +'\')"> <div class="card-text">'+ userInput +'</div> </div> </div> </div> </div>')
                }
                
        
                // render the bot part
                $(".conv-lins").append('<div class="mb-3"> <div class="row g-0" data-bs-toggle="collapse" data-bs-target="#line-label-'+oneLine['id']+'"> <div class="col-md-11 align-right"> <div class="line-body bot-response"> <div class="card-text">'+ oneLine['bot_response'] +'</div> </div> </div> <div class="col-md-1"> <div class="line-from"> <i class="fa-solid fa-robot fa-xl"></i> </div> </div> </div> <div class="collapse" id="line-label-'+oneLine['id']+'"><div class="row g-0 mt-3" data-bs-toggle="collapse" data-bs-target="#line-label-'+oneLine['id']+'"> <div class="col-md-11 align-right"> <div class="line-body line-detail"> <div class="card-text">'+ oneLine['backend_function'] +'</div> </div> </div> <div class="col-md-1"> <div class="line-from"> <i class="fa-solid fa-circle-info fa-xl"></i> </div> </div> </div> </div> </div>')
            }
        },
        error: function(error){
            console.log(error)
        }
    })
}

function setHeight(){
    // set the height of the conversation list: #conv-list-container
    // the height of the conversation list is the height of the window - the height of the navbar - the height of the #show-filter-button - the height of the #conv-pagination
    let height = $(window).height() - $("body>nav.navbar").height() - $("#show-filter-button").height() - $("#conv-pagination").height() - 90

    $("#conv-list-container").css("height", height+"px")

    // also set the max height and make it scroll when overflow
    $("#conv-list-container").css("max-height", height+"px")
    $("#conv-list-container").css("overflow-y", "auto")

}

function showAddInstructionModal(line_id, conv_id_str){
    $("#new-line-id").val(line_id)
    $("#new-conv-id").val(conv_id_str)
    $("#new-input").val(currentLines[line_id])
    $("#new-response").val("")
    $("#new-comment").val("")
    $("#new-context").val("")

    renderIntentList("new-function")

    $("#add-instruction-model").modal("show")
}

function addInstruction(){
    let user = $("#new-annotator").val()
    let category = ""
    let context = $("#new-context").val()
    let text_input = $("#new-input").val()
    let response_function = $("#new-function").val()
    let response_parameter = $("#new-response").val()
    let text_response = response_function + " - " + response_parameter
    let comment = $("#new-comment").val()

    if(text_input == ""){
        alert("User Input cannot be null!")
        return
    }

    if(text_response == ""){
        alert("Ideal Response cannot be null!")
        return
    }

    let data = {
        "line_id": parseInt($("#new-line-id").val()),
        "conversation_id": $("#new-conv-id").val(),
        "user": user,
        "category": category,
        "context": context,
        "text_input": text_input,
        "text_response": text_response,
        "comment": comment,
        "security_key": very_very_secure_key
    }

    console.log(data)

    let url = "http://3.141.44.228:8001/add_instruction"

    $.ajax({
        url: url,
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data),
        success: function(result){
        
            console.log(result)

            if(result == true){
                $("#add-instruction-model").modal("hide")
                // show toast #success-toast
                $("#success-toast").toast("show")
                // refresh the conversation
                getConvById(currentConvId)
            }else{
                alert("Add instruction failed! Please try again or contact Yifei.")
            }
        }
    })
}

function viewDebugInfo(conv_id_str){
    // get the debug info of the conversation
    let url = "http://3.141.44.228:8001/get_debug_info_by_conversation_id_str"
    let data = {
        "conversation_id": conv_id_str,
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
            // render the debug info
            $("#debug-conv-id").text(result['conversation_id'])

            $("#debug-line-container").html("")

            for(let i=0; i<result.length; i++){
                let oneLine = result[i]

                // oneLine['debug_info'] should be split by |||
                // render each item as a list item
                // create the debug info list
                let debugInfoList = oneLine['debug_info'].split("|||")
                let renderedDebugInfoList = ""
                for(let j=0; j<debugInfoList.length; j++){
                    renderedDebugInfoList += '<li>'+debugInfoList[j]+'</li>'
                }

                let renderedLine = '<div class="card mb-3"> <ul class="list-group list-group-flush"> <li class="list-group-item">User: '+oneLine['text']+'</li> <li class="list-group-item">Bot: '+oneLine['bot_response']+'</li> </ul> <div> <p class="card-text"><ul>'+ renderedDebugInfoList +'</ul></p> </div> </div>'

                $("#debug-line-container").append(renderedLine)

                // show modal
                $("#debug-info-model").modal("show")
            }
        },
        error: function(error){
            console.log(error)
        }
    })
    
}

// document ready
$(document).ready(function(){
    getAllConv()

    $("#new-function").change(function(){
        // change the place holder of the #new-response text area to the data-hint of the selected option
        let hint = $("#new-function option:selected").attr("data-hint")
        $("#new-response").attr("placeholder", hint)

        // if hint is null, disable the #new-response text area
        if(hint == ""){
            $("#new-response").val("")
            $("#new-response").attr("disabled", true)
        }else{
            $("#new-response").attr("disabled", false)
        }
    })
})