from django.utils.datetime_safe import datetime

PRODUCT_EDIT_URL = "organisaties:catalogi:producten:edit"
PRODUCT_DETAIL_URL = "organisaties:catalogi:producten:detail"

TAB_NL = ".tabs #nl"
TAB_EN = ".tabs #en"

DUMMY_TITLE = "abc"

PAST_DATE = datetime(day=1, month=1, year=2020).date()
NOW_DATE = datetime(day=1, month=1, year=2021).date()
FUTURE_DATE = datetime(day=1, month=1, year=3000).date()
