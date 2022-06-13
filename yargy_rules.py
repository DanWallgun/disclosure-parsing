# pylint: disable=E1101
from yargy import rule, or_, and_, not_
from yargy.interpretation import fact, attribute
from yargy.pipelines import morph_pipeline
from yargy.predicates import (
    normalized,
    is_capitalized,
    in_,
    true,
    eq,
    length_eq,
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

SEPARATOR = in_('.,:-–;')
EOL_PREDICATE = type_predicate('EOL')
NOT_EOL = not_(EOL_PREDICATE)

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
        NOT_EOL.optional().repeatable(max=10),
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
        NOT_EOL.optional().repeatable(max=10),
        normalized('собрание'),
        DATE,
    ),
).interpretation(MeetingDate)


PAY_DIVIDENDS_SENTENCE = or_(
    rule(
        or_(
            normalized('выплатить'),
            normalized('объявить'),
            normalized('начислить'),
            normalized('произвести'),
        ),
        true().optional().repeatable(max=20),
        normalized('дивиденды'),
    ),
    rule(
        normalized('дивиденды'),
        true().optional().repeatable(max=20),
        or_(
            normalized('выплатить'),
            normalized('объявить'),
            normalized('начислить'),
            normalized('произвести'),
        ),
    ),
)


DONT_PAY_DIVIDENDS_SENTENCE = or_(
    rule(
        normalized('не'),
        or_(
            normalized('выплачивать'),
            normalized('объявлять'),
            normalized('начислять'),
            normalized('производить'),
        ),
        true().optional().repeatable(max=20),
        normalized('дивиденды'),
    ),
    rule(
        normalized('дивиденды'),
        true().optional().repeatable(max=20),
        normalized('не'),
        or_(
            normalized('выплачивать'),
            normalized('объявлять'),
            normalized('начислять'),
            normalized('производить'),
        ),
    ),
)


Board = fact(
    'Board',
    [attribute('names').repeatable()]
)

RU_CAPITALIZED = and_(
    type_predicate('RU'),
    is_capitalized(),
)

ABBR = and_(
    length_eq(1),
    is_capitalized(),
)

RU_NAME_SIMPLE = rule(
    rule(RU_CAPITALIZED, rule('-', RU_CAPITALIZED).optional()).repeatable(min=2, max=4)
)

RU_NAME_WITH_NONCAPITALIZED = rule(
    rule(RU_CAPITALIZED, type_predicate('RU').optional()).repeatable(min=1, max=3)
)

RU_SURN_NAME_PATR_ABBR = rule(
    RU_CAPITALIZED, rule(ABBR, DOT), rule(ABBR, DOT),
)

def get_boardlist_rule(name_rule):
    return rule(
        morph_pipeline(['решение', 'решили', 'постановили']),
        true().repeatable(max=30),

        or_(
            rule(
                normalized('избрать'),
                NOT_EOL.repeatable().optional(),
                normalized('совет'),
                NOT_EOL.repeatable().optional(),
                normalized('директоров'),
            ),
            rule(
                normalized('совет'),
                NOT_EOL.repeatable().optional(),
                normalized('директоров'),
                NOT_EOL.repeatable().optional(),
                normalized('избраны'),
            )
        ),
        NOT_EOL.repeatable().optional(),
        EOL_PREDICATE,

        rule(
            eq('(').optional(), INT.optional(), in_('.)-•').optional(),
            morph_pipeline(['гражданина РФ']).optional(),
            name_rule.interpretation(Board.names),
            rule('(', not_(eq(')')).repeatable(), ')').optional(),
            QUOTE.optional(), SEPARATOR.optional(),
            EOL_PREDICATE.repeatable(max=2),
        ).repeatable(max=20)
    )

BOARD_PRESENTED = morph_pipeline(['совет директоров'])

BOARD_SENTENCE = or_(
    get_boardlist_rule(RU_NAME_SIMPLE.interpretation(Board.names)),
    # get_boardlist_rule(RU_NAME_WITH_NONCAPITALIZED.interpretation(Board.names)),
    get_boardlist_rule(RU_SURN_NAME_PATR_ABBR.interpretation(Board.names)),
).interpretation(Board)
