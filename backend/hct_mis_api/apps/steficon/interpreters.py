import datetime
import random
import traceback
from builtins import __build_class__
from decimal import Decimal
from symbol import classdef

import dateutil
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from jinja2 import Environment

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.steficon.score import Score
from hct_mis_api.apps.steficon.templatetags import engine
import logging

logger = logging.getLogger(__name__)


class Interpreter:
    def __init__(self, init_string):
        self.init_string = init_string

    def validate(self):
        try:
            self.execute(hh=Household.objects.first())
        except Exception as e:
            raise ValidationError(e)


class PythonFunction(Interpreter):
    label = "internal"

    @cached_property
    def code(self):
        return import_string(self.init_string)

    def execute(self, **context):
        return self.code(**context)


class PythonExec(Interpreter):
    label = "Python"

    @cached_property
    def code(self):
        return compile(self.init_string, "<code>", mode="exec")

    def execute(self, **context):
        gl = {
            "__builtins__": {
                "random": random,
                "__build_class__": __build_class__,
                "__name__": __name__,
                "int": int,
                "str": str,
                "float": float,
                "datetime": datetime,
                "dateutil": dateutil,
            }
        }
        pts = Score()
        locals_ = dict(context)
        locals_["score"] = pts
        exec(self.code, gl, locals_)
        return pts.value

    def validate(self):
        errors = []
        for forbidden in ["__import__", "raw", "connection", "import", "delete", "save", "eval", "exec"]:
            if forbidden in self.init_string:
                errors.append("Code contains an invalid statement '%s'" % forbidden)
        if errors:
            raise ValidationError(errors)
        try:
            self.execute(hh=Household.objects.first())
        except Exception as e:
            logger.exception(e)
            tb = traceback.format_exc(limit=-1)
            msg = tb.split('<code>", ')[-1]
            raise ValidationError(mark_safe(msg))


# from jinja2 import environment


def get_env(**options) -> Environment:
    env = Environment(**options)
    env.filters.update(
        {
            "adults": engine.adults
            # 'url': reverse,
        }
    )
    return env


# environment.DEFAULT_FILTERS['md5'] = lambda s: md5(s.encode('utf-8'))
# environment.DEFAULT_FILTERS['hexdigest'] = lambda s: s.hexdigest()
# environment.DEFAULT_FILTERS['urlencode'] = urlencode
# environment.DEFAULT_FILTERS['slugify'] = slugify


class Jinja(Interpreter):
    label = "Jinja2"

    @cached_property
    def code(self):
        return get_env().from_string(self.init_string)

    def execute(self, **context):
        pts = Score()
        context["score"] = pts
        output = self.code.render(**context)
        return Decimal(output.strip())


interpreters = [
    PythonExec,
    PythonFunction,
]
mapping = {a.label.lower(): a for a in interpreters}
