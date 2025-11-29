
def get_sug_prompt(input):
    return (('You are a master negotiator suggesting the next moves. Analyze the statement below and suggest the next move.'
             '\nInput Text: \n----------------\n"')+
            input+
            ('"\n----------------\n'
             '\nOutput Rules: '
             '\n1. Decide if the new suggestion is needed or not and output strictly: "NEXT MOVE: [YES / NO]".'
             '\n2. List the possible moves in the order of preference.'
             '\n3. Do not exceed 50 words. Be direct.'))
