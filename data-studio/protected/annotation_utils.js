function renderIntentList(container_id){
    let intent_list = [
        {
            "function": "===Please select a function===",
            "description": "",
            "response_example": ""
        },
        {
            "function": "search recipe",
            "description": "search recipe via whole foods api",
            "response_example": "recipe name / ingredient name(s)"
        },
        {
            "function": "search wikihow",
            "description": "search wikihow via wikihow api",
            "response_example": "verbb + noun / just verb / just noun"
        },
        {
            "function": "factual qa",
            "description": "asked about factual information",
            "response_example": ""
        },
        {
            "function": "neutral chitchat",
            "description": "normal/common chitchat",
            "response_example": "respond naturally. Then lead the user back to our main functions"
        },
        {
            "function": "offensive chitchat",
            "description": "uncommon/bad/rude chitchat",
            "response_example": "shut down the topic politely. Then lead the user back to our main functions"
        },
        {
            "function": "imcomplete sentence",
            "description": "user input is incomplete",
            "response_example": ""
        },
        {
            "function": "clarify",
            "description": "clarify our bot's abilities and scope",
            "response_example": "redirect the user back to our main functions but also consider the context info"
        },
        {
            "function": "unknown",
            "description": "this serves as all other categories",
            "response_example": ""
        }
    ]

    // clear the container
    document.getElementById(container_id).innerHTML = "";

    // render the intent list. The container should be a select element. Each option should have a value of the intent function. The text should be the intent function + description
    for (let i = 0; i < intent_list.length; i++){
        let option = document.createElement("option");
        if(i == 0){
            option.value = "";
            option.innerHTML = intent_list[i]["function"];
        }else{
            option.value = intent_list[i]["function"];
            option.innerHTML = intent_list[i]["function"] + " - " + intent_list[i]["description"];
        }
        // add response example to data-hint attribute of the option
        option.setAttribute("data-hint", intent_list[i]["response_example"]);

        document.getElementById(container_id).appendChild(option);
    }
}