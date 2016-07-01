/*
 * Copyright (c) 2014, Texas Instruments Incorporated - http://www.ti.com/
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */
/*---------------------------------------------------------------------------*/
/**
 * \addtogroup cc26xx-platforms
 * @{
 *
 * \defgroup cc26xx-examples CC26xx Example Projects
 *
 * Example projects for CC26xx-based platforms.
 * @{
 *
 * \defgroup cc26xx-demo CC26xx Demo Project
 *
 *   Example project demonstrating the CC26xx platforms
 *
 *   This example will work for the following boards:
 *   - srf06-cc26xx: SmartRF06EB + CC26XX EM
 *   - sensortag-cc26xx: CC26XX sensortag
 *
 *   By default, the example will build for the srf06-cc26xx board. To switch
 *   between platforms:
 *   - make clean
 *   - make BOARD=sensortag-cc26xx savetarget
 *
 *     or
 *
 *     make BOARD=srf06-cc26xx savetarget
 *
 *   This is an IPv6/RPL-enabled example. Thus, if you have a border router in
 *   your installation (same RDC layer, same PAN ID and RF channel), you should
 *   be able to ping6 this demo node.
 *
 *   This example also demonstrates CC26xx BLE operation. The process starts
 *   the BLE beacon daemon (implemented in the RF driver). The daemon will
 *   send out a BLE beacon periodically. Use any BLE-enabled application (e.g.
 *   LightBlue on OS X or the TI BLE Multitool smartphone app) and after a few
 *   seconds the cc26xx device will be discovered.
 *
 * - etimer/clock : Every CC26XX_DEMO_LOOP_INTERVAL clock ticks the LED defined
 *                  as CC26XX_DEMO_LEDS_PERIODIC will toggle and the device
 *                  will print out readings from some supported sensors
 * - sensors      : Some sensortag sensors are read asynchronously (see sensor
 *                  documentation). For those, this example will print out
 *                  readings in a staggered fashion at a random interval
 * - Buttons      : CC26XX_DEMO_SENSOR_1 button will toggle CC26XX_DEMO_LEDS_BUTTON
 *                - CC26XX_DEMO_SENSOR_2 turns on LEDS_REBOOT and causes a
 *                  watchdog reboot
 *                - The remaining buttons will just print something
 *                - The example also shows how to retrieve the duration of a
 *                  button press (in ticks). The driver will generate a
 *                  sensors_changed event upon button release
 * - Reed Relay   : Will toggle the sensortag buzzer on/off
 *
 * @{
 *
 * \file
 *     Example demonstrating the cc26xx platforms
 */
#include "contiki.h"
#include "sys/etimer.h"
#include "sys/ctimer.h"
#include "dev/leds.h"
#include "dev/watchdog.h"
#include "random.h"
#include "button-sensor.h"
#include "batmon-sensor.h"
#include "board-peripherals.h"
#include "rf-core/rf-ble.h"

#include "net/ip/uip.h"
#include "net/ipv6/uip-ds6.h"
#include "simple-udp.h"
#include "net/ip/uip-debug.h"

#include "ti-lib.h"

#include <stdio.h>
#include <stdint.h>
#include <string.h>
/*---------------------------------------------------------------------------*/
#define CC26XX_DEMO_LOOP_INTERVAL       (CLOCK_SECOND/10)
#define CC26XX_DEMO_LEDS_PERIODIC       LEDS_YELLOW
#define CC26XX_DEMO_LEDS_BUTTON         LEDS_RED
#define CC26XX_DEMO_LEDS_REBOOT         LEDS_ALL
/*---------------------------------------------------------------------------*/     
#define SEND_INTERVAL		     (CLOCK_SECOND/10)
#define SEND_TIME		         (CLOCK_SECOND/10)
#define UDP_PORT 1234
/*---------------------------------------------------------------------------*/
#define CC26XX_DEMO_SENSOR_NONE         (void *)0xFFFFFFFF

#define CC26XX_DEMO_SENSOR_1     &button_left_sensor
#define CC26XX_DEMO_SENSOR_2     &button_right_sensor

