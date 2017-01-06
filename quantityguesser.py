import re
import itertools


class QuantityGuesser:
    """QuantityGuesser attempts to determine the number of items sold in a listing, based on a
    string containing quantity information. For example 'set of 5' should return the integer 5.
    It can also take more complicated forms, like '4 sets of 1 dozen'. Often, listing will use
    abbreviated forms (such as 'dz' for dozen, or 'cs' for 'case'). QuantityGuesser can also take
    a longer string (such as a title with quantity info at the end) or a short paragraph (like
    a product details section).
    """

    # Match 'container' words, abbreviations and plurals. Ex: matches 'pk', 'pks', 'pack', or 'packs'
    _re_containers = r'(?:(?<![a-z])(?:quantity|quantitie|qty|package|pack|pk|case|cs|set|boxe|box|bx|count|ct|carton|ctn|bag|bg|roll|rl|sleeve)s?(?![a-z]))'

    # Match 'multiplier' words, abbreviations, and plurals. Ex: matches 'dz', 'dzs', 'dozen', or 'dozens'
    _re_multipliers = r'(?:(?<![a-z])(?P<mult>ea|each|unit|pc|piece|peice|pr|pair|dz|dzn|doz|dozen)s?(?![a-z]))'

    # Match numbers given in plain form, comma-separated, and/or enclosed in parentheses. Ex: (1,000)
    # Now recognizes fractions: 1/2, 1,000/2, (1/2), etc
    _re_numbers = r'(\(?(?P<num>\d(?:\d|,\d{3})*(?:/\d(?:\d|,\d{3})*)*)\)?)'

    _mult_lookup = {'ea': 1, 'each': 1,
                    'unit': 1,
                    'pc': 1, 'piece': 1,
                    'pr': 2, 'pair': 2,
                    'dz': 12, 'doz': 12, 'dozen': 12}

    def __init__(self, pair_value=2):
        self._mult_lookup['pr'] = pair_value
        self._mult_lookup['pair'] = pair_value

    def guess(self, string):
        """Guess the listing quantity from the given stirng."""
        quants = list(itertools.chain(self._type1_matches(string),
                                      self._type2_matches(string),
                                      self._type3_matches(string)))

        if not quants:
            return None

        # Calculate the modes (plural) of the quantities, and choose the largest one
        most = max(list(map(quants.count, quants)))
        modes = list(set(filter(lambda x: quants.count(x) == most, quants)))

        return max(modes) if modes else max(quants)

    def _mult(self, *args):
        """Take any number of literal terms (like 'dozen', 'pair' '5,000') and return their product."""
        product = 1
        for term in args:
            try:
                num = eval(term.replace(',', ''))
            except:
                try:
                    num = self._mult_lookup.get(term.strip().lower(), 1)
                except:
                    num = 1

            product *= num

        return product

    def _type1_matches(self, string):
        """Matches the form: (number)(container) of/consists of (number)(multiplier)
        Ex: "set of 6" "box of 2 doz" "set consists of 6 pieces" "30 sets of 10"
        """
        r = re.compile(r'{number1}?\s*{container}(?:\s+(?:consist|quantity|quantitie|qty)s?)?(?:\s+of)?(?:\s*:)?\s*{number2}\s*{multiplier}?'\
                       .format(number1=self._re_numbers.replace('num', 'num1'),
                               container=self._re_containers,
                               number2=self._re_numbers.replace('num', 'num2'),
                               multiplier=self._re_multipliers),
                       re.IGNORECASE)

        for match in r.finditer(string):
            yield self._mult(match.group('num1'), match.group('num2'), match.group('mult'))

    def _type2_matches(self, string):
        """Matches the form: (quantity) (per) (container)
        Ex: "12 per set" "1dz/case" "12-pack"
        """
        r = re.compile(r'{number}\s*{multiplier}?(?:\s*[a-z]+)?\s*(?:per|/|-| )?\s*{container}' \
                       .format(number=self._re_numbers, multiplier=self._re_multipliers, container=self._re_containers),
                       re.IGNORECASE)

        for match in r.finditer(string):
            yield self._mult(match.group('num'), match.group('mult'))

    def _type3_matches(self, string):
        """Matches the form: (quantity)(multiplier)
        Ex: "1 dozen" "2 pair" "6 each"
        """
        r = re.compile(r'{number}\s*[-/]?\s*{multiplier}(?![a-z])' \
                       .format(number=self._re_numbers, multiplier=self._re_multipliers),
                       re.IGNORECASE)

        for match in r.finditer(string):
            yield self._mult(match.group('num'), match.group('mult'))

    @property
    def pairs_singular(self):
        return bool(self._mult_lookup['pair'] == 1)

    @pairs_singular.setter
    def pairs_singular(self, value):
        self._mult_lookup['pair'] = 1 if value else 2
        self._mult_lookup['pr'] = 1 if value else 2