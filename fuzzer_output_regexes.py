import re

HEADER_RE = re.compile("__GARLIC_HEADER__(.*?)__ENDGARLIC__")
CALL_RE = re.compile("__GARLIC_CALL__(.*?)__ENDGARLIC__")
NOT_IMPLEMENTED_RE = re.compile("__GARLIC_NOT_IMPLEMENTED__(.*?)__ENDGARLIC__")
INTERCEPT_RE = re.compile("__GARLIC_INTERCEPT__(.*?)__ENDGARLIC__")
COULD_AS_WELL_BE_EQUAL_RE = re.compile("__GARLIC_COULD_AS_WELL_BE_EQUAL__(.*?)__AND__(.*?)__ENDGARLIC__", re.MULTILINE)
