/*
 * robot_receiver.h
 * * Tradução do script Python api_receiver.py para C++/Arduino (ESP32).
 * * Este código transforma o ESP32 em um cliente WebSocket que se conecta
 * a um servidor broker (o mesmo que o script Python usava).
 * * Requer a biblioteca 'WebSockets' por Markus Sattler.
*/

#pragma once // Evita inclusões múltiplas do header

#include <WiFi.h>
#include <WebSocketsClient.h>
#include <functional> // Para std::bind

// ===== CONFIGURAÇÃO =====
// Ajuste estes valores conforme seu ambiente
const char* SERVER_HOST = "10.212.20.30";  // IP do PC/Servidor com a API
const int   SERVER_PORT = 8000;
const char* SERVER_PATH = "/ws/robot";

// Configuração de reconexão
const int RECONNECT_DELAY_MS = 5000; // 5 segundos

// =======================

// Função "placeholder" que será chamada com o comando
// Você DEVE implementar esta função no seu arquivo .ino principal.
extern void handleRobotCommand(String command);

/*
// ===== OPÇÃO 2: Se você quer que o ESP32 retransmita para outro Arduino =====
// Descomente esta seção e comente a "handleRobotCommand" acima.
// Lembre-se de iniciar a Serial2 no seu setup() com:
// Serial2.begin(115200); // (TX: 17, RX: 16 por padrão)

void forwardCommandToArduino(String command) {
    if (Serial2.availableForWrite()) {
        command += "\n"; // Adiciona o terminador de linha
        Serial2.print(command);
        Serial.print("Encaminhado para Arduino: ");
        Serial.println(command);
    } else {
        Serial.println("Serial2 não disponível. Comando ignorado.");
    }
}
// =========================================================================
*/


class RobotReceiver {
private:
    WebSocketsClient webSocket;
    bool isConnected = false;
    unsigned long lastReconnectAttempt = 0;

    /**
     * @brief Processa a mensagem recebida do WebSocket.
     */
    void handleMessage(uint8_t * payload, size_t length) {
        String message = (char*)payload;
        message.trim(); // Remove espaços em branco
        
        Serial.print("Mensagem recebida: '");
        Serial.print(message);
        Serial.println("'");
        
        // Valida comando (caracteres únicos permitidos)
        if (message.length() == 1) {
            char cmd = message.charAt(0);
            
            // Converte para minúsculo
            if (cmd >= 'A' && cmd <= 'Z') {
                cmd = cmd + 32; // 'a' - 'A' = 32
            }
            
            if (cmd == 'w' || cmd == 'a' || cmd == 's' || cmd == 'd' ||
                cmd == 'q' || cmd == 'e' || cmd == 'x') 
            {
                // Chama a função principal no .ino para executar o comando
                handleRobotCommand(String(cmd));

                // Se estiver usando a OPÇÃO 2 (retransmitir)
                // forwardCommandToArduino(String(cmd)); 
            } else {
                Serial.print("Comando inválido ignorado: ");
                Serial.println(message);
            }
        } else {
            Serial.print("Comando inválido ignorado: ");
            Serial.println(message);
        }
    }

    /**
     * @brief Callback para todos os eventos do WebSocket.
     */
    void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
        switch(type) {
            case WStype_DISCONNECTED:
                Serial.println("[WSc] Desconectado!");
                isConnected = false;
                break;
            case WStype_CONNECTED:
                Serial.print("[WSc] Conectado a: ");
                Serial.println((char*)payload);
                isConnected = true;
                break;
            case WStype_TEXT:
                // Processa a mensagem de texto recebida
                handleMessage(payload, length);
                break;
            
            // Outros eventos (opcionais)
            case WStype_BIN:
                Serial.println("[WSc] Binário recebido");
                break;
            case WStype_PING:
                // Serial.println("[WSc] Ping recebido");
                break;
            case WStype_PONG:
                // Serial.println("[WSc] Pong recebido");
                break;
            case WStype_ERROR:
                Serial.println("[WSc] Erro");
                break;
            default:
                break;
        }
    }

    /**
     * @brief Tenta (re)conectar ao servidor WebSocket.
     */
    void connectWebSocket() {
        Serial.print("Conectando ao WebSocket: ");
        Serial.print(SERVER_HOST);
        Serial.println(SERVER_PATH);

        // Configura o callback de eventos
        // Usamos um lambda ou método estático para evitar problemas com std::bind
        webSocket.onEvent([this](WStype_t type, uint8_t * payload, size_t length) {
            this->webSocketEvent(type, payload, length);
        });
        
        // Inicia a conexão
        webSocket.begin(SERVER_HOST, SERVER_PORT, SERVER_PATH);
        
        // Configura timeouts (similar ao ping_interval/timeout do Python)
        webSocket.setExtraHeaders("User-Agent: ESP32-Robot-Client");
    }

public:
    /**
     * @brief Inicializa o WiFi e prepara o receptor.
     */
    void begin(const char* ssid, const char* pass) {
        Serial.begin(115200); // Inicia serial para logging
        Serial.println();
        Serial.println("Iniciando RobotReceiver (ESP32)...");

        WiFi.begin(ssid, pass);
        Serial.print("Conectando ao WiFi");
        while (WiFi.status() != WL_CONNECTED) {
            delay(500);
            Serial.print(".");
        }
        Serial.println("\nWiFi conectado!");
        Serial.print("Endereço IP: ");
        Serial.println(WiFi.localIP());
    }

    /**
     * @brief Loop principal. Deve ser chamado no loop() do Arduino.
     */
    void loop() {
        // Verifica se o WiFi está conectado
        if (WiFi.status() == WL_CONNECTED) {
            
            // Se o WebSocket não estiver conectado, tenta reconectar
            if (!isConnected) {
                unsigned long now = millis();
                if (now - lastReconnectAttempt > RECONNECT_DELAY_MS) {
                    lastReconnectAttempt = now;
                    Serial.println("Tentando reconectar WebSocket...");
                    connectWebSocket(); 
                }
            }
            
            // Mantém a conexão WebSocket viva e escuta por mensagens
            webSocket.loop();

        } else {
            // WiFi caiu, tenta reconectar
            if (isConnected) {
                 Serial.println("WiFi desconectado! Pausando WebSocket.");
                 isConnected = false;
                 webSocket.disconnect();
            }
            // A biblioteca WiFi do ESP32 geralmente tenta reconectar sozinha
            // Mas podemos forçar, se necessário.
            delay(1000); // Espera um pouco
        }
    }
};