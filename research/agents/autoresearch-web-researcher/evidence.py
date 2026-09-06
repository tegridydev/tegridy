"""Local source-version and citation trace through two explicit answer revisions."""

import hashlib
import json
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Passage:
    source: str
    version: str
    start: int
    end: int
    text: str


class Research:
    def __init__(self, question):
        self.question = question
        self.sources = {}
        self.latest = {}
        self.answers = []

    def capture(self, identity, text):
        version = hashlib.sha256(text.encode()).hexdigest()
        self.sources[(identity, version)] = text
        self.latest[identity] = version
        return version

    def passage(self, identity, version, start, end):
        text = self.sources[(identity, version)]
        if (
            type(start) is not int
            or type(end) is not int
            or not 0 <= start < end <= len(text)
        ):
            raise ValueError("invalid exact span")
        return Passage(identity, version, start, end, text[start:end])

    def check(self, passage):
        source = self.sources.get((passage.source, passage.version))
        if source is None:
            return "missing-version"
        if (type(passage.start) is not int or type(passage.end) is not int
                or not 0 <= passage.start < passage.end <= len(source)
                or source[passage.start : passage.end] != passage.text):
            return "span-mismatch"
        return (
            "current"
            if self.latest[passage.source] == passage.version
            else "historical-version"
        )

    def revise(self, claims):
        records = []
        for statement, passages in claims:
            if not statement.strip() or not passages:
                raise ValueError("each claim needs a statement and citation")
            statuses = [self.check(p) for p in passages]
            if any(s in {"missing-version", "span-mismatch"} for s in statuses):
                raise ValueError("unresolvable citation")
            records.append(
                dict(
                    statement=statement,
                    citations=[asdict(p) for p in passages],
                    citation_status=statuses,
                    support_review="unreviewed; exact span does not establish entailment",
                )
            )
        answer = dict(
            revision=len(self.answers),
            question=self.question,
            claims=records,
            parent_revision=len(self.answers) - 1 if self.answers else None,
        )
        self.answers.append(answer)
        return answer

    def export(self):
        return dict(
            question=self.question,
            sources=[
                dict(id=i, version=v, text=t) for (i, v), t in self.sources.items()
            ],
            latest=self.latest,
            answers=self.answers,
        )


def fixture():
    study = Research("What is the current timeout?")
    v1 = study.capture("manual", "The default timeout is 30 seconds.")
    p1 = study.passage("manual", v1, 0, 34)
    study.revise([("The captured manual says 30 seconds.", [p1])])
    v2 = study.capture("manual", "The default timeout is 10 seconds.")
    p2 = study.passage("manual", v2, 0, 34)
    study.revise([("The updated manual says 10 seconds.", [p2])])
    study.revise([("The old and new captured defaults differ.", [p1, p2])])
    return study


if __name__ == "__main__":
    print(json.dumps(fixture().export(), indent=2))
