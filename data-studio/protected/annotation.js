let pageSize = 30;
let currentPage = 1;
let totalItem = 0;
let pageResult = [];
let currentUser = $("#user-name").text()


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
        let url = "http://3.141.44.228:8001/get_instruction_total_count"
        let data = {
            "skip": 0, // not using it here
            "limit": 0, // not using it here
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
    console.log(page)
    getDataset(parseInt(page))
}

function getDataset(page) {
    let userFilter = $("#user-filter").val()
    let categoryFilter = null

    if(userFilter == "All"){
        userFilter = null
    }

    let url = "http://3.141.44.228:8001/get_all_instructions"
    let data = {
        "skip": (page-1)*pageSize,
        "limit": pageSize,
        "user": userFilter,
        "category": categoryFilter,
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
            
            $("#instruction-list").html("");

            pageResult = {}

            for (let i=0; i<result.length; i++){
                // let context = result[i]['context']
                // if(context == null || context == "" || context == "string"){
                //     context = "N/A"
                // }

                // let category = result[i]['category']
                // if(category == null || category == "" || category == "string"){
                //     category = "N/A"
                // }
                pageResult[result[i]['id']] = result[i]

                let action = ''
                if(result[i]['conversation_id'] != null){
                    action = '<span class="badge text-bg-primary show-conversation-button" onclick="showConversation(\''+result[i]['conversation_id']+'\', '+ result[i]['line_id'] +')">View Chat</span>'
                }

                // if this annotation is from the current user, add span with showEditInstructionModal function and id as parameter
                if(result[i]['user'] == currentUser){
                    if(action != ''){
                        action += '<br>'
                    }
                    action += '<span class="badge text-bg-warning edit-instruction-button" onclick="showEditInstructionModal(\''+result[i]['id']+'\')">Edit</span>'
                }

                let text_response = result[i]['text_response'].split(" - ")
                let response_function = '<span class="badge text-bg-info function-name-badge">' + text_response[0] + '</span><br>'
                let response_parameter = "N/A"
                if(text_response.length > 1){
                    response_parameter = text_response[1]
                }
                response_parameter = '<span class="parameter-badge">' + response_parameter + '</span>'

                let one_row = '<tr><td>'+result[i]['text_input']+'</td><td>'+response_function + response_parameter +'</td><td>'+result[i]['user']+'</td><td>'+action+'</td></tr>'

                $("#instruction-list").append(one_row)
            }

            renderPagination(page)
            currentPage = page
        },
        error: function(error){
            console.log(error)
        }
    })
}

function applyFilter(){
    getDataset(1)
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
                // add new label to the list
                let lebel_text = {
                    "2": "Danger",
                    "3": "Safe"
                }

                let new_label = '<span class="badge bg-'+(label == 2 ? 'danger' : 'success')+'">'+lebel_text[label]+' ('+username+')</span>'

                $("#wikihow-item-"+id).append(new_label)
            }
        }
    })
}

function showAddInstructionModal(){
    // clear all input
    $("#new-input").val("")
    $("#new-response").val("")
    $("#new-comment").val("")
    $("#new-context").val("")

    // set #new-conv-id to N/A
    $("#new-conv-id").val("N/A")

    // enable #new-input
    $("#new-input").prop("disabled", false)

    renderIntentList("new-function")

    // hide delete and update button
    $("#delete-instruction-btn").hide()
    $("#update-instruction-btn").hide()

    // show add button
    $("#add-instruction-btn").show()

    $("#add-instruction-model").modal("show")
}

function showEditInstructionModal(annotation_id){
     // show delete and update button
     $("#delete-instruction-btn").show()
     $("#update-instruction-btn").show()
 
     // hide add button
     $("#add-instruction-btn").hide()

     // set #annotation-id
    $("#annotation-id").val(annotation_id)

    // set other fields from pageResult
    let annotation = pageResult[parseInt(annotation_id)]

    // check if user is the same user who created the annotation
    if(currentUser != annotation['user']){
        alert("You are not allowed to edit this annotation")
        return
    }

    // set #new-conv-id to conversation_id
    $("#new-conv-id").val(annotation['conversation_id'])

    $("#new-input").val(annotation['text_input'])
    $("#new-comment").val(annotation['comment'])
    $("#new-context").val(annotation['context'])

    // if conversation_id is not null, disable #new-input
    if(annotation['conversation_id'] != null){
        $("#new-input").prop("disabled", true)
    }else{
        $("#new-input").prop("disabled", false)
    } 

    renderIntentList("new-function")

    let text_response = annotation['text_response'].split(" - ")
    $("#new-function").val(text_response[0])
    if(text_response.length > 1){
        $("#new-response").val(text_response[1])
    }else{
        $("#new-response").val("")
    }

    $("#add-instruction-model").modal("show")
}

