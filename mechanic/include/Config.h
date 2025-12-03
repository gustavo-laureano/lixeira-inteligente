#ifndef CONFIG_H
#define CONFIG_H

// Configurações do carrinho mecanum TB6612FNG

// TB6612FNG #1 - Motores A e C
#define MOTOR_A_PWM_PIN    14  // Marrom
#define MOTOR_A_DIR1_PIN   27  // Amarelo
#define MOTOR_A_DIR2_PIN   26  // Verde

#define MOTOR_C_PWM_PIN    17  // Amarelo
#define MOTOR_C_DIR1_PIN   19  // Marrom
#define MOTOR_C_DIR2_PIN   18  // Branco

// TB6612FNG #2 - Motores B e D
#define MOTOR_B_PWM_PIN    32  // Cinza
#define MOTOR_B_DIR1_PIN   33  // Azul
#define MOTOR_B_DIR2_PIN   25  // Roxo

#define MOTOR_D_PWM_PIN    21  // Roxo
#define MOTOR_D_DIR1_PIN   23  // Verde
#define MOTOR_D_DIR2_PIN   22  // Azul

// Configurações PWM
#define PWM_FREQUENCY       20000
#define PWM_RESOLUTION      8

// Velocidades (0-255)
#define DEFAULT_SPEED       180
#define MAX_SPEED          200
#define MIN_SPEED          40

// Escalonamento para velocidade de rotação enviado no vetor (0..1)
// 1.0 = rotações sem escala, valores menores reduzem a influência da rotação
#define ROTATION_SCALE     0.6

// Configurações gerais
#define STATUS_LED_PIN      2
#define SERIAL_BAUDRATE     115200
#define BT_DEVICE_NAME      "CarrinhoMovimentacao"
#define COMMAND_TIMEOUT     500
#define STATUS_UPDATE_INTERVAL 1000
#define MOTOR_STOP_DELAY    50

// Configurações WiFi para APIreceiver
#define WIFI_SSID           "POCO M3 Pro 5G"
#define WIFI_PASSWORD       "wifitop12347"

#endif