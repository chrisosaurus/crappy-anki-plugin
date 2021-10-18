# this library can be given verb kanji / kana pairs and perform various
# operations based on common prefixes and suffixes.
#
# MVP library to help with generating kanji/kana pairs for verbs in various
# forms (dictionary, masu, te).

def findCommonPrefixLen(a, b):
    '''find length of common prefix'''
    l = min(len(a), len(b))

    for i in range(0, l):
        if a[i] != b[i]:
            return i

    return l

def findCommonPrefix(a, b):
    '''find string common prefix'''
    common = ""

    l = min(len(a), len(b))

    for i in range(0, l):
        if a[i] != b[i]:
            break
        common += a[i]

    return common

def findCommonSuffix(a, b):
    '''find string common suffix'''
    common = ""

    a = a[::-1]
    b = b[::-1]

    common = findCommonPrefix(a, b)

    return common[::-1]

def findCommonSuffixLen(a, b):
    '''find lent of common suffix'''
    common = findCommonSuffix(a, b)
    return len(common)

def removeCommonPrefix(a, b):
    L = findCommonPrefixLen(a, b)
    a = a[L:]
    b = b[L:]
    return [a, b]

def removeCommonSuffix(a, b):
    L = findCommonSuffixLen(a, b)
    if L > 0:
        a = a[:-L]
        b = b[:-L]
    return [a, b]

def testPrefixSuffix(test_util):
    test_util.test_print("\ntesting findCommon*")
    test_util.test_assert('', findCommonPrefix('いく', '行く'))
    test_util.test_assert('く', findCommonSuffix('いく', '行く'))
    test_util.test_assert('い', findCommonPrefix('いく', 'いきます'))

    test_util.test_assert(1, findCommonPrefixLen('いく', 'いきます'))
    test_util.test_assert(0, findCommonPrefixLen('いく', ''))
    test_util.test_assert(0, findCommonPrefixLen('いく', '行く'))

    test_util.test_print("\ntesting findCommon*Len")
    test_util.test_assert(0, findCommonSuffixLen('いく', 'いきます'))
    test_util.test_assert(0, findCommonSuffixLen('いく', ''))
    test_util.test_assert(1, findCommonSuffixLen('いく', '行く'))

    test_util.test_print("\ntesting removeCommon*")
    test_util.test_assert(['行く', 'いく'], removeCommonPrefix( '行く', 'いく'))
    test_util.test_assert(['い', '行'], removeCommonSuffix('いく', '行く'))
    test_util.test_assert(['い', '行'], removeCommonSuffix('い', '行'))
    test_util.test_assert(['く', 'きます'], removeCommonPrefix('いく', 'いきます'))
    test_util.test_assert(['', ''], removeCommonPrefix( '行', '行'))

def generateKana(kanji, kana, iKanji):
    '''行く,　いく,　行きます -> いきます'''
    kanji, kana = removeCommonSuffix(kanji, kana)
    empty, stem = removeCommonPrefix(kanji, iKanji)
    if empty != '':
        test_util.test_print("unexpected remainder '%s'" %(empty))
    return kana + stem

def generateKanji(kanji, kana, iKana):
    '''行く,　いく,　いきます -> 行きます'''
    kanji, kana = removeCommonSuffix(kanji, kana)
    empty, stem = removeCommonPrefix(kana, iKana)
    if empty != '':
        test_util.test_print("unexpected remainder '%s'" %(empty))
    return kanji + stem

def testGenerate(test_util):
    cases = [
        {'kanji' : '行く',
         'kana'  : 'いく',
         'masu'  : '行きます',
         'masuKana' : 'いきます',
         'te'    : '行って',
         'teKana' : 'いって'
        },
    ]

    test_util.test_print("\ntesting generate*")
    for case in cases:
        kanji = case['kanji']
        kana = case['kana']
        masu = case['masu']
        masuKana = case['masuKana']
        te = case['te']
        teKana = case['teKana']

        out = generateKana(kanji, kana, masu)
        test_util.test_assert(masuKana, out)

        out = generateKana(kanji, kana, te)
        test_util.test_assert(teKana, out)

        out = generateKanji(kanji, kana, masuKana)
        test_util.test_assert(masu, out)

        out = generateKanji(kanji, kana, teKana)
        test_util.test_assert(te, out)

def checkInflections(inflections):
    expected_keys = ['kanji', 'kana', 'masu', 'masuKana', 'te', 'teKana']

    for k in inflections.keys():
        if k not in expected_keys:
            test_util.test_print("Unexpected inflections key '%s'" %(k))
            return False

    return True

inflections_pairs = [
    ('kanji', 'kana'),
    ('masu', 'masuKana'),
    ('te', 'teKana'),
]

def findPrimaryPair(inflections):
    '''provided with a list of partially filled in |inflections|, find complete pair'''
    for (l, r) in inflections_pairs:
        if l not in inflections:
            continue
        if not inflections[l]:
            continue
        if r not in inflections:
            continue
        if not inflections[r]:
            continue
        return (inflections[l], inflections[r])

    return (None, None)

def fillInBlanks(inflections):
    '''provided with a list of partially filled in |inflections|, fill in blanks'''
    if not checkInflections(inflections):
        return None

    (primary, primaryKana) = findPrimaryPair(inflections)
    if not primary or not primaryKana:
        test_util.test_print("ERROR: inflections lacked primary pair")
        return None

    for (targetKey, targetKanaKey) in inflections_pairs:
        if targetKey not in inflections:
            continue
        if targetKanaKey not in inflections:
            continue
        target = inflections[targetKey]
        targetKana = inflections[targetKanaKey]
        if not target and not targetKana:
            msg = ("warning: pair (%s, %s) both present and empty, skipping" %
                  (targetKey, targetKanaKey))
            test_util.test_print(msg)
            continue
        if target and not targetKana:
            targetKana = generateKana(primary, primaryKana, target)
        if targetKana and not target:
            target = generateKanji(primary, primaryKana, targetKana)
        inflections[targetKey] = target
        inflections[targetKanaKey] = targetKana

    return inflections

def testFillInBlanks(test_util):
    cases = [
        [
            {
                'kanji': '行く',
                'kana': 'いく',
            },
            {
                'kanji': '行く',
                'kana': 'いく',
            },
        ],
        [
            {
                'kanji': '行く',
                'kana': 'いく',
                'te': '行って',
                'teKana': '',
                'masu': '',
                'masuKana': 'いきます',
            },
            {
                'kanji': '行く',
                'kana': 'いく',
                'te': '行って',
                'teKana': 'いって',
                'masu': '行きます',
                'masuKana': 'いきます',
            },
        ],
        [
            {
                'kanji': '行く',
                'kana': '',
                'te': '行って',
                'teKana': 'いって',
                'masu': '',
                'masuKana': 'いきます',
            },
            {
                'kanji': '行く',
                'kana': 'いく',
                'te': '行って',
                'teKana': 'いって',
                'masu': '行きます',
                'masuKana': 'いきます',
            },
        ],

    ]
    test_util.test_print("\ntesting fillinBlanks")
    for case in cases:
        test_util.test_assert(case[1], fillInBlanks(case[0]))

def test(test_util):
    testPrefixSuffix(test_util)
    testGenerate(test_util)
    testFillInBlanks(test_util)
    test_util.test_report_results(print)

