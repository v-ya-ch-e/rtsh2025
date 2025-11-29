def get_sug_prompt(input, context="", author="user"):
    return (('You are a professional negotiator who is helping a user to negotiate. You need to suggest the next move for the user. You also get a part of text transcript of the actual conversation [look Input Text].'
             f'\nInput Text (from {author}): \n----------------\n"')+
            input+
            ('"----------------\n'
             '\nCONTEXT FROM KNOWLEDGE BASE:\n' + context + '\n'
             '\nYOUR OUTPUT RULES: '
              '\n1. Decide if the new suggestion is needed or not and output strictly: "NEXT MOVE: [YES / NO]".'
              '\n2. List the possible moves in the order of preference.'
              '\n3. Do not exceed 50 words. Be direct.'))
