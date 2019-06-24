import django_filters
from django.shortcuts import render
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import Http404
from django.http import HttpResponse
from django.contrib.auth import *
from django.contrib.auth.models import User#, Group
from django_filters.rest_framework import DjangoFilterBackend
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import action
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 

from .models import *
from django.db.models import Q
from .serializers import *

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone

import json
import os,smtplib
from PIL import Image
import hashlib
from string import Template
from django.core.mail import EmailMultiAlternatives
from datetime import datetime, timedelta
import random

from rest_framework.decorators import api_view
from .swagger_schema import CustomSchema

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
        
# class UserFilter(django_filters.rest_framework.FilterSet):
#     class Meta:
#         model = User
#         fields = ['username']

# # ViewSets 定义视图行为。
# class UserViewSet(viewsets.ModelViewSet):
#     """
#     允许用户查看或编辑的 API 端点。
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#     filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
#     filter_class = UserFilter


class Signup(APIView):
    schema = CustomSchema()
    response_data = {}

    @csrf_exempt 
    def post(self, request, format=None):
        """
        desc: 用户注册
        ret: code, msg
        err: code, msg
        input:
        - name: name
          desc: 名字
          type: string
          required: true
          location: form
        - name: stuId
          desc: 学号
          type: string
          required: true
          location: form
        - name: birth
          desc: 生日
          type: string
          required: true
          location: form
        - name: sex
          desc: 性别
          type: string
          required: true
          location: form
        - name: grade
          desc: 年级
          type: string
          required: true
          location: form
        - name: major
          desc: 专业
          type: string
          required: true
          location: form
        - name: email
          desc: 邮箱
          type: string
          required: true
          location: form
        - name: password
          desc: 密码
          type: string
          required: true
          location: form
        - name: code
          desc: 验证码
          type: string
          required: true
          location: form
        """
        # req = request.data
        req = json.loads(request.body)

        first_name = req.get('name')
        stuId = req.get('stuId')
        birth = req.get('birth')
        sex = req.get('sex')
        grade = req.get('grade')
        major = req.get('major')
        email = req.get('email')
        password = req.get('password')
        verification_code = req.get('code')
        print(email)
        try:
            # profile = Profile.objects.get(verification_code=verification_code)
            emailverify = EmailVerify.objects.get(email=email)
        except:
            response_data = {
                "msg" : "未为此邮箱生成验证码"
            }
            return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)
        
        if emailverify.verification_code == verification_code:
            if timezone.now() > emailverify.code_expires: 
                emailverify.delete()
                response_data = {
                    "msg" : "验证码过期，请重新获取"
                }
                return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)

            else:
                try:
                    new_user = User.objects.create(
                        username=email,
                        email=email,
                        first_name=first_name
                    )
                    new_user.set_password(password)
                    new_user.save()
                except:
                    response_data = {
                        "msg" : "此用户已经注册或邮箱和姓名格式不对"
                    }
                    return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)

                try:
                    profile = Profile.objects.create(
                        user=new_user,
                        balance=0,
                        stuId=stuId,
                        birth=birth,
                        sex=sex,
                        grade=grade,
                        major=major
                    )
                except:
                    new_user.delete()
                    response_data = {
                        "msg" : "用户 profile 字段格式不对"
                    }
                    return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)

                emailverify.delete()
                response_data = {
                    "msg" : "注册用户成功"
                }
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)

        response_data = {
            "msg" : "验证码错误"
        }
        return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)
        # if profile.user.is_active == False:
        #     if timezone.now() > profile.code_expires:   
        #         profile.user.delete()
        #         profile.delete()
        #         response_data = {
        #             "msg" : "验证码过期"
        #         }
        #         return HttpResponse(json.dumps(response_data), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        #     else: #Activation successful
        #         profile.user.is_active = True
        #         profile.user.set_password(password)
        #         profile.user.first_name = first_name
        #         profile.user.save()

        #         profile.stuId = stuId
        #         profile.birth = birth
        #         profile.sex = sex
        #         profile.grade = grade
        #         profile.major = major
        #         profile.save()

        #         response_data = {
        #             "msg" : "注册用户成功"
        #         }
        #         return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
        
        # #If user is already active, simply display error message
        # else:
        #     response_data = {
        #         "msg" : "该用户已经注册"
        #     }
        #     return HttpResponse(json.dumps(response_data), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @csrf_exempt 
    def get(self, request, format=None):
        """
        desc: 邮箱验证
        ret: code, msg
        err: code, msg
        input:
        - email: email
          desc: 邮箱
          type: string
          required: true
          location: path
        """
        email = request.GET['email']
        # print(email)  
        if email is not None and email is not '':
            try:
                new_emailverify = EmailVerify.objects.create(
                    email=email
                )
                # new_user = User.objects.create(
                #     username=email,
                #     email=email,
                #     is_active=False
                # )
            except:
                response_data = {
                    "msg" : "已经发送验证码此邮箱中"
                }
                return HttpResponse(json.dumps(response_data), 
                                    status=status.HTTP_201_CREATED)

            ''' 随机生成6位的验证码 '''
            code_list = []
            for i in range(10): # 0-9数字
                code_list.append(str(i))
            for i in range(65, 91): # A-Z
                code_list.append(chr(i))
            for i in range(97, 123): # a-z
                code_list.append(chr(i))

            myslice = random.sample(code_list, 6)  # 从list中随机获取6个元素，作为一个片断返回
            verification_code = ''.join(myslice) # list to string

            new_emailverify.verification_code = verification_code
            new_emailverify.code_expires=datetime.strftime(
                datetime.now() + timedelta(days=2), "%Y-%m-%d %H:%M:%S")
            new_emailverify.save()
            # profile = Profile.objects.create(
            #     user=new_user,
            #     balance=0,
            #     verification_code=verification_code,
            #     code_expires=datetime.strftime(datetime.now() + timedelta(days=2), "%Y-%m-%d %H:%M:%S")
            # )

            # 发送邮件
            email_subject = '来自 sysu_niffler 的注册确认邮件'
            text_content = '''欢迎注册 sysu_niffler, 您的6位验证码是 %s''' % \
                                                        verification_code
            try:
                msg = EmailMultiAlternatives(email_subject, 
                                             text_content, 
                                             settings.EMAIL_HOST_USER, [email])
                msg.send()
            except:
                response_data = {
                    "msg" : "验证码发送失败"
                }
                new_emailverify.delete()
                return HttpResponse(json.dumps(response_data), 
                                    status=status.HTTP_201_CREATED)

            response_data = {
                "msg" : "发送验证码成功"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_200_OK)
        
        response_data = {
            "msg" : "请输入邮箱地址"
        }
        return HttpResponse(json.dumps(response_data), 
                            status=status.HTTP_201_CREATED)
        
      
