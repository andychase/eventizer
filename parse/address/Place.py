from collections import namedtuple


class Place(namedtuple('place',
                       'city state zip street_number street_name street_direction street_type unit_number cross_street unit_letter')):
    """
    A simple python object for holding us place addresses.

    From http://www.metrogis.org/data/standards/address_guidelines.shtml
    1. Street number. (3186 PILOT KNOB RD)
      The street number is typically an integer value,
      but it may also include alpha characters, (e.g., 142A or 216 1/2).
      How these addresses will be located depends upon your geocoding software.
    2. Prefix direction. (156 E 18TH ST)
      The location of a direction designation may vary within an address.
      USPS street direction standard abbreviations: N, S, E, W, NE, SE, NW, SW
      (e.g., N 1ST AVE or 1ST AVE N).
    3. Street name. (3334 CEDAR AVE)
      In some cases streets may be known by more than one name.
      In these cases an alias or cross reference may be needed.
      Streets with numeric names may need to be entered as 1ST ST rather than FIRST ST.
    4. Street type. (3334 CEDAR AVE)
      Street types need to be entered using USPS recommended abbreviations.
    5. Suffix direction. (1200 34TH ST W)
    6. Unit Number (14955 GALAXIE AVE STE 300)
      Some common unit designators are APT (Apartment), STE (Suite), DEPT (Department), and the # sign. (See Postal Addressing Standards)
    7. City (MINNEAPOLIS MN 55406)
      Spell city names in their entirety when possible.
      13 character abbreviations from the USPS City State File.
    8. State (MINNEAPOLIS MN 55406)
      Use 2 letter USPS State Abbreviations.
    9. Zip Code (MINNEAPOLIS MN 55406)
      Zip Code or Zip+4 Number
    """

    def __new__(cls, city=None, state=None, zip=None, street_number=None, street_name=None,
                street_direction=None, street_type=None, unit_number=None,
                cross_street=None, unit_letter=None):
        return super(Place, cls).__new__(cls, city, state, zip, street_number, street_name, street_direction,
                                         street_type, unit_number, cross_street, unit_letter)