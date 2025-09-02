from django.contrib import admin
from .models import (
    Ticket, TicketCollaboratorsThrough, TicketTagsThrough, TicketLabelsThrough, 
    Thread, Attachment, Tag, SupportLabel, TicketPriority, TicketStatus, 
    TicketType, TicketRating, SavedReplies, SavedRepliesGroupsThrough, 
    SavedRepliesTeamsThrough, AgentActivity, PreparedResponse, 
    PreparedResponseSupportGroupsThrough, PreparedResponseSupportTeamsThrough, 
    Workflow, WorkflowEvent
)

admin.site.register(Ticket)
admin.site.register(TicketCollaboratorsThrough)
admin.site.register(TicketTagsThrough)
admin.site.register(TicketLabelsThrough)
admin.site.register(Thread)
admin.site.register(Attachment)
admin.site.register(Tag)
admin.site.register(SupportLabel)
admin.site.register(TicketPriority)
admin.site.register(TicketStatus)
admin.site.register(TicketType)
admin.site.register(TicketRating)
admin.site.register(SavedReplies)
admin.site.register(SavedRepliesGroupsThrough)
admin.site.register(SavedRepliesTeamsThrough)
admin.site.register(AgentActivity)
admin.site.register(PreparedResponse)
admin.site.register(PreparedResponseSupportGroupsThrough)
admin.site.register(PreparedResponseSupportTeamsThrough)
admin.site.register(Workflow)
admin.site.register(WorkflowEvent)
