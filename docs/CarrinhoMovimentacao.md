# CarrinhoMovimentacao — Módulo de Movimentação (Mecanum)

Este documento contém a parte do repositório responsável pelo controle de movimentação do carrinho com rodas mecanum. Ele foi extraído do módulo que implementa controle via Dabble, controle serial e a lógica de motores TB6612FNG para ESP32.

Principais arquivos deste módulo:
- `include/Config.h` - pinos e configurações PWM
- `include/MecanumDrive.h` - implementação de controle das 4 rodas mecanum
- `include/ControleDabble.h` - controlador baseado na biblioteca DabbleESP32
- `include/ControleSerial.h` - controlador via monitor serial (exemplo)
- `src/main.cpp` - entrypoint que instancia o controlador e o `MecanumDrive`

Resumo rápido de uso:
1. Configure `include/Config.h` com os pinos adequados.
2. Compile o projeto com PlatformIO (ambiente `esp32doit-devkit-v1`).
3. Faça o upload para o ESP32 e conecte o app Dabble via Bluetooth para controlar o carrinho.

Notas de integração
- Mantive este módulo dentro do repositório `lixeira-inteligente` como parte dos utilitários de robótica. Se preferir que ele fique em um repositório separado, podemos mover os arquivos para um subdiretório ou criar um repositório novo.
