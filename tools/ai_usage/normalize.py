"""Pure parsers for CLI quota reports; never infer quota from token usage."""
import json
import math
from datetime import datetime, timezone
from urllib.parse import quote


class ParseError(ValueError):
    """An unknown or invalid quota report."""


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def timestamp(value):
    if value is None:
        return None
    try:
        if isinstance(value, bool):
            raise ValueError('boolean time')
        if isinstance(value, (int, float)):
            parsed = datetime.fromtimestamp(value, timezone.utc)
        elif isinstance(value, str):
            parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
            if parsed.tzinfo is None:
                raise ValueError('naive time')
        else:
            raise ValueError('time type')
        return parsed.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    except (ValueError, OverflowError, OSError) as error:
        raise ParseError('invalid reset time') from error


def percentage(value, maximum=100):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ParseError('invalid percentage type')
    if not math.isfinite(value) or not 0 <= value <= maximum:
        raise ParseError('invalid percentage range')
    return value


def bucket(identifier, label, group, used, reset=None, scope=None,
           window=None, fields=None):
    if not all(isinstance(value, str) and value for value in (identifier, label, group)):
        raise ParseError('missing bucket identity')
    if scope is not None and not isinstance(scope, str):
        raise ParseError('invalid scope')
    if window is not None and (type(window) is not int or window <= 0):
        raise ParseError('invalid window')
    used = percentage(used)
    return dict(id=identifier, label=label, group=group, used_percent=used,
                remaining_percent=None if used is None else 100 - used,
                resets_at=timestamp(reset), scope=scope, window_minutes=window,
                source_fields=fields or {})


def _claude_report(event):
    if not isinstance(event, dict):
        return None
    if isinstance(event.get('usage_report'), dict):
        return event['usage_report']
    return None


def unique_buckets(buckets):
    identifiers = [item['id'] for item in buckets]
    if len(identifiers) != len(set(identifiers)):
        raise ParseError('duplicate bucket ids')
    return buckets


def _claude_scope(limit):
    data = limit.get('scope')
    if data is None:
        return None, None, None
    if not isinstance(data, dict):
        raise ParseError('invalid scope')
    model = data.get('model')
    scope = model.get('display_name') if isinstance(model, dict) else None
    surface = data.get('surface')
    if any(value is not None and not isinstance(value, str) for value in (scope, surface)):
        raise ParseError('invalid scope')
    clean = {'model': None if scope is None else {'display_name': scope}, 'surface': surface}
    return scope, surface, clean


def parse_claude(raw):
    reports = []
    for line in raw.splitlines():
        if line.strip():
            report = _claude_report(json.loads(line))
            if report is not None:
                reports.append(report)
    if not reports:
        raise ParseError('missing usage report')
    limits = reports[-1].get('rate_limits', {}).get('limits')
    if not isinstance(limits, list) or not limits:
        raise ParseError('missing limits')
    result = []
    for limit in limits:
        kind = limit['kind']
        if kind not in ('session', 'weekly_all', 'weekly_scoped'):
            raise ParseError('unknown Claude limit')
        scope, surface, clean_scope = _claude_scope(limit)
        if 'is_active' in limit and type(limit['is_active']) is not bool:
            raise ParseError('invalid active flag')
        fields = {key: limit[key] for key in ('kind', 'percent', 'is_active') if key in limit}
        fields['scope'] = clean_scope
        identifier = ':'.join(quote(value, safe='') for value in (kind, scope or '', surface or ''))
        result.append(bucket(identifier, kind, limit.get('group') or 'Claude',
                             limit.get('percent'), limit.get('resets_at'), scope,
                             300 if kind == 'session' else 10080, fields))
    return unique_buckets(result)


def parse_agy(raw):
    payload = json.loads(raw)
    groups = payload.get('command', {}).get('data', {}).get('groups')
    if not isinstance(groups, list) or not groups:
        raise ParseError('missing groups')
    result = []
    for group in groups:
        if not isinstance(group.get('buckets'), list):
            raise ParseError('missing buckets')
        for item in group['buckets']:
            fraction = percentage(item.get('remaining_fraction'), 1)
            window = {'weekly': 10080, '5h': 300}.get(item.get('window'))
            if item.get('window') is not None and window is None:
                raise ParseError('unknown window')
            fields = {key: item[key] for key in ('window', 'remaining_fraction') if key in item}
            result.append(bucket(f"{group['name']}:{item['id']}", item['name'], group['name'],
                                 None if fraction is None else 100 * (1 - fraction),
                                 item.get('reset_time'), window=window, fields=fields))
    if not result:
        raise ParseError('empty groups')
    return unique_buckets(result)


def parse_codex(payload):
    pools = payload.get('rateLimitsByLimitId')
    if pools is None:
        legacy = payload.get('rateLimits')
        pools = {'codex': legacy} if isinstance(legacy, dict) else None
    if not isinstance(pools, dict) or not pools:
        raise ParseError('missing rate limits')
    result = []
    is_blocked = payload.get('ordinaryUsageAllowed') is False
    for pool_id, pool in pools.items():
        if not isinstance(pool, dict):
            raise ParseError('invalid pool')
        is_blocked = is_blocked or pool.get('ordinaryUsageAllowed') is False
        for period in ('primary', 'secondary'):
            item = pool.get(period)
            if item is None:
                continue
            fields = {key: item[key] for key in ('usedPercent', 'windowDurationMins') if key in item}
            result.append(bucket(f'{pool_id}:{period}', f'{pool_id} {period}', pool_id,
                                 item.get('usedPercent'), item.get('resetsAt'),
                                 window=item.get('windowDurationMins'), fields=fields))
    if not result:
        raise ParseError('empty rate limits')
    return unique_buckets(result), is_blocked
