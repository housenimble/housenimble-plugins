"""Public Consumption configuration policy. SPDX-License-Identifier: MIT.

Copyright (c) 2026 HouseNimble contributors.

MIT License

Copyright (c) 2026 HouseNimble plugin-template contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import ipaddress
import re

def validate(values):
    expected={'country','language','api_origin','currency','refresh_seconds'}
    if not isinstance(values,dict) or set(values)!=expected:
        raise ValueError('Invalid Consumption settings')
    if values['country'] not in ('GLOBAL','DK','SE','DE') or values['language'] not in ('da','en') or values['currency'] not in ('DKK','SEK','NOK','EUR','USD'):
        raise ValueError('Invalid Consumption settings')
    refresh=values['refresh_seconds']
    if type(refresh) is not int or not 30<=refresh<=3600:
        raise ValueError('Invalid Consumption refresh interval')
    origin=values['api_origin']
    match=re.fullmatch(r'http://([0-9]{1,3}(?:\.[0-9]{1,3}){3})(?::([1-9][0-9]{0,4}))?',origin) if isinstance(origin,str) and len(origin)<=64 else None
    if not match:raise ValueError('Set an explicit local IPv4 Home API origin without path or credentials')
    try:address=ipaddress.IPv4Address(match[1])
    except ipaddress.AddressValueError:raise ValueError('Invalid Home API address') from None
    if str(address)!=match[1] or not any(address in ipaddress.ip_network(net) for net in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16')) or int(address)&255 in (0,255) or (match[2] is not None and int(match[2])>65535):
        raise ValueError('Home API must use an explicit RFC1918 IPv4 address and valid port')
    return values
