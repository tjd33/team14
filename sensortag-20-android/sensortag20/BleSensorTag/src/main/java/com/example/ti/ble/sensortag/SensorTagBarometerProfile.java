/**************************************************************************************************
 Filename:       SensorTagBarometerProfile.java

 Copyright (c) 2013 - 2015 Texas Instruments Incorporated

 All rights reserved not granted herein.
 Limited License.

 Texas Instruments Incorporated grants a world-wide, royalty-free,
 non-exclusive license under copyrights and patents it now or hereafter
 owns or controls to make, have made, use, import, offer to sell and sell ("Utilize")
 this software subject to the terms herein.  With respect to the foregoing patent
 license, such license is granted  solely to the extent that any such patent is necessary
 to Utilize the software alone.  The patent license shall not apply to any combinations which
 include this software, other than combinations with devices manufactured by or for TI ('TI Devices').
 No hardware patent is licensed hereunder.

 Redistributions must preserve existing copyright notices and reproduce this license (including the
 above copyright notice and the disclaimer and (if applicable) source code license limitations below)
 in the documentation and/or other materials provided with the distribution

 Redistribution and use in binary form, without modification, are permitted provided that the following
 conditions are met:

 * No reverse engineering, decompilation, or disassembly of this software is permitted with respect to any
 software provided in binary form.
 * any redistribution and use are licensed by TI for use only with TI Devices.
 * Nothing shall obligate TI to provide you with source code for the software licensed and provided to you in object code.

 If software source code is provided to you, modification and redistribution of the source code are permitted
 provided that the following conditions are met:

 * any redistribution and use of the source code, including any resulting derivative works, are licensed by
 TI for use only with TI Devices.
 * any redistribution and use of any object code compiled from the source code and any resulting derivative
 works, are licensed by TI for use only with TI Devices.

 Neither the name of Texas Instruments Incorporated nor the names of its suppliers may be used to endorse or
 promote products derived from this software without specific prior written permission.

 DISCLAIMER.

 THIS SOFTWARE IS PROVIDED BY TI AND TI'S LICENSORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
 BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 IN NO EVENT SHALL TI AND TI'S LICENSORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
 OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.


 **************************************************************************************************/
package com.example.ti.ble.sensortag;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattService;
import android.content.Context;
import android.util.Log;

import com.example.ti.ble.common.BluetoothLeService;
import com.example.ti.ble.common.GattInfo;
import com.example.ti.ble.common.GenericBluetoothProfile;
import com.example.ti.util.Point3D;

public class SensorTagBarometerProfile extends GenericBluetoothProfile {
	private BluetoothGattCharacteristic calibC;
	private boolean isCalibrated;
	private boolean isHeightCalibrated;
	private static final double PA_PER_METER = 12.0;
	public SensorTagBarometerProfile(Context con,BluetoothDevice device,BluetoothGattService service,BluetoothLeService controller) {
		super(con,device,service,controller);
		this.tRow =  new SensorTagBarometerTableRow(con);
		
		List<BluetoothGattCharacteristic> characteristics = this.mBTService.getCharacteristics();
		
		for (BluetoothGattCharacteristic c : characteristics) {
			if (c.getUuid().toString().equals(SensorTagGatt.UUID_BAR_DATA.toString())) {
				this.dataC = c;
			}
			if (c.getUuid().toString().equals(SensorTagGatt.UUID_BAR_CONF.toString())) {
				this.configC = c;
			}
			if (c.getUuid().toString().equals(SensorTagGatt.UUID_BAR_PERI.toString())) {
				this.periodC = c;
			}
			if (c.getUuid().toString().equals(SensorTagGatt.UUID_BAR_CALI.toString())) {
				this.calibC = c;
			}
		}
		if (this.mBTDevice.getName().equals("CC2650 SensorTag")) {
			this.isCalibrated = true;
		}
		else {
			this.isCalibrated = false;
		}
		this.isHeightCalibrated = false;
		this.tRow.sl1.autoScale = true;
		this.tRow.sl1.autoScaleBounceBack = true;
		this.tRow.sl1.setColor(255, 0, 150, 125);
		this.tRow.setIcon(this.getIconPrefix(), this.dataC.getUuid().toString());
		
		this.tRow.title.setText(GattInfo.uuidToName(UUID.fromString(this.dataC.getUuid().toString())));
		this.tRow.uuidLabel.setText(this.dataC.getUuid().toString());
		this.tRow.value.setText("0.0mBar, 0.0m");
		this.tRow.periodBar.setProgress(100);
	}
	
