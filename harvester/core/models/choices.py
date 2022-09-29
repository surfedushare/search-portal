from django.db import models


class EducationalLevels(models.IntegerChoices):

    VOCATIONAL_EDUCATION = 1
    APPLIED_SCIENCE = 2
    UNIVERSITY = 3
