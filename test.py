import os
import json
import time

CONFIG_FILE = "rotores.txt"

LETRAS_EN = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LETRAS_ES = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["Ñ"]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def obtener_alfabeto(tipo):
    return LETRAS_ES if tipo == "ES" else LETRAS_EN

def validar_cableado(cableado, alfabeto, nombre):
    cab = list(cableado.upper())
    n = len(alfabeto)
    if len(cab) != n:
        return False, f"{nombre}: necesita {n} chars (tiene {len(cab)})."
    for c in cab:
        if c not in alfabeto:
            return False, f"{nombre}: '{c}' no esta en el alfabeto."
    repetidos = [c for c in set(cab) if cab.count(c) > 1]
    if repetidos:
        return False, f"{nombre}: letras repetidas: {', '.join(repetidos)}"
    return True, ""

def validar_rotores_distintos(config):
    rotores = ["rotorI", "rotorII", "rotorIII"]
    if config.get("rotorIV", "").strip():
        rotores.append("rotorIV")
    for i in range(len(rotores)):
        for j in range(i + 1, len(rotores)):
            a, b = rotores[i], rotores[j]
            if config[a].upper() == config[b].upper():
                return False, f"{a} y {b} tienen el mismo cableado."
    return True, ""

def validar_reflector_simetrico(cableado, alfabeto):
    cab = list(cableado.upper())
    for i in range(len(alfabeto)):
        j = alfabeto.index(cab[i])
        if alfabeto.index(cab[j]) != i:
            ci = alfabeto[i]
            cj = cab[i]
            return False, f"No es simetrico: {ci}->{cj} pero {cj} no apunta a {ci}."
    return True, ""

def crear_template():
    template = [
        {
            "nombre": "Config 1",
            "rotorI": "",
            "rotorII": "",
            "rotorIII": "",
            "rotorIV": "",
            "reflector": "",
            "notchI": "Q",
            "notchII": "E",
            "notchIII": "V",
            "notchIV": "",
            "notchPorValor": False
        }
    ]
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    print(f"Se creo '{CONFIG_FILE}'. Abrelo, llena los cableados y vuelve a ejecutar.")

def validar_entrada(data, idx):
    etiqueta = f"Config #{idx+1}"
    for campo in ["rotorI", "rotorII", "rotorIII", "reflector"]:
        if campo not in data:
            return f"{etiqueta}: falta el campo '{campo}'."
        if not data[campo]:
            return f"{etiqueta}: el campo '{campo}' esta vacio."
    for campo in ["notchI", "notchII", "notchIII"]:
        if campo not in data or not data[campo]:
            return f"{etiqueta}: falta el notch '{campo}'."
        if len(data[campo]) != 1:
            return f"{etiqueta}: '{campo}' debe ser exactamente 1 letra."
    return None

def cargar_configs():
    if not os.path.exists(CONFIG_FILE):
        return None, "no_existe"
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return None, f"Error leyendo {CONFIG_FILE}: {e}"
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or len(data) == 0:
        return None, f"{CONFIG_FILE} debe contener al menos una configuracion."
    errores = []
    validas = []
    for i, entry in enumerate(data):
        err = validar_entrada(entry, i)
        if err:
            errores.append(err)
        else:
            validas.append(entry)
    if not validas:
        return None, "\n".join(errores)
    return validas, errores if errores else None

def tiene_cuarto_rotor(config):
    return bool(config.get("rotorIV", "").strip())

def extraer_con_espacios(texto, alfabeto):
    chars, antes, invalidos = [], [], []
    pendientes = 0
    for c in texto.upper():
        if c == " ":
            pendientes += 1
        elif c in alfabeto:
            antes.append(pendientes)
            chars.append(c)
            pendientes = 0
        else:
            invalidos.append(c)
    trailing = pendientes
    return chars, antes, trailing, invalidos

def reconstruir_con_espacios(letras, antes, trailing):
    resultado = []
    for i, c in enumerate(letras):
        resultado.extend([" "] * antes[i])
        resultado.append(c)
    resultado.extend([" "] * trailing)
    return "".join(resultado)

def compare_value_notch(value_char, notch_value, key_pos, n):
    if value_char != notch_value:
        return key_pos
    return (key_pos + 1) % n

