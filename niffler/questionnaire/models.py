from django.db import models

STATUS_CHOICES = [
    ('UNDERWAY', 'UNDERWAY'), # 进行中
    ('CANCELLED', 'CANCELLED'), # 发起者/参与者取消，发起者也会触发参与者
    ('OVERDUE', 'OVERDUE'), # 发起/参与超时
    ('REJECTED', 'REJECTED'), # 发起者/参与者违规，发起者也会触发参与者
    ('FINISHED', 'FINISHED'), # 仅用于发起者确认参与者完成
    ('COMMENTED', 'COMMENTED') # 仅用于发起者评价参与者
]

class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, blank=True)
    balance = models.IntegerField(blank=True, default=10000)
    avatar = models.ImageField(upload_to='avatar/%Y/%m/%d/', blank=True)

class Task(models.Model):
    title = models.CharField(maxlength=150)
    description = models.TextField(blank=True)
    poll = models.FileField(upload_to='task_poll/%Y/%m/%d/', blank=True)
    issuer = models.ForeignKey('auth.User', 
            related_name='issued_tasks', on_delete=models.CASCADE)
    fee = models.IntegerField(blank=True, null=True)
    participant_quota = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choice=STATUS_CHOICES,
                                    default='UNDERWAY', max_length=100)
    due_date = models.DateTimeField(blank=True, null=True)
    participants = models.ManyToManyField('auth.User',
        related_name='participanted_tasks', through='Participantship')
    claimers = models.ManyToManyField('auth.User',
                                      related_name='claimed_tasks')

class Participantship(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    participanted_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choice=STATUS_CHOICES,
                                    default='UNDERWAY', max_length=100)
    description = models.TextField(blank=True)
    poll = models.FileField(upload_to='participanted_poll/%Y/%m/%d/',
                            blank=True)
    finished_date = models.DateTimeField(blank=True, null=True)
    rate = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=150)
    users = models.ManyToManyField('auth.User')
    tasks = models.ManyToManyField(Task)