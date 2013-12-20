"""
This file contains the parsing functions related to patterns

The point is that each function can take in a result tuple and
   use custom logic to parse a meaningful date group from it.
"""
from string import digits
from Place import Place


def remove_non_numbers(input):
    return ''.join(c for c in input if c in digits)


def cleanint(input):
    if input is None:
        return None
    result = remove_non_numbers(input)
    if not any(result):
        return None
    return int(result)


def progressive_match(string, possibilities):
    part = ""
    for character in string.lower():
        part += character
        matches = []
        for month, value in possibilities.iteritems():
            if part in month:
                matches.append(month)
        if len(matches) == 1:
            return possibilities[matches[0]]
    return None


def BasicAddress(StreetNumber=None, UnitLetter=None, StreetDirection=None,
                 StreetName=None, StreetType=None, City=None,
                 State=None, Zip=None):
    try:
        return Place(city=City, state=State, zip=Zip, street_number=StreetNumber,
                     street_name=StreetName, street_direction=StreetDirection,
                     street_type=StreetType,
                     unit_letter=UnitLetter)
    except ValueError:
        return None


def CrossStreet(CrossStreetName=None, StreetName=None, StreetType=None,
                City=None, State=None, Zip=None):
    try:
        return Place(city=City, state=State, zip=Zip, street_name=StreetName,
                     street_type=StreetType, cross_street=CrossStreetName)
    except ValueError:
        return None


def StreetName(StreetNameGroup=None):
    if StreetNameGroup: return str(StreetNameGroup)


def CityGroup(CityName=None):
    if CityName: return str(CityName)


def StateAbbr(StateAbbrGroup=None):
    if StateAbbrGroup: return str(StateAbbrGroup)


def ZipStrToInt(ZipCode=None, ZipCodePlusFour=None):
    if ZipCodePlusFour:
        return cleanint(ZipCode + ZipCodePlusFour)
    if ZipCode:
        return cleanint(ZipCode)


def StreetNumber(StreetNum=None):
    if StreetNum: return cleanint(StreetNum)


def UnitLetter(UnitLetterGroup=None):
    if UnitLetterGroup: return str(UnitLetterGroup)


def Direction(StreetDirection=None):
    if StreetDirection: return str(StreetDirection)


def StreetType(StreetTypeGroup=None):
    if StreetTypeGroup: return str(StreetTypeGroup)

# --------------- The lists ------------------
functions = {
    # Groups
    # Expressions
    "Chase StreetName": StreetName,
    "Chase HighwayNumber": StreetName,
    "Chase StreetNumberName": StreetName,
    "Chase StreetNumber": StreetNumber,
    "Chase UnitLetter": UnitLetter,
    "Chase City": CityGroup,
    "Michael Ash 71808": StateAbbr,
    "Mark J Krisburg": ZipStrToInt,
    "Metrogis": Direction,
    "Chase FullDirection": Direction,
    "Semaphorecorp": StreetType,
    # Types
    # Patterns
    "BasicAddress": BasicAddress,
    "CrossStreet": CrossStreet,
}