#if BOARD_SENSORTAG
#define CC26XX_DEMO_SENSOR_3     CC26XX_DEMO_SENSOR_NONE
#define CC26XX_DEMO_SENSOR_4     CC26XX_DEMO_SENSOR_NONE
#define CC26XX_DEMO_SENSOR_5     &reed_relay_sensor
#else
#define CC26XX_DEMO_SENSOR_3     &button_up_sensor
#define CC26XX_DEMO_SENSOR_4     &button_down_sensor
#define CC26XX_DEMO_SENSOR_5     &button_select_sensor
#endif
/*---------------------------------------------------------------------------*/
//static struct etimer et;
static struct simple_udp_connection broadcast_connection;
/*---------------------------------------------------------------------------*/
PROCESS(cc26xx_demo_process, "cc26xx demo process");
AUTOSTART_PROCESSES(&cc26xx_demo_process);
/*---------------------------------------------------------------------------*/
#if BOARD_SENSORTAG
/*---------------------------------------------------------------------------*/
/*
 * Update sensor readings in a staggered fashion every SENSOR_READING_PERIOD
 * ticks + a random interval between 0 and SENSOR_READING_RANDOM ticks
 */
#define SENSOR_READING_PERIOD (CLOCK_SECOND/10)
#define SENSOR_READING_RANDOM (CLOCK_SECOND << 4)

uint16_t alight[2] = {0,0};
uint16_t ampu[18] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
uint16_t abmp[4] = {0,0,0,0};
uint16_t atmp[4] = {0,0,0,0};
uint16_t ahdc[4] = {0,0,0,0};
uint16_t abat[4] = {0,0,0,0};
//uint16_t asend[36] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
//uint8_t asend2[26] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
uint8_t asend3[3] = {0,0,0};
float mpu[3] = {0.0,0.0,0.0};
uint8_t old_in_use = 0;
unsigned count = 0;

//static struct ctimer bmp_timer, opt_timer, hdc_timer, tmp_timer, mpu_timer;
static struct ctimer mpu_timer;
/*---------------------------------------------------------------------------*/
/*
static void init_bmp_reading(void *not_used);
static void init_opt_reading(void *not_used);
static void init_hdc_reading(void *not_used);
static void init_tmp_reading(void *not_used);*/
static void init_mpu_reading(void *not_used);
/*---------------------------------------------------------------------------*/
/*
static void
print_mpu_reading(int reading)
{
  if(reading < 0) {
    printf("-");
    reading = -reading;
  }

  printf("%d.%02d", reading / 100, reading % 100);
}
*/
/*---------------------------------------------------------------------------*/
/*
static void
get_bmp_reading()
{
  int value;
  clock_time_t next = SENSOR_READING_PERIOD +
    (random_rand() % SENSOR_READING_RANDOM);

  value = bmp_280_sensor.value(BMP_280_SENSOR_TYPE_PRESS);
  if(value != CC26XX_SENSOR_READING_ERROR) {
    //printf("BAR: Pressure=%d.%02d hPa\r\n", value / 100, value % 100);
    abmp[0] = value / 100;
    abmp[1] = value % 100;
  } else {
    //printf("BAR: Pressure Read Error\r\n");
  }

  value = bmp_280_sensor.value(BMP_280_SENSOR_TYPE_TEMP);
  if(value != CC26XX_SENSOR_READING_ERROR) {
    //printf("BAR: Temp=%d.%02d C\r\n", value / 100, value % 100);
    abmp[2] = value / 100;
    abmp[3] = value % 100;
  } else {
    //printf("BAR: Temperature Read Error\r\n");
  }

  SENSORS_DEACTIVATE(bmp_280_sensor);

  ctimer_set(&bmp_timer, next, init_bmp_reading, NULL);
}
*/
/*---------------------------------------------------------------------------*/
/*
static void
get_tmp_reading()
{
  int value;
  clock_time_t next = SENSOR_READING_PERIOD +
    (random_rand() % SENSOR_READING_RANDOM);

  value = tmp_007_sensor.value(TMP_007_SENSOR_TYPE_ALL);

  if(value == CC26XX_SENSOR_READING_ERROR) {
    //printf("TMP: Ambient Read Error\r\n");
    return;
  }

  value = tmp_007_sensor.value(TMP_007_SENSOR_TYPE_AMBIENT);
  //printf("TMP: Ambient=%d.%03d C\r\n", value / 1000, value % 1000);
atmp[0] = value / 1000;
atmp[1] = value % 1000;

  value = tmp_007_sensor.value(TMP_007_SENSOR_TYPE_OBJECT);
  //printf("TMP: Object=%d.%03d C\r\n", value / 1000, value % 1000);
atmp[2] = value / 1000;
atmp[3] = value % 1000;

  SENSORS_DEACTIVATE(tmp_007_sensor);

  ctimer_set(&tmp_timer, next, init_tmp_reading, NULL);
}
*/
/*---------------------------------------------------------------------------*/
/*
static void
get_hdc_reading()
{
  int value;
  clock_time_t next = SENSOR_READING_PERIOD +
    (random_rand() % SENSOR_READING_RANDOM);

  value = hdc_1000_sensor.value(HDC_1000_SENSOR_TYPE_TEMP);
  if(value != CC26XX_SENSOR_READING_ERROR) {
    //printf("HDC: Temp=%d.%02d C\r\n", value / 100, value % 100);
ahdc[0] = value / 100;
ahdc[1] = value % 100;
  } else {
    //printf("HDC: Temp Read Error\r\n");
  }

  value = hdc_1000_sensor.value(HDC_1000_SENSOR_TYPE_HUMIDITY);
  if(value != CC26XX_SENSOR_READING_ERROR) {
    //printf("HDC: Humidity=%d.%02d %%RH\r\n", value / 100, value % 100);
ahdc[2] = value / 100;
ahdc[3] = value % 100;
  } else {
    //printf("HDC: Humidity Read Error\r\n");
  }

  ctimer_set(&hdc_timer, next, init_hdc_reading, NULL);
}
*/
/*---------------------------------------------------------------------------*/
/*
static void
get_light_reading()
{
  int value;
  clock_time_t next = SENSOR_READING_PERIOD +
    (random_rand() % SENSOR_READING_RANDOM);

  value = opt_3001_sensor.value(0);
  if(value != CC26XX_SENSOR_READING_ERROR) {
    //printf("OPT: Light=%d.%02d lux\r\n", value / 100, value % 100);
abmp[0] = value / 100;
abmp[1] = value % 100;
  } else {
    //printf("OPT: Light Read Error\r\n");
  }
*/
  /* The OPT will turn itself off, so we don't need to call its DEACTIVATE */
