
def get_final_prompt(input, sus, sug, fac):
    return (('You are a master negotiator who gives recommendations to a human-negotiator. You have three helpers: the first one is checking if the opponent tries to bluff, the second one trying to suggest next moves and the third one trying to find real-time facts about the topic of discussion. You need to decide which of the messages to give to user. The message you pick must be the most relevant at this point of discussion. You also get a part of text transcript of the actual conversation [look Input Text].'
             '\nInput Text: \n----------------\n"')+
            input+
            ('"\n----------------\n'
             '\nMessages from helpers: '
             '\nBLUFF HELPER: '+sus+
             '\nSUGGESTION HELPER: '+sug+
             '\nFACT HELPER: '+fac+
             '\nYOUR OUTPUT RULES: '
             '\n1. Output strictly: "MESSAGE_COLOR: {red, green, blue}\n". Use red for bluffs, green for next moves and blue for facts.'
             '\n2. Output strictly: "MESSAGE: [PICKED MESSAGE]".'
             '\n3. Do not exceed 50 words. Be direct.'
             '\n4. DO NOT RETURN ANY OF YOUR THOUGHTS. RETURN STRICTLY THE OUTPUT DEFINED ABOVE. DO NOT ADD ANY OTHER SYMBOLS OR TEXT FORMATING'))
