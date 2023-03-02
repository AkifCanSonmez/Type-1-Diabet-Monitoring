from sqlalchemy.orm import Session

def convert_str_to_float(*params):
    converted_values = []
    for text in params:
        converted_text = float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
        converted_values.append(converted_text)
    return tuple(converted_values)

def get_similar_meals(db):
    pass



