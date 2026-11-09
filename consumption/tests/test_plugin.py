"""Actual Lua code with an artificial host; never contacts a household API."""
import json,unittest
from pathlib import Path
from lupa.lua54 import LuaRuntime
ROOT=Path(__file__).resolve().parents[1]
class Host:
    def __init__(self,enabled=True,**settings):
        self.lua=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False)
        self.widgets={};self.requests=[];self.cancelled=[];self.charts=[]
        g=self.lua.globals();g._widget=lambda spec:self.widgets.update({spec['id']:spec['text']})
        g._text=lambda key,value:self.widgets.update({key:value})
        g._request=self.request;g._cancel=lambda ident:self.cancelled.append(ident);g._chart=self.chart
        self.ctx=self.lua.execute('''return {ui={page=function(_) end,label=_widget,button=_widget,
          set_text=_text,pie_chart=_chart},consumption={request=_request,cancel=_cancel}}''')
        config={k:v['default'] for k,v in json.loads((ROOT/'config.schema.json').read_text())['properties'].items()}
        config.update(api_origin='http://192.168.1.10:8111');config.update(settings);self.ctx.config=self.convert(config)
        if not enabled:self.ctx.consumption=None;self.ctx.ui.pie_chart=None
        for name in ('io','os','package','require','debug','load','loadfile','dofile','python'):g[name]=None
        self.plugin=self.lua.execute((ROOT/'main.lua').read_text());self.plugin.create(self.ctx);self.plugin.show(self.ctx)
    def convert(self,value):
        if isinstance(value,dict):return self.lua.table_from({k:self.convert(v) for k,v in value.items()})
        if isinstance(value,list):return self.lua.table_from([self.convert(v) for v in value])
        return value
    def request(self,spec):
        request={k:v for k,v in spec.items()};request['id']=len(self.requests)+1;self.requests.append(request);return request['id']
    def chart(self,spec):
        slices=[{k:v for k,v in row.items()} for _,row in spec['slices'].items()]
        self.charts.append(slices);return True
    def event(self,name,**values):self.plugin.event(self.ctx,self.convert(dict(name=name,**values)))
    def answer(self,groups=None,**overrides):
        req=self.requests[-1];data=dict(period=req['period'],**{'from':'2026-11-09','to':'2026-11-10'},is_current=True,groups=groups if groups is not None else [dict(name='Device A',kwh=2,price=4)])
        data.update(overrides.pop('data',{}));self.event('consumption',**dict(dict(id=req['id'],tag=req['tag'],status=200,json=data,now_ms=1000),**overrides))
