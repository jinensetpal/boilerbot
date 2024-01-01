function searchWikihowOurs(){
    let query = $("#search-wikihow-ours-query").val();
    if(query == ""){
        alert("Please enter a search query");
        return;
    }

    $(".api-results").css("display", "block")
    $(".api-results").html('<div class="loading-icon"><i class="fa-solid fa-cog fa-spin"></i></div>');


    data = {
        "query_text": query,
        "top_N": 10,
        "security_key": "ZjCjUp#!QzsLaxhw_GJX@Cb?TmGc8%hDcvqyfDKA5$qRUr+ft?4qWB+Ve_vMJTh$u4h@96w2VS=P+?xTFdD8UC?f@8&3=W&e8DNK*Av$sV7#!@8gP+Pa75^waTm#nC6d" 
    }

    let url = "http://3.145.188.173:8001/vectordb";

    $.ajax({
        url: url,
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data),
        success: function(result){
            console.log(result)
            
            $(".api-results").html("");

            for (let i=0; i<result["results"].length; i++){
                // append a button and coppapse for each result
                let button = '<button class="block-button" type="button" data-bs-toggle="collapse" data-bs-target="#search-result-' + i + '" aria-expanded="false">' + result["results"][i]["articleTitle"] + '</button>';

                let collapse_text = ""

                let hasParts = result["results"][i]["hasParts"];
                let indexText = "Part #"

                if(hasParts){
                    if(result["results"][i]["methods"].length > 1){
                        collapse_text += '<div class="text-primary my-2">This article has multiple <strong>PARTs</strong></div>'
                    }else{
                        collapse_text += '<div class="text-primary my-2">This article has only <strong>ONE PART</strong></div>'
                    }
                    indexText = "Part #"
                }else{
                    if(result["results"][i]["methods"].length > 1){
                        collapse_text += '<div class="text-success my-2">This article has multiple <strong>METHODs</strong></div>'
                    }else{
                        collapse_text += '<div class="text-success my-2">This article has only <strong>ONE METHOD</strong></div>'
                    }
                    indexText = "Method #"
                }

                for(let j=0; j<result["results"][i]["methods"].length; j++){
                    collapse_text += '<div class="wiki-part-title"><strong>'+indexText+(j+1)+':</strong> '+result["results"][i]["methodsNames"][j]+'</div><ol class="wiki-part-steps">'

                    let steps = result["results"][i]["methods"][j];
                    for(let k=0; k<steps.length; k++){
                        collapse_text += '<li>'+steps[k]+'</li>'
                    }

                    collapse_text += '</ol>'

                    collapse_text += '<hr>'
                }

                let collapse = '<div class="collapse" id="search-result-' + i + '">' + collapse_text + '</div>';

                $(".api-results").append(button);
                $(".api-results").append(collapse);
            }
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