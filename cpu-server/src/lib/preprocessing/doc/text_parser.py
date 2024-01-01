from copy import deepcopy

def get_sub_steptext(steptext):
    step_max_length = 150
    cur_sub_step = ""
    res = []
    sentences = steptext.split(". ")

    for i in range(len(sentences)):
        cur_sub_step += sentences[i].rstrip('. ').strip() + ". "
        if len(cur_sub_step) > step_max_length:
            res.append(deepcopy(cur_sub_step.strip()))
            cur_sub_step = ""
    
    if len(cur_sub_step) > 0:
        res.append(deepcopy(cur_sub_step.strip()))
    return res

test_text = "In the bowl of an electric mixer fitted with a paddle attachment, combine 4 cups of flour, 2 tablespoons sugar, baking powder, and salt. Blend in the cold butter at the lowest speed and mix until the butter is in pea-sized pieces. Combine the eggs and heavy cream and quickly add them to the flour and butter mixture. Combine until just blended. Toss the strawberries with 1 tablespoon of flour, add them to the dough, and mix quickly. The dough may be a bit sticky."

print(get_sub_steptext(test_text))