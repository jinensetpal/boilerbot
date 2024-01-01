$("#max_len").change(function(){
    let max_len = $(this).val();
    $("#max_len_indicator").html(max_len);
})

let default_system_msg = "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. USER: {Your prompt here} ASSISTANT:"

let default_prompt = "Tell me something about Purdue University. Make it short."

$("#system_msg").val(default_system_msg);
$("#prompt").val(default_prompt);

function submitPrompt(){
    let system_msg = $("#system_msg").val();
    let prompt = $("#prompt").val();
    let max_len = $("#max_len").val();

    // disable the button   
    $("#llm-submit-btn").prop("disabled", true)
    // show loading icon in the button
    $("#llm-submit-btn").html('Generating <i class="fa-solid fa-cog fa-spin"></i>');

    $("#llm-response").html('<div class="loading-icon"><i class="fa-solid fa-cog fa-spin"></i></div>');

    data = {
        "security_key": "ZjCjUp#!QzsLaxhw_GJX@Cb?TmGc8%hDcvqyfDKA5$qRUr+ft?4qWB+Ve_vMJTh$u4h@96w2VS=P+?xTFdD8UC?f@8&3=W&e8DNK*Av$sV7#!@8gP+Pa75^waTm#nC6d",
        "prompt": prompt
    }

    let url = "http://3.141.44.228:8001/LLM_generate";

    console.log(data)

    $.ajax({
        url: url,
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data),
        success: function(result){
            console.log(result)

            // replace \n with <br> in the result
            result = result.replace(/\n/g, "<br>");

            $("#llm-response").html(result);

            // enable the button
            $("#llm-submit-btn").prop("disabled", false)
            // change the button text back to Submit
            $("#llm-submit-btn").html('Submit');
        },
        error: function(error){
            console.log(error)
        }
    })
}

function setMaxHeight(){
    // set the max height of the .api-results div to the height of the window minus the height of the navbar and the height of active-panel
    let navbarHeight = $("body nav.navbar").outerHeight();
    let activePanelHeight = $("body .active-panel").outerHeight();

    let maxHeight = $(window).height() - navbarHeight - activePanelHeight - 50;

    $(".api-results").css("max-height", maxHeight);

    // set overflow-y to scroll
    $(".api-results").css("overflow-y", "auto");
}

setMaxHeight()