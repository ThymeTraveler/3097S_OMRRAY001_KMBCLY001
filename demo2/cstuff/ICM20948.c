#include "ICM20948.h"
#include <stdlib.h>
#include <string.h>
#include <bcm2835.h>

IMU_ST_SENSOR_DATA gstGyroOffset ={0,0,0};  
#ifdef __cplusplus
extern "C" {
#endif

void imuAHRSupdate(float gx, float gy, float gz, float ax, float ay, float az, float mx, float my, float mz);
float invSqrt(float x);

void icm20948init(void);
bool icm20948Check(void);
void icm20948GyroRead(int16_t* ps16X, int16_t* ps16Y, int16_t* ps16Z);
void icm20948AccelRead(int16_t* ps16X, int16_t* ps16Y, int16_t* ps16Z);
void icm20948MagRead(int16_t* ps16X, int16_t* ps16Y, int16_t* ps16Z);
bool icm20948MagCheck(void);
void icm20948CalAvgValue(uint8_t *pIndex, int16_t *pAvgBuffer, int16_t InVal, int32_t *pOutVal);
void icm20948GyroOffset(void);
void icm20948ReadSecondary(uint8_t u8I2CAddr, uint8_t u8RegAddr, uint8_t u8Len, uint8_t *pu8data);
void icm20948WriteSecondary(uint8_t u8I2CAddr, uint8_t u8RegAddr, uint8_t u8data);
bool icm20948Check(void);
/******************************************************************************
 * interface driver                                                           *
 ******************************************************************************/
 //Raspberry 3B+ platform's default I2C device file
#define IIC_Dev  "/dev/i2c-1"

int fd;



char I2C_ReadOneByte(char reg)
{
	char buf[] = { reg };
	bcm2835_i2c_read_register_rs(buf, buf, 1);
	return buf[0];
}

void I2C_WriteOneByte(char reg, char val)
{
	char buf[] = { reg,val };
	bcm2835_i2c_write(buf, 2);
}
/******************************************************************************
 * IMU module                                                                 *
 ******************************************************************************/
#define Kp 4.50f   // proportional gain governs rate of convergence to accelerometer/magnetometer
#define Ki 1.0f    // integral gain governs rate of convergence of gyroscope biases

float angles[3];
float q0, q1, q2, q3; 

void imuInit(IMU_EN_SENSOR_TYPE *penMotionSensorType)
{
  bool bRet = false;
  
  bcm2835_init();
  bcm2835_i2c_begin();
  bcm2835_i2c_setSlaveAddress(I2C_ADD_ICM20948);
  bcm2835_i2c_set_baudrate(10000);
  bRet = icm20948Check();
  if( true == bRet)
  {
    *penMotionSensorType = IMU_EN_SENSOR_TYPE_ICM20948;
    icm20948init();
  }
  else
  {
    *penMotionSensorType = IMU_EN_SENSOR_TYPE_NULL;
  }
  q0 = 1.0f;  
  q1 = 0.0f;
  q2 = 0.0f;
  q3 = 0.0f;

  return;
}
void imuDataGet(IMU_ST_ANGLES_DATA *pstAngles, 
                IMU_ST_SENSOR_DATA *pstGyroRawData,
                IMU_ST_SENSOR_DATA *pstAccelRawData,
                IMU_ST_SENSOR_DATA *pstMagnRawData)
{
  float MotionVal[9];
  int16_t s16Gyro[3], s16Accel[3], s16Magn[3];

  icm20948AccelRead(&s16Accel[0], &s16Accel[1], &s16Accel[2]);
  icm20948GyroRead(&s16Gyro[0], &s16Gyro[1], &s16Gyro[2]);
  icm20948MagRead(&s16Magn[0], &s16Magn[1], &s16Magn[2]);

  MotionVal[0]=s16Gyro[0]/32.8;
  MotionVal[1]=s16Gyro[1]/32.8;
  MotionVal[2]=s16Gyro[2]/32.8;
  MotionVal[3]=s16Accel[0];
  MotionVal[4]=s16Accel[1];
  MotionVal[5]=s16Accel[2];
  MotionVal[6]=s16Magn[0];
  MotionVal[7]=s16Magn[1];
  MotionVal[8]=s16Magn[2];
  imuAHRSupdate((float)MotionVal[0] * 0.0175, (float)MotionVal[1] * 0.0175, (float)MotionVal[2] * 0.0175,
                (float)MotionVal[3], (float)MotionVal[4], (float)MotionVal[5], 
                (float)MotionVal[6], (float)MotionVal[7], MotionVal[8]);


  pstAngles->fPitch = asin(-2 * q1 * q3 + 2 * q0* q2)* 57.3; // pitch
  pstAngles->fRoll = atan2(2 * q2 * q3 + 2 * q0 * q1, -2 * q1 * q1 - 2 * q2* q2 + 1)* 57.3; // roll
  pstAngles->fYaw = atan2(-2 * q1 * q2 - 2 * q0 * q3, 2 * q2 * q2 + 2 * q3 * q3 - 1) * 57.3; 

  pstGyroRawData->s16X = s16Gyro[0];
  pstGyroRawData->s16Y = s16Gyro[1];
  pstGyroRawData->s16Z = s16Gyro[2];

  pstAccelRawData->s16X = s16Accel[0];
  pstAccelRawData->s16Y = s16Accel[1];
  pstAccelRawData->s16Z  = s16Accel[2];

  pstMagnRawData->s16X = s16Magn[0];
  pstMagnRawData->s16Y = s16Magn[1];
  pstMagnRawData->s16Z = s16Magn[2];  

  return;  
}

void imuAHRSupdate(float gx, float gy, float gz, float ax, float ay, float az, float mx, float my, float mz) 
{
  float norm;
  float hx, hy, hz, bx, bz;
  float vx, vy, vz, wx, wy, wz;
  float exInt = 0.0, eyInt = 0.0, ezInt = 0.0;
  float ex, ey, ez, halfT = 0.024f;

  float q0q0 = q0 * q0;
  float q0q1 = q0 * q1;
  float q0q2 = q0 * q2;
  float q0q3 = q0 * q3;
  float q1q1 = q1 * q1;
  float q1q2 = q1 * q2;
  float q1q3 = q1 * q3;
  float q2q2 = q2 * q2;   
  float q2q3 = q2 * q3;
  float q3q3 = q3 * q3;          

  norm = invSqrt(ax * ax + ay * ay + az * az);       
  ax = ax * norm;
  ay = ay * norm;
  az = az * norm;

  norm = invSqrt(mx * mx + my * my + mz * mz);          
  mx = mx * norm;
  my = my * norm;
  mz = mz * norm;

  // compute reference direction of flux
  hx = 2 * mx * (0.5f - q2q2 - q3q3) + 2 * my * (q1q2 - q0q3) + 2 * mz * (q1q3 + q0q2);
  hy = 2 * mx * (q1q2 + q0q3) + 2 * my * (0.5f - q1q1 - q3q3) + 2 * mz * (q2q3 - q0q1);
  hz = 2 * mx * (q1q3 - q0q2) + 2 * my * (q2q3 + q0q1) + 2 * mz * (0.5f - q1q1 - q2q2);         
  bx = sqrt((hx * hx) + (hy * hy));
  bz = hz;     

  // estimated direction of gravity and flux (v and w)
  vx = 2 * (q1q3 - q0q2);
  vy = 2 * (q0q1 + q2q3);
  vz = q0q0 - q1q1 - q2q2 + q3q3;
  wx = 2 * bx * (0.5 - q2q2 - q3q3) + 2 * bz * (q1q3 - q0q2);
  wy = 2 * bx * (q1q2 - q0q3) + 2 * bz * (q0q1 + q2q3);
  wz = 2 * bx * (q0q2 + q1q3) + 2 * bz * (0.5 - q1q1 - q2q2);  

  // error is sum of cross product between reference direction of fields and direction measured by sensors
  ex = (ay * vz - az * vy) + (my * wz - mz * wy);
  ey = (az * vx - ax * vz) + (mz * wx - mx * wz);
  ez = (ax * vy - ay * vx) + (mx * wy - my * wx);

  if(ex != 0.0f && ey != 0.0f && ez != 0.0f)
  {
    exInt = exInt + ex * Ki * halfT;
    eyInt = eyInt + ey * Ki * halfT;  
    ezInt = ezInt + ez * Ki * halfT;

    gx = gx + Kp * ex + exInt;
    gy = gy + Kp * ey + eyInt;
    gz = gz + Kp * ez + ezInt;
  }

  q0 = q0 + (-q1 * gx - q2 * gy - q3 * gz) * halfT;
  q1 = q1 + (q0 * gx + q2 * gz - q3 * gy) * halfT;
  q2 = q2 + (q0 * gy - q1 * gz + q3 * gx) * halfT;
  q3 = q3 + (q0 * gz + q1 * gy - q2 * gx) * halfT;  

  norm = invSqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);
  q0 = q0 * norm;
  q1 = q1 * norm;
  q2 = q2 * norm;
  q3 = q3 * norm;
}

