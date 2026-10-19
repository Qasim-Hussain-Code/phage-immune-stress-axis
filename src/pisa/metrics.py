"""Validated community estimators, used only by software tests in this audit.

No biological abundance matrix is available; these functions do not generate
any scientific stability estimates in the present study.
"""
import math


def close(values):
    if not values or any(not math.isfinite(x) or x < 0 for x in values):
        raise ValueError('Abundances must be finite, nonnegative and nonempty')
    total = sum(values)
    if total <= 0:
        raise ValueError('All-zero community')
    return [x / total for x in values]


def clr(values, zero_fraction=0.5):
    """Replace zeros by fraction * smallest positive closed abundance, reclose.

    This is an explicit sensitivity parameter, not a claim of universal validity.
    Only zero values are replaced before closure. Positive ratios are preserved.
    """
    if not 0 < zero_fraction <= 1:
        raise ValueError('zero_fraction must be in (0,1]')
    p = close(values)
    floor = min(x for x in p if x > 0) * zero_fraction
    p = close([x if x > 0 else floor for x in p])
    logs = [math.log(x) for x in p]
    mean = sum(logs) / len(logs)
    return [x-mean for x in logs]


def aitchison(x, y, zero_fraction=0.5):
    if len(x) != len(y):
        raise ValueError('Feature dimensions differ')
    a, b = clr(x, zero_fraction), clr(y, zero_fraction)
    return math.sqrt(sum((u-v)**2 for u, v in zip(a,b)))


def bray_curtis(x,y):
    if len(x) != len(y):
        raise ValueError('Feature dimensions differ')
    a,b=close(x),close(y)
    return sum(abs(u-v) for u,v in zip(a,b))/sum(a+b)
