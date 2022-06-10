# pylint: disable=E1101
from yargy import rule, or_, not_
from yargy.interpretation import fact
from yargy.pipelines import morph_pipeline
from yargy.predicates import normalized, in_, type as type_predicate

MeetingForm = fact(
    'MeetingForm',
    ['value'],
)

MEETING_FORM = or_(
    morph_pipeline(['собрание'])
        .interpretation(MeetingForm.value.const('собрание')),
    morph_pipeline(['совместное присутствие'])
        .interpretation(MeetingForm.value.const('собрание')),
    morph_pipeline(['заочное голосование'])
        .interpretation(MeetingForm.value.const('заочное голосование')),
    morph_pipeline(['заочное'])
        .interpretation(MeetingForm.value.const('заочное голосование')),
)

SEPARATOR = in_('.:-–;')
EOL_PREDICATE = type_predicate('EOL')

MEETING_FORM_SENTENCE = or_(
    rule(
        normalized('форма'),
        not_(SEPARATOR).repeatable(max=10),
        normalized('собрание').optional(),
        rule(
            not_(SEPARATOR).repeatable(max=20).optional(),
            SEPARATOR,
        ).optional().repeatable(max=2),
        EOL_PREDICATE.optional(),
        not_(EOL_PREDICATE).optional().repeatable(max=10),
        MEETING_FORM,
    ),
    rule(
        normalized('форма'),
        MEETING_FORM,
    ),
).interpretation(MeetingForm)