float invSqrt(float x) 
{
  float halfx = 0.5f * x;
  float y = x;
  
  long i = *(long*)&y;                //get bits for floating value
  i = 0x5f3759df - (i >> 1);          //gives initial guss you
  y = *(float*)&i;                    //convert bits back to float
  y = y * (1.5f - (halfx * y * y));   //newtop step, repeating increases accuracy
  
  return y;
}
/******************************************************************************
 * icm20948 sensor device                                                     *
 ******************************************************************************/
void icm20948init(void)
{

  /* user bank 0 register */
  I2C_WriteOneByte( REG_ADD_REG_BANK_SEL, REG_VAL_REG_BANK_0);
  I2C_WriteOneByte( REG_ADD_PWR_MIGMT_1,  REG_VAL_ALL_RGE_RESET);
  bcm2835_delay(10);
  I2C_WriteOneByte( REG_ADD_PWR_MIGMT_1,  REG_VAL_RUN_MODE);  

  /* user bank 2 register */
  I2C_WriteOneByte( REG_ADD_REG_BANK_SEL, REG_VAL_REG_BANK_2);
  I2C_WriteOneByte( REG_ADD_GYRO_SMPLRT_DIV, 0x07);
  I2C_WriteOneByte( REG_ADD_GYRO_CONFIG_1,   
                  REG_VAL_BIT_GYRO_DLPCFG_6 | REG_VAL_BIT_GYRO_FS_1000DPS | REG_VAL_BIT_GYRO_DLPF);
  I2C_WriteOneByte( REG_ADD_ACCEL_SMPLRT_DIV_2,  0x07);
  I2C_WriteOneByte( REG_ADD_ACCEL_CONFIG,
                  REG_VAL_BIT_ACCEL_DLPCFG_6 | REG_VAL_BIT_ACCEL_FS_2g | REG_VAL_BIT_ACCEL_DLPF);

  /* user bank 0 register */
  I2C_WriteOneByte( REG_ADD_REG_BANK_SEL, REG_VAL_REG_BANK_0); 

  bcm2835_delay(100);
  /* offset */
  icm20948GyroOffset();

  icm20948MagCheck();

  icm20948WriteSecondary( I2C_ADD_ICM20948_AK09916|I2C_ADD_ICM20948_AK09916_WRITE,
                               REG_ADD_MAG_CNTL2, REG_VAL_MAG_MODE_20HZ);  
  return;
}

