"""
Created by [16340286](https://github.com/Ernie1).

TODO not here:
 * When create task,
   available_balance should be more than fee * participant_quota.
   
 * When determine task's fee,
   participant_quota should also be determined but not vice versa.
 
 * Task's due_date is only w.r.t. participantship's participanted_date,
   so participantship's confirmed_date is unrestricted.
 
 * When create a participantship,
   task issuer's balance is deducted 1 * fee.
 
 * When task cancelled, task issuer will not be refunded
   and affect corresponding participantship,
   participant whose _status == 'UNDERWAY' will be paid.
   
 * Task can be claimed when status == 'UNDERWAY' and
   claimer is not issuer.
   
 * When task invalid, task issuer will not be refunded
   and cause corresponding participantship invalid,
   participant whose _status == 'UNDERWAY' will NOT be paid.
   
 * Only participant has permission to modify _status
   from 'UNDERWAY' to 'CANCELLED' and task issuer is refunded 1 * fee.
   
 * Only task issuer has permission to modify _status
   from 'UNDERWAY' to 'CONFIRMED' and participant is paid 1 * fee.
   
 * Only task issuer has permission to comment
   when _status == 'CONFIRMED'.

Task statuses:
        INVALID : Has certain number of claimers
      CANCELLED : Cancelled by issuer
         CLOSED : due_date expires
     QUOTA FULL : Attain to participant_quota
       UNDERWAY : In progress

Participantship statuses:
      CANCELLED : Cancelled by participant
      COMMENTED : Has been commented by its task issuer
      CONFIRMED : Has been confirmed by its task issuer
   TASK INVALID : Its task has certain number of claimers
 TASK CANCELLED : Its task has been cancelled
       UNDERWAY : In progress
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

CLAIMER_THRESHOLD = 10

class EmailVerify(models.Model):
    email = models.CharField(max_length=50, unique=True)
    verification_code = models.CharField(max_length=40, default='123456')
    code_expires = models.DateTimeField(blank=True, null=True)

class Profile(models.Model):
    GenderChoices = (
        (u'女', u'女'),
        (u'男', u'男'),
    )
    YEAR_IN_SCHOOL_CHOICES = [
      (u'大一', u'大一'),
      (u'大二', u'大二'),
      (u'大三', u'大三'),
      (u'大四', u'大四'),
    ]
    def content_file_name(instance, filename):
      return 'avatar/' + str(instance.user.id) + '.jpg'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=50, blank=True)
    balance = models.IntegerField(blank=True, default=10000)
    avatar = models.ImageField(upload_to=content_file_name, blank=True)
    # avatar = models.CharField(max_length=100, default='https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1561038007116&di=36a197a4d42d2fc3d3d1b2d955c65d10&imgtype=0&src=http%3A%2F%2Fimg0.pclady.com.cn%2Fpclady%2Fpet%2Fchoice%2Fcat%2F1503%2F7.jpg')

    birth = models.DateField(blank=True, null=True)
    stuId = models.CharField(max_length=8,null=True)
    grade = models.CharField(
            max_length=4,
            choices=YEAR_IN_SCHOOL_CHOICES,
            default='大一',
        )
    major = models.CharField(max_length=20, blank=True, null=True)
    sex = models.CharField(max_length=2,choices=GenderChoices,null=True)

     
    @property
    def available_balance(self):
        budget = 0
        for t in self.user.issued_tasks.all():
            if t.status == 'UNDERWAY' and t.fee:
                budget += t.fee * t.remaining_quota
        return self.balance - budget


class Task(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    # poll = models.FileField(upload_to='task_poll/%Y/%m/%d/', blank=True)
    poll = models.TextField(blank=True)
    issuer = models.ForeignKey(User, 
            related_name='issued_tasks', on_delete=models.CASCADE)
    fee = models.FloatField(blank=True, null=True)
    participant_quota = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    participants = models.ManyToManyField(User,
        related_name='participanted_tasks', through='Participantship', blank=True)
    claimers = models.ManyToManyField(User,
                                      related_name='claimed_tasks', blank=True)
    cancelled = models.BooleanField(default=False)
    
    TASK_CHOICES = (
        (u'问卷', u'问卷'),
        (u'跑腿', u'跑腿'),
    )
    task_type = models.CharField(max_length=4, choices=TASK_CHOICES, default='questionnaire')


    @property
    def valid_participant_amount(self):
        return self.participantship_set.filter(
                models.Q(_status='UNDERWAY') | \
                models.Q(_status='CONFIRMED') | \
                models.Q(_status='COMMENTED')).count()
    
    @property
    def remaining_quota(self):
        if self.participant_quota:
            return max(self.participant_quota - \
                       self.valid_participant_amount, 0)
        return True
    
    @property
    def status(self):
        if self.claimers.count() >= CLAIMER_THRESHOLD:
            return 'INVALID'
        if self.cancelled:
            return 'CANCELLED'
        if self.due_date and timezone.now() >= self.due_date:
            return 'CLOSED'
        if self.remaining_quota == 0:
            return 'QUOTA FULL'
        return 'UNDERWAY'

    @property
    def issuer_first_name(self):
        return self.issuer.first_name


PARTICIPANTSHIP_STATUS = [
    ('UNDERWAY', 'UNDERWAY'),
    ('CANCELLED', 'CANCELLED'),
    ('CONFIRMED', 'CONFIRMED'),
]

class Participantship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    participanted_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    poll = models.TextField(blank=True)
    confirmed_date = models.DateTimeField(blank=True, null=True)
    rate = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True)
    _status = models.CharField(choices=PARTICIPANTSHIP_STATUS,
                blank=True, default='UNDERWAY', max_length=100)
    
    @property
    def status(self):
        if self._status == 'CANCELLED':
            return 'CANCELLED'
        if self._status == 'CONFIRMED':
            return 'COMMENTED' if self.comment else 'CONFIRMED'
        if self.task.status == 'INVALID':
            return 'TASK INVALID'
        if self.task.status == 'CANCELLED':
            return 'TASK CANCELLED'
        return 'UNDERWAY'


# maybe useless
class Tag(models.Model):
    name = models.CharField(max_length=150)
    users = models.ManyToManyField(User, blank=True)
    tasks = models.ManyToManyField(Task, blank=True)
