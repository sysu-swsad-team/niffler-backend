import django_filters
from django.shortcuts import render
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
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
from django.core.files.images import ImageFile
from django.utils.crypto import get_random_string

import json
import os, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from PIL import Image
import hashlib
from string import Template
from django.core.mail import EmailMultiAlternatives
from datetime import datetime, timedelta
import random

from rest_framework.decorators import api_view
from .swagger_schema import CustomSchema

# handle datetime
import dateutil.parser
# import datetime
from django.utils import timezone
import pytz

from alipay import AliPay


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class PaymentView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    schema = CustomSchema()

    def get(self, request):
        """
        desc: 充值
        ret: redirect to "支付链接"
        err: code, msg
        input:
        - name: amount
          desc: 充值金额
          type: string
          required: true
          location: query
        """
        user = request.user
        amount = request.query_params.get('amount', None)

        if user.is_authenticated == False:
            response_data = {
                "msg" : '未登录'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        if not amount:
            response_data = {
                "msg" : '充值金额有误'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        # 向支付宝发起请求，获取支付链接参数
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,   # 沙箱账号的 APPID
            app_notify_url=None,    # 默认回调 url，配置 notify_url 需要公网环境
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem"),    # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",    # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG    # 默认False
        )

        # 电脑网站支付，需要跳转到 https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay_client.api_alipay_trade_page_pay(
            out_trade_no=20190627,  # 订单编号
            total_amount=0.01,   # 订单总金额，在数据库中是 Decimal 类型，需要转换
            subject="测试订单：闲钱币充值",    # 订单标题，可以自己指定
            return_url="http://127.0.0.1:8080/#/balance",  # 支付成功回调url
            notify_url=None     # 可选
        )

        # 拼接支付链接地址
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        response_data = {
            "msg" : '返回成功',
            "url" : alipay_url
        }
        # return HttpResponse(json.dumps(response_data), 
                        # status=status.HTTP_200_OK)
        return redirect(alipay_url)

