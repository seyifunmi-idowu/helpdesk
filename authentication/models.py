from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone as django_timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('isEnabled', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=191, unique=True, null=True, blank=True)
    proxyId = models.CharField(max_length=191, unique=True, null=True, blank=True)
    firstName = models.CharField(max_length=191)
    lastName = models.CharField(max_length=191, null=True, blank=True)
    isEnabled = models.BooleanField(default=False)
    verificationCode = models.CharField(max_length=191, unique=True, null=True, blank=True)
    timezone = models.CharField(max_length=191, null=True, blank=True)
    timeformat = models.CharField(max_length=191, null=True, blank=True)
    lastOtpGeneratedAt = models.DateTimeField(null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) # Maps to isEnabled for Django's internal use
    date_joined = models.DateTimeField(default=django_timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "uv_user"

    def __str__(self):
        return self.email or self.firstName

    def get_full_name(self):
        return f"{self.firstName} {self.lastName}".strip()

    def get_short_name(self):
        return self.firstName


class UserInstance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_instances')
    source = models.CharField(max_length=191)
    skypeId = models.CharField(max_length=191, null=True, blank=True)
    contactNumber = models.CharField(max_length=191, null=True, blank=True)
    designation = models.CharField(max_length=191, null=True, blank=True)
    signature = models.TextField(null=True, blank=True)
    profileImage = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=False)
    isVerified = models.BooleanField(default=False)
    isStarred = models.BooleanField(default=False)
    ticketAccessLevel = models.CharField(max_length=32, null=True, blank=True)
    defaultFiltering = models.IntegerField(null=True, blank=True)

    supportRole = models.ForeignKey('SupportRole', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_instances')
    supportPrivileges = models.ManyToManyField('SupportPrivilege', related_name='user_instances', blank=True)
    supportTeams = models.ManyToManyField('SupportTeam', related_name='users', blank=True)
    supportGroups = models.ManyToManyField('SupportGroup', related_name='users', blank=True)

    # For team leads and group admins
    lead_of_teams = models.ManyToManyField('SupportTeam', related_name='leads', through='LeadSupportTeamThrough', blank=True)
    admin_of_groups = models.ManyToManyField('SupportGroup', related_name='admins', through='AdminSupportGroupThrough', blank=True)

    class Meta:
        verbose_name = "User Instance"
        verbose_name_plural = "User Instances"
        db_table = "uv_user_instance"

    def __str__(self):
        return f"{self.user.email} instance from {self.source}"


class LeadSupportTeamThrough(models.Model):
  userInstance = models.ForeignKey(UserInstance, on_delete=models.CASCADE)
  supportTeam = models.ForeignKey('SupportTeam', on_delete=models.CASCADE)

  class Meta:
    db_table = "uv_lead_support_teams"
    unique_together = ('userInstance', 'supportTeam')


class AdminSupportGroupThrough(models.Model):
  userInstance = models.ForeignKey(UserInstance, on_delete=models.CASCADE)
  supportGroup = models.ForeignKey('SupportGroup', on_delete=models.CASCADE)

  class Meta:
    db_table = "uv_admin_support_groups"
    unique_together = ('userInstance', 'supportGroup')


class SupportRole(models.Model):
  code = models.CharField(max_length=191, unique=True)
  description = models.CharField(max_length=191, null=True, blank=True)

  class Meta:
    verbose_name = "Support Role"
    verbose_name_plural = "Support Roles"
    db_table = "uv_support_role"

  def __str__(self):
    return self.code


class SupportGroup(models.Model):
  name = models.CharField(max_length=191)
  description = models.TextField()
  createdAt = models.DateTimeField(auto_now_add=True)
  isActive = models.BooleanField(default=False)
  userView = models.BooleanField(default=False)
  # users and admins are defined in UserInstance
  supportTeams = models.ManyToManyField('SupportTeam', related_name='groups_with_team',
                                        through='SupportGroupsTeamsThrough')

  class Meta:
    verbose_name = "Support Group"
    verbose_name_plural = "Support Groups"
    db_table = "uv_support_group"

  def __str__(self):
    return self.name


class SupportGroupsTeamsThrough(models.Model):
  supportGroup = models.ForeignKey(SupportGroup, on_delete=models.CASCADE)
  supportTeam = models.ForeignKey('SupportTeam', on_delete=models.CASCADE)

  class Meta:
    db_table = "uv_support_groups_teams"
    unique_together = ('supportGroup', 'supportTeam')


class SupportTeam(models.Model):
  name = models.CharField(max_length=191)
  description = models.TextField()
  createdAt = models.DateTimeField(auto_now_add=True)
  isActive = models.BooleanField(default=False)

  class Meta:
    verbose_name = "Support Team"
    verbose_name_plural = "Support Teams"
    db_table = "uv_support_team"

  def __str__(self):
    return self.name


class SupportPrivilege(models.Model):
  name = models.CharField(max_length=191)
  description = models.TextField()
  privileges = models.JSONField(null=True, blank=True)
  createdAt = models.DateTimeField(null=True, blank=True)

  class Meta:
    verbose_name = "Support Privilege"
    verbose_name_plural = "Support Privileges"
    db_table = "uv_support_privilege"

  def __str__(self):
    return self.name
