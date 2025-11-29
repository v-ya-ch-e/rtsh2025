
def get_sus_prompt(input):
    return (('You are a master negotiator detecting bluffs. Analyze the statement below for deception or exaggeration.'
             '\nInput Text: \n----------------\n"')+
            input+
            ('"\n----------------\n'
             '\nOutput Rules: '
             '\n1. Output strictly: "Decision: [TRUE / BLUFF]".'
             '\n2. List the specific linguistic or logical trigger for your decision.'
             '\n3. Do not exceed 50 words. Be direct.'))
