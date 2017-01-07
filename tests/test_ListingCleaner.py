from unittest import TestCase
from cleaner import ListingCleaner


class TestListingCleaner(TestCase):

    def setUp(self):
        self.cleaner = ListingCleaner()
        self.listing_in = {'brand': '  Evil Corp.  ',
                           'desc': 'The most evil product ever!\n\n\t Something for the whole family.  ',
                           'model': ' EVIL99 ',
                           'price': ' $1,000,000.00 dollars',
                           'sku': ' EVIL99',
                           'title': ' Super evil product!!! '}

        self.listing_out = {'brand': 'Evil Corp.',
                            'desc': 'The most evil product ever! Something for the whole family.',
                            'model': 'EVIL99',
                            'price': '1000000.00',
                            'sku': 'EVIL99',
                            'title': 'Super evil product!!!'}

    def test_normalize_whitespace(self):
        string = '   normalize\n\t\t this   '
        self.assertEqual(self.cleaner.normalize_whitespace(string),
                         'normalize this')

    def test_remove_symbols(self):
        string = 'get rid of &&*^//symbols'
        self.assertEqual(self.cleaner.remove_symbols(string),
                         'get rid of symbols')

    def test_default_cleaner(self):
        listing = {'field': '   normalize \t\t whitespace '}
        self.assertEqual(self.cleaner.default_cleaner(listing, key='field'),
                         'normalize whitespace')

    def test_clean_price(self):
        listing = {'price': '  $1,000,000.00\n'}
        self.assertEqual(self.cleaner.clean_price(listing),
                         '1000000.00')

    def test_clean(self):
        self.assertEqual(self.cleaner.clean(self.listing_in),
                         self.listing_out)
