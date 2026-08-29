# 🌙 Hyprland Dotfiles (CachyOS / Arch Linux)

Setup completo e minimalista do Hyprland configurado nativamente em **Lua**, com integração **Pywal**, **Waybar**, **Spotify Dynamic Island**, **Hyprlock**, **Rofi Spotlight**, **Cliphist** e **Starship Prompt**.

---

## 🎨 Componentes & Ferramentas

| Componente | Ferramenta | Descrição |
| :--- | :--- | :--- |
| **Compositor** | Hyprland (Lua) | Modular (`monitors`, `variables`, `decorations`, `keybinds`, `windowrules`) |
| **Status Bar** | Waybar | Pílula central com Calendário BR, Clima 4 dias e Spotify Island |
| **Spotify** | Dynamic Island + GTK3 | Capa ao vivo, linha do tempo interativa e controles |
| **Lockscreen** | Hyprlock | Blur dinâmico da tela atual e input glow |
| **Display Manager** | SDDM Astronaut | Tema nítido Totoro Stargazing |
| **Lançador** | Rofi Spotlight | Busca de apps + pesquisa direta no Google (Floorp) |
| **Clipboard** | Cliphist + Rofi | Histórico flutuante com `Super + C` |
| **Menu de Energia**| Wlogout | Glassmorphism com 5 botões centrais e Pywal |
| **Shell Prompt** | Starship + Fish | Diretório com ícones e status git |
| **Wallpaper** | Gslapper + Pywal | Vídeo animado 1080p + paleta de cores dinâmica |

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
* **`Super + [1-10]`**: Trocar de Workspace (pressione a mesma tecla para voltar)

---

## 🔄 Como Sincronizar / Fazer Backup

Para atualizar seu repositório no GitHub com as últimas alterações do seu sistema:

```bash
~/dotfiles/sync.sh
```
