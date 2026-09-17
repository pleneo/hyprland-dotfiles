# 🌙 Hyprland Dotfiles (CachyOS / Arch Linux)

Setup completo, moderno e minimalista do Hyprland configurado nativamente em **Lua**, com integração **Pywal**, **Waybar**, **Spotify Dynamic Island**, **Hyprlock**, **Rofi Spotlight**, **Cliphist** e **Starship Prompt**.

---

## 🎨 Componentes & Funcionalidades

| Componente | Ferramenta | Descrição |
| :--- | :--- | :--- |
| **Compositor** | Hyprland (Lua) | Modular (`monitors`, `variables`, `decorations`, `keybinds`, `windowrules`, `autostart`) |
| **Ponte IPC** | `hypr-ipc-proxy` | Serviço systemd em Python que traduz chamadas legacy do Waybar para a arquitetura Lua |
| **Status Bar** | Waybar | Pílula central com Calendário BR, Clima 4 dias, workspaces clicáveis e Spotify Island |
| **Spotify Island** | Dynamic Island + GTK3 | Capa ao vivo, linha do tempo arrastável, volume exclusivo e botão de like dinâmico |
| **Lockscreen** | Hyprlock | Blur dinâmico da tela atual e input glow com cores do Pywal |
| **Display Manager** | SDDM Astronaut | Tema nítido Totoro Stargazing |
| **Lançador** | Rofi Spotlight | Busca de aplicativos com ordenação por frequência de uso + busca direta no Google |
| **Clipboard** | Cliphist + Rofi | Histórico flutuante com suporte a texto e imagens (`Super + C`) |
| **Menu de Energia**| Wlogout | Glassmorphism com 5 botões centrais organizados e cores dinâmicas |
| **Shell Prompt** | Starship + Fish | Diretório com ícones, branch git limpo e sem poluição visual |
| **Wallpaper** | Gslapper + Pywal | Papéis de parede animados 1080p + paleta de cores dinâmica |

---

## 🎵 Spotify Dynamic Island

A ilha do Spotify na barra superior se expande em um card flutuante interativo com recursos avançados:

* **Capa e Metadados:** Renderização em alta definição da capa do álbum, nome da música e artista/álbum.
* **Linha do Tempo Interativa:** Slider para avançar/retroceder na música em tempo real.
* **Controles de Reprodução:** Anterior, Play/Pause e Próxima com atualização instantânea.
* **Slider de Volume Exclusivo:** Controla unicamente o volume interno do Spotify (`playerctl`), sem interferir no volume principal do computador. Possui botão rápido de Mute/Desmute.
* **Botão de Curtir (Like) com Efeito de Purpurina:** 
  * Conectado diretamente à **API Web do Spotify** (`/v1/me/library`).
  * Identifica automaticamente se a música atual está na sua playlist de *Músicas Curtidas* (`󰋑` verde do Spotify) ou não (`󰋑` cinza discreto).
  * Ao clicar para curtir, dispara uma animação personalizada de **purpurinas verdes e estrelinhas** em *Cairo/GTK* ao redor do coração!

---

## ⌨️ Principais Atalhos de Teclado

* **`Super + Enter`**: Abrir terminal (Alacritty)
* **`Super + Espaço`**: Lançador de Aplicativos & Busca Web (Rofi Spotlight)
* **`Super + C`** / **`Super + Alt + V`**: Histórico da Área de Transferência (Cliphist)
* **`Super + W`**: Galeria de Wallpapers Animados (Gslapper)
* **`Super + L`**: Bloquear Tela (Hyprlock)
* **`Super + Q`**: Fechar Janela
* **`Super + V`**: Alternar Janela Flutuante (*Float*)
* **`Super + F`**: Alternar Tela Cheia (*Fullscreen*)
* **`Print`**: Tirar Print da Tela Inteira
* **`Shift + Print`**: Tirar Print de Área Selecionada
* **`Super + [1-10]`**: Alternar entre Workspaces (ou clique direto com o mouse na barra Waybar)

---

## 🔄 Sincronização Automática

Para salvar e enviar qualquer modificação futura diretamente para o GitHub:

```bash
~/dotfiles/sync.sh
```
