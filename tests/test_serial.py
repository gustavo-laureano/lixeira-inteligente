#!/usr/bin/env python3
"""
Script de teste para comunicação serial com Arduino
"""

import serial
import time
import sys

def test_serial(port='/dev/ttyUSB0', baudrate=9600):
    """Testa comunicação serial"""
    print(f"Testando comunicação serial...")
    print(f"Porta: {port}")
    print(f"Baudrate: {baudrate}")
    print("-" * 50)
    
    try:
        # Abre conexão serial
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Aguarda Arduino resetar
        
        print("✅ Conexão serial estabelecida!")
        
        # Limpa buffer
        if ser.in_waiting:
            initial_data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"Dados iniciais: {initial_data}")
        
        # Comandos de teste
        test_commands = [
            "BOTTLE:LEFT:SMALL",
            "CAN:CENTER:LARGE",
            "CUP:RIGHT:SMALL",
            "BOTTLE:CENTER:LARGE"
        ]
        
        print("\nEnviando comandos de teste...")
        print("-" * 50)
        
        for cmd in test_commands:
            print(f"\n➡️  Enviando: {cmd}")
            ser.write(f"{cmd}\n".encode())
            
            # Aguarda resposta
            time.sleep(0.5)
            
            if ser.in_waiting:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"⬅️  Resposta: {response}")
            else:
                print("⬅️  Sem resposta")
            
            time.sleep(1)
        
        print("\n" + "-" * 50)
        print("✅ Teste concluído!")
        
        # Modo interativo
        print("\nModo interativo (digite 'exit' para sair):")
        while True:
            cmd = input("Comando: ").strip()
            
            if cmd.lower() == 'exit':
                break
            
            if cmd:
                ser.write(f"{cmd}\n".encode())
                time.sleep(0.3)
                
                if ser.in_waiting:
                    response = ser.readline().decode('utf-8', errors='ignore').strip()
                    print(f"Resposta: {response}")
        
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"❌ Erro de comunicação serial: {e}")
        print("\nVerifique:")
        print("  - Arduino está conectado?")
        print("  - Porta está correta? (ls /dev/tty*)")
        print("  - Permissões: sudo usermod -aG dialout $USER")
        print("  - Outro programa está usando a porta?")
        return False
    
    except KeyboardInterrupt as e:
        print("\n\nInterrompido pelo usuário")
        if 'ser' in locals() and ser.is_open:
            ser.close()
        return True
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 9600
    
    success = test_serial(port, baudrate)
    sys.exit(0 if success else 1)