class PluginTests(unittest.TestCase):
    def test_starts_one_typed_request_without_any_url(self):
        h=Host();self.assertEqual(len(h.widgets),11);self.assertEqual(len(h.requests),1);self.assertEqual(set(h.requests[0]),{'id','period','date','shift','tag'})
    def test_missing_host_explains_requirement_without_request(self):
        h=Host(enabled=False);self.assertEqual(h.requests,[]);self.assertIn('nyere core',h.widgets['status'])
    def test_unconfigured_api_is_not_contacted(self):
        h=Host(api_origin='');self.assertEqual(h.requests,[]);self.assertIn('Home API',h.widgets['status'])
    def test_positive_shares_and_total_price(self):
        h=Host();h.answer([dict(name='B',kwh=1,price=2),dict(name='A',kwh=3,price=6)]);self.assertEqual(h.widgets['total'],'4.00 kWh');self.assertEqual(h.widgets['price'],'8.00 DKK');self.assertEqual(h.charts[-1][0]['label'],'A');self.assertIn('75.0%',h.charts[-1][0]['detail'])
    def test_negative_corrections_are_in_net_total_but_not_pie(self):
        h=Host();h.answer([dict(name='A',kwh=4,price=8),dict(name='Adjustment',kwh=-1,price=-2)]);self.assertEqual(h.widgets['total'],'3.00 kWh');self.assertEqual(h.charts[-1][1]['value'],0);self.assertIn('-1.00',h.widgets['status'])
    def test_missing_price_stays_unknown_without_fabricating_zero(self):
        h=Host();h.answer([dict(name='A',kwh=2)]);self.assertEqual(h.widgets['price'],'-- DKK');self.assertIn('-- DKK',h.charts[-1][0]['detail'])
    def test_zero_price_is_known(self):
        h=Host();h.answer([dict(name='A',kwh=2,price=0)]);self.assertEqual(h.widgets['price'],'0.00 DKK')
    def test_empty_result_has_no_invented_price(self):
        h=Host();h.answer([]);self.assertEqual(h.charts[-1],[]);self.assertEqual(h.widgets['total'],'0.00 kWh');self.assertEqual(h.widgets['price'],'-- DKK')
    def test_twenty_categories_and_unicode_are_preserved(self):
        h=Host();h.answer([dict(name='Køkken '+str(i),kwh=i+1,price=i) for i in range(20)]);self.assertEqual(len(h.charts[-1]),20)
    def test_too_many_categories_fails_without_partial_chart(self):
        h=Host();h.answer([dict(name=str(i),kwh=1) for i in range(33)]);self.assertEqual(h.charts[-1],[]);self.assertIn('Ingen gyldige',h.widgets['status'])
    def test_invalid_numeric_values_are_rejected(self):
        for value in (True,'12',float('inf'),float('nan')):
            h=Host();h.answer([dict(name='A',kwh=value)]);self.assertEqual(h.charts[-1],[])
    def test_wrong_id_or_tag_cannot_replace_data(self):
        h=Host();h.answer(id=999);self.assertEqual(h.charts[-1],[]);h.answer(tag='other');self.assertEqual(h.charts[-1],[]);h.answer();self.assertEqual(h.widgets['total'],'2.00 kWh')
    def test_hide_cancels_and_ignores_late_reply(self):
        h=Host();h.plugin.hide(h.ctx);h.answer();self.assertEqual(h.cancelled,[1]);self.assertEqual(h.charts[-1],[]);h.event('tick',now_ms=999999);self.assertEqual(len(h.requests),1)
    def test_period_change_cancels_and_rejects_old_result(self):
        h=Host();old=dict(h.requests[-1]);h.event('month');self.assertEqual(h.cancelled,[1]);self.assertEqual(h.requests[-1]['period'],'month');h.event('consumption',id=old['id'],tag=old['tag'],status=200,json={});self.assertEqual(h.widgets['total'],'-- kWh')
    def test_previous_and_current_navigation(self):
        h=Host();h.answer();h.event('previous');self.assertEqual(h.requests[-1]['shift'],-1);h.answer(data={'from':'2026-11-08','to':'2026-11-09','is_current':False});h.event('current');self.assertEqual(h.requests[-1]['date'],'current');self.assertEqual(h.requests[-1]['shift'],0)
    def test_next_current_period_does_not_request_future_data(self):
        h=Host();h.answer();h.event('next');self.assertEqual(len(h.requests),1)
    def test_error_keeps_same_period_data_and_says_stale(self):
        h=Host();h.answer();h.event('refresh');h.answer(status=500,json=None);self.assertEqual(h.widgets['total'],'2.00 kWh');self.assertIn('tidligere data',h.widgets['status'])
    def test_navigation_clears_old_period_before_error(self):
        h=Host();h.answer();h.event('month');h.answer(status=500,json=None);self.assertEqual(h.widgets['total'],'-- kWh');self.assertEqual(h.charts[-1],[])
    def test_refresh_interval_does_not_poll_while_pending(self):
        h=Host();h.event('tick',now_ms=10000);self.assertEqual(len(h.requests),1);h.answer(now_ms=10000);h.event('tick',now_ms=69999);self.assertEqual(len(h.requests),1);h.event('tick',now_ms=70000);self.assertEqual(len(h.requests),2)
    def test_currency_is_displayed_without_conversion(self):
        h=Host(currency='EUR',language='en');h.answer();self.assertEqual(h.widgets['price'],'4.00 EUR');self.assertIn('Updated',h.widgets['status'])
    def test_after_completed_request_nil_id_is_not_an_answer(self):
        h=Host();h.answer();before=h.widgets['total'];h.event('consumption',tag=h.requests[-1]['tag'],status=200,json={});self.assertEqual(h.widgets['total'],before)
if __name__=='__main__':unittest.main()