bool icm20948Check(void)
{
    bool bRet = false;
    if(REG_VAL_WIA == I2C_ReadOneByte( REG_ADD_WIA))
    {
        bRet = true;
    }
    return bRet;
}
void icm20948GyroRead(int16_t* ps16X, int16_t* ps16Y, int16_t* ps16Z)
{
   uint8_t u8Buf[6];
    int16_t s16Buf[3] = {0}; 
    uint8_t i;
    int32_t s32OutBuf[3] = {0};
    static ICM20948_ST_AVG_DATA sstAvgBuf[3];
    static int16_t ss16c = 0;
    ss16c++;

    u8Buf[0]=I2C_ReadOneByte(REG_ADD_GYRO_XOUT_L); 
    u8Buf[1]=I2C_ReadOneByte(REG_ADD_GYRO_XOUT_H);
    s16Buf[0]=  (u8Buf[1]<<8)|u8Buf[0];

    u8Buf[0]=I2C_ReadOneByte(REG_ADD_GYRO_YOUT_L); 
    u8Buf[1]=I2C_ReadOneByte(REG_ADD_GYRO_YOUT_H);
    s16Buf[1]=  (u8Buf[1]<<8)|u8Buf[0];

    u8Buf[0]=I2C_ReadOneByte(REG_ADD_GYRO_ZOUT_L); 
    u8Buf[1]=I2C_ReadOneByte(REG_ADD_GYRO_ZOUT_H);
    s16Buf[2]=  (u8Buf[1]<<8)|u8Buf[0];

    for(i = 0; i < 3; i ++) 
    {
        icm20948CalAvgValue(&sstAvgBuf[i].u8Index, sstAvgBuf[i].s16AvgBuffer, s16Buf[i], s32OutBuf + i);
    }
    *ps16X = s32OutBuf[0] - gstGyroOffset.s16X;
    *ps16Y = s32OutBuf[1] - gstGyroOffset.s16Y;
    *ps16Z = s32OutBuf[2] - gstGyroOffset.s16Z;
    
    return;
}
void icm20948AccelRead(int16_t* ps16X, int16_t* ps16Y, int16_t* ps16Z)
{
    uint8_t u8Buf[2];
    int16_t s16Buf[3] = {0}; 
    uint8_t i;
    int32_t s32OutBuf[3] = {0};
    static ICM20948_ST_AVG_DATA sstAvgBuf[3];

    u8Buf[0]=I2C_ReadOneByte(REG_ADD_ACCEL_XOUT_L); 
    u8Buf[1]=I2C_ReadOneByte(REG_ADD_ACCEL_XOUT_H);
    s16Buf[0]=  (u8Buf[1]<<8)|u8Buf[0];

    u8Buf[0]=I2C_ReadOneByte(REG_ADD_ACCEL_YOUT_L); 
    u8Buf[1]=I2C_ReadOneByte(REG_ADD_ACCEL_YOUT_H);
    s16Buf[1]=  (u8Buf[1]<<8)|u8Buf[0];

    u8Buf[0]=I2C_ReadOneByte(REG_ADD_ACCEL_ZOUT_L); 
    u8Buf[1]=I2C_ReadOneByte(REG_ADD_ACCEL_ZOUT_H);
    s16Buf[2]=  (u8Buf[1]<<8)|u8Buf[0];

    for(i = 0; i < 3; i ++) 
    {
        icm20948CalAvgValue(&sstAvgBuf[i].u8Index, sstAvgBuf[i].s16AvgBuffer, s16Buf[i], s32OutBuf + i);
    }
    *ps16X = s32OutBuf[0];
    *ps16Y = s32OutBuf[1];
    *ps16Z = s32OutBuf[2];
  
    return;

}
void icm20948MagRead(int16_t* ps16X, int16_t* ps16Y, int16_t* ps16Z)
{
    uint8_t counter = 20;
    uint8_t u8Data[MAG_DATA_LEN];
    int16_t s16Buf[3] = {0}; 
    uint8_t i;
    int32_t s32OutBuf[3] = {0};
    static ICM20948_ST_AVG_DATA sstAvgBuf[3];
    while( counter>0 )
    {
        //bcm2835_delay(10);
        icm20948ReadSecondary( I2C_ADD_ICM20948_AK09916|I2C_ADD_ICM20948_AK09916_READ, 
                                    REG_ADD_MAG_ST2, 1, u8Data);
        
        if ((u8Data[0] & 0x01) != 0)
            break;
        
        counter--;
    }
    
    if(counter != 0)
    {
        icm20948ReadSecondary( I2C_ADD_ICM20948_AK09916|I2C_ADD_ICM20948_AK09916_READ, 
                                    REG_ADD_MAG_DATA, 
                                    MAG_DATA_LEN,
                                    u8Data);
        s16Buf[0] = ((int16_t)u8Data[1]<<8) | u8Data[0];
        s16Buf[1] = ((int16_t)u8Data[3]<<8) | u8Data[2];
        s16Buf[2] = ((int16_t)u8Data[5]<<8) | u8Data[4];       
    }

    for(i = 0; i < 3; i ++) 
    {
        icm20948CalAvgValue(&sstAvgBuf[i].u8Index, sstAvgBuf[i].s16AvgBuffer, s16Buf[i], s32OutBuf + i);
    }
    
    *ps16X =  s32OutBuf[0];
    *ps16Y = -s32OutBuf[1];
    *ps16Z = -s32OutBuf[2];
    return;
}

