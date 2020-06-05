#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Configuration
'''

__author__ = 'Michael Liao'

import config_default

class Dict(dict):
    '''
    Simple dict but support access as x.y style.
    '''
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

# 作用就是两个不同的字典进行组合，两个都有的k,就取第二个字典的值；第一个有第二个没有的组合在一起，第一个没有，第二个有的，舍弃。
def merge(defaults, override):  
    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])  # 递进回归应用，(v, override[k])如果相同继续调用本方法，一直到括号中两个值不相等，然后取后者
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r

def toDict(d):   # 方法的作用是可以使用这样的去数据形式D.item
    D = Dict()   # Dict()是一个类，k相当于Dict类的属性，v为属性的值，所以支持D.k的形式
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D

# d = {'id':2,'name':'tom','age':25}
# D = toDict(d)
# print(D)
# print(D.age,D.name)   # D其实是一个类，所以可以这样取值
# print(d.age,d.name)  这一句会报错，字典类型不能这样取值

# default1 = {
#     'test':2222,
#     'id':2,
#     'student':{
#         'name':'tom',
#         'age':25
#         }
#     }
# default2 = {
#     'id':3,
#     'student':{
#         'name':'jerry',
#         'age':26
#         },
#     # 'test2':555
#     }
# r = merge(default1,default2)
# print(r)


configs = config_default.configs

try:
    import config_override
    configs = merge(configs, config_override.configs)
except ImportError:
    pass
# print(configs)
configs = toDict(configs)
# print(configs)