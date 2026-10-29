import contextlib
import datetime as dt
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('trace_reports_runner', ROOT/'scripts'/'orchestrate.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class TraceReportTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        patch = mock.patch.dict(os.environ, {'ORQUESTRADOR_ORCHESTRATE_HOME':str(self.root/'runs'),
            'ORQUESTRADOR_ORCHESTRATE_POLICY':str(self.root/'policy.json')})
        patch.start()
        self.addCleanup(patch.stop)
        self.assertEqual(self.call('new','Native report')[0],0)
        self.folder = runner.current_folder()

    def call(self,*args):
        out,err=io.StringIO(),io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            code=runner.main([str(arg) for arg in args])
        return code,out.getvalue(),err.getvalue()

    def record(self, **extra):
        value={'version':1,'host':'test-host','id':'native-one','status':'completed',
               'observedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'source':'fixture',
               'task':'Read </script><script>alert(1)</script> | safely',**extra}
        path=self.root/'observation.json'
        path.write_text(json.dumps(value),encoding='utf-8')
        code,out,err=self.call('trace','record',path,'--in',self.folder)
        self.assertEqual(code,0,err)
        return json.loads(out)

    def test_native_only_report_and_list_preserve_unknown_consumption(self):
        self.record(parent='lead')
        code,out,err=self.call('trace','list','--in','current')
        self.assertEqual(code,0,err)
        self.assertEqual(len(json.loads(out)['agents']),1)
        code,out,err=self.call('report','--format','json')
        self.assertEqual(code,0,err)
        report=json.loads(out)
        self.assertEqual(report['totals']['calls'],0)
        self.assertIsNone(report['totals']['tokens'])
        self.assertEqual(report['agents'][0]['backend'],'native')
        self.assertEqual(report['agentCoverage']['missingTokens'],[report['agents'][0]['key']])
        self.assertIsNone(report['agentCoverage']['combinedCost'])
        code,explicit,err=self.call('report',self.folder,'--format','json')
        self.assertEqual(code,0,err)
        self.assertEqual(len(json.loads(explicit)['agents']),1)

    def test_markdown_and_html_include_native_agents_without_inventing_totals(self):
        self.record(metrics={'cost':{'value':1,'currency':'EUR','scope':'descendants','basis':'api-equivalent'}})
        code,out,err=self.call('report')
        self.assertEqual(code,0,err)
        self.assertIn('native-one',out)
        self.assertIn('EUR',out)
        self.assertIn('api-equivalent',out)
        self.assertIn('descendants',out)
        page=self.root/'report.html'
        code,out,err=self.call('report','--format','html','--no-open','--write',page)
        self.assertEqual(code,0,err)
        text=page.read_text(encoding='utf-8')
        self.assertNotIn('Read </script><script>alert(1)</script>',text)
        match=re.search(r'<script type="application/json" id="report-data">\n(.*?)\n</script>',text,re.S)
        self.assertEqual(json.loads(match.group(1))['agents'][0]['id'],'native-one')

    def test_bad_observation_returns_cli_error_instead_of_traceback(self):
        path=self.root/'bad.json'
        path.write_text('{"version":1,"status":[]}',encoding='utf-8')
        code,out,err=self.call('trace','record',path,'--in',self.folder)
        self.assertEqual(code,2)
        self.assertIn('error:',err)
        self.assertEqual(out,'')
        path.write_bytes(b'\xff')
        code,out,err=self.call('trace','record',path,'--in',self.folder)
        self.assertEqual(code,2)
        self.assertIn('UTF-8',err)

    @unittest.skipUnless(shutil.which('node'), 'node is not installed')
    def test_html_table_renders_unknowns_scopes_and_untrusted_text_as_text(self):
        page=(ROOT/'assets'/'report.html').read_text(encoding='utf-8')
        function='function agentTraceTable(r) {'+page.split('function agentTraceTable(r) {',1)[1].split('\nfunction todo(r)',1)[0]
        harness="""
function h(tag, props={}, children=[]) {
  const node={tag,props,children:Array.isArray(children)?children:[children]};
  node.append=(...values)=>node.children.push(...values);
  return node;
}
"""+function+"\nconsole.log(JSON.stringify(agentTraceTable(JSON.parse(require('fs').readFileSync(0,'utf8')))));"
        data={'agents':[{'key':'native:key','id':'<script>unsafe</script>', 'backend':'native',
            'status':'running','parentKey':'lead','metrics':{'cost':{'value':2,'currency':'EUR',
            'basis':'api-equivalent','scope':'descendants'}}}]}
        result=subprocess.run([shutil.which('node'),'-e',harness],input=json.dumps(data),capture_output=True,text=True,check=True)
        tree=json.loads(result.stdout)
        values=[]
        def visit(node):
            if not isinstance(node,dict): return
            self.assertNotIn('innerHTML',node.get('props',{}))
            if 'textContent' in node.get('props',{}): values.append(node['props']['textContent'])
            for child in node.get('children',[]): visit(child)
        visit(tree)
        self.assertIn('<script>unsafe</script>',values)
        self.assertIn('desconhecido',values)
        self.assertIn('2 EUR (api-equivalent; descendants)',values)
        self.assertIn('principal',values)

    def test_mixed_report_keeps_cli_totals_and_exposes_individual_blind_spots(self):
        self.record(metrics={'tokens':{'value':999,'scope':'descendants'}})
        # Use genuine CLI fixtures to produce a report with one measured and one unmeasured worker.
        path=self.folder/'wave'
        path.mkdir()
        state={'status':'succeeded','workers':{},'budgetUsage':{'calls':2},
               'startedAt':'2026-10-29T12:00:00Z','finishedAt':'2026-10-29T12:01:00Z'}
        for worker,metrics in [('measured',{'usage':{'total_tokens':7}}),('unknown',{})]:
            state['workers'][worker]={'id':worker,'provider':'example','status':'succeeded',
                'metrics':metrics,'startedAt':state['startedAt'],'finishedAt':state['finishedAt']}
        (path/'state.json').write_text(json.dumps(state),encoding='utf-8')
        code,out,err=self.call('report','--format','json')
        self.assertEqual(code,0,err)
        report=json.loads(out)
        self.assertEqual(report['totals']['tokens'],7)
        self.assertEqual(len(report['agents']),3)
        blind=[agent for agent in report['agents'] if agent['id']=='unknown'][0]
        self.assertIn(blind['key'],report['agentCoverage']['missingTokens'])


if __name__ == '__main__':
    unittest.main()