function deleteInstruction(){
    let id = parseInt($("#annotation-id").val())

    // get annotation from pageResult
    let annotation = pageResult[id]

    // check if user is the same user who created the annotation
    if(currentUser != annotation['user']){
        alert("You are not allowed to delete this annotation")
        return
    }

    // use confirm to make sure user want to delete
    let confirm_delete = confirm("Are you sure you want to delete this annotation?")
    if(!confirm_delete){
        return
    }

    let data = {
        "id": id,
        "security_key": very_very_secure_key
    }

    let url = "http://3.141.44.228:8001/delete_instruction_by_id"

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
                getDataset(currentPage)

                // show delete-toast
                $("#delete-toast").toast('show')
            }
        }
    })
}

function collectData(){
    let user = $("#new-annotator").val()
    let category = ""
    let context = $("#new-context").val()
    let text_input = $("#new-input").val()
    let response_function = $("#new-function").val()
    let response_parameter = $("#new-response").val()
    let text_response = response_function + " - " + response_parameter
    let comment = $("#new-comment").val()

    if(text_input == ""){
        return ["0", "User Input cannot be null!"]
    }

    if(text_response == ""){
        return ["0", "Ideal Response cannot be null!"]
    }

    if(response_function == ""){
        return ["0", "Response Function cannot be null!"]
    }

    let data = {
        "user": user,
        "category": category,
        "context": context,
        "text_input": text_input,
        "text_response": text_response,
        "comment": comment,
        "security_key": very_very_secure_key
    }

    return [true, data]
}

function updateInstruction(){
    let id = parseInt($("#annotation-id").val())

    // get annotation from pageResult
    let annotation = pageResult[id]

    // check if user is the same user who created the annotation
    if(currentUser != annotation['user']){
        alert("You are not allowed to update this annotation")
        return false
    }

    let data = collectData()
    if(data[0] == false){
        return data[1]
    }

    data = data[1]
    data['id'] = id
    data['line_id'] = annotation['line_id']
    data['conversation_id'] = annotation['conversation_id']

    console.log(data)

    let url = "http://3.141.44.228:8001/edit_instruction"

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
                getDataset(currentPage)

                // show toast #success-toast
                $("#update-toast").toast("show")
            }else{
                alert("Edit instruction failed! Please try again or contact Yifei.")
            }
        }
    })
}

function addInstruction(){
    let data = collectData()

    if(data[0] == false){
        return data[1]
    }

    data = data[1]

    console.log(data)

    let url = "http://3.141.44.228:8001/add_instruction_no_ref"

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
                getDataset(currentPage)
            }else{
                alert("Add instruction failed! Please try again or contact Yifei.")
            }
        }
    })
}



function showConversation(id, line_id){
    let url = "http://3.141.44.228:8001/get_conversation_by_id_str"
    let data = {
        "id": -1,
        "id_str": id,
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
            renderConversation(result['results'], line_id)
        },
        error: function(error){
            console.log(error)
        }
    })
}
            
function renderConversation(conv, line_id){
    // render conversation meta data
    let totalTurns = conv['lines'].length

    $("#conv-metadata-id").text(conv['id_str'])
    $("#conv-metadata-turns").text(totalTurns)
    $("#conv-metadata-rating").text(conv['rating'])
    $("#conv-metadata-time").text(conv['start_at'].substr(0, 10)+' '+conv['start_at'].substr(11, 8))

    $(".conv-metadata").css("display", "block")

    // render conversation line list
    $(".conv-lins").html("")
    currentLines = {}

    for(let i=0; i<conv['lines'].length; i++){
        let oneLine = conv['lines'][i]

        currentLines[oneLine['id']] = oneLine['text']

        // render the user part
        if(oneLine['id'] == line_id){
            $(".conv-lins").append('<div class="mb-3"> <div class="row g-0"> <div class="col-md-1"> <div class="line-from"> <i class="fa fa-user fa-xl"></i> </div> </div> <div class="col-md-11 align-left"> <div class="line-body" style="background-color: #198754;"> <div class="card-text">'+ oneLine['text'] +'</div> </div> </div> </div> </div>')
        }else{
            $(".conv-lins").append('<div class="mb-3"> <div class="row g-0"> <div class="col-md-1"> <div class="line-from"> <i class="fa fa-user fa-xl"></i> </div> </div> <div class="col-md-11 align-left"> <div class="line-body"> <div class="card-text">'+ oneLine['text'] +'</div> </div> </div> </div> </div>')
        }
        

        // render the bot part
        $(".conv-lins").append('<div class="mb-3"> <div class="row g-0" data-bs-toggle="collapse" data-bs-target="#line-label-'+oneLine['id']+'"> <div class="col-md-11 align-right"> <div class="line-body bot-response"> <div class="card-text">'+ oneLine['bot_response'] +'</div> </div> </div> <div class="col-md-1"> <div class="line-from"> <i class="fa-solid fa-robot fa-xl"></i> </div> </div> </div>')
    }

    $(".conv-lins").css("display", "block")

    console.log("rendered")

    // show the modal
    $("#show-conversation-model").modal("show")
}

// document ready, call getDataset(currentPage) and showAddInstructionModal()
$(document).ready(function(){
    getDataset(currentPage)
    // showAddInstructionModal()

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