/*
  ctimer_set(&opt_timer, next, init_opt_reading, NULL);
}
*/
/*---------------------------------------------------------------------------*/
static void
get_mpu_reading()
{
  int value;
  //clock_time_t next = SENSOR_READING_PERIOD +
  //  (random_rand() % SENSOR_READING_RANDOM);
  clock_time_t next = SENSOR_READING_PERIOD;

  //printf("MPU Gyro: X=");
  value = mpu_9250_sensor.value(MPU_9250_SENSOR_TYPE_GYRO_X);
  mpu[0] = abs(value)/100.0;
  //print_mpu_reading(value);
if(value < 0){
ampu[0] = 1;
}else{
ampu[0] = 0;
}
ampu[1] = abs(value) / 100;
ampu[2] = abs(value) % 100;
  //printf(" deg/sec\r\n");

  //printf("MPU Gyro: Y=");
  value = mpu_9250_sensor.value(MPU_9250_SENSOR_TYPE_GYRO_Y);
  mpu[1] = abs(value)/100.0;
  //print_mpu_reading(value);
if(value < 0){
ampu[3] = 1;
}else{
ampu[3] = 0;
}
ampu[4] = abs(value) / 100;
ampu[5] = abs(value) % 100;
  //printf(" deg/sec\r\n");

  //printf("MPU Gyro: Z=");
  value = mpu_9250_sensor.value(MPU_9250_SENSOR_TYPE_GYRO_Z);
  mpu[2] = abs(value)/100.0;
  //print_mpu_reading(value);
if(value < 0){
ampu[6] = 1;
}else{
ampu[6] = 0;
}
ampu[7] = abs(value) / 100;
ampu[8] = abs(value) % 100;
  //printf(" deg/sec\r\n");

  //printf("MPU Acc: X=");
  value = mpu_9250_sensor.value(MPU_9250_SENSOR_TYPE_ACC_X);
  //print_mpu_reading(value);
if(value < 0){
ampu[9] = 1;
}else{
ampu[9] = 0;
}
ampu[10] = abs(value) / 100;
ampu[11] = abs(value) % 100;
  //printf(" G\r\n");

  //printf("MPU Acc: Y=");
  value = mpu_9250_sensor.value(MPU_9250_SENSOR_TYPE_ACC_Y);
  //print_mpu_reading(value);
if(value < 0){
ampu[12] = 1;
}else{
ampu[12] = 0;
}
ampu[13] = abs(value) / 100;
ampu[14] = abs(value) % 100;
  //printf(" G\r\n");

  //printf("MPU Acc: Z=");
  value = mpu_9250_sensor.value(MPU_9250_SENSOR_TYPE_ACC_Z);
  //print_mpu_reading(value);
if(value < 0){
ampu[15] = 1;
}else{
ampu[15] = 0;
}
  ampu[16] = abs(value) / 100;
ampu[17] = abs(value) % 100;
  //printf(" G\r\n");

  SENSORS_DEACTIVATE(mpu_9250_sensor);

  ctimer_set(&mpu_timer, next, init_mpu_reading, NULL);
}
/*---------------------------------------------------------------------------*/
/*
static void
init_bmp_reading(void *not_used)
{
  SENSORS_ACTIVATE(bmp_280_sensor);
}
*/
/*---------------------------------------------------------------------------*/
/*
static void
init_opt_reading(void *not_used)
{
  SENSORS_ACTIVATE(opt_3001_sensor);
}
*/
/*---------------------------------------------------------------------------*/
/*
static void
init_hdc_reading(void *not_used)
{
  SENSORS_ACTIVATE(hdc_1000_sensor);
}
*/
/*---------------------------------------------------------------------------*/
/*
static void
init_tmp_reading(void *not_used)
{
  SENSORS_ACTIVATE(tmp_007_sensor);
}
*/
/*---------------------------------------------------------------------------*/
static void
init_mpu_reading(void *not_used)
{
  mpu_9250_sensor.configure(SENSORS_ACTIVE, MPU_9250_SENSOR_TYPE_ALL);
}
#endif
/*---------------------------------------------------------------------------*/
static void
get_sync_sensor_readings(void)
{
  int value;

  //printf("-----------------------------------------\r\n");

  //value = batmon_sensor.value(BATMON_SENSOR_TYPE_TEMP);
  //printf("Bat: Temp=%d C\r\n", value);
  //abat[0] = value;


  value = batmon_sensor.value(BATMON_SENSOR_TYPE_VOLT);
  //printf("Bat: Volt=%d mV\r\n", (value * 125) >> 5);
  abat[1] = (abs(value) * 125) >> 5;
  return;
}
/*---------------------------------------------------------------------------*/
static void
init_sensors(void)
{
#if BOARD_SENSORTAG
  SENSORS_ACTIVATE(reed_relay_sensor);
#endif

  SENSORS_ACTIVATE(batmon_sensor);
}
/*---------------------------------------------------------------------------*/
static void
init_sensor_readings(void)
{
#if BOARD_SENSORTAG
  //SENSORS_ACTIVATE(hdc_1000_sensor);
  //SENSORS_ACTIVATE(tmp_007_sensor);
  //SENSORS_ACTIVATE(opt_3001_sensor);
  //SENSORS_ACTIVATE(bmp_280_sensor);

  init_mpu_reading(NULL);
#endif
}
/*---------------------------------------------------------------------------*/
/*static void
receiver(struct simple_udp_connection *c,
         const uip_ipaddr_t *sender_addr,
         uint16_t sender_port,
         const uip_ipaddr_t *receiver_addr,
         uint16_t receiver_port,
         const uint8_t *data,
         uint16_t datalen)
{
  //printf("Data received on port %d from port %d with length %d\r\n",
  //       receiver_port, sender_port, datalen);
  //printf("Sender: ");
  uip_debug_ipaddr_print(sender_addr);
  printf("\r\n");
  printf("%d\r\n",data[2]);
  printf("%d\r\n\r\n", (data[0]<<8)|data[1]);
}*/
  //printf("Receiver: ");
  //uip_debug_ipaddr_print(receiver_addr);
  //printf("\r\n");