class PaymentStatusView(APIView):   
    authentication_classes = (CsrfExemptSessionAuthentication,)

    schema = CustomSchema()

    def put(self, request):
        """
        desc: 保存支付结果
        ret: code, msg, profile
        err: code, msg
        input:
        - name: amount
          desc: 充值金额
          type: string
          required: true
          location: query
        input:
        - name: out_trade_no
          desc: 订单号
          type: string
          required: true
          location: query
        - name: trade_no
          desc: 交易流水编号
          type: string
          required: true
          location: query
        - name: total_amount
          desc: 充值金额
          type: string
          required: true
          location: query
        - name: seller_id
          desc: 支付宝唯一用户编号
          type: string
          required: true
          location: query
        """
        # 获取查询字符串数据
        # out_trade_no: 订单号，    trade_no: 交易流水编号
        # total_amount: 订单总金额   seller_id: 支付宝唯一用户编号
        alipay_request_dict = request.query_params  # query_params是一个QueryDict对象

        # 如果查询字符串为空，表示前端没有将支付宝回调时携带的参数传递过来
        if not alipay_request_dict:
            response_data = {
                "msg" : '缺少支付成功返回的参数'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        # 将QueryDict转换成python中的字典
        data = alipay_request_dict.dict()
        # 用pop方法取出签名，接口文档中推荐使用的方法
        sign = data.pop("sign")

        # 校验参数，使用AliPay模块来验证前端传过来的数据是否真的是支付宝在回调时携带的参数
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,    # 沙箱账号的APPID
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False，是否是沙箱环境
        )

        # verify函数返回验证结果，True 或 False
        result = alipay_client.verify(data, sign)
        if result:
            # 获得支付结果数据

            order_id = data.get("out_trade_no")     # 订单编号
            trade_id = data.get("trade_no")         # 交易流水号
            total_amount = data.get("total_amount") # 订单总金额
            seller_id = data.get("seller_id") # 支付宝唯一用户号

            user = request.user
            if user.is_authenticated == False:
                response_data = {
                    "msg" : '未登录'
                }
                return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)
                                    
            profile = user.profile
            profile.balance += total_amount
            profile.save()

            # 返回 profile
            response_data = {
                "msg" : '充值成功',
                "profile" : ProfileSerializer(profile).data
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_200_OK)
        else:
            # 返回参数错误
            response_data = {
                "msg" : '参数错误'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)


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
        
        req = json.loads(request.body)

        first_name = req.get('name').strip()
        stuId = req.get('stuId').strip()
        birth = req.get('birth').strip()
        sex = req.get('sex').strip()
        grade = req.get('grade').strip()
        major = req.get('major').strip()
        email = req.get('email').strip()
        password = req.get('password')
        verification_code = req.get('code')
        # print(email)
        try:
            # profile = Profile.objects.get(verification_code=verification_code)
            emailverify = EmailVerify.objects.get(email=email)
        except:
            response_data = {
                "msg" : "未为此邮箱生成验证码"
            }
            return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)
        # print(verification_code)
        # print(emailverify.verification_code)
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
                    # profile.avatar = ImageFile(open("avatar/default.jpg", "rb"))  
                    # profile.save()
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
        
    def get(self, request, format=None):
        """
        desc: 邮箱验证
        ret: code, msg
        err: code, msg
        input:
        - name: email
          desc: 邮箱
          type: string
          required: true
          location: query
        """
        email = request.query_params.get('email', None)
        
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
                new_emailverify = EmailVerify.objects.get(email=email)
                if timezone.now() < new_emailverify.code_expires: 
                    response_data = {
                        "msg" : "已经发送验证码此邮箱中，请1分钟后重新发送"
                    }
                    return HttpResponse(json.dumps(response_data), 
                                        status=status.HTTP_201_CREATED)
                else:
                    response_data = {
                        "msg" : "已经重新发送验证码到此邮箱中"
                    }
                    pass 


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
                datetime.now() + timedelta(minutes=1), "%Y-%m-%d %H:%M:%S")
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
            
            # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
            message = MIMEText(text_content, 'plain', 'utf-8')
            message['Subject'] = Header(email_subject, 'utf-8')

            # Create the plain-text and HTML version of your message
            # text = """\
            # Hi,
            # How are you?
            # Real Python has many great tutorials:
            # www.realpython.com"""
            # html = """\
            # <html>
            # <body>
            #     <p>Hi,<br>
            #     How are you?<br>
            #     <a href="http://www.realpython.com">Real Python</a> 
            #     has many great tutorials.
            #     </p>
            # </body>
            # </html>
            # """
            # # Turn these into plain/html MIMEText objects
            # part1 = MIMEText(text, "plain")
            # part2 = MIMEText(html, "html")

            # # Add HTML/plain-text parts to MIMEMultipart message
            # # The email client will try to render the last part first
            # message = MIMEMultipart("alternative")
            # message.attach(part1)
            # message.attach(part2)
          
            try:
                # msg = EmailMultiAlternatives(email_subject, 
                #                              text_content, 
                #                              settings.EMAIL_HOST_USER, [email])
                # msg.send()

                # send_mail(email_subject, text_content, settings.EMAIL_HOST_USER, [email], fail_silently=False)

                #  initiate a TLS-encrypted connection
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as server:
                    server.login(settings.DEFAULT_FROM_EMAIL, settings.EMAIL_HOST_PASSWORD)
                    # TODO: Send email here
                    server.sendmail(settings.DEFAULT_FROM_EMAIL, [email], message.as_string())
            except Exception as e:
                print(e)
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
        # req = json.loads(request.body)
        # logic to check username/password
        email = request.POST.get('email')
        password = request.POST.get('password')   
        # email = req.get('email').strip()
        # password = req.get('password')

        user = authenticate(username=email, password=password)  #用户验证
        if user:
            login(request, user)  #用户登录
            request.session['user_id'] = user.id
            # user_serialized = UserSerializer(user)
            profile_serialized = ProfileSerializer(user.profile)

            response_data = {
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
                "msg" : "用户名（邮箱名）或密码不正确",
                "profile" : None
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_201_CREATED)


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
    authentication_classes = (CsrfExemptSessionAuthentication,)

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
                "msg" : "未登录或文件错误"
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        response_data = {
            "msg" : "头像更新成功",
            "profile": ProfileSerializer(request.user.profile).data
        }
        return HttpResponse(json.dumps(response_data),
                            status=status.HTTP_200_OK)
    
    def get(self, request):
        """
        desc: 获取当前用户头像
        ret: image
        err: 404页面
        """
        try:
            user = request.user
            profile = user.profile
            avatar = profile.avatar
        except:
            response_data = {
                "msg" : "未登录"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_201_CREATED)
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
    authentication_classes = (CsrfExemptSessionAuthentication,)

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
        desc: 获取当前用户资料
        ret: 用户资料
        err: 404页面
        """
        user = request.user
        if user.is_authenticated == False:
            response_data = {
                "msg" : '未登录'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        try:
            profile_serialized = ProfileSerializer(user.profile)
            return HttpResponse(json.dumps(profile_serialized.data), 
                                status=status.HTTP_200_OK)
        except:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        desc: 修改个人资料
        ret: code, msg, profile
        err: code, msg
        input:
        - name: first_name
          desc: 姓名
          type: string
          required: false
          location: form
        - name: stuId
          desc: 学号
          type: string
          required: false
          location: form
        - name: birth
          desc: 生日
          type: string
          required: false
          location: form
        - name: sex
          desc: “男” 或 “女”
          type: string
          required: false
          location: form
        - name: grade
          desc: “大一/二/三/四”
          type: string
          required: false
          location: form
        - name: major
          desc: 专业
          type: string
          required: false
          location: form
        """
        user = request.user
        profile = user.profile

        if user.is_authenticated == False:
            response_data = {
                "msg" : '未登录'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED) 

        req = json.loads(request.body)
        key = req.get('key')

        if key == 'first_name':
            first_name = req.get('value')
            first_name.strip()
            user.first_name = first_name
            user.save()

        if key == 'stuId':
            stuId = req.get('value')
            stuId.strip()
            profile.stuId = stuId

        if key == 'birth':   
            birth = req.get('value')
            birth.strip()
            profile.birth = birth
        
        if key == 'sex':
            sex = req.get('value')
            sex.strip()
            try:
                assert sex == '男' or sex == '女', "性别必须为‘男’或‘女’"
            except AssertionError as msg:
                response_data = {
                    "msg" : str(msg)
                }
                return HttpResponse(json.dumps(response_data),
                                        status=status.HTTP_201_CREATED)
            profile.sex = sex

        if key == 'grade':
            grade = req.get('value')
            grade.strip()
            try:
                assert grade == '大一' or \
                    grade == '大二' or \
                    grade == '大三' or \
                    grade == '大四', "年级错误"
            except AssertionError as msg:
                response_data = {
                    "msg" : str(msg)
                }
                return HttpResponse(json.dumps(response_data),
                                        status=status.HTTP_201_CREATED)
            profile.grade = grade

        if key == 'major':
            major = req.get('value')
            major.strip()
            profile.major = major 

        # old_password = req.get('old_password').strip()
        # new_password = req.get('new_password').strip()
        # try:
            # assert old_password != new_password, "密码修改前后一样"
        # except AssertionError as msg:
        #     response_data = {
        #         "msg" : str(msg)
        #     }
        #     return HttpResponse(json.dumps(response_data),
        #                             status=status.HTTP_201_CREATED)

        # user.set_password(new_password)
        # user.save()

        profile.save()
        response_data = {
            "msg" : "修改成功",
            "profile" : ProfileSerializer(profile).data
        }
        return HttpResponse(json.dumps(response_data),
                        status=status.HTTP_200_OK)

