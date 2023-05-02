from langchain.prompts import PromptTemplate

refine_template = """
    You are an AI scraper extracting travel itineraries in a structured format from a website.
    There maybe multiple itineraries on the page, so you will need each one to be in a separate JSON object.
    The output should be a list of JSON objects, each one representing a travel itinerary with each day seperated.
    Here is the format of the JSON object:
    ------------
    [{{
        'itinerary_name": '3 day Ireland itinerary',
        'days': [
            {{
                'day': 1,
                'location': ['Dublin'],
                'day_description: 'This is a description of the day',
                'activities': [
                    {{
                        'name': 'Guinness Storehouse',
                        'type: 'attraction',
                        'address': 'St James's Gate, Ushers, Dublin 8, D08 VF8H, Ireland',
                        'suggested_duration_minutes': 60,
                        'description': 'The Guinness Storehouse is a Guinness-themed tourist attraction at St. James's Gate Brewery in Dublin, Ireland. Since opening in 2000, it has received over twenty million visitors.',
                    }}
                ]
            }},
            {{
                'day': 2,
                'location': ['Kent'],
                'activities': []
            }},
            {{
                'day': 3,
                'location': ['Cork','Dublin'],
                'activities': []
            }}
        ]
    }},
    {{
        'itinerary_name": '2 day Ireland itinerary',
        'days': [
            {{
                'day': 1,
                'location': ['Dublin'],
                'day_description: 'This is a description of the day',
                'activities': [
                    {{
                        'name': 'Guinness Storehouse',
                        'type: 'attraction',
                        'address': 'St James's Gate, Ushers, Dublin 8, D08 VF8H, Ireland',
                        'suggested_duration_minutes': 60,
                        'description': 'The Guinness Storehouse is a Guinness-themed tourist attraction at St. James's Gate Brewery in Dublin, Ireland. Since opening in 2000, it has received over twenty million visitors.',
                    }}
                ]
            }},
            {{
                'day': 2,
                'location': ['Cork'],
                'activities': []
            }}
        ]
    }}
    ]
    ------------
    So far you have created this itinerary:
    ------------ 
    {existing_answer}
    ------------
    You have the opportunity to add to the existing itinerary
    with some more information below.
    ------------
    {text}
    ------------
    Given the new information, refine the original itinerary.
    If the new information isn't useful, return the original full itinerary.
"""
refine_prompt = PromptTemplate(
    input_variables=[ "existing_answer", "text"],
    template=refine_template,
)


question_template = """
    You are an AI scraper extracting travel itineraries in a structured format from a website.
    There maybe multiple itineraries on the page, so you will need each one to be in a separate JSON object.
    The output should be a list of JSON objects, each one representing a travel itinerary with each day seperated.
    Here is the format of the JSON object:
    ------------
    [{{
        'itinerary_name": '3 day Ireland itinerary',
        'days': [
            {{
                'day': 1,
                'location': ['Dublin'],
                'day_description: 'This is a description of the day',
                'activities': [
                    {{
                        'name': 'Guinness Storehouse',
                        'type: 'attraction',
                        'address': 'St James's Gate, Ushers, Dublin 8, D08 VF8H, Ireland',
                        'suggested_duration_minutes': 60,
                        'description': 'The Guinness Storehouse is a Guinness-themed tourist attraction at St. James's Gate Brewery in Dublin, Ireland. Since opening in 2000, it has received over twenty million visitors.',
                    }}
                ]
            }},
            {{
                'day': 2,
                'location': ['Kent'],
                'activities': []
            }},
            {{
                'day': 3,
                'location': ['Cork','Dublin'],
                'activities': []
            }}
        ]
    }},
    {{
        'itinerary_name": '2 day Ireland itinerary',
        'days': [
            {{
                'day': 1,
                'location': ['Dublin'],
                'day_description: 'This is a description of the day',
                'activities': [
                    {{
                        'name': 'Guinness Storehouse',
                        'type: 'attraction',
                        'address': 'St James's Gate, Ushers, Dublin 8, D08 VF8H, Ireland',
                        'suggested_duration_minutes': 60,
                        'description': 'The Guinness Storehouse is a Guinness-themed tourist attraction at St. James's Gate Brewery in Dublin, Ireland. Since opening in 2000, it has received over twenty million visitors.',
                    }}
                ]
            }},
            {{
                'day': 2,
                'location': ['Cork'],
                'activities': []
            }}
        ]
    }}
    ]
    ------------
    The first part of the website is below
    ---------------------
    {text}
    ---------------------
    Given the context information and not prior knowledge, 
    generate an itinerary JSON.
"""
question_prompt = PromptTemplate(
    input_variables=["text"], template=question_template
)