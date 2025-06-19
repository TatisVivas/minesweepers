# 🚨 Minesweeper Pygame 🎮

¡Bienvenido al clásico juego de buscaminas hecho con Python y Pygame!

---

## 🔹 ¿Cómo jugar?

Minesweeper es un juego de lógica para un solo jugador. El objetivo es **limpiar todo el tablero sin hacer explotar ninguna mina** 💣. Usa los números como pistas para deducir dónde están las bombas.

---

### 🎯 Controles

🔹 **Clic Izquierdo**
➞ Revela una celda oculta
  • 💥 Si es una mina, pierdes
  • 🌫️ Si está vacía, se revela automáticamente toda la zona segura (efecto cascada)
  • 🔢 Si tiene un número, muestra cuántas minas la rodean

🔸 **Clic Derecho**
➞ Coloca una 🚩 bandera para marcar una celda como posible mina
➞ Vuelve a hacer clic derecho para quitar la bandera

🔁 **Tecla R**
➞ Reinicia el juego con un nuevo tablero

---

### 🧹 Entendiendo el Tablero

🗚️ **Celdas Ocultas**
Cuadros grises que aún no has explorado

⬛ **Celdas Vacías**
Color gris oscuro que indica que no hay minas cercanas

🔢 **Números (1-8)**
Indican cuántas minas hay en las 8 celdas adyacentes

🚩 **Banderas**
Círculos azules que tú colocas para marcar minas sospechosas

💣 **Minas**
Cuadros rojos revelados si pierdes

---

## ⚙️ Requisitos e Instalación

### 🧰 Lo que necesitas

✔️ Python 3
✔️ La librería Pygame

---

### 📦 Instalación rápida

1. Asegúrate de tener Python instalado:
   👉 [Descargar Python](https://www.python.org/downloads/)

2. Instala Pygame ejecutando en tu terminal:

```bash
pip install pygame
```

📌 Usa `pip3` si estás en macOS o Linux:

```bash
pip3 install pygame
```

---

## 🚀 Cómo ejecutar el juego

1. Guarda el archivo `minesweeper.py` en una carpeta
2. Abre tu terminal o consola de comandos
3. Navega a la carpeta donde guardaste el juego:

```bash
cd ruta/del/directorio
```

4. Ejecuta el juego:

```bash
python minesweeper.py
```

o:

```bash
python3 minesweeper.py
```

---

## 🎉 ¡Disfrútalo!

Diviértete desactivando minas, usando la lógica y superando tus récords personales.
💡 *¿Puedes ganar sin usar ninguna bandera? ¡Rétate a ti mismo!* 💪

---
**By:** *Tatiana Vivas*😉