import re

from django import VERSION as DJANGO_VERSION
from django.core.management.commands import makemessages
from django.template.base import BLOCK_TAG_START, BLOCK_TAG_END

if DJANGO_VERSION[:2] < (1, 11):
    from django.utils.translation import trans_real
else:
    from django.utils.translation import template as trans_real

strip_whitespace_right = re.compile(r"(%s-?\s*(trans|pluralize).*?-%s)\s+" % (BLOCK_TAG_START, BLOCK_TAG_END), re.U)
strip_whitespace_left = re.compile(r"\s+(%s-\s*(endtrans|pluralize).*?-?%s)" % (BLOCK_TAG_START, BLOCK_TAG_END), re.U)


def strip_whitespaces(src):
    src = strip_whitespace_left.sub(r'\1', src)
    src = strip_whitespace_right.sub(r'\1', src)
    return src


class Command(makemessages.Command):

    def handle(self, *args, **options):
        old_endblock_re = trans_real.endblock_re
        old_block_re = trans_real.block_re
        old_constant_re = trans_real.constant_re

        old_templatize = trans_real.templatize
        # Extend the regular expressions that are used to detect
        # translation blocks with an "OR jinja-syntax" clause.
        trans_real.endblock_re = re.compile(
            trans_real.endblock_re.pattern + '|' + r"""^-?\s*endtrans\s*-?$""")
        trans_real.block_re = re.compile(
            trans_real.block_re.pattern + '|' + r"""^-?\s*trans(?:\s+(?!'|")(?=.*?=.*?)|\s*-?$)""")
        trans_real.plural_re = re.compile(
            trans_real.plural_re.pattern + '|' + r"""^-?\s*pluralize(?:\s+.+|-?$)""")
        trans_real.constant_re = re.compile(r""".*?_\(((?:".*?(?<!\\)")|(?:'.*?(?<!\\)')).*?\)""")

        def my_templatize(src, origin=None, **kwargs):
            new_src = strip_whitespaces(src)
            return old_templatize(new_src, origin, **kwargs)

        trans_real.templatize = my_templatize

        try:
            super(Command, self).handle(*args, **options)
        finally:
            trans_real.endblock_re = old_endblock_re
            trans_real.block_re = old_block_re
            trans_real.templatize = old_templatize
            trans_real.constant_re = old_constant_re
