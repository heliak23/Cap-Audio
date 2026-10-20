import re
from src.config import Config

CLEANUP_SYSTEM_PROMPT = """Você é o motor de limpeza e pontuação de ditado de voz inteligente.
Sua única tarefa é transformar a transcrição bruta do usuário em um texto limpo, polido e natural.

Regras Estritas:
1. Remova vícios de fala e hesitações (ex: "éee", "hum", "hã", "tipo assim", "né", "sabe").
2. Resolva correções automáticas no meio da frase (ex: "vamos nos encontrar na quarta, não, na quinta-feira" -> "Vamos nos encontrar na quinta-feira").
3. Remova gaguejos e repetições involuntárias (ex: "eu eu acho" -> "eu acho").
4. Adicione pontuação adequada (vírgulas, pontos finais, interrogações) e capitalize corretamente.
5. NÃO resuma, NÃO responda à pergunta e NÃO adicione explicações. Retorne EXCLUSIVAMENTE o texto final polido."""

class TextCleaner:
    def __init__(self, groq_client=None, openai_client=None):
        self.groq_client = groq_client
        self.openai_client = openai_client

    def clean(self, raw_text: str) -> str:
        if not raw_text or not raw_text.strip():
            return ""

        raw_text = raw_text.strip()

        # 1. Tentar limpeza avançada com LLM (Groq é super rápido ~150ms)
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": CLEANUP_SYSTEM_PROMPT},
                        {"role": "user", "content": raw_text}
                    ],
                    temperature=0.1,
                    max_tokens=256
                )
                cleaned = response.choices[0].message.content.strip()
                if cleaned:
                    return cleaned
            except Exception as e:
                print(f"[Cleaner LLM Groq Erro]: {e}")

        # 2. Tentar limpeza com OpenAI se disponível
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": CLEANUP_SYSTEM_PROMPT},
                        {"role": "user", "content": raw_text}
                    ],
                    temperature=0.1,
                    max_tokens=256
                )
                cleaned = response.choices[0].message.content.strip()
                if cleaned:
                    return cleaned
            except Exception as e:
                print(f"[Cleaner LLM OpenAI Erro]: {e}")

        # 3. Fallback: Limpeza Determinística Local com Regex
        return self._rule_based_clean(raw_text)

    def _rule_based_clean(self, text: str) -> str:
        # Remover hesitações comuns em português e inglês
        fillers = [
            r"\b(éee+|éh+|hã+|hum+|uhm+|umm+)\b",
            r"\b(tipo assim|tipo|sabe|né)\b",
            r"\b(quer dizer|ou melhor)\b",
        ]
        result = text
        for pattern in fillers:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE)

        # Remover palavras duplicadas consecutivas (gaguejo: "o o", "que que")
        result = re.sub(r"\b(\w+)\s+\1\b", r"\1", result, flags=re.IGNORECASE)

        # Limpar múltiplos espaços
        result = re.sub(r"\s+", " ", result).strip()

        # Capitalizar primeira letra
        if result and len(result) > 0:
            result = result[0].upper() + result[1:]

        # Adicionar pontuação se não terminar com pontuação
        if result and result[-1] not in ".?!,:;":
            result += "."

        return result
