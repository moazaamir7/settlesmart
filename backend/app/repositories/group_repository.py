from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.models.expense import Expense, ExpenseParticipant
from app.models.group import Group, GroupInvite, GroupMessage, Participant


class GroupRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_group(self, name: str, currency: str, admin_id: str, settlement_contact: str) -> Group:
        group = Group(
            name=name,
            currency=currency.upper(),
            admin_id=admin_id,
            settlement_contact=settlement_contact,
        )
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def list_groups(self, admin_id: str | None = None) -> list[Group]:
        statement = select(Group).options(selectinload(Group.participants)).order_by(Group.created_at.desc())
        if admin_id is not None:
            statement = statement.where(Group.admin_id == admin_id)
        return list(
            self.db.scalars(statement)
        )

    def get_group(self, group_id: str) -> Group | None:
        return self.db.scalar(
            select(Group)
            .where(Group.id == group_id)
            .options(selectinload(Group.participants))
        )

    def delete_group(self, group_id: str) -> None:
        expense_ids = select(Expense.id).where(Expense.group_id == group_id)
        self.db.execute(delete(ExpenseParticipant).where(ExpenseParticipant.expense_id.in_(expense_ids)))
        self.db.execute(delete(Expense).where(Expense.group_id == group_id))
        self.db.execute(delete(GroupInvite).where(GroupInvite.group_id == group_id))
        self.db.execute(delete(GroupMessage).where(GroupMessage.group_id == group_id))
        self.db.execute(delete(Participant).where(Participant.group_id == group_id))
        self.db.execute(delete(Group).where(Group.id == group_id))
        self.db.commit()

    def update_group(self, group: Group, name: str, settlement_contact: str) -> Group:
        group.name = name
        group.settlement_contact = settlement_contact
        self.db.commit()
        self.db.refresh(group)
        return group

    def update_group_image(self, group: Group, image_url: str) -> Group:
        group.image_url = image_url
        self.db.commit()
        self.db.refresh(group)
        return group

    def add_participant(self, group_id: str, name: str) -> Participant:
        participant = Participant(group_id=group_id, name=name)
        self.db.add(participant)
        self.db.flush()
        group = self.db.get(Group, group_id)
        if group is not None and group.owner_participant_id is None:
            group.owner_participant_id = participant.id
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def create_invite(self, group_id: str, token: str) -> GroupInvite:
        invite = GroupInvite(group_id=group_id, token=token)
        self.db.add(invite)
        self.db.commit()
        self.db.refresh(invite)
        return invite

    def get_invite_by_token(self, token: str) -> GroupInvite | None:
        return self.db.scalar(
            select(GroupInvite)
            .where(GroupInvite.token == token)
            .options(selectinload(GroupInvite.group).selectinload(Group.participants))
        )

    def create_message(self, group_id: str, sender_name: str, body: str) -> GroupMessage:
        message = GroupMessage(group_id=group_id, sender_name=sender_name, body=body)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def list_messages(self, group_id: str) -> list[GroupMessage]:
        return list(
            self.db.scalars(
                select(GroupMessage)
                .where(GroupMessage.group_id == group_id)
                .order_by(GroupMessage.created_at.asc())
            )
        )

    def remove_participant(self, participant: Participant) -> None:
        participant.is_active = False
        self.db.commit()

    def get_participants(self, group_id: str, participant_ids: set[str] | None = None) -> list[Participant]:
        statement = select(Participant).where(Participant.group_id == group_id, Participant.is_active.is_(True))
        if participant_ids is not None:
            statement = statement.where(Participant.id.in_(participant_ids))
        return list(self.db.scalars(statement))

    def get_participant(self, group_id: str, participant_id: str) -> Participant | None:
        return self.db.scalar(
            select(Participant).where(
                Participant.group_id == group_id,
                Participant.id == participant_id,
                Participant.is_active.is_(True),
            )
        )
