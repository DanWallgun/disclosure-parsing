# pylint: disable=E1101
from yargy import rule, or_, and_, not_
from yargy.interpretation import fact
from yargy.pipelines import morph_pipeline
from yargy.predicates import (
    normalized,
    in_,
    true,
    eq,
    dictionary,
    gte,
    lte,
    type as type_predicate,
)
from yargy.tokenizer import LEFT_QUOTES, RIGHT_QUOTES, QUOTES

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


Date = fact(
    'Date',
    ['year', 'month', 'day']
)

INT = type_predicate('INT')
DOT = eq('.')

MONTHS = {
    'январь': 1,
    'февраль': 2,
    'март': 3,
    'апрель': 4,
    'май': 5,
    'июнь': 6,
    'июль': 7,
    'август': 8,
    'сентябрь': 9,
    'октябрь': 10,
    'ноябрь': 11,
    'декабрь': 12,
}

MONTH_NAME = dictionary(MONTHS).interpretation(
    Date.month.normalized().custom(MONTHS.get)
)

MONTH = and_(
    INT,
    gte(1),
    lte(12)
).interpretation(
    Date.month.custom(int)
)

YEAR = and_(
    INT,
    gte(1000),
    lte(3000)
).interpretation(
    Date.year.custom(int)
)

YEAR_SUFFIX = rule(
    or_(
        eq('г'),
        normalized('год')
    ),
    DOT.optional()
)

QUOTE = in_(QUOTES)
LEFT_QUOTE = in_(LEFT_QUOTES)
RIGHT_QUOTE = in_(RIGHT_QUOTES)

DAY = rule(
    LEFT_QUOTE.optional(),
    and_(
        INT,
        gte(1),
        lte(31)
    ).interpretation(Date.day.custom(int)),
    RIGHT_QUOTE.optional(),
)

DATE = or_(
    rule(
        YEAR,
        YEAR_SUFFIX
    ),
    rule(
        MONTH_NAME,
        YEAR
    ),
    rule(
        DAY,
        DOT,
        MONTH,
        DOT,
        YEAR
    ),
    rule(
        DAY,
        MONTH_NAME,
        YEAR
    ),
).interpretation(Date)


MeetingDate = Date

MEETING_DATE_SENTENCE = or_(
    rule(
        or_(
            morph_pipeline(['дата наступления события']),
            morph_pipeline(['дата (момент) наступления'])
        ),
        not_(INT).optional().repeatable(max=20),
        DATE,
    ),
    rule(
        morph_pipeline(['дата проведения']),
        true().optional().repeatable(max=10),
        SEPARATOR,
        DATE,
    ),
    rule(
        normalized('дата'),
        not_(SEPARATOR).optional().repeatable(),
        normalized('проведение'),
        not_(SEPARATOR).optional().repeatable(),
        normalized('собрание'),
        not_(INT).repeatable(max=40),
        DATE,
    ),
    rule(
        normalized('дата'),
        not_(EOL_PREDICATE).optional().repeatable(max=10),
        normalized('собрание'),
        DATE,
    ),
).interpretation(MeetingDate)
