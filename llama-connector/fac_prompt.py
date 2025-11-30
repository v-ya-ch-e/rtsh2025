
def get_fac_prompt(input, context="", author="user"):
    return (('You are a fact checker who is watching a negotiation. You need to find real-time facts about the topic of discussion. You also get a part of text transcript of the actual conversation [look Input Text].'
             f'\nInput Text (from {author}): \n----------------\n"')+
            input+
            ('"\n----------------\n'
             '\nCONTEXT FROM KNOWLEDGE BASE:\n' + context + '\n'
             '\nYOUR OUTPUT RULES: '
             '\n1. Facts must be precise and relevant to the topic of discussion.'
             '\n2. List the facts in the order of importance.'
             '\n3. Do not exceed 50 words. Be direct.'))