/*
  printf("OPTION 1:\r\n");
  printf("Gyro X: %d.%d\r\n",((data[6]<<8)|data[7]),((data[8]<<8)|data[9]));
  printf("Gyro Y: %d.%d\r\n",((data[12]<<8)|data[13]),((data[14]<<8)|data[15]));
  printf("Gyro Z: %d.%d\r\n",((data[18]<<8)|data[19]),((data[20]<<8)|data[21]));
  printf("Acc X: %d.%d\r\n",((data[24]<<8)|data[25]),((data[26]<<8)|data[27]));
  printf("Acc Y: %d.%d\r\n",((data[30]<<8)|data[31]),((data[32]<<8)|data[33]));
  printf("Acc Z: %d.%d\r\n",((data[36]<<8)|data[37]),((data[38]<<8)|data[39]));
  printf("Bat mV: %d\r\n",((data[66]<<8)|data[67]));
  printf("OPTION 2:\r\n");
  printf("Gyro X: %d.%d\r\n",(data[6]|(data[7]<<8)),(data[8]|(data[9]<<8)));
  printf("Gyro Y: %d.%d\r\n",(data[12]|(data[13]<<8)),(data[14]|(data[15]<<8)));
  printf("Gyro Z: %d.%d\r\n",(data[18]|(data[19]<<8)),(data[20]|(data[21]<<8)));
  printf("Acc X: %d.%d\r\n",(data[24]|(data[25]<<8)),(data[26]|(data[27]<<8)));
  printf("Acc Y: %d.%d\r\n",(data[30]|(data[31]<<8)),(data[32]|(data[33]<<8)));
  printf("Acc Z: %d.%d\r\n",(data[36]|(data[37]<<8)),(data[38]|(data[39]<<8)));
  printf("Bat mV: %d\r\n",(data[66]|(data[67]<<8)));
*/
  /*printf("Bat mV: %d\r\n", (data[0]<<8)|data[1]);
  printf("Gyro X: %d.%02d\r\n", (data[2]<<8)|data[3], (data[4]<<8)|data[5]);
  printf("Gyro Y: %d.%02d\r\n", (data[6]<<8)|data[7], (data[8]<<8)|data[9]);
  printf("Gyro Z: %d.%02d\r\n", (data[10]<<8)|data[11], (data[12]<<8)|data[13]);
  printf("Acc X: %d.%02d\r\n", (data[14]<<8)|data[15], (data[16]<<8)|data[17]);
  printf("Acc Y: %d.%02d\r\n", (data[18]<<8)|data[19], (data[20]<<8)|data[21]);
  printf("Acc Z: %d.%02d\r\n", (data[22]<<8)|data[23], (data[24]<<8)|data[25]);*/

  /*printf("%d.%02d\r\n", (data[2]<<8)|data[3], (data[4]<<8)|data[5]);
  printf("%d.%02d\r\n", (data[6]<<8)|data[7], (data[8]<<8)|data[9]);
  printf("%d.%02d\r\n", (data[10]<<8)|data[11], (data[12]<<8)|data[13]);
  printf("%d.%02d\r\n", (data[14]<<8)|data[15], (data[16]<<8)|data[17]);
  printf("%d.%02d\r\n", (data[18]<<8)|data[19], (data[20]<<8)|data[21]);
  printf("%d.%02d\r\n", (data[22]<<8)|data[23], (data[24]<<8)|data[25]);
  printf("%d\r\n\r\n", (data[0]<<8)|data[1]);
}*/
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(cc26xx_demo_process, ev, data)
{
  /* udp */
  //static struct etimer periodic_timer;
  //static struct etimer send_timer;
  uip_ipaddr_t addr;
  uint8_t in_use = 0;

  PROCESS_BEGIN();
    
  simple_udp_register(&broadcast_connection, UDP_PORT,
                      NULL, UDP_PORT, NULL);
                      //receiver);

  //printf("CC26XX demo\r\n");

  init_sensors();

  /* Init the BLE advertisement daemon */
  //rf_ble_beacond_config(0, BOARD_STRING);
  //rf_ble_beacond_start();

  //etimer_set(&et, CC26XX_DEMO_LOOP_INTERVAL);
  //get_sync_sensor_readings();
  init_sensor_readings();

    
   // etimer_set(&periodic_timer, SEND_INTERVAL);
  while(1) {
	PROCESS_YIELD();
      
    //PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&periodic_timer));
    //etimer_reset(&periodic_timer);
    //etimer_set(&send_timer, SEND_TIME);
//leds_toggle(CC26XX_DEMO_LEDS_PERIODIC);
    //get_sync_sensor_readings();

 // etimer_set(&et, CC26XX_DEMO_LOOP_INTERVAL);

      get_mpu_reading();
      /*if(ev == sensors_event && data == &bmp_280_sensor) {
        get_bmp_reading();
      } else if(ev == sensors_event && data == &opt_3001_sensor) {
        get_light_reading();
      } else if(ev == sensors_event && data == &hdc_1000_sensor) {
        get_hdc_reading();
      } else if(ev == sensors_event && data == &tmp_007_sensor) {
        get_tmp_reading();
      } else if(ev == sensors_event && data == &mpu_9250_sensor) {
        get_mpu_reading();
      } */
    //printf("Sending broadcast\r\n");
    //uip_create_linklocal_allnodes_mcast(&addr);

/*asend[0] = alight[0];
asend[1] = alight[1];
asend[2] = ampu[0];
asend[3] = ampu[1];
asend[4] = ampu[2];
asend[5] = ampu[3];
asend[6] = ampu[4];
asend[7] = ampu[5];
asend[8] = ampu[6];
asend[9] = ampu[7];
asend[10] = ampu[8];
asend[11] = ampu[9];
asend[12] = ampu[10];
asend[13] = ampu[11];
asend[14] = ampu[12];
asend[15] = ampu[13];
asend[16] = ampu[14];
asend[17] = ampu[15];
asend[18] = ampu[16];
asend[19] = ampu[17];
asend[20] = abmp[0];
asend[21] = abmp[1];
asend[22] = abmp[2];
asend[23] = abmp[3];
asend[24] = atmp[0];
asend[25] = atmp[1];
asend[26] = atmp[2];
asend[27] = atmp[3];
asend[28] = ahdc[0];
asend[29] = ahdc[1];
asend[30] = ahdc[2];
asend[31] = ahdc[3];
asend[32] = abat[0];
asend[33] = abat[1];
asend[34] = abat[2];
asend[35] = abat[3];*/

/*asend2[0] = abat[1] >> 8;
asend2[1] = abat[1] & 0xFF;
asend2[2] = ampu[1] >> 8;
asend2[3] = ampu[1] & 0xFF;
asend2[4] = ampu[2] >> 8;
asend2[5] = ampu[2] & 0xFF;
asend2[6] = ampu[4] >> 8;
asend2[7] = ampu[4] & 0xFF;
asend2[8] = ampu[5] >> 8;
asend2[9] = ampu[5] & 0xFF;
asend2[10] = ampu[7] >> 8;
asend2[11] = ampu[7] & 0xFF;
asend2[12] = ampu[8] >> 8;
asend2[13] = ampu[8] & 0xFF;
asend2[14] = ampu[10] >> 8;
asend2[15] = ampu[10] & 0xFF;
asend2[16] = ampu[11] >> 8;
asend2[17] = ampu[11] & 0xFF;
asend2[18] = ampu[13] >> 8;
asend2[19] = ampu[13] & 0xFF;
asend2[20] = ampu[14] >> 8;
asend2[21] = ampu[14] & 0xFF;
asend2[22] = ampu[16] >> 8;
asend2[23] = ampu[16] & 0xFF;
asend2[24] = ampu[17] >> 8;
asend2[25] = ampu[17] & 0xFF;*/

in_use = 0;
if((mpu[0]+mpu[1]+mpu[2]) >= 16)
{
  in_use = 1;
}
if((in_use != old_in_use) || (count >= 20))
{
  get_sync_sensor_readings();
  asend3[0] = abat[1] >> 8;
  asend3[1] = abat[1] & 0xFF;
  asend3[2] = in_use;
  uip_create_linklocal_allnodes_mcast(&addr);
  simple_udp_sendto(&broadcast_connection, asend3, sizeof(asend3), &addr);
  count = 0;
}
else
{
  count++;
}
old_in_use = in_use;

  //printf("Bat mV: %d\r\n", (asend2[0]<<8)|asend2[1]);
  //printf("Gyro X: %d.%02d\r\n", (asend2[2]<<8)|asend2[3], (asend2[4]<<8)|asend2[5]);
  //printf("Gyro Y: %d.%02d\r\n", (asend2[6]<<8)|asend2[7], (asend2[8]<<8)|asend2[9]);
  //printf("Gyro Z: %d.%02d\r\n", (asend2[10]<<8)|asend2[11], (asend2[12]<<8)|asend2[13]);
  //printf("Acc X: %d.%02d\r\n", (asend2[14]<<8)|asend2[15], (asend2[16]<<8)|asend2[17]);
  //printf("Acc Y: %d.%02d\r\n", (asend2[18]<<8)|asend2[19], (asend2[20]<<8)|asend2[21]);
  //printf("Acc Z: %d.%02d\r\n", (asend2[22]<<8)|asend2[23], (asend2[24]<<8)|asend2[25]);

//printf("TMP: %d-%d-%d-%d \r\nBAT:%d-%d-%d-%d", asend[24],asend[25],asend[26],asend[27],asend[32],asend[33],asend[34],asend[35]);
    //simple_udp_sendto(&broadcast_connection, asend3, sizeof(asend3), &addr);
    //printf("Sending broadcast success\r\n");
    }
    PROCESS_END();
    
}
/*---------------------------------------------------------------------------*/
/**
 * @}
 * @}
 * @}
 */
