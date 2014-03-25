from django.contrib import admin
from players.models import Player, Cron, Mop

class CronAdmin(admin.ModelAdmin):
    list_filter = ('email',)

admin.site.register(Player)
admin.site.register(Cron, CronAdmin)
admin.site.register(Mop)
