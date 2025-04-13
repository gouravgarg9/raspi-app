#include <DHT.h>

#define MQ135_PIN A0
#define MQ2_PIN A1
#define TRIG_PIN 6
#define ECHO_PIN 7
#define DHT_PIN 5
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
    Serial.begin(115200);
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    dht.begin();
}

void loop() {
    int mq135_value = analogRead(MQ135_PIN);
    int mq2_value = analogRead(MQ2_PIN);

    // Ultrasonic Sensor Distance Measurement
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH);
    float distance = duration * 0.034 / 2; // Convert to cm

    // Read temperature and humidity
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    // Handle read errors
    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("Error reading from DHT11 sensor");
    } else {
        // Send data in CSV format: mq135, mq2, distance, temperature, humidity
        Serial.print(mq135_value);
        Serial.print(",");
        Serial.print(mq2_value);
        Serial.print(",");
        Serial.print(distance);
        Serial.print(",");
        Serial.print(temperature);
        Serial.print(",");
        Serial.println(humidity);
    }

    delay(500);
}
