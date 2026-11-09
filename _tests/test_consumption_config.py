import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_tools'))
import hn
from consumption_config import validate
class ConsumptionConfigurationTests(unittest.TestCase):
 def setUp(self):
  self.config={'country':'GLOBAL','language':'da','currency':'DKK','refresh_seconds':60,'api_origin':'http://192.168.1.10:8111'}
 def test_explicit_rfc1918_origins_only(self):
  for origin in ['http://10.0.0.1','http://172.16.1.10:65535','http://192.168.1.10:8111']:
   self.assertEqual(validate(dict(self.config,api_origin=origin))['api_origin'],origin)
  for origin in ['',None,123,'http://127.0.0.1','https://192.168.1.10','http://192.168.1.10/path','http://192.168.1.10?x=1','http://user@192.168.1.10','http://192.168.1.10:0','http://192.168.1.10:65536','http://192.168.1.10:080','http://192.168.01.10','http://192.168.1.0','http://192.168.1.255','http://localhost','http://[::1]','http://172.32.0.1','http://169.254.1.1']:
   with self.subTest(origin=origin),self.assertRaises(ValueError):validate(dict(self.config,api_origin=origin))
 def test_closed_types_and_limits(self):
  for key,value in [('country','XX'),('language','xx'),('currency','XXX'),('refresh_seconds',True),('refresh_seconds',30.0),('refresh_seconds',29),('refresh_seconds',3601),('extra',1)]:
   with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate(dict(self.config,**{key:value}))
 def test_only_named_service_grant_is_accepted(self):
  manifest,files=hn.validate(ROOT/'consumption');hn.device_subset(manifest,files)
  for grant in [[],['http://192.168.1.10'],['home-api:consumption','https://example.org']]:
   bad=copy.deepcopy(manifest);bad['permissions']['network']=grant
   with self.assertRaises(hn.InvalidPlugin):hn.device_subset(bad,files)
  bad=copy.deepcopy(manifest);bad['id']='housenimble.counter'
  with self.assertRaises(hn.InvalidPlugin):hn.device_subset(bad,files)
 def test_exact_capabilities_required_before_pairing(self):
  manifest,_=hn.validate(ROOT/'consumption')
  for key in ['consumptionData','pieChart']:
   for value in [None,False,True,0,'1',2]:
    caps={'consumptionData':1,'pieChart':1,'settingsSchema':1};caps[key]=value
    stream=Mock();peer=Mock();peer.hello.return_value={'capabilities':caps}
    args=SimpleNamespace(port='synthetic',command='test',config_values=self.config)
    with patch.object(hn,'open_serial',return_value=stream),patch.object(hn,'Device',return_value=peer):
     with self.assertRaises(hn.DeviceError):hn.run_device(args,b'fixture',manifest)
    peer.pair.assert_not_called();peer.upload.assert_not_called()
