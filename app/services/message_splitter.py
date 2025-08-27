"""
Message Splitter Service - Quebra mensagens preservando emojis e palavras
"""
try:
    import regex
    HAS_REGEX = True
except ImportError:
    import re as regex
    HAS_REGEX = False

try:
    from nltk.tokenize import sent_tokenize
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
        except Exception:
            raise ImportError("Não foi possível baixar dados punkt do NLTK")
    HAS_NLTK = True
except (ImportError, LookupError) as e:
    HAS_NLTK = False
    print(f"NLTK não disponível: {e}")

from typing import List, Optional
from app.utils.logger import emoji_logger


class MessageSplitter:
    """
    Splitter inteligente que preserva emojis, palavras e frases
    """

    def __init__(
        self, max_length: int = 250, add_indicators: bool = False,
        enable_smart_splitting: bool = True,
        smart_splitting_fallback: bool = True
    ):
        self.max_length = max_length
        self.add_indicators = add_indicators
        self.enable_smart_splitting = enable_smart_splitting
        self.smart_splitting_fallback = smart_splitting_fallback
        if not HAS_REGEX:
            emoji_logger.system_warning(
                "Módulo 'regex' não instalado. Usando 're' padrão."
            )
        if self.enable_smart_splitting and not HAS_NLTK:
            emoji_logger.system_warning(
                "NLTK não disponível. Divisão inteligente desabilitada."
            )
            self.enable_smart_splitting = False
        smart_status = (
            "ativada" if self.enable_smart_splitting else "desativada"
        )
        emoji_logger.system_info(
            f"Message Splitter inicializado (max={max_length}, "
            f"smart={smart_status})"
        )

    def split_message(self, text: str) -> List[str]:
        """
        Divide mensagem em chunks, com tratamento especial para a mensagem das 4 soluções,
        que é formatada com quebras de linha e nunca é dividida.
        """
        if not text:
            return []

        # Lógica padrão de divisão para todas as outras mensagens
        if len(text) <= self.max_length:
            return [text.strip()]
        
        if self.enable_smart_splitting and HAS_NLTK:
            try:
                chunks = self._split_by_sentences(text)
                if self.add_indicators and len(chunks) > 1:
                    chunks = self._add_indicators(chunks)
                return chunks
            except Exception as e:
                emoji_logger.system_warning(
                    f"Divisão inteligente falhou: {e}. Usando fallback."
                )
                if not self.smart_splitting_fallback:
                    raise
        
        chunks = (
            self._split_with_regex(text) if HAS_REGEX
            else self._split_simple(text)
        )
        if self.add_indicators and len(chunks) > 1:
            chunks = self._add_indicators(chunks)
        return chunks

    def _split_by_sentences(self, text: str) -> List[str]:
        """Divide texto por frases usando NLTK"""
        try:
            sentences = sent_tokenize(text, language='portuguese')
            if not sentences:
                return [text.strip()]
            if len(sentences) == 1 and len(sentences[0]) > self.max_length:
                return self._force_split_long_sentence(sentences[0])
            chunks, current_chunk = [], ""
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                test_chunk = (
                    current_chunk + (" " if current_chunk else "") + sentence
                )
                if len(test_chunk) <= self.max_length:
                    current_chunk = test_chunk
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    if len(sentence) > self.max_length:
                        chunks.extend(
                            self._force_split_long_sentence(sentence)
                        )
                        current_chunk = ""
                    else:
                        current_chunk = sentence
            if current_chunk:
                chunks.append(current_chunk.strip())
            return chunks if chunks else [text.strip()]
        except Exception as e:
            emoji_logger.system_warning(f"Erro na divisão por frases: {e}")
            raise

    def _force_split_long_sentence(self, sentence: str) -> List[str]:
        """Força divisão de frase muito longa"""
        return (
            self._split_with_regex(sentence) if HAS_REGEX
            else self._split_simple(sentence)
        )

    def _split_with_regex(self, text: str) -> List[str]:
        """Divide usando regex module (preserva emojis)"""
        chunks, graphemes = [], regex.findall(r'\X', text)
        while graphemes:
            chunk_size = min(self.max_length, len(graphemes))
            chunk_text, chunk_count = "", 0
            for i, grapheme in enumerate(graphemes[:chunk_size]):
                if len(chunk_text + grapheme) > self.max_length:
                    break
                chunk_text += grapheme
                chunk_count = i + 1
            if len(graphemes) > chunk_count and chunk_text:
                last_space = -1
                for i, grapheme in enumerate(graphemes[:chunk_count]):
                    if grapheme.isspace():
                        last_space = i + 1
                if last_space > 0:
                    chunk_text = ''.join(graphemes[:last_space]).rstrip()
                    chunk_count = last_space
            chunk_text = chunk_text.strip()
            if chunk_text:
                chunks.append(chunk_text)
            graphemes = graphemes[chunk_count:]
            while graphemes and graphemes[0].isspace():
                graphemes.pop(0)
        return chunks

    def _split_simple(self, text: str) -> List[str]:
        """Divide de forma simples (fallback)"""
        chunks, words = [], text.split()
        current_chunk, current_length = [], 0
        for word in words:
            word_length = len(word)
            if word_length > self.max_length:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                while len(word) > self.max_length:
                    chunks.append(word[:self.max_length])
                    word = word[self.max_length:]
                current_chunk, current_length = (
                    [word] if word else []
                ), (len(word) if word else 0)
            elif current_length + word_length + 1 > self.max_length:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk, current_length = [word], word_length
            else:
                current_chunk.append(word)
                current_length += word_length + 1
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def _add_indicators(self, chunks: List[str]) -> List[str]:
        """Adiciona indicadores [1/3], [2/3] etc"""
        total = len(chunks)
        result = []
        for i, chunk in enumerate(chunks, 1):
            indicator = f"[{i}/{total}] "
            if len(indicator + chunk) > self.max_length:
                max_content = self.max_length - len(indicator) - 3
                chunk = chunk[:max_content] + "..."
            result.append(indicator + chunk)
        return result

    


message_splitter: Optional[MessageSplitter] = None


def get_message_splitter() -> MessageSplitter:
    """Retorna instância global do splitter"""
    global message_splitter
    if not message_splitter:
        message_splitter = MessageSplitter()
    return message_splitter


def set_message_splitter(splitter: MessageSplitter) -> None:
    """Define instância global do splitter"""
    global message_splitter
    message_splitter = splitter

