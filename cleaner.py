import re
import functools
import csv


class ListingCleaner:
    """Base class for listing cleaner objects. Handles opening/writing data files, some common cleaning tasks,
    and error reporting."""

    def __init__(self):
        pass

    def normalize_whitespace(self, string):
        """Return string with leading and trailing whitespace removed, and any spaces/newlines/tabs normalized to
        a single space."""
        return re.sub(r'\s+', ' ', string).strip()

    def remove_symbols(self, string):
        """Return string with anything that isn't a character, digit, or whitespace removed."""
        return re. sub(r'[^\w\s]', '', string)

    def clean(self, listing):
        """Return a dictionary of 'cleaned' values for the given listing. clean() expects a dictionary-like
        object."""
        response = dict()

        for key in listing.keys():
            cleaner_name = 'clean_' + str(key)
            try:
                cleaner = eval('self.%s' % cleaner_name)
            except AttributeError:
                cleaner = functools.partial(self.default_cleaner, key=key)

            response[key] = cleaner(listing)

        return response

    def default_cleaner(self, listing, key):
        """Default cleaner. Just returns listing[key]."""
        return self.normalize_whitespace(str(listing[key]))

    def clean_price(self, listing):
        """Remove anything from the price field that isn't a digit or a period."""
        return re.sub(r'[^\d.]', '', listing['price'])


class CSVCleaner:
    """Opens a CSV file and cleans each row."""

    def __init__(self):
        pass

    def clean(self, filename_in, filename_out, cleaner=ListingCleaner(), **kwargs):
        rows = []

        with open(filename_in) as file_in:
            reader = csv.DictReader(file_in, **kwargs)
            for row in reader:
                rows.append(cleaner.clean(row))

        keys = sorted(rows, key=len, reverse=True)[0].keys()

        with open(filename_out, 'w') as file_out:
            writer = csv.DictWriter(file_out, keys, **kwargs)
            writer.writeheader()
            writer.writerows(rows)