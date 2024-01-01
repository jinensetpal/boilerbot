
def filter_action(state):
    option = state.current_state.user_event.get('arguments')[0]
    responder = None

    if 'INTENT.Filter' in option:
        print(f"Filter Action|Choose {option}")
        filter_item = option.split('_')[1]
        setattr(state.user_attributes, 'recipe_filter', filter_item)
        responder = 'RECIPE_QUERY_RESPONDER'
    elif 'RESET' == option:
        setattr(state.user_attributes, 'recipe_filter', None)
        responder = 'RECIPE_QUERY_RESPONDER'
    
    return responder
