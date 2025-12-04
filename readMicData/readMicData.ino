//https://docs.espressif.com/projects/esp-idf/en/v4.2.3/esp32/api-reference/peripherals/i2s.html

#include <driver/i2s.h>

#define I2S I2S_NUM_0
#define SAMPLERATE 24000

#define WS 25
#define SD 33
#define SCK 32

void setup() {
  Serial.begin(1000000);

  i2s_config_t config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLERATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = 0,
    .dma_buf_count = 4,
    .dma_buf_len = 1024
  };

  i2s_pin_config_t pins = {
    .bck_io_num = SCK,
    .ws_io_num = WS,
    .data_out_num = -1,
    .data_in_num = SD
  };

  i2s_driver_install(I2S, &config, 0, NULL);
  i2s_set_pin(I2S, &pins);
}

void loop() {
  int32_t buffer[512];
  size_t bytesRead = 0;

  i2s_read(I2S, buffer, sizeof(buffer), &bytesRead, portMAX_DELAY);
  Serial.write((uint8_t*)buffer, bytesRead);
}
