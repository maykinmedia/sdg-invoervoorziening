from django.utils.datetime_safe import datetime

PRODUCT_EDIT_URL = "producten:edit"
PRODUCT_DETAIL_URL = "producten:detail"

TAB_NL = ".tabs #nl"
TAB_EN = ".tabs #en"

DUMMY_TITLE = "abc"

PAST_DATE = datetime(day=1, month=1, year=2020).date()
NOW_DATE = datetime(day=1, month=1, year=2021).date()
FUTURE_DATE = datetime(day=1, month=1, year=2022).date()
