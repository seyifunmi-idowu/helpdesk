from django.db import models


class Ticket(models.Model):
    source = models.CharField(max_length=191)
    mailboxEmail = models.CharField(max_length=191, null=True, blank=True)
    subject = models.TextField()
    reference_ids = models.TextField(blank=True, null=True)
    is_new = models.BooleanField(default=True)
    isReplied = models.BooleanField(default=False)
    isReplyEnabled = models.BooleanField(default=True)
    isStarred = models.BooleanField(default=False)
    isTrashed = models.BooleanField(default=False)
    isAgentViewed = models.BooleanField(default=False)
    isCustomerViewed = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    customerRepliedAt = models.DateTimeField(null=True, blank=True)
    outlookConversationId = models.TextField(null=True, blank=True)
    responseSlaLevel = models.IntegerField(null=True, blank=True)
    resolveSlaLevel = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)

    # Relationships
    status = models.ForeignKey('TicketStatus', on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.ForeignKey('TicketPriority', on_delete=models.SET_NULL, null=True, blank=True)
    type = models.ForeignKey('TicketType', on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey('authentication.UserInstance', on_delete=models.CASCADE, related_name='tickets_as_customer')
    agent = models.ForeignKey('authentication.UserInstance', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_as_agent')
    supportGroup = models.ForeignKey('authentication.SupportGroup', on_delete=models.SET_NULL, null=True, blank=True)
    supportTeam = models.ForeignKey('authentication.SupportTeam', on_delete=models.SET_NULL, null=True, blank=True)

    # ManyToMany relationships with explicit through tables
    collaborators = models.ManyToManyField('authentication.UserInstance', related_name='tickets_as_collaborator', through='TicketCollaboratorsThrough')
    supportTags = models.ManyToManyField('Tag', related_name='tickets_with_tag', through='TicketTagsThrough')
    supportLabels = models.ManyToManyField('SupportLabel', related_name='tickets_with_label', through='TicketLabelsThrough')

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        db_table = "uv_ticket"

    def __str__(self):
        return self.subject or f"Ticket #{self.id}"


class TicketCollaboratorsThrough(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey('authentication.UserInstance', on_delete=models.CASCADE)

    class Meta:
        db_table = "uv_tickets_collaborators"
        unique_together = ('ticket', 'user')

class TicketTagsThrough(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)

    class Meta:
        db_table = "uv_tickets_tags"
        unique_together = ('ticket', 'tag')

class TicketLabelsThrough(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    label = models.ForeignKey('SupportLabel', on_delete=models.CASCADE)

    class Meta:
        db_table = "uv_tickets_labels"
        unique_together = ('ticket', 'label')

class Thread(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='threads')
    user = models.ForeignKey('authentication.UserInstance', on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=191)
    messageId = models.TextField(null=True, blank=True)
    threadType = models.CharField(max_length=191)
    createdBy = models.CharField(max_length=191)
    cc = models.JSONField(null=True, blank=True)
    bcc = models.JSONField(null=True, blank=True)
    replyTo = models.JSONField(null=True, blank=True)
    deliveryStatus = models.CharField(max_length=255, null=True, blank=True)
    isLocked = models.BooleanField(default=False)
    isBookmarked = models.BooleanField(default=False)
    message = models.TextField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    agentViewedAt = models.DateTimeField(null=True, blank=True)
    customerViewedAt = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Thread"
        verbose_name_plural = "Threads"
        db_table = "uv_thread"

    def __str__(self):
        return f"Thread for {self.ticket.subject} by {self.user.email if self.user else 'N/A'}"

class Attachment(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='attachments')
    name = models.TextField(null=True, blank=True)
    path = models.TextField(null=True, blank=True)
    contentType = models.CharField(max_length=255, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)
    contentId = models.CharField(max_length=255, null=True, blank=True)
    fileSystem = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"
        db_table = "uv_ticket_attachments"

    def __str__(self):
        return self.name or f"Attachment for {self.thread.ticket.subject}"

class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        db_table = "uv_tag"

    def __str__(self):
        return self.name

class SupportLabel(models.Model):
    name = models.CharField(max_length=191)
    colorCode = models.CharField(max_length=191, null=True, blank=True)
    user = models.ForeignKey('authentication.UserInstance', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Support Label"
        verbose_name_plural = "Support Labels"
        db_table = "uv_support_label"

    def __str__(self):
        return self.name

class TicketPriority(models.Model):
    code = models.CharField(max_length=191, unique=True)
    description = models.TextField(null=True, blank=True)
    colorCode = models.CharField(max_length=191, null=True, blank=True)

    class Meta:
        verbose_name = "Ticket Priority"
        verbose_name_plural = "Ticket Priorities"
        db_table = "uv_ticket_priority"

    def __str__(self):
        return self.code

class TicketStatus(models.Model):
    code = models.CharField(max_length=191, unique=True)
    description = models.TextField(null=True, blank=True)
    colorCode = models.CharField(max_length=191, null=True, blank=True)
    sortOrder = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Ticket Status"
        verbose_name_plural = "Ticket Statuses"
        db_table = "uv_ticket_status"

    def __str__(self):
        return self.code

class TicketType(models.Model):
    code = models.CharField(max_length=191, unique=True)
    description = models.TextField(null=True, blank=True)
    isActive = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Ticket Type"
        verbose_name_plural = "Ticket Types"
        db_table = "uv_ticket_type"

    def __str__(self):
        return self.code

class TicketRating(models.Model):
    stars = models.IntegerField(default=0)
    feedback = models.TextField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='ratings')
    customer = models.ForeignKey('authentication.UserInstance', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Ticket Rating"
        verbose_name_plural = "Ticket Ratings"
        db_table = "uv_ticket_rating"

    def __str__(self):
        return f"Rating for {self.ticket.subject}: {self.stars} stars"

class SavedReplies(models.Model):
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField()
    templateId = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey('authentication.UserInstance', on_delete=models.CASCADE, null=True, blank=True) # Assuming UserInstance is the correct foreign key
    isPredefind = models.BooleanField(default=True, null=True, blank=True)
    messageInline = models.TextField(null=True, blank=True)
    templateFor = models.CharField(max_length=255, null=True, blank=True)
    groups = models.ManyToManyField('authentication.SupportGroup', related_name='saved_replies_groups', through='SavedRepliesGroupsThrough')
    teams = models.ManyToManyField('authentication.SupportTeam', related_name='saved_replies_teams', through='SavedRepliesTeamsThrough')

    class Meta:
        verbose_name = "Saved Reply"
        verbose_name_plural = "Saved Replies"
        db_table = "uv_saved_replies"

    def __str__(self):
        return self.name

class SavedRepliesGroupsThrough(models.Model):
    savedReply = models.ForeignKey(SavedReplies, on_delete=models.CASCADE)
    group = models.ForeignKey('authentication.SupportGroup', on_delete=models.CASCADE)

    class Meta:
        db_table = "uv_saved_replies_groups"
        unique_together = ('savedReply', 'group')

class SavedRepliesTeamsThrough(models.Model):
    savedReply = models.ForeignKey(SavedReplies, on_delete=models.CASCADE)
    team = models.ForeignKey('authentication.SupportTeam', on_delete=models.CASCADE)

    class Meta:
        db_table = "uv_saved_replies_teams"
        unique_together = ('savedReply', 'team')

class AgentActivity(models.Model):
    agent = models.ForeignKey('authentication.UserInstance', on_delete=models.CASCADE)
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    agentName = models.CharField(max_length=255, null=True, blank=True)
    customerName = models.CharField(max_length=255, null=True, blank=True)
    threadType = models.CharField(max_length=255, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Agent Activity"
        verbose_name_plural = "Agent Activities"
        db_table = "uv_agent_activity"

    def __str__(self):
        return f"{self.agent.email} - {self.action} at {self.createdAt}"

class PreparedResponse(models.Model):
    name = models.CharField(max_length=191)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=191) # 'public' or 'private'
    actions = models.JSONField(null=True, blank=True) # Stores serialized array of actions
    user = models.ForeignKey('authentication.UserInstance', on_delete=models.SET_NULL, null=True, blank=True) # Links to uv_user_instance(id)
    groups = models.ManyToManyField('authentication.SupportGroup', related_name='prepared_responses_groups', through='PreparedResponseSupportGroupsThrough')
    teams = models.ManyToManyField('authentication.SupportTeam', related_name='prepared_responses_teams', through='PreparedResponseSupportTeamsThrough')

    class Meta:
        verbose_name = "Prepared Response"
        verbose_name_plural = "Prepared Responses"
        db_table = "uv_prepared_responses"

    def __str__(self):
        return self.name

class PreparedResponseSupportGroupsThrough(models.Model):
    preparedResponse = models.ForeignKey(PreparedResponse, on_delete=models.CASCADE)
    group = models.ForeignKey('authentication.SupportGroup', on_delete=models.CASCADE)

    class Meta:
        db_table = "uv_prepared_response_support_groups"
        unique_together = ('preparedResponse', 'group')

class PreparedResponseSupportTeamsThrough(models.Model):
    preparedResponse = models.ForeignKey(PreparedResponse, on_delete=models.CASCADE)
    team = models.ForeignKey('authentication.SupportTeam', on_delete=models.CASCADE)

    class Meta:
        db_table = "uv_prepared_response_support_teams"
        unique_together = ('preparedResponse', 'team')

class Workflow(models.Model):
    name = models.CharField(max_length=191)
    description = models.TextField(null=True, blank=True)
    conditions = models.JSONField(null=True, blank=True) # Stores serialized array of conditions
    actions = models.JSONField(null=True, blank=True) # Stores serialized array of actions
    status = models.BooleanField(default=True) # Whether the rule is active or not
    is_predefind = models.BooleanField(default=False) # System-defined vs custom rule flag

    class Meta:
        verbose_name = "Workflow"
        verbose_name_plural = "Workflows"
        db_table = "uv_workflow"

    def __str__(self):
        return self.name

class WorkflowEvent(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='events')
    event = models.CharField(max_length=191) # Stores the trigger name as a string (e.g., 'ticket.created')

    class Meta:
        verbose_name = "Workflow Event"
        verbose_name_plural = "Workflow Events"
        db_table = "uv_workflow_events"

    def __str__(self):
        return f"{self.workflow.name} - {self.event}"