# class ProfileViewSet(viewsets.ModelViewSet):
#     authentication_classes = (SessionAuthentication, BasicAuthentication)
#     permission_classes = (IsAuthenticated,)
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer


class TaskView(viewsets.ViewSet):
    # authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    # permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,)

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    schema = CustomSchema()

    def retrieve(self, request, pk):
        """
        desc: 获取指定任务
        ret: 任务
        err: 404页面
        input:
        - name: id
          desc: 任务id
          type: string
          required: true
          location: path
        """
        response_data = {}
        try:
            task = Task.objects.get(pk=pk)
            task_serialized = TaskSerializer(task)
            response_data['code'] = 200
            response_data['msg'] = '查询成功'
            response_data['questionnaire'] = task_serialized.data
            return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
        except:
            response_data['code'] = 201
            response_data['msg'] = '查询失败'
            response_data['questionnaire'] = ''
            return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)

       
    def get(self, request):
        """
        desc: 检索所有任务
        ret: 任务列表
        input:
        - name: type
          desc: 问卷 or 跑腿
          type: string
          required: false
          location: query
        - name: asIssuer
          desc: 不为空时表示用户发表
          type: boolean
          required: false
          location: query
        - name: asParticipant
          desc: 不为空时表示用户参与
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

        queryset = Task.objects.all().order_by('created_date')
        
        # 问卷 or 跑腿
        task_type = request.query_params.get('type', None)
        if task_type:
            task_type = task_type.strip()
        # 用户 or 所有
        asIssuer = request.query_params.get('asIssuer', None)
        if asIssuer:
            asIssuer = asIssuer.strip()
        asParticipant = request.query_params.get('asParticipant', None)
        if asParticipant:
            asParticipant = asParticipant.strip()
        
        asIssuer = asIssuer and asIssuer.lower() != 'false'
        asParticipant = asParticipant and asParticipant.lower() != 'false'

        if asIssuer or asParticipant:
            user = request.user
            
            if not user.id: # invalid for anonymous user
                response_data = {
                    "msg" : "未登录"
                }
                return HttpResponse(json.dumps(response_data), 
                                    status=status.HTTP_201_CREATED)
            
            if asIssuer and asParticipant:
                queryset = queryset.filter(Q(issuer=user) | Q(participants=user))
            elif asIssuer:
                queryset = queryset.filter(Q(issuer=user))
            else:
                queryset = queryset.filter(Q(participants=user))

        if task_type:
            queryset = queryset.filter(task_type=task_type)

        title = request.query_params.get('title', None)
        if title:
            title = title.strip()
        issuer_first_name = request.query_params.get('issuer', None)
        if issuer_first_name:
            issuer_first_name = issuer_first_name.strip()

        if title:
            queryset = queryset.filter(title__icontains=title)
        
        if issuer_first_name:
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
          desc: 参与截止时间
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
        - name: tag
          desc: 标签名数组，标签名若不存在会创建
          type: array
          required: false
          location: form
        - name: questions
          desc: 问卷，taskType为问卷才有效
          type: string
          required: false
          location: form
        """
        user = request.user
        form = json.loads(request.body)
        if user.is_authenticated == False:
            response_data = {
                "msg" : '未登录'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)
        available_balance = user.profile.available_balance
        
        # belows auto checked by models
        task_type = form.get('taskType', None)
        if task_type:
            task_type = task_type.strip()
        title = form.get('title', None)
        if title:
            title = title.strip()
        
        try:
            assert task_type == "问卷" or task_type == "跑腿", \
                    "任务类型必须为“问卷”或“跑腿”"
            assert title, "标题不能为空"
        except AssertionError as msg:
            response_data = {
                "msg" : str(msg)
            }
            return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)
        
        description = form.get('description', '')
        if description:
            description = description.strip()
        due_date = form.get('dueDate', None)
        
        if due_date:
            due_date = due_date.strip()
            try:
                # suppose front-end only uses Chinese timezone
                # convert it to UTC
                due_date = dateutil.parser.parse(due_date[:25]).replace(
                    tzinfo=pytz.utc) - timedelta(hours=8)
            except:
                response_data = {
                    "msg" : "参与截止时间格式错误，正确示例：\'Mon Jun 10 2019 00:00:00\'"
                }
                return HttpResponse(json.dumps(response_data), 
                                    status=status.HTTP_201_CREATED)
            if due_date - timedelta(minutes=30) < timezone.now():
                response_data = {
                    "msg" : "参与截止时间至少为30分钟之后"
                }
                return HttpResponse(json.dumps(response_data), 
                                    status=status.HTTP_201_CREATED)
        else:
            due_date = None

        try:
            fee = int(form.get('fee', None)) \
                            if form.get('fee', None) else None
            participant_quota = int(form.get('maxNumber', None)) \
                      if form.get('maxNumber', None) else None
        except:
            response_data = {
                "code" : status.HTTP_201_CREATED,
                "msg" : "金额与参与名额必须为数字"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_201_CREATED)

        if fee:
            if not participant_quota:
                response_data = {
                    "msg" : "设定金额时必须同时设定参与名额"
                }
                return HttpResponse(json.dumps(response_data), 
                                        status=status.HTTP_201_CREATED)
            if available_balance < fee * participant_quota:
                response_data = {
                    "msg" : "可用余额不足"
                }
                return HttpResponse(json.dumps(response_data), 
                                        status=status.HTTP_201_CREATED)

        tag_set = form.get('tag', None)
        try:
            assert(tag_set == None or isinstance(tag_set, list))
        except:
            response_data = {
                "msg" : "标签必须为空或数组"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_201_CREATED)


        if task_type == '问卷':
            poll = form.get('questions', '')
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
                    if tag_name and tag_name.strip():
                        tag_name = tag_name.strip()
                        if Tag.objects.filter(name=tag_name).exists():
                            tag_obj = Tag.objects.get(name=tag_name)
                        else:
                            tag_obj = Tag.objects.create(name=tag_name)
                        tag_obj.tasks.add(task)
        except:
            response_data = {
                "msg" : "发布失败，字段异常"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_201_CREATED)

        response_data = {
            "msg" : "发布成功"
        }
        return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_200_OK)
    
    def cancel(self, request, pk):
        """
        desc: 取消任务，进行中的参与者得到报酬
        ret: msg
        err: 404页面/msg
        input:
        - name: id
          desc: 任务id
          type: string
          required: true
          location: path
        """
        try:
            task = Task.objects.get(pk=pk)
        except:
            response_data = {
                "msg" : "查无此 task"
            }
            return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)

        user = request.user

        if user.is_authenticated == False:
            response_data = {
                "msg" : '未登录'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        try:
            assert task.issuer == user, "当前用户非发布者"
            assert task.status == 'QUOTA FULL' or \
                    task.status == 'UNDERWAY', \
                    "无法取消非进行中的任务"
        except AssertionError as msg:
            response_data = {
                "msg" : str(msg)
            }
            return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)

        # pay underway participants fee
        if task.fee:
            for p in task.participantship_set.all():
                if p.status == 'UNDERWAY':
                    p.user.profile.balance += task.fee
                    p.user.profile.save()

        # modify task status
        task.cancelled = True
        task.save()
        
        response_data = {
            "msg" : "取消成功，进行中的参与者得到报酬"
        }
        return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_200_OK)
    
    def claim(self, request, pk):
        """
        desc: 举报任务
        ret: msg
        err: 404页面/msg
        input:
        - name: id
          desc: 任务id
          type: string
          required: true
          location: path
        """
        try:
            task = Task.objects.get(pk=pk)
        except:
            response_data = {
                "msg" : "查无此 task"
            }
            return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)

        user = request.user

        try:
            assert user.id, "未登录"
            assert task.issuer != user, "无法自我举报"
            assert not task.claimers.filter(pk=user.pk).exists(), \
                    "无法重复举报"
            assert task.status == 'QUOTA FULL' or \
                    task.status == 'UNDERWAY', \
                    "非进行中的任务"
        except AssertionError as msg:
            response_data = {
                "msg" : str(msg)
            }
            return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)

        # add claimers
        task.claimers.add(user)
        task.save()
        
        response_data = {
            "msg" : "举报成功"
        }
        return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_200_OK)


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

    
class ParticipantshipView(viewsets.ViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    queryset = Participantship.objects.all()
    serializer_class = ParticipantshipSerializer
    schema = CustomSchema()
    # authentication_classes = (SessionAuthentication, BasicAuthentication)
    # permission_classes = (IsAuthenticated,)
    
    def retrieve(self, request, pk):
        """
        desc: 获取指定参与
        ret: 参与
        err: 404页面
        input:
        - name: id
          desc: 参与id
          type: string
          required: true
          location: path
        """
        try:
            participantship_serialized = ParticipantshipSerializer(
                                            Participantship.objects.get(pk=pk))
            return HttpResponse(json.dumps(participantship_serialized.data), 
                                status=status.HTTP_200_OK)
        except:
            response_data = {
                "msg" : "查询失败"
            } 
            return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)

    def create(self, request):
        """
        desc: 参与任务，系统暂扣报酬
        ret: msg
        err: msg
        input:
        - name: task_id
          desc: 任务id
          type: string
          required: true
          location: form
        - name: description
          desc: 参与备注
          type: string
          required: false
          location: form
        - name: poll
          desc: 问卷
          type: string
          required: false
          location: form
        """
        user = request.user
        # form = request.data
        form = json.loads(request.body)

        try:
            task_id = form.get('task_id', None)
            task = Task.objects.get(pk=task_id)
        except:
            response_data = {
                "msg" : "任务不存在"
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        task_status = task.status

        try:
            assert task_status != 'INVALID', "任务被举报次数过多"
            assert task_status != 'CANCELLED', "任务被发布者取消"
            assert task_status != 'CLOSED', "任务已经过截至日期"
            assert task_status != 'QUOTA FULL', "任务参与人数已满"
            assert user.id, "未登录"
            assert task.issuer != user, "无法自我参与"
            assert not task.participants.filter(pk=user.pk).exists(), \
                                                            "无法重复参与"
        except AssertionError as msg:
            response_data = {
                "msg" : str(msg)
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        description = form.get('description', '')
        if description:
            description = description.strip()
        poll = form.get('poll', '')
        if task.task_type=='跑腿':
            poll = ''

        try:
            Participantship.objects.create(
                user=user,
                task=task,
                description=description,
                poll=poll,
            )
            # task issuer's balance is deducted 1 * fee
            if task.fee:
                task.issuer.profile.balance -= task.fee
                task.issuer.profile.save()
        except:
            response_data = {
                "msg" : "参与失败，字段异常"
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        response_data = {
            "msg" : "参与成功，系统暂扣报酬"
        }
        return HttpResponse(json.dumps(response_data),
                            status=status.HTTP_200_OK)
    
    def cancel(self, request, pk):
        """
        desc: 取消参与，系统退回任务发布者报酬
        ret: msg
        err: 404页面/msg
        input:
        - name: id
          desc: 参与id
          type: string
          required: true
          location: path
        """
        # participantship = get_object_or_404(Participantship, pk=pk)
        try:
            participantship = Participantship.objects.get(pk=pk)
        except:
            response_data = {
                "msg" : "查无此 participantship"
            }
            return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)

        user = request.user
        if user.is_authenticated == False:
            response_data = {
                "msg" : '未登录'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        try:
            assert participantship.user == user, "当前用户非参与者"
            assert participantship.status == 'UNDERWAY', "无法取消非进行中的参与"
        except AssertionError as msg:
            response_data = {
                "msg" : str(msg)
            }
            return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)

        # modify participantship status
        participantship._status = 'CANCELLED'
        participantship.save()

        # refund issuer fee
        if participantship.task.fee:
            participantship.task.issuer.profile.balance += \
                                        participantship.task.fee
            participantship.task.issuer.profile.save()
        
        response_data = {
            "msg" : "取消成功，系统已退回任务发布者报酬"
        }
        return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_200_OK)
    
    def confirm(self, request, pk):
        """
        desc: 发起者确认参与，系统交纳参与者报酬
        ret: msg
        err: 404页面/msg
        input:
        - name: id
          desc: 参与id
          type: string
          required: true
          location: path
        """
        # participantship = get_object_or_404(Participantship, pk=pk)
        try:
            participantship = Participantship.objects.get(pk=pk)
        except:
            response_data = {
                "msg" : "查无此 participantship"
            }
            return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)
                                    
        user = request.user
        if user.is_authenticated == False:
            response_data = {
                "msg" : '未登录'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)
                                
        try:
            assert participantship.task.issuer == user, "当前用户非发起者"
            assert participantship.status == 'UNDERWAY', "无法确认非进行中的参与"
        except AssertionError as msg:
            response_data = {
                "msg" : str(msg)
            }
            return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)

        # pay participant fee
        if participantship.task.fee:
            participantship.user.profile.balance += \
                                        participantship.task.fee
            participantship.user.profile.save()

        # modify participantship status
        participantship._status = 'CONFIRMED'
        participantship.save()
        
        response_data = {
            "msg" : "确认成功，系统已交纳参与者报酬"
        }
        return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_200_OK)
    
    def comment(self, request):
        """
        desc: 发起者评价参与
        ret: msg
        err: msg
        input:
        - name: participantship_id
          desc: 参与id
          type: string
          required: true
          location: form
        - name: rate
          desc: 评分
          type: integer
          required: false
          location: form
        - name: comment
          desc: 评价内容
          type: string
          required: true
          location: form
        """
        user = request.user
        # form = request.data
        form = json.loads(request.body)
        
        if user.is_authenticated == False:
            response_data = {
                "msg" : '未登录'
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)
                                
        try:
            participantship_id = form.get('participantship_id', None)
            participantship = Participantship.objects.get(pk=participantship_id)
        except:
            response_data = {
                "msg" : "参与不存在"
            }
            return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_201_CREATED)

        try:
            assert participantship.task.issuer != user, "当前用户非发起者"
            assert participantship.status == 'CONFIRMED', \
                                              "只能评价已确认但未评价的参与"
            comment = form.get('comment', '')
            if comment:
                comment = comment.strip()
            assert comment, "评价内容不能为空"

        except AssertionError as msg:
            response_data = {
                "msg" : str(msg)
            }
            return HttpResponse(json.dumps(response_data),
                                    status=status.HTTP_201_CREATED)
        
        try:
            rate = form.get('rate', None)
            rate = int(rate) if rate else None
        except:
            response_data = {
                "msg" : "评分必须为数字"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_201_CREATED)

        participantship.rate = rate
        participantship.comment = comment
        participantship.save()
        
        response_data = {
            "msg" : "评价成功"
        }
        return HttpResponse(json.dumps(response_data),
                                status=status.HTTP_200_OK)
        


# class TagViewSet(viewsets.ModelViewSet):
#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer


class TagView(viewsets.ViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    schema = CustomSchema()
    
    def retrieve(self, request, pk):
        """
        desc: 获取指定标签
        ret: 标签
        err: 404页面
        input:
        - name: id
          desc: 标签id
          type: string
          required: true
          location: path
        """
        try:
            tag_serialized = TagSerializer(Tag.objects.get(pk=pk))
            return HttpResponse(json.dumps(tag_serialized.data), 
                                status=status.HTTP_200_OK)
        except:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    
    def get(self, request):
        """
        desc: 获取所有标签
        ret: 标签
        err: 404页面
        """
        try:
            tag_serialized = TagSerializer(Tag.objects.all(), many=True)
            return HttpResponse(json.dumps(tag_serialized.data), 
                                status=status.HTTP_200_OK)
        except:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

# def UserLogin():

# class EmailVerifyViewSet(viewsets.ModelViewSet):
#     queryset = EmailVerify.objects.all()
#     serializer_class = EmailVerifySerializer