void icm20948ReadSecondary(uint8_t u8I2CAddr, uint8_t u8RegAddr, uint8_t u8Len, uint8_t *pu8data)
{
    uint8_t i;
    uint8_t u8Temp;

    I2C_WriteOneByte( REG_ADD_REG_BANK_SEL,  REG_VAL_REG_BANK_3); //swtich bank3
    I2C_WriteOneByte( REG_ADD_I2C_SLV0_ADDR, u8I2CAddr);
    I2C_WriteOneByte( REG_ADD_I2C_SLV0_REG,  u8RegAddr);
    I2C_WriteOneByte( REG_ADD_I2C_SLV0_CTRL, REG_VAL_BIT_SLV0_EN|u8Len);

    I2C_WriteOneByte( REG_ADD_REG_BANK_SEL, REG_VAL_REG_BANK_0); //swtich bank0
    
    u8Temp = I2C_ReadOneByte(REG_ADD_USER_CTRL);
    u8Temp |= REG_VAL_BIT_I2C_MST_EN;
    I2C_WriteOneByte( REG_ADD_USER_CTRL, u8Temp);
    //bcm2835_delay(5);
    u8Temp &= ~REG_VAL_BIT_I2C_MST_EN;
    I2C_WriteOneByte( REG_ADD_USER_CTRL, u8Temp);
    
    for(i=0; i<u8Len; i++)
    {
        *(pu8data+i) = I2C_ReadOneByte( REG_ADD_EXT_SENS_DATA_00+i);
        
    }
    I2C_WriteOneByte( REG_ADD_REG_BANK_SEL, REG_VAL_REG_BANK_3); //swtich bank3
    
    u8Temp = I2C_ReadOneByte(REG_ADD_I2C_SLV0_CTRL);
    u8Temp &= ~((REG_VAL_BIT_I2C_MST_EN)&(REG_VAL_BIT_MASK_LEN));
    I2C_WriteOneByte( REG_ADD_I2C_SLV0_CTRL,  u8Temp);
    
    I2C_WriteOneByte( REG_ADD_REG_BANK_SEL, REG_VAL_REG_BANK_0); //swtich bank0

}

