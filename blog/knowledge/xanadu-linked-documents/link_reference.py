"""Versioned link identity example; no persistence service or passage resolver."""
from dataclasses import dataclass, asdict
import json
import unittest
from uuid import uuid4


@dataclass(frozen=True)
class Link:
    link_id: str
    target_document_id: str
    link_type: str

    def __post_init__(self):
        for value in (self.link_id, self.target_document_id, self.link_type):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("link fields must be nonempty strings")

    @classmethod
    def create(cls, target_document_id, link_type='hyperlink'):
        return cls(str(uuid4()), target_document_id, link_type)

    def to_dict(self):
        return {'schema_version': 1, **asdict(self)}

    @classmethod
    def from_dict(cls, data):
        if data.get('schema_version') != 1:
            raise ValueError('unsupported schema')
        # A missing saved ID is an error, never an instruction to create a new identity.
        return cls(data['link_id'], data['target_document_id'], data['link_type'])


class LinkTests(unittest.TestCase):
    def test_round_trip(self):
        original = Link('link-17', 'document-2', 'quote')
        self.assertEqual(Link.from_dict(json.loads(json.dumps(original.to_dict()))), original)

    def test_new_identity_and_invalid_load(self):
        self.assertNotEqual(Link.create('d').link_id, Link.create('d').link_id)
        with self.assertRaises(KeyError):
            Link.from_dict({'schema_version': 1, 'target_document_id': 'd', 'link_type': 'quote'})
        with self.assertRaises(ValueError):
            Link.from_dict({'schema_version': 2})


if __name__ == '__main__':
    unittest.main()
