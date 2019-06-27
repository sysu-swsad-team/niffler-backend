from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import *
from django.test import Client
# Create your tests here.

class TaskTestCase(APITestCase):
    
    def setUp(self):
        # 环境构造
        # User.objects.create(
        #     email="tu1",
        #     password="tu1"
        # )

        # task = Task.objects.create(
        #     title='test1'
        # )
        self.user1 = User.objects.create_user(username='user1',
                                              email='user1@niffler.com',
                                              password='user1')
        self.user2 = User.objects.create_user(username='user2',
                                              email='user2@niffler.com',
                                              password='user2')
        Profile.objects.create(user=self.user1,
                               phone='',
                               balance=10000,
                               avatar='')
        Profile.objects.create(user=self.user2,
                               phone='',
                               balance=10000,
                               avatar='')


    def test_retrieve(self):
        # 测试my_func方法
        # response_login = self.client.post(path='/login/', data={'email':'tu1', 'password':'tu1'}, content_type='application/json')
        users = User.objects.all()
        print(users)
        # self.assertEqual(response_login.status_code, 200)
        # response_succ = self.client.get('/questionnaire/task/1/')
        # self.assertEqual(response_succ.status_code, 200)
        # response_failed = self.client.get('/questionnaire/task/2/')
        # self.assertEqual(response_failed.status_code, 201)

    def test_ProfileView_retrieve(self):
        response = self.client.get('/questionnaire/profile/1/')
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/questionnaire/profile/2/')
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/questionnaire/profile/3/')
        self.assertEquals(response.status_code, 404)



    
        
#         """APP用户登录接口成功情况"""
#         # path使用硬编码，不要使用reverse反解析url，以便在修改url之后能及时发现接口地址变化，并通知接口使用人员
#         path = '/api/api-token-auth/'
#         data = {'mobile_phone': '15999999999', 'password': '111111'}
#         response = self.client.post(path, data)
#         # response.data是字典对象
#         # response.content是json字符串对象
#         self.assertEquals(response.status_code,
#                           status.HTTP_200_OK,
#                           '登录接口返回状态码错误: 错误信息: {}'.format(response.content))
#         self.assertIn('token', response.data, '登录成功后无token返回')

#     def test_app_user_login_with_error_pwd(self):
#         path = '/api/api-token-auth/'
#         data = {'mobile_phone': '15999999999', 'password': '123456'}
#         response = self.client.post(path, data)
#         self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertJSONEqual('{"errors":["用户名或密码错误。"]}', response.content)

#     def test_get_app_user_profile_success(self):
#         """成功获取app用户个人信息接口"""
#         path = '/api/account/user/profile/'
#         headers = self.get_headers(user=self.user)
#         response = self.client.get(path, **headers)
#         # 校验一些关键数据即可
#         # 如果是创建新数据，不仅要校验返回的状态码和数据，
#         # 还需要到使用Django ORM去数据库查询数据是否创建成功
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(6, len(response.data))
#         self.assertIn('url', response.data)
#         self.assertIn('mobile_phone', response.data)
#         self.assertIn('avatar', response.data)
#         self.assertIn('company_name', response.data)
#         self.assertIn('username', response.data)
#         self.assertIn('is_inviter', response.data)

#     def test_get_app_user_profile_without_token(self):
#         """不传token请求获取用户信息接口"""
#         path = '/api/account/user/profile/'
#         response = self.client.get(path)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)