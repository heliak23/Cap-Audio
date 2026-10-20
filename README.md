# 🎙️ CapAudio

**CapAudio** é uma aplicação desktop de ditado de voz com inteligência artificial para Windows. Ele permite falar naturalmente e ter seu texto transcrito, pontuado, limpo de vícios de fala e inserido automaticamente em qualquer aplicativo ativo através de um simples atalho global no teclado.

---

## 🔒 100% Offline e Privado por Padrão

O CapAudio opera **100% offline no seu computador** utilizando o modelo neural **faster-whisper**:
* **Privacidade Total:** Sua voz nunca sai da sua máquina.
* **Sem Custos ou Mensalidades:** Não precisa de nenhuma conta, cadastro, cartão de crédito ou chaves de API.
* **Funciona sem Internet:** Dite textos mesmo desconectado de qualquer rede Wi-Fi.

*(Se desejar latência ultrarrápida de ~200ms na nuvem, você pode opcionalmente configurar uma chave da Groq ou OpenAI no `.env`).*

---

## ⚡ Como Funciona

1. **Atalho Push-to-Talk:** Pressione e segure a tecla **`F8`** (ou configure para *Toggle*).
2. **Gravação Instantânea:** Um sinal sonoro discreto e uma cápsula flutuante (*Dynamic Island*) com ondas sonoras animadas indicam que o microfone está ouvindo.
3. **Transcrição e Limpeza IA:** Ao soltar o `F8`, o áudio é transcrito localmente e processado para remover hesitações (*"éee"*, *"tipo assim"*, *"né"*), corrigir auto-interrupções e adicionar pontuação.
4. **Injeção Automática no Cursor:** O texto final é colado instantaneamente onde o seu cursor estiver posicionado (WhatsApp, Bloco de Notas, VS Code, Word, Slack, navegadores, etc.).

---

## 🚀 Como Iniciar

Basta dar dois cliques no arquivo:
```cmd
iniciar.bat
```
Ou executar via terminal:
```powershell
python main.py
```

---

## ⚙️ Configurações (.env)

O arquivo `.env` permite customizar atalhos e provedores:

```ini
# Provedores de STT:
# 'local' -> 100% OFFLINE (roda no seu PC via faster-whisper)
# 'groq'  -> Whisper turbo ultrarrápido na nuvem (~200ms)
# 'openai'-> Whisper oficial OpenAI
STT_PROVIDER=local

# Tamanho do modelo Whisper local (para modo offline):
# 'tiny' (~75MB, ultrarrápido)
# 'base' (~145MB, recomendado, excelente precisão em pt-BR)
# 'small' (~480MB, máxima precisão)
LOCAL_MODEL_SIZE=base
LOCAL_DEVICE=cpu

# Chaves de API (Opcional - deixe vazio no modo offline)
GROQ_API_KEY=
OPENAI_API_KEY=

# Atalho do Teclado (f8, f9, f10, scroll_lock, etc.)
HOTKEY=f8

# Modo de Ativação:
# 'push_to_talk' -> Segura a tecla para falar, solta para colar
# 'toggle' -> Pressiona uma vez para falar, pressiona de novo para parar
MODE=push_to_talk

# Som de feedback (bip discreto ao gravar e parar)
AUDIO_FEEDBACK=true

# Barra de status flutuante animada (HUD)
SHOW_HUD=true
```

---

## 🛠️ Arquitetura do Projeto

* `src/audio_recorder.py`: Gravação de áudio do microfone em buffer de memória (16kHz mono).
* `src/stt_engine.py`: Motor de reconhecimento de fala local (faster-whisper) e APIs.
* `src/text_cleaner.py`: Motor de limpeza de vícios de fala e pontuação contextual.
* `src/text_injector.py`: Injeção de texto no aplicativo ativo com proteção da área de transferência.
* `src/hotkey_listener.py`: Monitoramento global de teclas com a biblioteca `pynput`.
* `src/overlay_hud.py`: Widget flutuante com equalizador de ondas sonoras animadas a 40 FPS.