def avanzar_rotores(kp, notches, alfabeto, n):
    en_notch_der = (alfabeto[kp[2]] == notches[2])
    en_notch_med = (alfabeto[kp[1]] == notches[1])
    kp[2] = (kp[2] + 1) % n
    if en_notch_der or en_notch_med:
        kp[1] = (kp[1] + 1) % n
    if en_notch_med:
        kp[0] = (kp[0] + 1) % n

def avanzar_rotores_4(kp, notches, alfabeto, n):
    en_notch_iv  = (alfabeto[kp[3]] == notches[3])
    en_notch_iii = (alfabeto[kp[2]] == notches[2])
    en_notch_ii  = (alfabeto[kp[1]] == notches[1])
    kp[3] = (kp[3] + 1) % n
    if en_notch_iv or en_notch_iii:
        kp[2] = (kp[2] + 1) % n
    if en_notch_iii or en_notch_ii:
        kp[1] = (kp[1] + 1) % n
    if en_notch_ii:
        kp[0] = (kp[0] + 1) % n

def cifrar_letra(char, kp, rI, rII, rIII, ref, alfabeto, notches):
    n = len(alfabeto)
    x = (alfabeto.index(char) + kp[0]) % n
    v = rI[x]
    x = (alfabeto.index(v) + kp[1]) % n
    v = rII[x]
    x = (alfabeto.index(v) + kp[2]) % n
    v = rIII[x]
    v = ref[alfabeto.index(v)]
    x = (rIII.index(v) - kp[2]) % n
    v = alfabeto[x]
    x = (rII.index(v) - kp[1]) % n
    v = alfabeto[x]
    return alfabeto[(rI.index(v) - kp[0]) % n]

def cifrar_letra_4(char, kp, rI, rII, rIII, rIV, ref, alfabeto, notches):
    n = len(alfabeto)
    x = (alfabeto.index(char) + kp[0]) % n
    v = rI[x]
    x = (alfabeto.index(v) + kp[1]) % n
    v = rII[x]
    x = (alfabeto.index(v) + kp[2]) % n
    v = rIII[x]
    x = (alfabeto.index(v) + kp[3]) % n
    v = rIV[x]
    v = ref[alfabeto.index(v)]
    x = (rIV.index(v) - kp[3]) % n
    v = alfabeto[x]
    x = (rIII.index(v) - kp[2]) % n
    v = alfabeto[x]
    x = (rII.index(v) - kp[1]) % n
    v = alfabeto[x]
    return alfabeto[(rI.index(v) - kp[0]) % n]

def cifrar_letra_valor(char, kp, rI, rII, rIII, ref, alfabeto, notches):
    n = len(alfabeto)
    x = (alfabeto.index(char) + kp[0]) % n
    v = rI[x]
    kp[0] = compare_value_notch(v, notches[0], kp[0], n)
    x = (alfabeto.index(v) + kp[1]) % n
    v = rII[x]
    kp[1] = compare_value_notch(v, notches[1], kp[1], n)
    x = (alfabeto.index(v) + kp[2]) % n
    v = rIII[x]
    kp[2] = compare_value_notch(v, notches[2], kp[2], n)
    v = ref[alfabeto.index(v)]
    x = rIII.index(v)
    kp[2] = compare_value_notch(v, notches[2], kp[2], n)
    x = (x - kp[2]) % n
    v = alfabeto[x]
    x = rII.index(v)
    kp[1] = compare_value_notch(v, notches[1], kp[1], n)
    x = (x - kp[1]) % n
    v = alfabeto[x]
    x = rI.index(v)
    kp[0] = compare_value_notch(v, notches[0], kp[0], n)
    return alfabeto[(x - kp[0]) % n]

