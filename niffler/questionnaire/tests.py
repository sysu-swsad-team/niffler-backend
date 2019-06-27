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

    def test_ProfileView_get(self):
        response = self.client.get('/questionnaire/profile/')
        self.assertEquals(response.status_code, 201)
        self.client.force_authenticate(self.user1)
        response = self.client.get('/questionnaire/profile/')
        self.assertEquals(response.status_code, 200)
        self.client.force_authenticate(None)
        response = self.client.get('/questionnaire/profile/')
        self.assertEquals(response.status_code, 201)