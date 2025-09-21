# 🎲 Dice Roller MCP Server

Un servidor MCP simple y limpio para tiradas de dados, lanzamiento de monedas y otras mecánicas de dados para juegos de rol.

## 🎯 Características

- **🪙 Lanzamiento de moneda** - Simple cara o cruz, con soporte para múltiples monedas
- **🎲 Notación estándar de dados** - Soporta notación como `2d6+3`, `1d20-2`, etc.
- **🎮 Dados estándar de juegos** - d4, d6, d8, d10, d12, d20, d100
- **⚔️ Ventaja/Desventaja** - Mecánica de D&D 5e (tirar dos veces, quedarse con el mayor/menor)
- **💥 Dados explosivos** - Los dados que sacan el valor máximo se vuelven a tirar
- **🎯 Dados percentil** - Dado d100 tradicional (1-100)
- **🎲 Dados Fudge** - Dados especiales que dan -1, 0, o +1
- **📜 Historial de tiradas** - Mantiene registro de las últimas 100 tiradas
- **🧹 Gestión de historial** - Ver y limpiar el historial de tiradas
- **✅ Validación robusta** - Validación completa de todos los parámetros de entrada
- **🛡️ Manejo de errores** - Mensajes de error claros y descriptivos

## 📦 Instalación

1. Clona o descarga este repositorio
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 🚀 Uso

### Ejecutar el servidor

```bash
python server.py
```

### Configurar en Claude Desktop

Agrega la siguiente configuración a tu archivo de configuración de Claude Desktop:

**En macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**En Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "dice-roller": {
      "command": "python",
      "args": ["/ruta/a/tu/server.py"]
    }
  }
}
```

## 🎲 Herramientas Disponibles

### 1. `flip_coin`
Lanza una o más monedas.
- **Parámetros:**
  - `num_flips` (opcional): Número de monedas a lanzar (1-100, por defecto: 1)

### 2. `roll_dice`
Tira dados usando notación estándar.
- **Parámetros:**
  - `notation`: Notación de dados (ej: "2d6+3", "1d20", "3d8-2")

### 3. `roll_standard`
Tira dados de juegos estándar.
- **Parámetros:**
  - `die_type`: Tipo de dado ("d4", "d6", "d8", "d10", "d12", "d20", "d100")
  - `num_dice` (opcional): Número de dados (1-100, por defecto: 1)
  - `modifier` (opcional): Modificador a agregar (-1000 a 1000, por defecto: 0)

### 4. `roll_advantage`
Tira con ventaja (D&D 5e) - tira dos veces y quédate con el mayor.
- **Parámetros:**
  - `die_size` (opcional): Tamaño del dado (2-1000, por defecto: 20)
  - `modifier` (opcional): Modificador a agregar (-1000 a 1000, por defecto: 0)

### 5. `roll_disadvantage`
Tira con desventaja (D&D 5e) - tira dos veces y quédate con el menor.
- **Parámetros:**
  - `die_size` (opcional): Tamaño del dado (2-1000, por defecto: 20)
  - `modifier` (opcional): Modificador a agregar (-1000 a 1000, por defecto: 0)

### 6. `roll_exploding`
Tira dados explosivos - vuelve a tirar cuando sale el valor máximo.
- **Parámetros:**
  - `die_size`: Tamaño del dado (2-1000)
  - `num_dice` (opcional): Número de dados (1-100, por defecto: 1)
  - `modifier` (opcional): Modificador a agregar (-1000 a 1000, por defecto: 0)

### 8. `roll_percentile`
Tira un dado percentil (d100).

### 9. `roll_fudge`
Tira dados Fudge (dF) - cada dado puede dar -1, 0, o +1.
- **Parámetros:**
  - `num_dice` (opcional): Número de dados Fudge (1-100, por defecto: 4)

### 10. `get_history`
Obtiene el historial de tiradas recientes.
- **Parámetros:**
  - `limit` (opcional): Número de tiradas recientes a mostrar (1-100, por defecto: 10)

### 11. `clear_history`
Limpia el historial de tiradas.

## 📝 Ejemplos de Uso

### Tiradas Básicas
- "Lanza una moneda" → `flip_coin()`
- "Tira 2d6+3" → `roll_dice(notation="2d6+3")`
- "Tira un d20" → `roll_standard(die_type="d20")`

### Tiradas Avanzadas
- "Tira con ventaja" → `roll_advantage()`
- "Tira 3d6 explosivos" → `roll_exploding(num_dice=3, die_size=6)`
- "Tira percentil" → `roll_percentile()`
- "Tira 4 dados Fudge" → `roll_fudge(num_dice=4)`
- "Muestra las últimas 5 tiradas" → `get_history(limit=5)`

## 🎮 Notación de Dados

El servidor soporta notación estándar de dados:
- `XdY`: Tira X dados de Y caras
- `XdY+Z`: Tira X dados de Y caras y suma Z
- `XdY-Z`: Tira X dados de Y caras y resta Z

Ejemplos:
- `1d20`: Un dado de 20 caras
- `2d6+3`: Dos dados de 6 caras más 3
- `3d8-2`: Tres dados de 8 caras menos 2

## 📜 Historial

El servidor mantiene un historial de las últimas 100 tiradas, incluyendo:
- Timestamp de cada tirada
- Tipo de tirada realizada
- Resultado obtenido

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si tienes ideas para nuevas características o mejoras, no dudes en abrir un issue o enviar un pull request.

## 📄 Licencia

MIT License - Siéntete libre de usar este código en tus proyectos.
log.json
{
  "mcpServers": {
    "dice-roller": {
      "command": "python",
      "args": ["D:\\servidor_mcp\\server.py"],
      "env": {}
    }
  }
}