"""Observations of native agents, independent of any host or provider.

Only the lead writes this registry. Observations do not launch/control agents,
enforce native budgets, or imply that the host exposed every descendant.
"""

import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

FILE = 'agents.json'
STATUSES = {'pending', 'running', 'completed', 'failed', 'cancelled', 'unknown'}
TERMINAL = {'completed', 'failed', 'cancelled'}
STALE_MINUTES = 30
MAX_REGISTRY_BYTES = 16 * 1024 * 1024


def _text(value, label, limit=200, optional=False):
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip() or len(value) > limit or '\x00' in value:
        raise ValueError(f'{label} must be nonempty text up to {limit} characters')
    return value


def _time(value):
    try:
        stamp = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError()
        return stamp.astimezone(dt.timezone.utc)
    except (AttributeError, TypeError, ValueError, OverflowError):
        raise ValueError('observedAt must be an ISO timestamp with timezone') from None


def _identity(value):
    if not isinstance(value, dict) or set(value) - {'host', 'id', 'attempt'}:
        raise ValueError('agent reference must contain host, id and optional attempt')
    host = _text(value.get('host'), 'host')
    agent = _text(value.get('id'), 'id')
    attempt = value.get('attempt', 1)
    if type(attempt) is not int or not 1 <= attempt <= 1000000:
        raise ValueError('attempt must be an integer from 1 to 1000000')
    return {'host': host, 'id': agent, 'attempt': attempt}


