"""Issue model."""
import collections


Issue = collections.namedtuple("Issue", ["title", "body", "labels"])
