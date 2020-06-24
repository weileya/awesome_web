# import asyncio
# import orm
# from models import User, Blog, Comment

# async def test():
#     await orm.create_pool(loop=loop,user='root', password='root', database='awesome')
#     u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
#     await u.save()


# if __name__ == '__main__':
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(test())
#         print('Test finished.')
#         loop.close()



# def say_hello(*args):
#     print('hello {0}'.format(args))

# # 通过位置传值
# say_hello('jack', 'tom')

# def func_b(**kwargs):
#     print(kwargs)

# # 通过关键字传值
# func_b(a=1, b=2)

# import time

# def timmer(fun1):
#     def wrapper(*args,**kwargs):
#         start_time=time.time()
#         res=fun1(*args,**kwargs)
#         stop_time=time.time()
#         print('run time is %s' %(stop_time-start_time))
#         return res
#     return wrapper

# @timmer
# def foo():
#     time.sleep(3)
#     print('from foo')

# @timmer
# def foo1():
#     time.sleep(5)
#     print('from foo1')

# foo()
# foo1()
#-*- coding:utf-8 -*-
# def decorator(func):
#     def inner_function():
#         pass
#     return inner_function

# @decorator
# def func():
#     pass

# print(func.__name__)
#inner_function
# from functools import wraps

# def decorator(func):
#     @wraps(func) 
#     def inner_function():
#         pass
#     return inner_function

# @decorator
# def func():
#     pass

# print(func.__name__)
#func
#@wraps：避免被装饰函数自身的信息丢失


# def makebold(f):
#     return lambda:'<b>'+f()+'</b>'
# def makeitalic(f):
#     return lambda:'<i>'+f()+'</i>'
# def makeitalic1(f):
#     return lambda:'<strong>'+f()+'</strong>'

# @makebold
# @makeitalic1
# @makeitalic
# def say():
#     return 'hello'

# print(say())
# #<b><strong><i>hello</i></strong></b>
# #多个装饰器的执行顺序：是从近到远依次执行。


# import time

# def deco01(func):
#     def wrapper(*args, **kwargs):
#         print("this is deco01")
#         startTime = time.time()
#         func(*args, **kwargs)
#         endTime = time.time()
#         msecs = (endTime - startTime)*1000
#         print("time is %d ms" %msecs)
#         print("deco01 end here")
#     return wrapper

# def deco02(func):
#     def wrapper(*args, **kwargs):
#         print("this is deco02")
#         func(*args, **kwargs)
#         print("deco02 end here")
#     return wrapper

# @deco01
# @deco02
# def func(a,b):
#     print("hello，here is a func for add :")
#     time.sleep(1)
#     print("result is %d" %(a+b))

# if __name__ == '__main__':
#     f = func
#     f(3,4)

'''
this is deco01
this is deco02
hello,here is a func for add :
result is 7
deco02 end here
time is 1032 ms
deco01 end here
'''
#多个装饰器执行的顺序就是从最后一个装饰器开始，执行到第一个装饰器，再执行函数本身。
# d = {
#     'id':1,
#     'b':2,
#     'c':2,
#     'student':{
#         'name':'tom',
#         'age':25
#         }
#     }
# print(d['id'])
# print(d['student']['name'])

# def hello(self):
#     self.name = 10
#     print("hello world")

# t = type("hello",(),{"a":1,"hello":hello})
# # class hello():
# #     cls.a=1
# #     cls.hello=hello

# print(t)
# T = t()
# print(T.a)
# T.hello()
# print(T.name)

# 协程例子
# def consumer():
#     r = ''
#     while True:
#         n = yield r
#         if not n:
#             return
#         print('[CONSUMER] Consuming %s...' % n)
#         r = '200 OK'

# def produce(c):
#     c.send(None)    # 如果send不携带参数，那么send(None) 和next()的作用的相同的,启动生成器
#     n = 0
#     while n < 5:
#         n = n + 1
#         print('[PRODUCER] Producing %s...' % n)
#         r = c.send(n)    # 相当于next()，不过是传了参数
#         print('[PRODUCER] Consumer return: %s' % r)
#     c.close()

# c = consumer()
# produce(c)
# 注意到consumer函数是一个generator，把一个consumer传入produce后：
# 首先调用c.send(None)启动生成器；
# 然后，一旦生产了东西，通过c.send(n)切换到consumer执行；
# consumer通过yield拿到消息，处理，又通过yield把结果传回；
# produce拿到consumer处理的结果，继续生产下一条消息；
# produce决定不生产了，通过c.close()关闭consumer，整个过程结束。
# 整个流程无锁，由一个线程执行，produce和consumer协作完成任务，所以称为“协程”，而非线程的抢占式多任务。


# def fun_inner():
#     i = 0
#     while True:
#         i = yield i

# def fun_outer():
#     a = 0
#     b = 1
#     inner = fun_inner()
#     inner.send(None)
#     while True:
#         a = inner.send(b)
#         b = yield a

# if __name__ == '__main__':
#     outer = fun_outer()
#     outer.send(None)
#     for i in range(5):
#         print(outer.send(i))

# def fun_inner():
#     i = 0
#     while True:
#         i = yield i

# def fun_outer():
#     yield from fun_inner()

# if __name__ == '__main__':
#     outer = fun_outer()
#     outer.send(None)
#     for i in range(5):
#         print(outer.send(i))

# def my_generator():
#     for i in range(5):
#         if i==2:
#             return '我被迫中断了'
#         else:
#             yield i
 
# def wrap_my_generator(generator):  #定义一个包装“生成器”的生成器，它的本质还是生成器
#     result=yield from generator    #自动触发StopIteration异常，并且将return的返回值赋值给yield from表达式的结果，即result
#     print(result)
 
# def main(generator):
#     for j in generator:
#         print(j)
 
# g=my_generator()
# wrap_g=wrap_my_generator(g)
# main(wrap_g)  #调用


# import asyncio

# @asyncio.coroutine
# def wget(host):
#     print('wget %s...' % host)
#     connect = asyncio.open_connection(host, 80)
#     reader, writer = yield from connect
#     header = 'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % host
#     writer.write(header.encode('utf-8'))
#     yield from writer.drain()
#     while True:
#         line = yield from reader.readline()
#         if line == b'\r\n':
#             break
#         print('%s header > %s' % (host, line.decode('utf-8').rstrip()))
#     # Ignore the body, close the socket
#     writer.close()

# loop = asyncio.get_event_loop()
# tasks = [wget(host) for host in ['www.sina.com.cn', 'www.sohu.com', 'www.163.com']]
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()

from PIL import Image
img = Image.open('f:/python/awesome-python3-webapp/www/static/img/user.png')
# img.show()
print(type(img))
img.save('f:/python/awesome-python3-webapp/www/static/img/111.png','jpeg')
