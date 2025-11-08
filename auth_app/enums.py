from django.db import models
from django.utils.translation import gettext_lazy as _

class DriverType(models.TextChoices):
    middle_bus = "middle bus", _('میدل باس')
    mini_bus = "mini bus", _('مینی باس')
    van = "van", _('ون')
    riding = "riding", _('سواری')


class Province(models.TextChoices):
    TEHRAN = 'TEH', _('تهران')
    ISFAHAN = 'ISF', _('اصفهان')
    FARS = 'FAR', _('فارس')
    KHOY = 'KHO', _('خوزستان')
    GILAN = 'GIL', _('گیلان')
    EAST_AZARBAIJAN = 'EAZ', _('آذربایجان شرقی')
    WEST_AZARBAIJAN = 'WAZ', _('آذربایجان غربی')
    ALBORZ = 'ALB', _('البرز')
    HORMOZGAN = 'HOM', _('هرمزگان')
    KERMAN = 'KER', _('کرمان')
    YAZD = 'YAZ', _('یزد')
    KURDESTAN = 'KUR', _('کردستان')
    ZANJAN = 'ZAN', _('زنجان')
    SEMNAN = 'SEM', _('سمنان')
    LORESTAN = 'LOR', _('لرستان')
    MARKAZI = 'MAR', _('مرکزی')
    GOLISTAN = 'GOL', _('گلستان')
    MADAKTO = 'MAD', _('مازندران')
    CHAHARMAHAL_VA_BAKHTIARI = 'CHO', _('چهارمحال و بختیاری')
    SYSTAN_AND_BALUCHISTAN = 'SIS', _('سیستان و بلوچستان')
    NORTH_KHORASAN = 'NKO', _('خراسان شمالی')
    RAZAVI_KHORASAN = 'RAZ', _('خراسان رضوی')
    SOUTH_KHORASAN = 'SKO', _('خراسان جنوبی')


class VerificationStatus(models.TextChoices):
    # DRAFT = 'draft', _('پیش‌نویس')
    SUBMITTED = 'submitted', _('ارسال شده')
    # UNDER_REVIEW = 'under_review', _('در حال بررسی')
    APPROVED = 'approved', _('تایید شده')
    REJECTED = 'rejected', _('رد شده')


class DocumentType(models.TextChoices):
    ID_FRONT = 'id_front', _('جلوی کارت شناسایی')
    ID_BACK = 'id_back', _('پشت کارت شناسایی')
    CAR_FRONT = 'car_front', _('جلوی خودرو')
    CAR_BACK = 'car_back', _('پشت خودرو')
    INSURANCE = 'insurance', _('بیمه')
    IDENTITY_VERIF = 'identity_verif', _('تایید هویت')
