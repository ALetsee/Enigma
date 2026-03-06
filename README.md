# Enigma

Simulador de la máquina Enigma por consola, con soporte para alfabeto en inglés (26 letras) y español (27 letras incluyendo Ñ), múltiples configuraciones de rotores, y dos modos de avance: estándar histórico y notch por valor.

---

## Requisitos

Solo necesitas **Python 3** instalado. El programa no requiere librerías externas — usa únicamente módulos de la librería estándar (`os`, `json`, `time`).

---

## Instalación

```bash
git clone https://github.com/ALetsee/Enigma
cd Enigma
python enigma.py
```

En algunos sistemas puede ser necesario usar `python3` en lugar de `python`.

---

## Archivos

```
Enigma/
├── enigma.py       # programa principal
└── rotores.txt     # configuraciones de rotores
```

Ambos archivos deben estar en la misma carpeta.

---

## Uso

Al ejecutar el programa se muestra primero el menú de selección de configuración y luego el menú principal.

### 1. Selección de configuración

```
####################################################
#          SELECCION DE CONFIGURACION              #
####################################################

  [1]  Ingles > NotchValor=F
  [2]  Ingles > NotchValor=T
  [3]  Espanol > NotchValor=F
  [4]  Espanol > NotchValor=T
  [5]  Ingles 4R > NotchValor=F
```

Escribe el número de la configuración que quieras usar y presiona Enter.

### 2. Menú principal

```
####################################################
#            Ingles > NotchValor=F                 #
####################################################

  [1]  Cifrar mensaje
  [2]  Descifrar mensaje
  [3]  Cambiar configuracion
  [4]  Ayuda
  [5]  Salir
```

| Opción | Descripción |
|--------|-------------|
| `1` | Cifrar un mensaje |
| `2` | Descifrar un mensaje cifrado |
| `3` | Volver al menú de configuraciones |
| `4` | Ver ayuda sobre la configuración activa |
| `5` | Salir del programa |

También puedes pulsar `Ctrl+C` en cualquier momento para salir.

### 3. Cifrar o descifrar

Al elegir cifrar o descifrar se piden dos datos:

- **Mensaje** — el texto a cifrar o descifrar. Acepta letras y espacios. Los espacios se conservan en el resultado y deben mantenerse al descifrar.
- **Clave** — exactamente 3 letras (o 4 si la configuración tiene 4 rotores). Define las posiciones iniciales de los rotores.

Ejemplo de cifrado:

```
  Mensaje  : HOLA MUNDO
  Clave (3 letras): ABC

  # Original  : HOLA MUNDO
  # Clave     : ABC
  # Resultado : XKQZ PWTÑL
```

Para descifrar ese resultado se usa el mismo mensaje cifrado y la misma clave:

```
  Mensaje  : XKQZ PWTÑL
  Clave (3 letras): ABC

  # Original  : XKQZ PWTÑL
  # Clave     : ABC
  # Resultado : HOLA MUNDO
```

> Los espacios en el cifrado corresponden a los mismos espacios del original. Si el texto cifrado tiene espacios, pégalo tal cual al descifrar.

---

## Configuraciones (rotores.txt)

El archivo `rotores.txt` contiene un array JSON con todas las configuraciones disponibles. Puedes agregar, quitar o modificar configuraciones editando ese archivo directamente.

### Estructura de una configuración

```json
{
  "nombre":    "Ingles > NotchValor=F",
  "rotorI":    "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
  "rotorII":   "AJDKSIRUXBLHWTMCQGZNPYFVOE",
  "rotorIII":  "BDFHJLCPRTXVZNYEIWGAKMUSQO",
  "rotorIV":   "",
  "reflector": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
  "notchI":    "Q",
  "notchII":   "E",
  "notchIII":  "V",
  "notchIV":   "",
  "notchPorValor": false
}
```

| Campo | Descripción |
|-------|-------------|
| `nombre` | Nombre que aparece en el menú de selección |
| `rotorI` | Cableado del rotor izquierdo — permutación del alfabeto |
| `rotorII` | Cableado del rotor central |
| `rotorIII` | Cableado del rotor derecho |
| `rotorIV` | Cableado del cuarto rotor — dejar vacío `""` para usar solo 3 |
| `reflector` | Cableado del reflector — debe ser simétrico (si A→B entonces B→A) |
| `notchI/II/III/IV` | Letra de notch de cada rotor — exactamente 1 carácter |
| `notchPorValor` | Modo de avance de rotores — `true` o `false` |

### Alfabeto detectado automáticamente

El programa detecta el alfabeto según el largo del cableado:

- **26 caracteres** → inglés (A-Z)
- **27 caracteres** → español (A-Z + Ñ)

No hace falta indicarlo — si el cableado de `rotorI` tiene 27 letras, el programa usa el alfabeto español automáticamente.

### Reglas para cableados

- Debe ser una permutación completa del alfabeto — sin repetir letras y sin que falte ninguna.
- Los tres (o cuatro) rotores deben ser distintos entre sí.
- El reflector debe ser simétrico: si la posición `i` mapea a la letra `X`, entonces la posición de `X` debe mapear a la letra `i`.
- Con alfabeto español (27 letras, número impar), el reflector tiene un punto fijo obligatorio — una letra que se mapea a sí misma. En las configs incluidas esa letra es la Ñ.

### notchPorValor

Controla cuándo y cómo avanzan los rotores al cifrar cada letra.

**`false` — modo estándar (histórico)**

Los rotores avanzan antes de cifrar, según la posición visible. El rotor derecho avanza siempre. El central avanza si el derecho está en su notch. El izquierdo avanza si el central está en su notch. Es el comportamiento mecánico real de la máquina Enigma.

**`true` — modo notch por valor**

Los rotores avanzan durante el cifrado, cuando el valor en tránsito por el rotor coincide con su notch. Ocurre tanto en la ida como en la vuelta de la señal. El avance depende del contenido del mensaje, no solo de la posición.

> Un mensaje cifrado con `true` solo puede descifrarse con `true`, y viceversa. Son incompatibles.

> Con 4 rotores solo funciona `false`.

---

## Configs incluidas

| Config | Alfabeto | Rotores | notchPorValor |
|--------|----------|---------|---------------|
| Ingles > NotchValor=F | Inglés | 3 | false |
| Ingles > NotchValor=T | Inglés | 3 | true |
| Espanol > NotchValor=F | Español | 3 | false |
| Espanol > NotchValor=T | Español | 3 | true |
| Ingles 4R > NotchValor=F | Inglés | 4 | false |