void icm20948WriteSecondary(uint8_t u8I2CAddr, uint8_t u8RegAddr, uint8_t u8data)
{
  uint8_t u8Temp;
  I2C_WriteOneByte( REG_ADD_REG_BANK_SEL,  REG_VAL_REG_BANK_3); //swtich bank3
  I2C_WriteOneByte( REG_ADD_I2C_SLV1_ADDR, u8I2CAddr);
  I2C_WriteOneByte( REG_ADD_I2C_SLV1_REG,  u8RegAddr);
  I2C_WriteOneByte( REG_ADD_I2C_SLV1_DO,   u8data);
  I2C_WriteOneByte( REG_ADD_I2C_SLV1_CTRL, REG_VAL_BIT_SLV0_EN|1);

  I2C_WriteOneByte( REG_ADD_REG_BANK_SEL, REG_VAL_REG_BANK_0); //swtich bank0

  u8Temp = I2C_ReadOneByte(REG_ADD_USER_CTRL);
  u8Temp |= REG_VAL_BIT_I2C_MST_EN;
  I2C_WriteOneByte( REG_ADD_USER_CTRL, u8Temp);
  //bcm2835_delay(5);
  u8Temp &= ~REG_VAL_BIT_I2C_MST_EN;
  I2C_WriteOneByte( REG_ADD_USER_CTRL, u8Temp);

  I2C_WriteOneByte( REG_ADD_REG_BANK_SEL, REG_VAL_REG_BANK_3); //swtich bank3

  u8Temp = I2C_ReadOneByte(REG_ADD_I2C_SLV0_CTRL);
  u8Temp &= ~((REG_VAL_BIT_I2C_MST_EN)&(REG_VAL_BIT_MASK_LEN));
  I2C_WriteOneByte( REG_ADD_I2C_SLV0_CTRL,  u8Temp);

  I2C_WriteOneByte( REG_ADD_REG_BANK_SEL, REG_VAL_REG_BANK_0); //swtich bank0
    
    return;
}

void icm20948CalAvgValue(uint8_t *pIndex, int16_t *pAvgBuffer, int16_t InVal, int32_t *pOutVal)
{ 
  uint8_t i;
  
  *(pAvgBuffer + ((*pIndex) ++)) = InVal;
    *pIndex &= 0x07;
    
    *pOutVal = 0;
  for(i = 0; i < 8; i ++) 
    {
      *pOutVal += *(pAvgBuffer + i);
    }
    *pOutVal >>= 3;
}

void icm20948GyroOffset(void)
{
  uint8_t i;
  int16_t s16Gx = 0, s16Gy = 0, s16Gz = 0;
  int32_t s32TempGx = 0, s32TempGy = 0, s32TempGz = 0;
  for(i = 0; i < 32; i ++)
  {
    icm20948GyroRead(&s16Gx, &s16Gy, &s16Gz);
    s32TempGx += s16Gx;
    s32TempGy += s16Gy;
    s32TempGz += s16Gz;
    //bcm2835_delay(10);
  }
  gstGyroOffset.s16X = s32TempGx >> 5;
  gstGyroOffset.s16Y = s32TempGy >> 5;
  gstGyroOffset.s16Z = s32TempGz >> 5;
  return;
}

