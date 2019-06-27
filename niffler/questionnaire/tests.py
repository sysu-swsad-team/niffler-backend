from django.test import TestCase
from .models import *
from django.test import Client
# Create your tests here.

class TaskTestCase(TestCase):
    
    def setUp(self):
        # 环境构造
        User.objects.create(
            email="tu1",
            password="tu1"
        )

        # task = Task.objects.create(
        #     title='test1'
        # )


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




