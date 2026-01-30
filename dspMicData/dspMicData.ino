#include <driver/i2s.h>
#include <math.h>

#define I2S_PORT I2S_NUM_0
#define SAMPLE_RATE_HZ 24000.0f

#define MIN_FREQUENCY_HZ 50.0f
#define MAX_FREQUENCY_HZ 350.0f

#define FILTER_HALF_LENGTH 25
#define FILTER_LENGTH (2 * FILTER_HALF_LENGTH + 1)

#define I2S_BCK_PIN 32
#define I2S_WS_PIN  25
#define I2S_DATA_IN_PIN 33

#define INT32_AUDIO_SCALE (-(float)INT32_MIN)

float bandPassKernel[FILTER_LENGTH];
float sampleBuffer[FILTER_LENGTH];
int bufferIndex = 0;

float convertHertzToRadians(float frequencyHertz, float samplingRateHertz) {
    return 2.0f * PI * frequencyHertz / samplingRateHertz;
}

float normalizedSinc(float x) {
    if (x == 0.0f) return 1.0f;
    return sinf(PI * x) / (PI * x);
}

void createLowPassKernel(float cutoffRadiansPerSample, int filterHalfLength, float *kernelOut) {
    for (int n = -filterHalfLength; n <= filterHalfLength; n++) {
        int index = n + filterHalfLength;
        float scaledIndex = (cutoffRadiansPerSample / PI) * n;

        kernelOut[index] = (cutoffRadiansPerSample / PI) * normalizedSinc(scaledIndex);
    }
}

void createBandPassKernel(float lowCutoffHertz, float highCutoffHertz, float samplingRateHertz, int filterHalfLength, float *kernelOut) {
    float lowPassLow[FILTER_LENGTH];
    float lowPassHigh[FILTER_LENGTH];

    float lowCutoffRadians = convertHertzToRadians(lowCutoffHertz, samplingRateHertz);

    float highCutoffRadians = convertHertzToRadians(highCutoffHertz, samplingRateHertz);
    createLowPassKernel(lowCutoffRadians, filterHalfLength, lowPassLow);
    createLowPassKernel(highCutoffRadians, filterHalfLength, lowPassHigh);

    for (int i = 0; i < FILTER_LENGTH; i++) kernelOut[i] = lowPassHigh[i] - lowPassLow[i];
}

void pushSample(float sample) {
    sampleBuffer[bufferIndex] = sample;
    bufferIndex++;
    if (bufferIndex >= FILTER_LENGTH) bufferIndex = 0;
}

float applyFIR() {
    float output = 0.0f;
    int idx = bufferIndex;

    for (int i = 0; i < FILTER_LENGTH; i++) {
        idx--;
        if (idx < 0) idx = FILTER_LENGTH - 1;

        output += sampleBuffer[idx] * bandPassKernel[i];
    }

    return output;
}

void setupI2S()
{
    i2s_config_t config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE_HZ,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = 0,
        .dma_buf_count = 4,
        .dma_buf_len = 256
    };

    i2s_pin_config_t pins = {
        .bck_io_num = I2S_BCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = -1,
        .data_in_num = I2S_DATA_IN_PIN
    };

    i2s_driver_install(I2S_PORT, &config, 0, NULL);
    i2s_set_pin(I2S_PORT, &pins);
}

void setup() {
    Serial.begin(1000000);

    setupI2S();

    createBandPassKernel(MIN_FREQUENCY_HZ, MAX_FREQUENCY_HZ, SAMPLE_RATE_HZ, FILTER_HALF_LENGTH, bandPassKernel
    );

    for (int i = 0; i < FILTER_LENGTH; i++) sampleBuffer[i] = 0.0f;
}

void loop() {
    const int BLOCK_SIZE = 256;
    int32_t samples[BLOCK_SIZE];
    size_t bytesRead = 0;

    i2s_read(I2S_PORT, samples, sizeof(samples), &bytesRead, portMAX_DELAY);

    int count = bytesRead / sizeof(int32_t);

    for (int i = 0; i < count; i++) {
        float input = samples[i] / INT32_AUDIO_SCALE;
        pushSample(input);
        float output = applyFIR();
        samples[i] = (int32_t)(output * INT32_AUDIO_SCALE);
    }

    Serial.write((uint8_t *)samples, bytesRead);
}
