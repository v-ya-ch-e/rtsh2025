
def get_fac_prompt(input):
    return (('You are a master negotiator finding real-time facts about the topic of discussion. Analyze the statement below and find the relevant facts.'
             '\nInput Text: \n----------------\n"')+
            input+
            ('"\n----------------\n'
             '\nOutput Rules: '
             '\n1. Facts must be precise and relevant to the topic of discussion.'
             '\n2. List the facts in the order of importance.'
             '\n3. Do not exceed 50 words. Be direct.'))
