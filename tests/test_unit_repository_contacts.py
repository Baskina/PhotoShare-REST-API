import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User, Contact
from src.schemas.contacts import ContactValidationSchema, ContactValidationSchemaResponse
from src.repository.contacts import (
    read_all_contacts,
    read_contact,
    add_contact,
    update_contact,
    delete_contact
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1)

    async def test_read_all_contacts(self):
        contacts = [Contact(id=1, name="test", last_name="test", email="test1", phone_number=1, birth_date="01.01.2000",
                            rest="test"),
                    Contact(id=2, name="test", last_name="test", email="test2", phone_number=1, birth_date="01.01.2000",
                            rest="test"),
                    Contact(id=3, name="test", last_name="test", email="test3", phone_number=1, birth_date="01.01.2000",
                            rest="test")]

        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await read_all_contacts(limit=10,
                                         offset=0,
                                         name="test",
                                         last_name="test",
                                         email="test1",
                                         find_BD=False,
                                         user_id=self.user.id,
                                         db=self.session)
        self.assertEqual(result, contacts)

    async def test_read_contact(self):
        contact = [Contact(name="test", last_name="test", email="test1@mail.com",
                           phone_number=1,
                           birth_date="2000-01-01", rest="test")]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await read_contact(contact_id=1,
                                    user_id=self.user.id,
                                    db=self.session)
        self.assertEqual(result, contact)

    async def test_add_contact(self):
        body = ContactValidationSchema(name="test", last_name="test", email="test1@mail.com",
                                       phone_number=1,
                                       birth_date="2000-01-01", rest="test")
        result = await add_contact(body=body, user_id=self.user.id, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1,
                                                                 name="test",
                                                                 last_name="test",
                                                                 email="test1@mail.com",
                                                                 phone_number=1,
                                                                 birth_date="2000-01-01", rest="test")
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(contact_id=1, user_id=self.user.id, db=self.session)
        self.assertIsInstance(result, Contact)

    async def test_update_contact_found(self):
        body = ContactValidationSchemaResponse(
            name="test",
            last_name="test",
            email="test1@mail.com",
            phone_number=1,
            birth_date="2000-01-01",
            rest="test",
            id=1
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(name="test",
                                                                 last_name="test",
                                                                 phone_number=1,
                                                                 email="test1@mail.com",
                                                                 birth_date="2000-01-01",
                                                                 rest="test",
                                                                 user_id=self.user.id)
        self.session.execute.return_value = mocked_contact
        result = await update_contact(contact_id=1, body=body, user_id=self.user.id, db=self.session)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)


if __name__ == '__main__':
    unittest.main()