def native_key(host, agent_id, attempt=1):
    identity = _identity({'host':host, 'id':agent_id, 'attempt':attempt})
    encoded = json.dumps(identity, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return 'native:' + hashlib.sha256(encoded).hexdigest()


def cli_key(run, worker):
    encoded = json.dumps([str(Path(run).resolve()), worker], ensure_ascii=False).encode('utf-8')
    return 'cli:' + hashlib.sha256(encoded).hexdigest()


def _within(folder, relative):
    root = Path(folder).resolve()
    target = (root / relative).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise ValueError('trace path must stay inside its orchestration') from None
    return target


def _cli_ref(folder, value):
    if not isinstance(value, dict) or set(value) != {'run', 'worker'}:
        raise ValueError('cliRef must contain run and worker')
    relative = _text(value['run'], 'cliRef.run', 500)
    if Path(relative).is_absolute():
        raise ValueError('cliRef.run must be relative to the orchestration')
    worker = _text(value['worker'], 'cliRef.worker')
    run = _within(folder, relative)
    root = Path(folder).resolve()
    if (root / 'state.json').is_file():
        recognized = run == root
    else:
        recognized = run.parent == root
    if not recognized:
        raise ValueError('cliRef run must be a CLI wave recognized by the orchestration report')
    state_path = _within(folder, str(run / 'state.json'))
    try:
        state = json.loads(state_path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise ValueError('cliRef must identify an existing CLI run') from None
    if not isinstance(state, dict) or not isinstance(state.get('workers'), dict) or worker not in state['workers']:
        raise ValueError('cliRef worker does not exist in the referenced run')
    return {'run': str(run.relative_to(Path(folder).resolve())), 'worker': worker}


def _metrics(value):
    if not isinstance(value, dict) or set(value) - {'tokens', 'cost'}:
        raise ValueError('metrics may contain tokens and cost only')
    result = {}
    for name, metric in value.items():
        allowed = {'value', 'scope'} | ({'currency', 'basis'} if name == 'cost' else set())
        if not isinstance(metric, dict) or set(metric) != allowed:
            raise ValueError(f'{name} requires value, scope' + (', currency and basis' if name == 'cost' else ''))
        number = metric['value']
        if type(number) not in (int, float) or number < 0 or number > 2**53 - 1 or not math.isfinite(number):
            raise ValueError(f'{name}.value must be finite, nonnegative and safe for JSON consumers')
        if name == 'tokens' and (type(number) is not int):
            raise ValueError('tokens.value must be an integer')
        if metric['scope'] not in ('self', 'descendants', 'unknown'):
            raise ValueError('metric scope must be self, descendants or unknown')
        if name == 'cost':
            currency = metric['currency']
            if not isinstance(currency, str) or len(currency) != 3 or not currency.isascii() or not currency.isalpha() or not currency.isupper():
                raise ValueError('cost.currency must be a three-letter uppercase code')
            if metric['basis'] not in ('reported-expense', 'api-equivalent', 'unknown'):
                raise ValueError('cost.basis must be reported-expense, api-equivalent or unknown')
        result[name] = dict(metric)
    return result


def _validate(folder, raw):
    allowed = {'version', 'host', 'id', 'attempt', 'parent', 'provider', 'model', 'effort',
               'task', 'result', 'status', 'observedAt', 'source', 'metrics', 'cliRef'}
    if not isinstance(raw, dict) or set(raw) - allowed or type(raw.get('version')) is not int or raw['version'] != 1:
        raise ValueError('observation must be version 1 with supported fields')
    value = {'version': 1, **_identity({k: raw[k] for k in ('host','id','attempt') if k in raw})}
    if not isinstance(raw.get('status'), str) or raw['status'] not in STATUSES:
        raise ValueError('unsupported native agent status')
    value.update(status=raw['status'], observedAt=_time(raw.get('observedAt')).isoformat(),
                 source=_text(raw.get('source'), 'source', 1000))
    for name in ('provider','model','effort','task','result'):
        value[name] = _text(raw.get(name), name, 2000 if name in ('task','result') else 200, optional=True)
    parent = raw.get('parent')
    value['parent'] = parent if parent in (None, 'lead') else _identity(parent)
    value['metrics'] = _metrics(raw.get('metrics', {}))
    value['cliRef'] = _cli_ref(folder, raw['cliRef']) if raw.get('cliRef') is not None else None
    return value


def _key(value):
    return native_key(value['host'], value['id'], value['attempt'])


def _canonical(folder, value):
    ref = value.get('cliRef')
    return cli_key(_within(folder, ref['run']), ref['worker']) if ref else _key(value)


def _parents(folder, observations):
    aliases = {_key(value): _canonical(folder, value) for value in observations}
    parents = {}
    for value in observations:
        parent = value['parent']
        if not parent:
            continue
        parent_key = 'lead' if parent == 'lead' else native_key(parent['host'], parent['id'], parent['attempt'])
        child_key = aliases[_key(value)]
        parent_key = aliases.get(parent_key, parent_key)
        if child_key in parents and parents[child_key] != parent_key:
            raise ValueError('conflicting parents for the same CLI-linked execution')
        parents[child_key] = parent_key
    for child in parents:
        seen = set()
        node = child
        while node in parents:
            if node in seen:
                raise ValueError('agent parent relationships must not form a cycle')
            seen.add(node)
            node = parents[node]
    return aliases, parents


def read(folder):
    if folder is None:
        return []
    path = _within(folder, FILE)
    if not path.exists():
        return []
    if path.stat().st_size > MAX_REGISTRY_BYTES:
        raise ValueError('agent registry exceeds the supported size')
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise ValueError('invalid agent registry JSON') from None
    if not isinstance(raw, dict) or type(raw.get('version')) is not int or raw['version'] != 1 or not isinstance(raw.get('observations'), list):
        raise ValueError('agent registry requires version 1 and observations')
    if len(raw['observations']) > 5000:
        raise ValueError('agent registry supports up to 5000 attempts')
    values = [_validate(folder, value) for value in raw['observations']]
    if len({_key(value) for value in values}) != len(values):
        raise ValueError('agent registry contains duplicate identities')
    _parents(folder, values)
    return values


def record(folder, observation):
    folder = Path(folder).resolve()
    if not (folder / 'orchestration.json').is_file():
        raise ValueError('trace requires an orchestration folder created with new')
    value = _validate(folder, observation)
    values = read(folder)
    prior = next((item for item in values if _key(item) == _key(value)), None)
    if prior:
        before, after = _time(prior['observedAt']), _time(value['observedAt'])
        if after < before or value == prior:
            return {'changed': False, 'key': _key(value), 'observation': prior}
        if after == before:
            raise ValueError('conflicting observations at the same timestamp')
        if prior.get('cliRef') and value.get('cliRef') != prior['cliRef']:
            raise ValueError('a linked execution cannot change or drop its CLI reference; register a new attempt')
        if prior['status'] in TERMINAL and value['status'] != prior['status']:
            raise ValueError('a terminal attempt cannot reopen; register a new attempt')
    updated = [item for item in values if _key(item) != _key(value)] + [value]
    if len(updated) > 5000:
        raise ValueError('agent registry supports up to 5000 attempts')
    _parents(folder, updated)
    path = _within(folder, FILE)
    descriptor, temporary = tempfile.mkstemp(prefix='.agents-', suffix='.tmp', dir=folder)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            json.dump({'version':1, 'observations':updated}, handle, ensure_ascii=False, allow_nan=False, indent=2)
            handle.write('\n')
        if os.path.getsize(temporary) > MAX_REGISTRY_BYTES:
            raise ValueError('agent registry exceeds the supported size; previous registry was preserved')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {'changed': True, 'key': _key(value), 'observation': value}


def agent_list(runs, folder=None, now=None):
    current = now or dt.datetime.now(dt.timezone.utc)
    rows = []
    for run in runs:
        for worker in run['workers']:
            metrics = {}
            if worker.get('tokens') is not None:
                metrics['tokens'] = {'value':worker['tokens'], 'scope':'unknown'}
            if worker.get('costUsd') is not None:
                metrics['cost'] = {'value':worker['costUsd'], 'currency':'USD', 'scope':'unknown',
                    'basis':'api-equivalent' if worker.get('provider') == 'claude' else 'unknown'}
            rows.append({'key':cli_key(run['runDir'],worker['id']), 'id':worker['id'],
                'backend':'cli', 'run':run['runDir'], 'host':None, 'attempt':None, 'parentKey':None,
                'parentUnresolved':False, 'provider':worker.get('provider'), 'model':worker.get('model'),
                'effort':worker.get('effort'), 'task':worker.get('why'), 'result':worker.get('summary'),
                'status':worker.get('status'), 'observedAt':run.get('finishedAt') or run.get('startedAt'),
                'source':run['runDir'], 'stale':None, 'metrics':metrics, 'observations':[]})
    by_key = {row['key']:row for row in rows}
    observations = read(folder)
    aliases, parents = _parents(folder, observations) if folder is not None else ({},{})
    for value in observations:
        key = aliases[_key(value)]
        if value.get('cliRef'):
            if key not in by_key:
                raise ValueError('CLI-linked agent is outside the runs included in this report')
            by_key[key]['observations'].append(value)
            continue
        age = max(0, (current - _time(value['observedAt'])).total_seconds() / 60)
        row = {**value, 'key':key, 'backend':'native', 'run':None, 'parentKey':None,
               'parentUnresolved':False, 'stale':age > STALE_MINUTES, 'observations':[]}
        by_key[key] = row
        rows.append(row)
    for row in rows:
        parent = parents.get(row['key'])
        if parent:
            row.update(parentKey=parent, parentUnresolved=parent != 'lead' and parent not in by_key)
        elif row.get('parent') == 'lead' or any(value.get('parent') == 'lead' for value in row['observations']):
            row['parentKey'] = 'lead'
        row['coverage'] = {metric:metric in row['metrics'] for metric in ('tokens','cost')}
    return rows