def procesar(mensaje, clave, config, modo, tipo_alfa):
    alfabeto = obtener_alfabeto(tipo_alfa)
    uso_4 = tiene_cuarto_rotor(config)
    min_letras = 4 if uso_4 else 3

    campos = [("rotorI","Rotor I"),("rotorII","Rotor II"),("rotorIII","Rotor III")]
    if uso_4:
        campos.append(("rotorIV","Rotor IV"))
    campos.append(("reflector","Reflector"))

    for key, nombre in campos:
        ok, msg = validar_cableado(config[key], alfabeto, nombre)
        if not ok:
            return None, f"Error con alfabeto {tipo_alfa}: {msg}"

    ok, msg = validar_rotores_distintos(config)
    if not ok:
        return None, f"Error en rotores.txt: {msg}"

    ok, msg = validar_reflector_simetrico(config["reflector"], alfabeto)
    if not ok:
        return None, f"Error en reflector: {msg}"

    letras_clave = [c for c in clave.upper() if c in alfabeto]
    if len(letras_clave) < min_letras:
        return None, f"La clave necesita al menos {min_letras} letras del alfabeto."

    kp   = [alfabeto.index(letras_clave[i]) for i in range(min_letras)]
    rI   = list(config["rotorI"].upper())
    rII  = list(config["rotorII"].upper())
    rIII = list(config["rotorIII"].upper())
    ref  = list(config["reflector"].upper())
    rIV  = list(config["rotorIV"].upper()) if uso_4 else None
    notches = [config["notchI"].upper(), config["notchII"].upper(), config["notchIII"].upper()]
    if uso_4:
        notches.append(config.get("notchIV", "Z").upper())

    n = len(alfabeto)

    def cifrar(c):
        if uso_4:
            return cifrar_letra_4(c, kp, rI, rII, rIII, rIV, ref, alfabeto, notches)
        return cifrar_letra(c, kp, rI, rII, rIII, ref, alfabeto, notches)

    def avanzar():
        if uso_4:
            avanzar_rotores_4(kp, notches, alfabeto, n)
        else:
            avanzar_rotores(kp, notches, alfabeto, n)

    notch_por_valor = config.get("notchPorValor", False)
    if notch_por_valor and not uso_4:
        chars, antes, trailing, invalidos = extraer_con_espacios(mensaje, alfabeto)
        if invalidos:
            return None, f"Caracteres invalidos: {list(set(invalidos))}"
        if not chars:
            return None, "El mensaje no tiene caracteres validos."

        if modo == "cifrar":
            resultado = [cifrar_letra_valor(c, kp, rI, rII, rIII, ref, alfabeto, notches) for c in chars]
            return reconstruir_con_espacios(resultado, antes, trailing), None
        else:
            todas = []
            def descifrar_todas(idx, kp_actual, prefijo):
                if idx == len(chars):
                    todas.append(prefijo)
                    return
                c = chars[idx]
                for P in alfabeto:
                    kp_try = list(kp_actual)
                    if cifrar_letra_valor(P, kp_try, rI, rII, rIII, ref, alfabeto, notches) != c:
                        continue
                    descifrar_todas(idx + 1, kp_try, prefijo + P)
            descifrar_todas(0, kp, "")
            if not todas:
                return None, "No se pudo descifrar (modo notch por valor)."
            frec_en = {'E':.127,'T':.091,'A':.082,'O':.075,'I':.070,'N':.067,'S':.063,'H':.061,
                       'R':.060,'D':.043,'L':.040,'C':.028,'U':.028,'M':.024,'W':.024,'F':.022,
                       'G':.020,'Y':.020,'P':.019,'B':.015,'V':.010,'K':.008,'J':.002,'X':.002,
                       'Q':.001,'Z':.001}
            mejor = list(max(todas, key=lambda s: sum(frec_en.get(c, 0.001) for c in s)))
            return reconstruir_con_espacios(mejor, antes, trailing), None

    chars, antes, trailing, invalidos = extraer_con_espacios(mensaje, alfabeto)
    if invalidos:
        return None, f"Caracteres invalidos: {list(set(invalidos))}"
    if not chars:
        return None, "El mensaje no tiene caracteres validos."

    resultado = []
    for c in chars:
        avanzar()
        resultado.append(cifrar(c))

    return reconstruir_con_espacios(resultado, antes, trailing), None

# ---------------------------------------------------------------------------

