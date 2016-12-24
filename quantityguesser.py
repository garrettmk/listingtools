import re
import itertools


class QuantityGuesser:

    # Match 'container' words, abbreviations and plurals. Ex: matches 'pk', 'pks', 'pack', or 'packs'
    _re_containers = r'(?:(?<![a-z])(?:package|pack|pk|case|cs|set|st|boxe|box|bx|count|ct|carton|bag|bg|roll|rl|sleeve|quantity)s?(?![a-z]))'

    # Match 'multiplier' words, abbreviations, and plurals. Ex: matches 'dz', 'dzs', 'dozen', or 'dozens'
    _re_multipliers = r'(?:(?<![a-z])(?P<mult>ea|each|unit|pc|piece|pr|pair|dz|doz|dozen)s?(?![a-z]))'

    # Match numbers given in plain form, comma-separated, and/or enclosed in parentheses. Ex: (1,000)
    # Now recognizes fractions: 1/2, 1,000/2, (1/2), etc
    _re_numbers = r'\(?(?P<num>\d[\d,]*(?:/\d[\d,]*)?)\)?'

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
        """Matches the form: (container) of/consists of (number)(multiplier)
        Ex: "set of 6" "box of 2 doz" "set consists of 6 pieces"
        """
        r = re.compile(r'{container}(?:\s+consists?)?(?:\s+of)\s*{number}\s*{multiplier}?' \
                       .format(container=self._re_containers, number=self._re_numbers, multiplier=self._re_multipliers),
                       re.IGNORECASE)

        for match in r.finditer(string):
            yield self._mult(match.group('num'), match.group('mult'))

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

