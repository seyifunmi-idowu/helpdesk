from .models import SupportPrivilege, SupportGroup, SupportTeam, UserInstance

class PrivilegeService:

    @staticmethod
    def get_all_privileges():
        """Returns all support privilege sets."""
        return SupportPrivilege.objects.all()

    @staticmethod
    def get_privilege_by_id(privilege_id):
        """Returns a single support privilege set by its ID."""
        try:
            return SupportPrivilege.objects.get(pk=privilege_id)
        except SupportPrivilege.DoesNotExist:
            return None

    @staticmethod
    def create_privilege(name, description, privileges_list):
        """Creates a new support privilege set."""
        privilege = SupportPrivilege.objects.create(
            name=name,
            description=description,
            privileges=privileges_list
        )
        return privilege

    @staticmethod
    def update_privilege(privilege_id, name, description, privileges_list):
        """Updates an existing support privilege set."""
        privilege = PrivilegeService.get_privilege_by_id(privilege_id)
        if not privilege:
            return None

        privilege.name = name
        privilege.description = description
        privilege.privileges = privileges_list
        privilege.save()
        return privilege

    @staticmethod
    def delete_privilege(privilege_id):
        """Deletes a support privilege set."""
        privilege = PrivilegeService.get_privilege_by_id(privilege_id)
        if not privilege:
            return False
        
        privilege.delete()
        return True


class GroupService:

    @staticmethod
    def get_all_groups():
        return SupportGroup.objects.all()

    @staticmethod
    def get_group_by_id(group_id):
        try:
            return SupportGroup.objects.prefetch_related('users', 'supportTeams').get(pk=group_id)
        except SupportGroup.DoesNotExist:
            return None

    @staticmethod
    def create_group(name, description, is_active, user_ids, team_ids):
        group = SupportGroup.objects.create(
            name=name,
            description=description,
            isActive=is_active
        )
        group.users.set(user_ids)
        group.supportTeams.set(team_ids)
        return group

    @staticmethod
    def update_group(group_id, name, description, is_active, user_ids, team_ids):
        group = GroupService.get_group_by_id(group_id)
        if not group:
            return None

        group.name = name
        group.description = description
        group.isActive = is_active
        group.users.set(user_ids)
        group.supportTeams.set(team_ids)
        group.save()
        return group

    @staticmethod
    def delete_group(group_id):
        group = GroupService.get_group_by_id(group_id)
        if not group:
            return False
        
        group.delete()
        return True

class TeamService:

    @staticmethod
    def get_all_teams():
        return SupportTeam.objects.all()

    @staticmethod
    def get_team_by_id(team_id):
        try:
            return SupportTeam.objects.prefetch_related('users', 'groups_with_team').get(pk=team_id)
        except SupportTeam.DoesNotExist:
            return None

    @staticmethod
    def create_team(name, description, is_active, user_ids, group_ids):
        team = SupportTeam.objects.create(
            name=name,
            description=description,
            isActive=is_active
        )
        team.users.set(user_ids)
        # Note: The relation from Team to Group is through SupportGroup's M2M field 'supportTeams'
        # To set this, we iterate through the groups.
        for group_id in group_ids:
            group = SupportGroup.objects.get(pk=group_id)
            group.supportTeams.add(team)
        return team

    @staticmethod
    def update_team(team_id, name, description, is_active, user_ids, group_ids):
        team = TeamService.get_team_by_id(team_id)
        if not team:
            return None

        team.name = name
        team.description = description
        team.isActive = is_active
        team.users.set(user_ids)
        
        # Clear existing group relations and set new ones
        team.groups_with_team.clear()
        for group_id in group_ids:
            group = SupportGroup.objects.get(pk=group_id)
            group.supportTeams.add(team)

        team.save()
        return team

    @staticmethod
    def delete_team(team_id):
        team = TeamService.get_team_by_id(team_id)
        if not team:
            return False
        
        team.delete()
        return True
