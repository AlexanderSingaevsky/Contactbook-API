import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.contacts.repository import add_contact, get_contact, update_contact, remove_contact
from src.contacts.schemas import ContactIn


class TestContactFunctions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(
            id=1, username='test', email="test@test.com", password="1234567", is_confirmed=True
        )
        self.contact = ContactIn(
            first_name="test_name",
            last_name="test_name",
            birthday="1970-01-01",
            description='test string',
        )

    async def test_get_contact(self):
        mock_result = MagicMock()
        mock_result.scalars().unique().one_or_none.return_value = self.contact
        self.session.execute.return_value = mock_result
        contact = await get_contact(1, self.user, self.session)
        self.assertEqual(contact, self.contact)

    async def test_add_contact(self):
        new_contact = await add_contact(self.contact, self.user, self.session)
        self.session.add.assert_called_once_with(new_contact)

        self.assertEqual(new_contact.first_name, self.contact.first_name)
        self.assertEqual(new_contact.last_name, self.contact.last_name)

    async def test_update_contact(self):
        mock_result = MagicMock()
        mock_result.scalars().unique().one_or_none.return_value = self.contact
        self.session.execute.return_value = mock_result

        updated_contact = ContactIn(
            first_name="updated_name",
            last_name="updated_name",
            birthday="1970-01-02",
            description='updated string',
        )
        contact = await update_contact(updated_contact, 1, self.user, self.session)

        self.assertEqual(contact, updated_contact)
        self.session.flush.assert_called_once()

    async def test_remove_contact(self):
        mock_result = MagicMock()
        mock_result.scalars().unique().one_or_none.return_value = self.contact
        self.session.execute.return_value = mock_result

        result = await remove_contact(1, self.user, self.session)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