	public static boolean isCorrectService(BluetoothGattService service) {
		if ((service.getUuid().toString().compareTo(SensorTagGatt.UUID_BAR_SERV.toString())) == 0) {
			return true;
		}
		else return false;
	}
	public void enableService() {
		while (!(mBTLeService.checkGatt())) {
			mBTLeService.waitIdle(GATT_TIMEOUT);
		}
		if (!(this.isCalibrated)) {
			// Write the calibration code to the configuration registers
			mBTLeService.writeCharacteristic(this.configC, Sensor.CALIBRATE_SENSOR_CODE);
			mBTLeService.waitIdle(GATT_TIMEOUT);
			mBTLeService.readCharacteristic(this.calibC);
			mBTLeService.waitIdle(GATT_TIMEOUT);
		}
		else {
            int error = mBTLeService.writeCharacteristic(this.configC, (byte)0x01);
            if (error != 0) {
                if (this.configC != null)
                Log.d("SensorTagBarometerProfile","Sensor config failed: " + this.configC.getUuid().toString() + " Error: " + error);
            }
            error = this.mBTLeService.setCharacteristicNotification(this.dataC, true);
            if (error != 0) {
                if (this.dataC != null)
                Log.d("SensorTagBarometerProfile","Sensor notification enable failed: " + this.configC.getUuid().toString() + " Error: " + error);
            }
		}
        this.isEnabled = true;

	}
	@Override
	public void didReadValueForCharacteristic(BluetoothGattCharacteristic c) {
        if (this.calibC != null) {
            if (this.calibC.equals(c)) {
                //We have been calibrated
                // Sanity check
                byte[] value = c.getValue();
                if (value.length != 16) {
                    return;
                }

                // Barometer calibration values are read.
                List<Integer> cal = new ArrayList<Integer>();
                for (int offset = 0; offset < 8; offset += 2) {
                    Integer lowerByte = (int) value[offset] & 0xFF;
                    Integer upperByte = (int) value[offset + 1] & 0xFF;
                    cal.add((upperByte << 8) + lowerByte);
                }

                for (int offset = 8; offset < 16; offset += 2) {
                    Integer lowerByte = (int) value[offset] & 0xFF;
                    Integer upperByte = (int) value[offset + 1];
                    cal.add((upperByte << 8) + lowerByte);
                }
                Log.d("SensorTagBarometerProfile", "Barometer calibrated !!!!!");
                BarometerCalibrationCoefficients.INSTANCE.barometerCalibrationCoefficients = cal;
                this.isCalibrated = true;
                int error = mBTLeService.writeCharacteristic(this.configC, (byte)0x01);
                if (error != 0) {
                    if (this.configC != null)
                    Log.d("SensorTagBarometerProfile","Sensor config failed: " + this.configC.getUuid().toString() + " Error: " + error);
                }
                error = this.mBTLeService.setCharacteristicNotification(this.dataC, true);
                if (error != 0) {
                    if (this.dataC != null)
                    Log.d("SensorTagBarometerProfile","Sensor notification enable failed: " + this.configC.getUuid().toString() + " Error: " + error);
                }
            }
        }
	}
	@Override 
	public void didUpdateValueForCharacteristic(BluetoothGattCharacteristic c) {
        byte[] value = c.getValue();
		if (c.equals(this.dataC)){
			Point3D v;
			v = Sensor.BAROMETER.convert(value);
			if (!(this.isHeightCalibrated)) {
				BarometerCalibrationCoefficients.INSTANCE.heightCalibration = v.x;
				//Toast.makeText(this.tRow.getContext(), "Height measurement calibrated",
				//			    Toast.LENGTH_SHORT).show();
				this.isHeightCalibrated = true;
			}
			double h = (v.x - BarometerCalibrationCoefficients.INSTANCE.heightCalibration)
			    / PA_PER_METER;
			h = (double) Math.round(-h * 10.0) / 10.0;
			//msg = decimal.format(v.x / 100.0f) + "\n" + h;
			if (this.tRow.config == false) this.tRow.value.setText(String.format("%.1f mBar %.1f meter", v.x / 100, h));
			this.tRow.sl1.addValue((float)v.x / 100.0f);
			//mBarValue.setText(msg);
		}
	}
	
	protected void calibrationButtonTouched() {
		this.isHeightCalibrated = false;
	}
    @Override
    public Map<String,String> getMQTTMap() {
        Point3D v = Sensor.BAROMETER.convert(this.dataC.getValue());
        Map<String,String> map = new HashMap<String, String>();
        map.put("air_pressure",String.format("%.2f",v.x / 100));
        return map;
    }
}
