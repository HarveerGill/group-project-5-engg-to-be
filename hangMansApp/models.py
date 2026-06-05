import uuid

from django.conf import settings
from django.db import models


class Word(models.Model):
    uui = models.UUIDField(default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=255, verbose_name='Word', unique=True)

    def __str__(self):
        return str(self.word)


class Game(models.Model):
    # Task 7 secure coding principle: link scores to the authenticated user who created them.
    # The field remains nullable so anonymous games can still be played without account creation.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    word = models.ForeignKey(Word, on_delete=models.PROTECT, verbose_name='Word')
    win = models.BooleanField(verbose_name='Win', default=False)
    session = models.TextField(verbose_name='Session')
    letterKnows = models.CharField(verbose_name='Letter Knows', default='', max_length=255)
    fault = models.IntegerField(verbose_name='Faults', default=0)

    # Task 7 secure score sharing: users can share a non-editable score URL with non-users.
    share_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Part 3 feature 1: one-use hint tracking prevents unlimited enumeration of the word.
    hints_used = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        owner = self.user.username if self.user else 'anonymous'
        return f'Game {self.pk} ({owner})'
