#include "driver\pcnt.h"
#include "driver\timer.h"

#define PinA 34
#define PinB 35

bool flag     = 0;
int16_t MAX_LIM=32767;
int16_t MIN_LIM=-32768;


uint64_t Period = 100;      //micros (1e-6)秒
String inputString = "";  // 通讯指令串

const int list_len = 100; // 一次性上传多少信息
int16_t counter_list[list_len];
int now_key = 0;



void send_msg(){
    Serial.write(highByte(MAX_LIM));
    Serial.write(lowByte(MAX_LIM));
    for (int i = 0; i<list_len; i++){
        // Serial.print(counter_list[i]);
        Serial.write(highByte(counter_list[i]));
        Serial.write(lowByte(counter_list[i]));
        // Serial.print(',');
    }
    flag = false;
}


static bool IRAM_ATTR timer_call_back(void *args){
    bool *a = (bool*) args;
    // 定时回调函数
    pcnt_get_counter_value(PCNT_UNIT_0, &counter_list[now_key]);    
    // counter_list[now_key] = counter;
    now_key ++;
    if(now_key > list_len){
        now_key = 0;
        flag = true;
    }
    return pdTRUE;
}


void set_pcnt(){
    // Configure channel 0
    pcnt_config_t dev_config = {
        .pulse_gpio_num = 34,
        .ctrl_gpio_num  = 35,
        .lctrl_mode     = PCNT_MODE_REVERSE,
        .hctrl_mode     = PCNT_MODE_KEEP,
        .pos_mode       = PCNT_COUNT_DEC,
        .neg_mode       = PCNT_COUNT_DIS,        
        .counter_h_lim  = MAX_LIM,          
        .counter_l_lim  = MIN_LIM,        
        .unit           = PCNT_UNIT_0,
        .channel        = PCNT_CHANNEL_0,
    };
    pcnt_unit_config(&dev_config);
    pcnt_counter_pause(PCNT_UNIT_0);     // 暂停
    pcnt_counter_clear(PCNT_UNIT_0);     // 清除
    pcnt_counter_resume(PCNT_UNIT_0);    // 开始
}

void set_timer(){
    timer_config_t dev_t_config = {
        .alarm_en    = TIMER_ALARM_EN,        /*!< Timer alarm enable */
        .counter_en  = TIMER_START,           /*!< Counter enable */
        .intr_type   = TIMER_INTR_LEVEL,      /*!< Interrupt mode */
        .counter_dir = TIMER_COUNT_UP,        /*!< Counter direction  */
        .auto_reload = TIMER_AUTORELOAD_EN,   /*!< Timer auto-reload */
        .divider     = 80,                    /*!< Counter clock divider. The divider's range is from from 2 to 65536. */
        //.clk_src     = TIMER_SRC_CLK_APB,
    };
    timer_init(TIMER_GROUP_0, TIMER_0, &dev_t_config);
    timer_set_counter_value(TIMER_GROUP_0, TIMER_0, 0);
    timer_set_alarm_value(TIMER_GROUP_0, TIMER_0, Period);
    timer_enable_intr(TIMER_GROUP_0, TIMER_0);
    timer_isr_callback_add(TIMER_GROUP_0, TIMER_0, timer_call_back, &flag, 0);
}


void setup(){

    Serial.begin(250000);
    set_pcnt();
    set_timer();

}

void loop(){
    
    if(flag){
        send_msg();
    }

}