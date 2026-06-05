from django.contrib import admin

from .models import Game, Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    search_fields = ('word',)
    list_display = ('id', 'word', 'uui')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    # Administrators may edit/delete game records via Django admin, as required by the specification.
    list_display = ('id', 'user', 'word', 'win', 'fault', 'hints_used', 'created_at')
    list_filter = ('win', 'created_at')
    search_fields = ('user__username', 'word__word', 'share_id')
    readonly_fields = ('share_id', 'created_at', 'updated_at')