bool icm20948MagCheck(void)
{
    bool bRet = false;
    uint8_t u8Ret[2];
    
    icm20948ReadSecondary( I2C_ADD_ICM20948_AK09916|I2C_ADD_ICM20948_AK09916_READ,
                                REG_ADD_MAG_WIA1, 2,u8Ret);
    if( (u8Ret[0] == REG_VAL_MAG_WIA1) && ( u8Ret[1] == REG_VAL_MAG_WIA2) )
    {
        bRet = true;
    }
    
    return bRet;
}

float * getValues(int numberOfValues)
{
  //output array
  float * output = (float *)malloc(sizeof(float) * numberOfValues*9);
  //Arrays for data aquisition
  float * roll = (float *)malloc(sizeof(float) * numberOfValues);
  float * pitch = (float *)malloc(sizeof(float) * numberOfValues);
  float * yaw = (float *)malloc(sizeof(float) * numberOfValues);
  float * Ax = (float *)malloc(sizeof(float) * numberOfValues);
  float * Ay = (float *)malloc(sizeof(float) * numberOfValues);
  float * Az = (float *)malloc(sizeof(float) * numberOfValues);
  float * Gx = (float *)malloc(sizeof(float) * numberOfValues);
  float * Gy = (float *)malloc(sizeof(float) * numberOfValues);
  float * Gz = (float *)malloc(sizeof(float) * numberOfValues);



  //sensor stuff
	IMU_EN_SENSOR_TYPE enMotionSensorType;
	IMU_ST_ANGLES_DATA stAngles;
	IMU_ST_SENSOR_DATA stGyroRawData;
	IMU_ST_SENSOR_DATA stAccelRawData;
	IMU_ST_SENSOR_DATA stMagnRawData;
	imuInit(&enMotionSensorType);
	if(IMU_EN_SENSOR_TYPE_ICM20948 == enMotionSensorType)
	{
		//printf("Motion sersor is ICM-20948\n" );
	}
	else
	{
		printf("Motion sersor NULL\n");
	}
	 for (int i = 0; i < numberOfValues; i++)
	{
		imuDataGet( &stAngles, &stGyroRawData, &stAccelRawData, &stMagnRawData);
    roll[i]=stAngles.fRoll;
    pitch[i]=stAngles.fPitch;
    yaw[i]=stAngles.fYaw;
    Ax[i]=stAccelRawData.s16X;
    Ay[i]=stAccelRawData.s16Y;
    Az[i]=stAccelRawData.s16Z;
    Gx[i]=stGyroRawData.s16X;
    Gy[i]=stGyroRawData.s16Y;
    Gz[i]=stGyroRawData.s16Z;
		//printf("\r\n /-------------------------------------------------------------/ \r\n");
		//printf("\r\n Roll: %.2f     Pitch: %.2f     Yaw: %.2f \r\n",stAngles.fRoll, stAngles.fPitch, stAngles.fYaw);
		//printf("\r\n Acceleration: X: %d     Y: %d     Z: %d \r\n",stAccelRawData.s16X, stAccelRawData.s16Y, stAccelRawData.s16Z);
		//printf("\r\n Gyroscope: X: %d     Y: %d     Z: %d \r\n",stGyroRawData.s16X, stGyroRawData.s16Y, stGyroRawData.s16Z);
		//printf("\r\n Magnetic: X: %d     Y: %d     Z: %d \r\n",stMagnRawData.s16X, stMagnRawData.s16Y, stMagnRawData.s16Z);
		//bcm2835_delay(10);
	}
  memcpy(output,roll, numberOfValues * sizeof(float)); 
  memcpy(output + 1*numberOfValues,pitch, numberOfValues * sizeof(float)); 
  memcpy(output + 2*numberOfValues,yaw, numberOfValues * sizeof(float)); 
  memcpy(output + 3*numberOfValues,Ax, numberOfValues * sizeof(float)); 
  memcpy(output + 4*numberOfValues,Ay, numberOfValues * sizeof(float)); 
  memcpy(output + 5*numberOfValues,Az, numberOfValues * sizeof(float)); 
  memcpy(output + 6*numberOfValues,Gx, numberOfValues * sizeof(float)); 
  memcpy(output + 7*numberOfValues,Gy, numberOfValues * sizeof(float)); 
  memcpy(output + 8*numberOfValues,Gz, numberOfValues * sizeof(float)); 
	return output;
}

#ifdef __cplusplus
}
#endif
