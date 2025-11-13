import pytest

from app.services.message_splitter import MessageSplitter


def test_split_respects_sentence_boundaries():
    splitter = MessageSplitter(max_length=60, enable_smart_splitting=True)
    text = (
        "Oi, Mateus! Espero que você esteja bem. Queria saber se você ainda "
        "está pensando sobre o programa de sócios do Náutico. O plano 100% "
        "Timba realmente oferece benefícios incríveis, e seria uma ótima forma de apoiar o nosso time nessa fase decisiva."
    )

    chunks = splitter.split_message(text)

    assert len(chunks) >= 3
    # Cada chunk deve terminar preferencialmente em pontuação ou ser menor que o limite
    for c in chunks[:-1]:
        assert c.endswith(('.', '!', '?', '…', ',', ';', ':')) or len(c) <= 60

