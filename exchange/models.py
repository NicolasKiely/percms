# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import crypto.models


class Ticker(models.Model):
    """ Latest ticker price of currency from an exchange """
    #: Asset pair
    pair = models.OneToOneField(crypto.models.Pair)

    #: Value of currency
    last = models.FloatField(default=0.0)

    #: Time when last updated
    stamp = models.DateTimeField()

    def __str__(self):
        return '%s [%s %s]: %s' % (
            self.pair.exc.name,
            self.pair.c1,
            self.pair.c2,
            self.last
        )
