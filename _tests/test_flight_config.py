import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_tools'))
import hn

class FlightConfigurationTests(unittest.TestCase):
    def test_bounded_nonsecret_settings_pass(self):
        value={'latitude':55.6761,'longitude':12.5683,'radius_km':30,'language':'en','show_ground':False}
        self.assertEqual(hn.flight_configuration(value),value)

    def test_credentials_unknown_values_null_and_bad_types_are_rejected(self):
        for value in [[],{'token':'synthetic'},{'latitude':None},{'latitude':True},{'latitude':float('nan')},
                      {'longitude':181},{'refresh_seconds':1},{'max_aircraft':2.5},{'show_ground':1},{'language':'fr'}]:
            with self.subTest(value=value):
                with self.assertRaises(hn.InvalidPlugin):hn.flight_configuration(value)

    def test_only_flight_provider_is_accepted_by_device_subset(self):
        manifest,files=hn.validate(ROOT/'flight');hn.device_subset(manifest,files)
        manifest['permissions']['network']=['https://example.org']
        with self.assertRaises(hn.InvalidPlugin):hn.device_subset(manifest,files)
        manifest,files=hn.validate(ROOT/'spotify')
        with self.assertRaises(hn.InvalidPlugin):hn.device_subset(manifest,files)

    def test_media_requires_exact_capability_before_pairing(self):
        from unittest.mock import patch,Mock
        from types import SimpleNamespace
        manifest,_=hn.validate(ROOT/'flight')
        for capability in (None,False,True,0,'1',2):
            stream=Mock();peer=Mock();peer.hello.return_value={'capabilities':{'httpFlight':True,'settingsSchema':1,'flightMedia':capability}}
            args=SimpleNamespace(port='synthetic',command='test',config_values=None)
            with patch.object(hn,'open_serial',return_value=stream),patch.object(hn,'Device',return_value=peer):
                with self.assertRaisesRegex(hn.DeviceError,'map/logo'):hn.run_device(args,b'fixture',manifest)
            peer.pair.assert_not_called();peer.upload.assert_not_called();stream.close.assert_called_once()

    def test_media_origins_are_exact_and_ordered(self):
        import copy
        manifest,files=hn.validate(ROOT/'flight')
        for origins in ([*reversed(manifest['permissions']['network'])],manifest['permissions']['network'][:2],['https://opendata.adsb.fi','https://example.org']):
            bad=copy.deepcopy(manifest);bad['permissions']['network']=origins
            with self.assertRaises(hn.InvalidPlugin):hn.device_subset(bad,files)
        manifest['permissions']['network']=['https://opendata.adsb.fi'];hn.device_subset(manifest,files)