# 验证邮箱
# @csrf_exempt
# def email_verify(request, key):
#     response_data = {}
#     activation_expired = False
#     already_active = False
#     # print(key)
#     try:
#         profile = Profile.objects.get(verification_code=key)
#     except:
#         response_data = {
#             "msg" : "验证码错误"
#         }
#         return HttpResponse(json.dumps(response_data), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#     if profile.user.is_active == False:
#         if timezone.now() > profile.code_expires:
#             activation_expired = True #Display: offer the user to send a new activation link
#             id_user = profile.user.id
#             response_data = {
#                 "msg" : "验证码过期"
#             }
#             return HttpResponse(json.dumps(response_data), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         else: #Activation successful
#             profile.user.is_active = True
#             profile.user.save()
#             response_data = {
#                 "msg" : "验证成功"
#             }
#             return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
    
#     #If user is already active, simply display error message
#     else:
#         already_active = True #Display : error message
#         response_data = {
#             "msg" : "用户已经验证"
#         }
#         return HttpResponse(json.dumps(response_data), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Login(APIView):
    schema = CustomSchema()
    def post(self, request, format=None):
        """
        desc: 用户登录
        ret: code, msg, email, name, profile
        err: code, msg, profile (None)
        input:
        - name: email
          desc: 用户名
          type: string
          required: true
          location: form
        - name: password
          desc: 密码
          type: string
          required: true
          location: form
        """
        req = json.loads(request.body)
        # logic to check username/password
        # username = request.POST.get('email')
        # password = request.POST.get('password')   
        email = req.get('email')
        password = req.get('password')

        user = authenticate(username=email, password=password)  #用户验证
        if user:
            login(request, user)  #用户登录
            request.session['user_id'] = user.id
            # user_serialized = UserSerializer(user)
            profile_serialized = ProfileSerializer(user.profile)

            response_data = {
                "code" : 200,
                "msg" : "登录成功",
                # "user" : user_serialized.data,
                "email" : user.email,
                "name" : user.first_name,
                "profile" : profile_serialized.data
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_200_OK)
        else:
            response_data = {
                "code" : 500,
                "msg" : "用户名（邮箱名）或密码不正确",
                "profile" : None
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_200_OK)


