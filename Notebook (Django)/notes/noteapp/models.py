from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=25, null=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    # Add constrain field to have unique user-tag relationship
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'name'], name='tag of username')
        ]

    def __str__(self):
        return f"{self.name}: {self.user_id}"


class Note(models.Model):
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=150, null=False)
    done = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)  # through='NoteToTag'
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}: {self.user_id}"


# class NoteToTag(models.Model):
#     note = models.ForeignKey(Note, on_delete=models.CASCADE)
#     tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