ASCII_ART = r"""
                                                            
 ▄▄▄▄▄▄▄▄               ██                                  
 ██▀▀▀▀▀▀               ▀▀                                  
 ██        ██▄████▄   ████      ▄███▄██  ████▄██▄   ▄█████▄ 
 ███████   ██▀   ██     ██     ██▀  ▀██  ██ ██ ██   ▀ ▄▄▄██ 
 ██        ██    ██     ██     ██    ██  ██ ██ ██  ▄██▀▀▀██ 
 ██▄▄▄▄▄▄  ██    ██  ▄▄▄██▄▄▄  ▀██▄▄███  ██ ██ ██  ██▄▄▄███ 
 ▀▀▀▀▀▀▀▀  ▀▀    ▀▀  ▀▀▀▀▀▀▀▀   ▄▀▀▀ ██  ▀▀ ▀▀ ▀▀   ▀▀▀▀ ▀▀ 
                                ▀████▀▀                     
"""

NUMS = ["I","II","III","IV","V","VI","VII","VIII","IX","X"]

def etiqueta_config(idx):
    return NUMS[idx] if idx < len(NUMS) else str(idx + 1)

def typing_print(texto, delay=0.03):
    for c in texto:
        print(c, end="", flush=True)
        time.sleep(delay)
    print()

def header(titulo):
    ancho = 52
    borde = "#" * ancho
    centrado = titulo.center(ancho - 2)
    print(f"\n{borde}")
    print(f"#{centrado}#")
    print(f"{borde}\n")

def menu_configs(configs, advertencias):
    clear()
    print(ASCII_ART)
    if advertencias:
        for w in advertencias:
            print(f"  [!] {w}")
        print()
    header("SELECCION DE CONFIGURACION")
    for i in range(len(configs)):
        print(f"  [{i+1}]  Config {etiqueta_config(i)}")
    print()
    while True:
        sel = input("> ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(configs):
            return configs[int(sel) - 1]
        print(f"  [!] Escribe un numero entre 1 y {len(configs)}.")

def menu_alfabeto():
    header("SELECCION DE ALFABETO")
    print("  [1]  Ingles")
    print("  [2]  Espanol")
    print()
    while True:
        sel = input("> ").strip()
        if sel == "1": return "EN"
        if sel == "2": return "ES"
        print("  [!] Escribe 1 o 2.")

def menu_principal(etiqueta):
    clear()
    print(ASCII_ART)
    header(f"CONFIG {etiqueta}  //  MENU PRINCIPAL")
    print("  [1]  Cifrar mensaje")
    print("  [2]  Descifrar mensaje")
    print("  [3]  Cambiar configuracion")
    print("  [4]  Salir")
    print()

def pantalla_operacion(modo):
    clear()
    print(ASCII_ART)
    accion = "CIFRADO" if modo == "cifrar" else "DESCIFRADO"
    header(accion)

def main():
    configs, advertencias = cargar_configs()
    if configs is None:
        if advertencias == "no_existe":
            crear_template()
        else:
            print(f"Error: {advertencias}")
        return

    config = menu_configs(configs, advertencias)

    while True:
        idx = configs.index(config)
        etiqueta = etiqueta_config(idx)
        uso_4 = tiene_cuarto_rotor(config)

        menu_principal(etiqueta)
        op = input("> ").strip()

        if op == "4":
            clear()
            break
        if op == "3":
            config = menu_configs(configs, None)
            continue
        if op not in ["1", "2"]:
            continue

        modo = "cifrar" if op == "1" else "descifrar"

        pantalla_operacion(modo)
        tipo_alfa = menu_alfabeto()

        clear()
        print(ASCII_ART)
        header("CIFRADO" if modo == "cifrar" else "DESCIFRADO")

        mensaje = input("  Mensaje  : ").strip()
        if not mensaje:
            print("\n  [!] El mensaje no puede estar vacio.")
            input("\n> ")
            continue

        min_letras = 4 if uso_4 else 3
        clave = input(f"  Clave ({min_letras}+): ").strip()
        if not clave:
            print("\n  [!] La clave no puede estar vacia.")
            input("\n> ")
            continue

        resultado, err = procesar(mensaje, clave, config, modo, tipo_alfa)

        clear()
        print(ASCII_ART)
        header("CIFRADO" if modo == "cifrar" else "DESCIFRADO")
        print()
        if err:
            print(f"  [!] {err}")
        else:
            typing_print(f"  # Original  : {mensaje.upper()}", delay=0.01)
            typing_print(f"  # Clave     : {clave.upper()}", delay=0.01)
            typing_print(f"  # Resultado : {resultado}", delay=0.04)
        print()

        input("\n> ")

if __name__ == "__main__":
    main()