@api_view()
@login_required
def user_logout(request):
    """
    用户登出
    """
    try:
        del request.session['user_id']
        request.session.flush()
        logout(request)
    except KeyError:
        pass
    return HttpResponse("You're logged out.")


class GetImage(APIView):
    def get(self, request, image):
        """
        获取图片
        """
        try:
            with open('avatar/' + image, "rb") as f:
                return HttpResponse(f.read(), 
                                    content_type="image/jpeg",
                                    status=status.HTTP_200_OK)
        except IOError:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

class UserAvatar(APIView):
    schema = CustomSchema()
    
    def post(self, request, format=None):
        """
        desc: 用户更新头像
        ret: msg, profile
        err: code, msg
        input:
        - name: file
          desc: 图片文件
          type: string
          required: true
          location: form
        """
        try: 
            avatar = request.FILES['file']
            profile = request.user.profile
            profile.avatar = avatar
            profile.save()
        except:
            response_data = {
                "code" : status.HTTP_400_BAD_REQUEST,
                "msg" : "未登录或文件错误"
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_200_OK)

        response_data = {
            "msg" : "头像更新成功",
            "profile": ProfileSerializer(request.user.profile).data
        }
        return HttpResponse(json.dumps(response_data),
                            status=status.HTTP_200_OK)
    
    def get(self, request):
        """
        desc: 用户获取头像
        ret: image
        err: 404页面
        """
        try:
            user = request.user
            profile = user.profile
            avatar = profile.avatar
        except:
            response_data = {
                "code" : status.HTTP_404_NOT_FOUND,
                "msg" : "未登录"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_404_NOT_FOUND)
        try:
            with open(avatar.url, "rb") as f:
                return HttpResponse(f.read(),
                                    content_type="image/jpeg",
                                    status=status.HTTP_200_OK)
        except IOError: # fail to find file
            red = Image.new('RGB', (1, 1))
            response = HttpResponse(content_type="image/jpeg", 
                                    status=status.HTTP_200_OK)
            red.save(response, "JPEG")
            return response


# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     允许组查看或编辑的 API 端点。
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer


class ProfileView(viewsets.ViewSet):
    
    schema = CustomSchema()
    
    def retrieve(self, request, pk):
        """
        desc: 获取用户资料
        ret: 用户资料
        err: 404页面
        input:
        - name: id
          desc: 用户id
          type: string
          required: true
          location: path
        """
        try:
            profile_serialized = ProfileSerializer(User.objects.get(pk=pk).profile)
            return HttpResponse(json.dumps(profile_serialized.data), 
                                status=status.HTTP_200_OK)
        except:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    
    def get(self, request):
        """
        desc: 获取用户资料
        ret: 用户资料
        err: 404页面
        """
        try:
            profile_serialized = ProfileSerializer(request.user.profile)
            return HttpResponse(json.dumps(profile_serialized.data), 
                                status=status.HTTP_200_OK)
        except:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)


