#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio

from coroweb import get, post
from aiohttp import web
from models import User, Comment, Blog, next_id
from apis import APIValueError, APIResourceNotFoundError,APIError,APIPermissionError,Page
from config import configs
import markdown2
# @get('/')
# async def index(request):
#     users = await User.findAll()
#     return {
#         '__template__': 'test.html',
#         'users': users
#     }
COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs['session']['secret']
# _COOKIE_KEY = configs.session.secret
# print(_COOKIE_KEY)
# async def check_admin(request):   # 在没有加入auth_factory middlewares前自己改正的
#     # print("1111")
#     # print(request.cookies)
#     # print(request.cookies[COOKIE_NAME])
#     # print(dir(request))
#     cookie_str = request.cookies[COOKIE_NAME]
#     request.__user__ = await cookie2user(cookie_str)
#     # print(request.__user__)
#     # print(type(request.__user__))
#     if request.__user__ is None or not request.__user__.admin:
#         raise APIPermissionError()
def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()

def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as _:
        pass
    if p < 1:
        p = 1
    return p

def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    # print(expires)
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    # print(s)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

# @asyncio.coroutine
async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

# @get('/')     # 首页，写死的数据
# def index(request):
#     summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
#     blogs = [
#         Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
#         Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
#         Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
#     ]
#     return {
#         '__template__': 'blogs.html',
#         'blogs': blogs
#     }

@get('/')   # 首页
async def index(*, page='1'):
    # page_index = get_page_index(page)
    # num = await Blog.findNumber('count(id)')
    # page1 = Page(num,page_index)
    # if num == 0:
    #     blogs = []
    # else:
    #     blogs = await Blog.findAll(orderBy='created_at desc', limit=(page1.offset, page1.limit))
    return {
        '__template__': 'blogs.html',
        # 'page': page1,
        # 'blogs': blogs
        'page_index': get_page_index(page)
    }

@get('/manage/')    # 管理页面的入口
def manage():
    return 'redirect:/manage/comments'

# 日志模块接口
@get('/manage/blogs')   # 日志管理列表页面，只展示第一页
def manage_blogs(*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }

@get('/manage/blogs/create')       # 添加一个日志
def manage_create_blog():
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }

@post('/api/blogs')    # 添加日志接口
async def api_create_blog(request, *, name, summary, content):
    # print(request)
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip())
    await blog.save()
    return blog

@get('/api/blogs')   # 该接口只返回数据，不用指向一个页面,与/mangage/blogs/接口配合，该接口返回数据，/mangage/blogs/负责展示出来
async def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)


@get('/api/blogs/{id}')    # 该接口用于返回/manage/blogs/edit修改接口的数据
async def api_get_blog(*, id):
    blog = await Blog.find(id)
    return blog

@get('/blog/{id}')   # 单个日志页面,填写评论页面
async def get_blog(id):
    blog = await Blog.find(id)
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog_comment.html',
        'blog': blog,
        'comments': comments
    }

@post('/api/blogs/{id}/comments')   # 添加评论接口
async def api_comment_blog(id,request, *, content):
    # check_admin(request)
    user = request.__user__
    if user is None:
        raise APIPermissionError('Please signin first.')
    blog = await Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('blog is not found.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    comment = Comment(blog_id=blog.id,user_id=user.id, user_name=user.name, user_image=user.image,content=content.strip())
    await comment.save()
    return comment

@get('/manage/blogs/edit')   # 编辑日志页面
def manage_edit_blog(*, id):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s' % id
    }

@post('/api/blogs/{id}')   # 编辑日志接口
async def api_update_blog(id, request, *, name, summary, content):
    check_admin(request)
    blog = await Blog.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    await blog.update()
    return blog

@post('/api/blogs/{id}/delete')   # 删除日志接口
async def api_delete_blog(request, *, id):
    check_admin(request)
    blog = await Blog.find(id)
    await blog.remove()
    return dict(id=id)

# 评论模块接口
@get('/manage/comments')   # 评论管理列表页面，只展示第一页
def manage_comments(*, page='1'):
    return {
        '__template__': 'manage_comments.html',
        'page_index': get_page_index(page)
    }

@get('/api/comments')   # 该接口只返回数据，不用指向一个页面,与/mangage/comments/接口配合，该接口返回数据，/mangage/comments/负责展示出来
async def api_comments(*, page='1'):
    page_index = get_page_index(page)
    num = await Comment.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comment=())
    comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comment=comments)

@post('/api/comments/{id}/delete')   # 删除评论接口
async def api_delete_comment(request, *, id):
    check_admin(request)
    comment = await Comment.find(id)
    if comment is None:
        raise APIResourceNotFoundError('Comment')
    await comment.remove()
    return dict(id=id)


# 用户管理模块接口
@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')
@post('/api/users')    # 用户提交信息注册接口
async def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }

@post('/api/authenticate')     # 登录验证接口
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@get('/manage/users') # 用户管理页面
def manage_users(*, page='1'):
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page)
    }

@get('/api/users')   # 获取用户信息，返回给管理页面
async def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    num = await User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)

@get('/user/{id}')   # 单个用户查看页面
async def get_user(id):
    user = await User.find(id)
    return {
        '__template__': 'user.html',
        'user': user
    }

@get('/api/users/{id}')    # 该接口用于返回/manage/users/edit修改接口的数据
async def api_get_user(*, id):
    user = await User.find(id)
    return user

@get('/manage/users/edit')   # 管理员编辑用户页面
def manage_edit_user(*, id):
    return {
        '__template__': 'manage_user_edit.html',
        'id': id,
        'action': '/api/users/%s' % id
    }

@get('/api/user/userinfo')   #修改个人信息时获取个人信息
def user_getinfo(request):
    user = request.__user__
    return user


@get('/user/edit')   # 个人修改信息
def edit_user():
    # user = request.__user__
    return {
        '__template__': 'user_edit.html',
        # 'user':user,
        'action': '/api/userinfo' 
    }

@post('/api/userinfo')   # 个人编辑用户接口
async def api_update_userinfo(request, *, name, email, passwd):
    # check_admin(request)
    user = request.__user__
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email', 'email cannot be empty.')
    if passwd and _RE_SHA1.match(passwd):
        uid = user.id
        sha1_passwd = '%s:%s' % (uid, passwd)
        user.passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest()
    user.name = name.strip()
    user.email = email.strip()
    await user.update()
    return user

@post('/api/users/{id}')   # 管理员编辑用户接口
async def api_update_user(id, request, *, name, email, admin):
    check_admin(request)
    user = await User.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not email or not email.strip():
        raise APIValueError('email', 'email cannot be empty.')
    if not admin:
        raise APIValueError('admin', 'admin cannot be empty.')
    user.name = name.strip()
    user.email = email.strip()
    user.admin = admin
    await user.update()
    return user

@get('/signout')   # 注销登录状态
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r




