#!/usr/bin/env python3
"""
Teste de controle manual via teclado
Permite controlar o Arduino/Raspberry via serial usando as setas do teclado
"""

import serial
import sys
import time

# Windows
try:
    import msvcrt
    WINDOWS = True
except ImportError:
    WINDOWS = False

# Linux/Mac
if not WINDOWS:
    import tty
    import termios


def get_key_windows():
    """Captura tecla no Windows"""
    if msvcrt.kbhit():
        key = msvcrt.getch()
        # Teclas especiais (setas) retornam 2 bytes
        if key == b'\xe0':  # Prefixo para setas
            key = msvcrt.getch()
            if key == b'H':    # Seta para cima
                return 'UP'
            elif key == b'P':  # Seta para baixo
                return 'DOWN'
            elif key == b'K':  # Seta para esquerda
                return 'LEFT'
            elif key == b'M':  # Seta para direita
                return 'RIGHT'
        elif key == b'q' or key == b'Q':
            return 'QUIT'
        elif key == b' ':
            return 'STOP'
    return None


def get_key_unix():
    """Captura tecla no Linux/Mac"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        
        # Verifica se é uma sequência de escape (setas)
        if ch == '\x1b':
            ch = sys.stdin.read(2)
            if ch == '[A':    # Seta para cima
                return 'UP'
            elif ch == '[B':  # Seta para baixo
                return 'DOWN'
            elif ch == '[D':  # Seta para esquerda
                return 'LEFT'
            elif ch == '[C':  # Seta para direita
                return 'RIGHT'
        elif ch == 'q' or ch == 'Q':
            return 'QUIT'
        elif ch == ' ':
            return 'STOP'
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None


def keyboard_control(port='/dev/ttyUSB0', baudrate=9600):
    """Controla Arduino via teclado"""
    print("="*60)
    print("🎮 CONTROLE POR TECLADO - Lixeira Inteligente")
    print("="*60)
    print(f"\n📡 Conectando à porta: {port}")
    print(f"   Baudrate: {baudrate}")
    
    try:
        # Conecta ao Arduino
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Aguarda Arduino resetar
        
        print("✅ Conexão estabelecida!")
        print("\n" + "="*60)
        print("COMANDOS:")
        print("="*60)
        print("  ⬆️  Seta CIMA    → FORWARD (avançar)")
        print("  ⬇️  Seta BAIXO   → BACKWARD (recuar)")
        print("  ⬅️  Seta ESQUERDA → LEFT (virar esquerda)")
        print("  ➡️  Seta DIREITA  → RIGHT (virar direita)")
        print("  ESPAÇO          → STOP (parar)")
        print("  Q               → QUIT (sair)")
        print("="*60)
        print("\n🎯 Aguardando comandos... (pressione Q para sair)\n")
        
        last_command = None
        
        while True:
            # Captura tecla
            if WINDOWS:
                key = get_key_windows()
            else:
                key = get_key_unix()
            
            if key:
                command = None
                
                if key == 'UP':
                    command = "FORWARD"
                    print("⬆️  AVANÇAR")
                elif key == 'DOWN':
                    command = "BACKWARD"
                    print("⬇️  RECUAR")
                elif key == 'LEFT':
                    command = "LEFT"
                    print("⬅️  ESQUERDA")
                elif key == 'RIGHT':
                    command = "RIGHT"
                    print("➡️  DIREITA")
                elif key == 'STOP':
                    command = "STOP"
                    print("⏸️  PARAR")
                elif key == 'QUIT':
                    print("\n🛑 Encerrando...")
                    command = "STOP"
                    ser.write(f"{command}\n".encode())
                    time.sleep(0.1)
                    break
                
                # Envia comando apenas se mudou
                if command and command != last_command:
                    ser.write(f"{command}\n".encode())
                    last_command = command
                    
                    # Aguarda resposta do Arduino
                    time.sleep(0.05)
                    if ser.in_waiting:
                        response = ser.readline().decode('utf-8', errors='ignore').strip()
                        print(f"   ← Arduino: {response}")
            
            time.sleep(0.05)  # Pequeno delay para não sobrecarregar CPU
        
        ser.close()
        print("✅ Desconectado com sucesso!")
        return True
        
    except serial.SerialException as e:
        print(f"\n❌ Erro de comunicação serial: {e}")
        print("\n🔍 Verificações:")
        print("  • Arduino está conectado?")
        print("  • Porta está correta?")
        if WINDOWS:
            print("    Windows: COM3, COM4, etc.")
            print("    Verifique no Gerenciador de Dispositivos")
        else:
            print("    Linux: /dev/ttyUSB0, /dev/ttyACM0, etc.")
            print("    Execute: ls /dev/tty*")
            print("  • Permissões (Linux): sudo usermod -aG dialout $USER")
        print("  • Outro programa está usando a porta?")
        return False
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário (Ctrl+C)")
        if 'ser' in locals() and ser.is_open:
            ser.write(b"STOP\n")
            ser.close()
        return True
    
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        if 'ser' in locals() and ser.is_open:
            ser.close()
        return False


if __name__ == "__main__":
    print("\n")
    
    # Detecta porta automaticamente ou usa argumento
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        # Tenta detectar porta comum
        if WINDOWS:
            port = 'COM3'  # Ajuste conforme necessário
            print(f"⚠️  Usando porta padrão: {port}")
            print(f"   Para especificar: python {sys.argv[0]} COM4")
        else:
            port = '/dev/ttyUSB0'
            print(f"⚠️  Usando porta padrão: {port}")
            print(f"   Para especificar: python {sys.argv[0]} /dev/ttyACM0")
    
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 9600
    
    print()
    success = keyboard_control(port, baudrate)
    sys.exit(0 if success else 1)