# class ProfileViewSet(viewsets.ModelViewSet):
#     authentication_classes = (SessionAuthentication, BasicAuthentication)
#     permission_classes = (IsAuthenticated,)
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer


class TaskView(viewsets.ViewSet):
    """
    允许 Task 查看或编辑的 API 端点。
    """
    # authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    # permission_classes = (IsAuthenticated,)

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    schema = CustomSchema()
    
    def retrieve(self, request, pk):
        """
        desc: 检索任务
        ret: 任务
        err: 404页面
        input:
        - name: id
          desc: 任务id
          type: string
          required: true
          location: path
        """
        task = get_object_or_404(Task, pk=pk)
        task_serialized = TaskSerializer(task)
        return HttpResponse(json.dumps(task_serialized.data), status=status.HTTP_200_OK)

    def get(self, request):
        """
        desc: 检索任务
        ret: 任务列表
        input:
        - name: type
          desc: 问卷 or 跑腿
          type: string
          required: false
          location: query
        - name: mine
          desc: 不为空时表示用户发表或参与
          type: boolean
          required: false
          location: query
        - name: title
          desc: 标题
          type: string
          required: false
          location: query
        - name: issuer
          desc: 发起者名字
          type: string
          required: false
          location: query
        """
        # maybe need pagination
        
        print(self.request.GET)
        queryset = Task.objects.all().order_by('created_date')
        
        # 问卷 or 跑腿
        task_type = request.query_params.get('type', None)
        # 用户 or 所有
        mine = request.query_params.get('mine', None)

        if mine is not None and mine is not '' \
                            and mine.lower() != 'false':
            user = request.user
            queryset = queryset.filter(Q(issuer=user) | Q(participants=user))

        if task_type is not None and task_type is not '':
            queryset = queryset.filter(task_type=task_type)

        title = request.query_params.get('title', None)
        issuer_first_name = request.query_params.get('issuer', None)

        if title is not None and title is not '':
            queryset = queryset.filter(title__icontains=title)
        
        if issuer_first_name is not None and issuer_first_name is not '':
            userset = User.objects.filter(first_name__icontains=issuer_first_name)
            queryset = queryset.filter(issuer__in=userset)

        #filtered = [x for x in queryset if x.status=='UNDERWAY' and x.task_type=='问卷']
        filtered = queryset
        
        task_serialized = TaskSerializer(filtered, many=True)
        return HttpResponse(json.dumps(task_serialized.data), 
                            status=status.HTTP_200_OK)

    def create(self, request):
        """
        desc: 发布问卷 或 跑腿委托
        ret: code, msg
        err: code, msg
        input:
        - name: taskType
          desc: 问卷 or 跑腿
          type: string
          required: true
          location: form
        - name: title
          desc: 标题
          type: string
          required: true
          location: form
        - name: description
          desc: 描述
          type: string
          required: false
          location: form
        - name: dueDate
          desc: 参与截止日期
          type: string
          required: false
          location: form
        - name: fee
          desc: 每人报酬
          type: integer
          required: false
          location: form
        - name: maxNumber
          desc: 参与限额
          type: integer
          required: false
          location: form
        - name: tagSet
          desc: 标签名数组，标签名若不存在会创建
          type: array
          required: false
          location: form
        - name: question
          desc: 问卷，taskType为问卷才有效
          type: string
          required: false
          location: form
        """
        user = request.user
        form = request.data
        available_balance = user.profile.available_balance
        
        # belows auto checked by models
        task_type = form.get('taskType', None)
        title = form.get('title', None)
        description = form.get('description', None)
        due_date = form.get('dueDate', None)

        try:
            fee = int(form.get('fee', None)) \
                            if form.get('fee', None) else None
            participant_quota = int(form.get('maxNumber', None)) \
                      if form.get('maxNumber', None) else None
        except:
            response_data = {
                "code" : status.HTTP_400_BAD_REQUEST,
                "msg" : "金额与参与名额必须为数字"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_200_OK)

        if fee:
            if not participant_quota:
                response_data = {
                    "code" : status.HTTP_400_BAD_REQUEST,
                    "msg" : "设定金额时必须同时设定参与名额"
                }
                return HttpResponse(json.dumps(response_data), 
                                        status=status.HTTP_200_OK)
            if available_balance < fee * participant_quota:
                response_data = {
                    "code" : status.HTTP_400_BAD_REQUEST,
                    "msg" : "可用余额不足"
                }
                return HttpResponse(json.dumps(response_data), 
                                        status=status.HTTP_200_OK)

        tag_set = form.get('tagSet', None) # maybe also need check
        try:
            assert(tag_set == None or isinstance(tag_set, list))
        except:
            response_data = {
                "code" : status.HTTP_400_BAD_REQUEST,
                "msg" : "标签必须为空或数组"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_200_OK)


        if task_type == '问卷':
            poll = form.get('question', None)
        else:
            poll = ''
      
        try:
            task = Task.objects.create(
                issuer=user,
                title=title,
                description=description,
                poll=poll,
                fee=fee,
                participant_quota=participant_quota,
                due_date=due_date,
                task_type=task_type
            )
            task.save()

            if tag_set:
                for tag_name in tag_set:
                    if Tag.objects.filter(name=tag_name).exists():
                        tag_obj = Tag.objects.get(name=tag_name)
                    else:
                        tag_obj = Tag.objects.create(name=tag_name)
                    tag_obj.tasks.add(task)
        except:
            response_data = {
                "code" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                "msg" : "发布失败，字段异常"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_200_OK)

        response_data = {
            "code" : status.HTTP_201_CREATED,
            "msg" : "发布成功"
        }
        return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_201_CREATED)

    # def update(self, request, pk=None):
    # 
    # def retrieve(self, request, pk=None):
    #     task = get_object_or_404(Task, pk=pk)
    #     task_serialized = TaskSerializer(task)
    #     return HttpResponse(json.dumps(task_serialized.data), status=status.HTTP_200_OK)

    # def partial_update(self, request, pk=None):
    # pass
    # def destroy(self, request, pk=None):
    #     task = get_object_or_404(Task, pk=pk)
    #     task.delete()
    #     return HttpResponse(status=status.HTTP_200_OK)
    # """
    # 如果你有特别的需要被路由到的方法,可以将它们标记为需要路由使用@detail_route或@list_route修饰符。
    # """

    # @detail_route(methods=[‘post’], permission_classes=[IsAdminOrIsSelf])
    # def set_password(self, request, pk=None):

    # """
    # 可以通过访问^users/{pk}/set_password/$来访问改视图


class ParticipantshipViewSet(viewsets.ModelViewSet):
    queryset = Participantship.objects.all()
    serializer_class = ParticipantshipSerializer
    
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        response_data = {}
        if request.method == 'POST':
            user = request.user
            form = json.loads(request.body)

            task_id = form['task_id']
            task = Task.objects.get(pk=task_id)
            task_status = task.status

            if task_status == 'INVALID':
                response_data['code'] = 500
                response_data['msg'] = "问卷存在争议"
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
            elif task_status == 'CANCELLED':
                response_data['code'] = 500
                response_data['msg'] = "问卷被发布者取消"
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
            elif task_status == 'CLOSED':
                response_data['code'] = 500
                response_data['msg'] = "问卷已经过截至日期"
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
            elif task_status == 'QUOTA FULL':
                response_data['code'] = 500
                response_data['msg'] = "问卷参与人数已满"
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
            
            description = task.description
            poll = form['poll']
            rate = int(form['rate'])
            comment = form['comment']

            participantship = Participantship.objects.create(
                user=user,
                task=task,
                description=description,
                poll=poll,
                rate=rate,
                comment=comment
            )
            participantship.save()

            response_data['code'] = 200
            response_data['msg'] = "参与问卷成功"
            return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

# def UserLogin():
