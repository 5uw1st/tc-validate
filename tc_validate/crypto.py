#!usr/bin/env python3
# -*- coding:utf-8 _*-

import base64
import ctypes

import execjs


def int_overflow(val):
    maxint = 2147483647
    if not -maxint - 1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val


def unsigned_right_shift(n, i):
    if n < 0:
        n = ctypes.c_uint32(n).value
    if i < 0:
        return -int_overflow(n << abs(i))
    return int_overflow(n >> i)


def _encode_four_chars(n):
    _ret = ""
    for i in range(4):
        c = i * 8
        cv = n >> c
        _r = cv & 255
        _ret += chr(_r)
    return _ret


def _char_to_digit(chars):
    t = 0
    for i, c in enumerate(chars):
        _r = ord(c)
        r = _r << (8 * i)
        t |= r
    return t


_encode_js = """
function get_ur(r, u){
    var e = 2654435769,
    o = 84941944608,
    i = 0,
    rn = [
        1500147022,
        1411657020,
        1344087856,
        1734894922
    ];
    while(i!=o){
        _a = u << 4;
        _b = u >>> 5;
        t0 = (_a ^ _b) + u;
        _f1 = i & 3;
        if(_f1==1){
            t1 = i + (rn[_f1] + 2171143);
        }else if(_f1==2){
            t1 = i + (rn[_f1] + 2565928);
        }else{
            t1 = i + (rn[_f1]);
        }
        r += t0 ^ t1;
        i += e;

        _c = r << 4;
        _d = r >>> 5;
        t2 = (_c ^ _d) + r;
        _f2 = (i >>> 11) & 3;
        if(_f2 == 1){
            t3 = i + (rn[_f2] + 2171143);
        }else if(_f2 == 2){
            t3 = i + (rn[_f2] + 2565928);
        }else{
            t3 = i + (rn[_f2]);
        }
        u += t2 ^ t3;
    }

    return [r, u];
}
"""

js_func = execjs.compile(_encode_js)


def _encode_digit(us):
    _r, _u = us
    r, u = js_func.call('get_ur', _r, _u)
    return r, u


def _full_chars(c, flag=False):
    if not c:
        return ""
    r = 24 % len(c)
    if r > 14 or flag:
        _r = 24 - r
        c += _r * " "
        return c
    return False


def _encode(data):
    length = len(data)
    ds = length // 8
    _ret = ""
    for i in range(ds):
        _us = data[i * 8:(i + 1) * 8]
        u0 = _us[0:4]
        u1 = _us[4:8]
        _u0 = _char_to_digit(u0)
        _u1 = _char_to_digit(u1)
        us = [_u0, _u1]
        r, u = _encode_digit(us=us)
        mid = _encode_four_chars(r) + _encode_four_chars(u)
        _ret += mid
    ret = base64.b64encode(_ret.encode(encoding="latin1")).decode()
    return ret


def encrypt(record_data):
    d = {"cd": ""}
    t = '{"cd":['
    r = ""
    u = True
    for e in record_data:
        if not e:
            continue
        c, i, f = e
        if u:
            t += ","
            u = False
        if f != 2:
            if not c:
                t += "null"
            elif isinstance(c, int):
                t += str(c or 0)
            elif f == 1:
                t += c
            else:
                t += '"{0}"'.format(t)
            if isinstance(i, int):
                t += "," + str(i or 0)

            a = _full_chars(t)
            if a:
                r += _encode(a)
                t = ""
        else:
            s = _full_chars(t, True)
            _t = _encode(s) if s else ""
            r += _t + c
            t = ""
    t += "],"
    r += _encode(_full_chars(t, True))
    d["cd"] = r
    return d


if __name__ == '__main__':
    _n = -14034538812
    ret1 = _encode_four_chars(n=_n)
    print(ret1)

    ret2 = _char_to_digit('//xu')
    ret3 = _char_to_digit('i.pt')
    print(ret2, ret3)

    ret = unsigned_right_shift(-1, 20)
    print(ret)

    _u = [1768386412, 1898852974]
    # 1933983141,4588192872
    ret = _encode_digit(_u)
    print(ret)

    d = ',00,0,,,,,"Win7"        '
    print(_encode(data=d))
