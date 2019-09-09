import math

MALE = "Male"
FEMALE = "Female"


def calculate_pef(age, height, gender):
    if gender == FEMALE:
        return calculate_female(age, height)
    if gender == MALE:
        return calculate_male(age, height)
    raise ValueError("Unable to recognise gender {}".format(gender))


def calculate_female(age, height):
    """
    The formula for a female is

    e((0.376*ln(Age))-(0.012*Age)-(58.8/Height)+5.63)
    """
    stage_1 = 0.376 * math.log(age)
    stage_2 = 0.012 * age
    stage_3 = 58.8/height
    return round(math.exp(stage_1 - stage_2 - stage_3 + 5.63))


def calculate_male(age, height):
    """
    The formula for a male is

    e((0.544*ln(Age))-(0.0151*Age)-(74.7/Height)+5.48)
    """
    stage_1 = 0.544 * math.log(age)
    stage_2 = 0.0151 * age
    stage_3 = 74.7/height
    return round(math.exp(stage_1 - stage_2 - stage_3 + 5.48))
