"""Iranian-specific form helpers."""
from __future__ import unicode_literals

import re

from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.forms.fields import Field, RegexField, Select
from django.utils.translation import ugettext_lazy as _

from .ir_provinces import PROVINCE_CHOICES

id_number_re = re.compile(r'^\d{10}$')


class IRProvinceSelect(Select):
    """A Select widget that uses a list of Iran provinces cities as its choices."""

    def __init__(self, attrs=None):
        super(IRProvinceSelect, self).__init__(attrs, choices=PROVINCE_CHOICES)


class IRPostalCodeField(RegexField):
    """
    A form field that validates its input as an Iran postal code.

    Valid form is XXXXXXXXXX where X represents integer.

    Validate code:
        - don't use 0 in first 5 digit
        - don't use 2 in postal code
        - First 4 digit is not the same
        - The 5th digit cannot be 5
        - all digits aren't the same

    """

    default_error_messages = {
        'invalid': _('Enter a postal code in the format XXXXXXXXXX - digits only'),
    }

    def __init__(self, *args, **kwargs):
        super(IRPostalCodeField, self).\
            __init__(r'\b(?!(\d)\1{3})[13-9]{4}[1346-9][013-9]{5}\b$', *args, **kwargs)

    def clean(self, value):
        if value not in self.empty_values:
            value = value.replace(' ', '')
        return super(IRPostalCodeField, self).clean(value)


class IRIDNumberField(Field):
    """
    A form field that validates its input as an Iranian identification number.

    Valid form is per the Iranian ID specification.

    """

    default_error_messages = {
        'invalid': _('Enter a valid ID number.'),
    }

    def clean(self, value):
        value = super(IRIDNumberField, self).clean(value)

        if value in EMPTY_VALUES:
            return ''

        match = id_number_re.match(value)
        if not match:
            raise ValidationError(self.error_messages['invalid'])

        check = int(value[9])
        s = sum([int(value[x]) * (10 - x) for x in range(9)]) % 11

        if (2 > s == check) or (s >= 2 and check + s == 11):
            return value
        else:
            raise ValidationError(self.error_messages['invalid'])
