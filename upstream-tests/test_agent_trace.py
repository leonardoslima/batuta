import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

PATH = Path(__file__).resolve().parents[1] / 'scripts' / 'agent_trace.py'
spec = importlib.util.spec_from_file_location('agent_trace_tests_module', PATH)
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)


class AgentTraceTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        (self.folder/'orchestration.json').write_text('{"version":1}', encoding='utf-8')
        self.now = dt.datetime.now(dt.timezone.utc)

    def observation(self, **updates):
        return {'version': 1, 'host': 'example-host', 'id': 'one', 'attempt': 1,
                'status': 'running', 'observedAt': self.now.isoformat(),
                'source': 'host snapshot', **updates}

    def test_repeated_snapshot_is_idempotent_and_older_snapshot_does_not_revert(self):
        first = self.observation()
        trace.record(self.folder, first)
        trace.record(self.folder, first)
        self.assertEqual(len(trace.read(self.folder)), 1)
        newer = self.observation(status='completed', observedAt=(self.now+dt.timedelta(seconds=1)).isoformat())
        trace.record(self.folder, newer)
        trace.record(self.folder, first)
        self.assertEqual(trace.read(self.folder)[0]['status'], 'completed')

    def test_equal_timestamp_conflict_and_terminal_reopening_are_rejected(self):
        trace.record(self.folder, self.observation(status='completed'))
        for change in [dict(status='failed'), dict(status='running', observedAt=(self.now+dt.timedelta(seconds=1)).isoformat())]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                trace.record(self.folder, self.observation(**change))
        trace.record(self.folder, self.observation(attempt=2))
        self.assertEqual(len(trace.read(self.folder)), 2)

    def test_full_snapshots_replace_metrics_without_summing(self):
        def metric(value):
            return {'tokens': {'value': value, 'scope': 'descendants'}}
        trace.record(self.folder, self.observation(metrics=metric(10)))
        trace.record(self.folder, self.observation(metrics=metric(20), observedAt=(self.now+dt.timedelta(seconds=1)).isoformat()))
        self.assertEqual(trace.read(self.folder)[0]['metrics']['tokens']['value'], 20)
        trace.record(self.folder, self.observation(observedAt=(self.now+dt.timedelta(seconds=2)).isoformat()))
        self.assertEqual(trace.read(self.folder)[0]['metrics'], {})

    def test_parent_may_arrive_later_but_cycles_are_rejected(self):
        parent = {'host': 'example-host', 'id': 'parent', 'attempt': 1}
        trace.record(self.folder, self.observation(parent=parent))
        agents = trace.agent_list([], self.folder, now=self.now)
        self.assertTrue(agents[0]['parentUnresolved'])
        trace.record(self.folder, self.observation(id='parent', parent='lead'))
        self.assertFalse(trace.agent_list([], self.folder, now=self.now)[0]['parentUnresolved'])
        with self.assertRaises(ValueError):
            trace.record(self.folder, self.observation(id='parent', parent={'host':'example-host','id':'one'},
                observedAt=(self.now+dt.timedelta(seconds=1)).isoformat()))

    def test_metric_boundaries_and_external_parent_are_rejected(self):
        invalid = [dict(metrics={'tokens': {'value': -1, 'scope':'self'}}),
            dict(metrics={'tokens': {'value': float('nan'), 'scope':'self'}}),
            dict(metrics={'cost': {'value': 1, 'scope':'self'}}),
            dict(parent={'host':'x','id':'x','orchestration':'elsewhere'}),
            dict(task='x'*5000), dict(attempt=True), dict(observedAt='yesterday'), dict(status=[]),
            dict(observedAt='0001-01-01T00:00:00+01:00'), dict(observedAt='9999-12-31T23:59:59-01:00'),
            dict(metrics={'tokens':{'value':10**1000,'scope':'self'}}),
            dict(metrics={'tokens':{'value':-10**1000,'scope':'self'}})]
        for update in invalid:
            with self.subTest(fields=list(update)), self.assertRaises(ValueError):
                trace.record(self.folder, self.observation(**update))

    def test_zero_is_explicit_unknown_is_not_zero_and_stale_is_not_failure(self):
        trace.record(self.folder, self.observation(metrics={'tokens': {'value':0,'scope':'self'}}))
        row = trace.agent_list([], self.folder, now=self.now+dt.timedelta(hours=1))[0]
        self.assertEqual(row['metrics']['tokens']['value'], 0)
        self.assertNotIn('cost', row['metrics'])
        self.assertTrue(row['stale'])
        self.assertEqual(row['status'], 'running')

    def test_cli_link_deduplicates_and_repeated_worker_ids_are_distinct(self):
        runs=[]
        for name in ('wave1','wave2'):
            path=self.folder/name
            path.mkdir()
            (path/'state.json').write_text(json.dumps({'workers':{'one':{'status':'succeeded'}}}),encoding='utf-8')
            runs.append({'runDir':str(path), 'workers':[{'id':'one','provider':'example',
                'status':'succeeded','tokens':7,'costUsd':None,'summary':'ok'}]})
        trace.record(self.folder, self.observation(cliRef={'run':'wave1','worker':'one'}))
        rows=trace.agent_list(runs,self.folder,now=self.now)
        self.assertEqual(len(rows),2)
        self.assertNotEqual(rows[0]['key'],rows[1]['key'])
        self.assertEqual(rows[0]['observations'][0]['host'],'example-host')
        self.assertEqual(rows[0]['metrics']['tokens']['value'],7)
        self.assertFalse(rows[0]['coverage']['cost'])
        with self.assertRaises(ValueError):
            trace.record(self.folder,self.observation(id='bad',cliRef={'run':'../elsewhere','worker':'one'}))

    def test_linked_execution_cannot_silently_change_or_drop_its_cli_identity(self):
        for name in ('wave1','wave2'):
            path=self.folder/name
            path.mkdir()
            (path/'state.json').write_text('{"workers":{"one":{}}}',encoding='utf-8')
        for index, ref in enumerate((None, {'run':'wave2','worker':'one'})):
            agent_id=f'linked-{index}'
            trace.record(self.folder,self.observation(id=agent_id,cliRef={'run':'wave1','worker':'one'}))
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                trace.record(self.folder,self.observation(id=agent_id,cliRef=ref,
                    observedAt=(self.now+dt.timedelta(seconds=1)).isoformat()))

    def test_registry_size_limit_cannot_destroy_a_readable_previous_registry(self):
        with mock.patch.object(trace,'MAX_REGISTRY_BYTES',1024,create=True):
            trace.record(self.folder,self.observation())
            original=(self.folder/trace.FILE).read_bytes()
            with self.assertRaises(ValueError):
                trace.record(self.folder,self.observation(id='large',task='á'*900))
            self.assertEqual((self.folder/trace.FILE).read_bytes(),original)
            self.assertEqual(len(trace.read(self.folder)),1)

    def test_nested_cli_reference_is_rejected_before_it_breaks_reports(self):
        nested=self.folder/'nested'/'wave'
        nested.mkdir(parents=True)
        (nested/'state.json').write_text('{"workers":{"one":{}}}',encoding='utf-8')
        with self.assertRaises(ValueError):
            trace.record(self.folder,self.observation(cliRef={'run':'nested/wave','worker':'one'}))


if __name__ == '__main__':
    unittest.main()
