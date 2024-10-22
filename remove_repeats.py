import logging


def _remove_repeats_list(words: list[str]) -> list[str]:
    res = []
    last_word = ''
    for word in words:
        if word != last_word:
            res.append(word)
        last_word = word
    return res


def _chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def remove_repeats(text: str) -> str:
    logging.debug('func atr text=%r', text)
    words = text.split()
    logging.debug('after split words=%r', words)
    max_seq = len(words) // 2
    logging.debug('calc max_seq=%r', max_seq)
    for seq_len in range(1, max_seq+1):
        logging.debug('seq_len=%r', seq_len)
        words = [' '.join(chunk) for chunk in _chunk_list(words, seq_len)]
        logging.debug('after chunk_list func words=%r', words)
        words = _remove_repeats_list(words)
        logging.debug('after _remove_repeats_list words=%r', words)
        text = ' '.join(words)
        words = text.split()

    if len(words) == 1:
        logging.debug('returning %r cas len(words)=1', words[0])
        return words[0]
    return ' '.join((words[0], remove_repeats(' '.join(words[1:]))))


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN)

    print(remove_repeats('hi hi'))
    assert remove_repeats('hi hi') == 'hi'
    print(remove_repeats('bye bye bye'))
    assert remove_repeats('bye bye bye') == 'bye';
    print(remove_repeats('a b b'))
    assert remove_repeats('a b b') == 'a b'
    print(remove_repeats('a a b'))
    assert remove_repeats('a a b') == 'a b'
    print(remove_repeats('a b a b'))
    assert remove_repeats('a b a b') == 'a b'
    print(remove_repeats('c d a d a c'))
    assert remove_repeats('c d a d a c') == 'c d a c'
    print(remove_repeats('yo hi guys! guys! guys! erm... sry sry bro'))
    assert remove_repeats('yo hi guys! guys! guys! erm... sry sry bro') == 'yo hi guys! erm... sry bro'
