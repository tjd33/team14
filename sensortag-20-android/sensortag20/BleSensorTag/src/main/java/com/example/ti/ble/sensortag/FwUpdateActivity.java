/**************************************************************************************************
  Filename:       FwUpdateActivity.java

  Copyright (c) 2013 - 2014 Texas Instruments Incorporated

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

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

import android.app.Activity;
import android.app.AlertDialog;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattService;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.os.Environment;
import android.text.Html;
import android.text.method.ScrollingMovementMethod;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.example.ti.ble.common.BluetoothLeService;
import com.example.ti.ble.sensortag.R;
import com.example.ti.util.Conversion;

public class FwUpdateActivity extends Activity {
  public final static String EXTRA_MESSAGE = "com.example.ti.ble.sensortag.MESSAGE";
  // Log
  private static String TAG = "FwUpdateActivity";

  // Activity
  public static final int FILE_ACTIVITY_REQ = 0;

  // Programming parameters
  private static final short OAD_CONN_INTERVAL = 12; // 15 milliseconds
  private static final short OAD_SUPERVISION_TIMEOUT = 50; // 500 milliseconds
  private static final int GATT_WRITE_TIMEOUT = 300; // Milliseconds

  private static final int FILE_BUFFER_SIZE = 0x40000;
  public static final String FW_CUSTOM_DIRECTORY = Environment.DIRECTORY_DOWNLOADS;
  private static final String FW_FILE_A = "SensorTagImgA.bin";
  private static final String FW_FILE_B = "SensorTagImgB.bin";

  private static final int OAD_BLOCK_SIZE = 16;
  private static final int HAL_FLASH_WORD_SIZE = 4;
  private static final int OAD_BUFFER_SIZE = 2 + OAD_BLOCK_SIZE;
  private static final int OAD_IMG_HDR_SIZE = 8;
  private static final long TIMER_INTERVAL = 1000;
  private static final int SEND_INTERVAL = 20; // Milliseconds (make sure this is longer than the connection interval)
  private static final int BLOCKS_PER_CONNECTION = 1; // May sent up to four blocks per connection

  // GUI
  private TextView mTargImage;
  private TextView mFileImage;
  private TextView mProgressInfo;
  private TextView mLog;
  private ProgressBar mProgressBar;
  private Button mBtnLoadA;
  private Button mBtnLoadB;
  private Button mBtnLoadC;
  private Button mBtnStart;

  // BLE
  private BluetoothGattService mOadService;
  private BluetoothGattService mConnControlService;
  private List<BluetoothGattCharacteristic> mCharListOad;
  private List<BluetoothGattCharacteristic> mCharListCc;
  private BluetoothGattCharacteristic mCharIdentify = null;
  private BluetoothGattCharacteristic mCharBlock = null;
  private BluetoothGattCharacteristic mCharConnReq = null;
  private DeviceActivity mDeviceActivity = null;
  private BluetoothLeService mLeService;

  // Programming
  private final byte[] mFileBuffer = new byte[FILE_BUFFER_SIZE];
  private final byte[] mOadBuffer = new byte[OAD_BUFFER_SIZE];
  private ImgHdr mFileImgHdr = new ImgHdr();
  private ImgHdr mTargImgHdr = new ImgHdr();
  private Timer mTimer = null;
  private ProgInfo mProgInfo = new ProgInfo();
  private TimerTask mTimerTask = null;

  // Housekeeping
  private boolean mServiceOk = false;
  private boolean mProgramming = false;
  private IntentFilter mIntentFilter;

  FwUpdateActivity mThis;


  public FwUpdateActivity() {
    mDeviceActivity = DeviceActivity.getInstance();

    // BLE Gatt Service
    mLeService = BluetoothLeService.getInstance();

    // Service information
    mOadService = mDeviceActivity.getOadService();
    mConnControlService = mDeviceActivity.getConnControlService();

    // Characteristics list
    mCharListOad = mOadService.getCharacteristics();
    mCharListCc = mConnControlService.getCharacteristics();

    mServiceOk = mCharListOad.size() == 2 && mCharListCc.size() >= 3;
    if (mServiceOk) {
      mCharIdentify = mCharListOad.get(0);
      mCharBlock = mCharListOad.get(1);
      mCharBlock.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE);
      mLeService.setCharacteristicNotification(mCharBlock,true);
      mCharConnReq = mCharListCc.get(1);
    }
    mThis = this;
  }

  @Override
  public void onCreate(Bundle savedInstanceState) {
    Log.d(TAG, "onCreate");

    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_fwupdate);

    // Icon padding
    ImageView view = (ImageView) findViewById(android.R.id.home);
    view.setPadding(10, 0, 20, 10);

    // Context title
    setTitle(R.string.title_oad);

    // Initialize widgets
    mProgressInfo = (TextView) findViewById(R.id.tw_info);
    mTargImage = (TextView) findViewById(R.id.tw_target);
    mFileImage = (TextView) findViewById(R.id.tw_file);
    mLog = (TextView) findViewById(R.id.tw_log);
    mLog.setMovementMethod(new ScrollingMovementMethod());
    mProgressBar = (ProgressBar) findViewById(R.id.pb_progress);
    mBtnStart = (Button) findViewById(R.id.btn_start);
    mBtnStart.setEnabled(false);
    mBtnLoadA = (Button) findViewById(R.id.btn_load_a);
    mBtnLoadB = (Button) findViewById(R.id.btn_load_b);
    mBtnLoadC = (Button) findViewById(R.id.btn_load_c);

    // Sanity check
    mBtnLoadA.setEnabled(mServiceOk);
    mBtnLoadB.setEnabled(mServiceOk);
    mBtnLoadC.setEnabled(mServiceOk);
  	initIntentFilter();
      getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
  }

  @Override
  public void onDestroy() {
    Log.d(TAG, "onDestroy");
    super.onDestroy();
    if (mTimerTask != null)
      mTimerTask.cancel();
    mTimer = null;
      getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
  }

  @Override
  public void onBackPressed() {
    Log.d(TAG, "onBackPressed");
    if (mProgramming) {
      Toast.makeText(this, R.string.prog_ogoing, Toast.LENGTH_LONG).show();
    } else
      super.onBackPressed();
  }
  
  @Override
  public boolean onOptionsItemSelected(MenuItem item) {
    Log.d(TAG, "onOptionsItemSelected");
    // Handle presses on the action bar items
    switch (item.getItemId()) {
    // Respond to the action bar's Up/Home button
    case android.R.id.home:
      onBackPressed();
      return true;
    default:
      return super.onOptionsItemSelected(item);
    }
  }
  
  @Override 
  protected void onResume()
  {
    super.onResume();
    if (mServiceOk) {
    	registerReceiver(mGattUpdateReceiver, mIntentFilter);
    	
      // Read target image info
      getTargetImageInfo();
      
  		// Connection interval is too low by default
	  	setConnectionParameters();
    } else {
      Toast.makeText(this, "OAD service initialisation failed", Toast.LENGTH_LONG).show();
    }
    mLeService.abortTimedDisconnect();
  }

  @Override
  protected void onPause() {
  	super.onPause();
  	unregisterReceiver(mGattUpdateReceiver);
  }

  private final BroadcastReceiver mGattUpdateReceiver = new BroadcastReceiver() {
    @Override
    public void onReceive(Context context, Intent intent) {

      final String action = intent.getAction();

      if (BluetoothLeService.ACTION_DATA_NOTIFY.equals(action)) {
        byte [] value = intent.getByteArrayExtra(BluetoothLeService.EXTRA_DATA);
        String uuidStr = intent.getStringExtra(BluetoothLeService.EXTRA_UUID);

        if (uuidStr.equals(mCharIdentify.getUuid().toString())) {
          // Image info notification
          mTargImgHdr.ver = Conversion.buildUint16(value[1], value[0]);
          mTargImgHdr.imgType = ((mTargImgHdr.ver & 1) == 1) ? 'B' : 'A';
          mTargImgHdr.len = Conversion.buildUint16(value[3], value[2]);
          displayImageInfo(mTargImage, mTargImgHdr);
        }
        if (uuidStr.equals(mCharBlock.getUuid().toString())) {
          if (mProgramming == true) programBlock(((value[1] << 8) & 0xff00) + (value[0] & 0x00ff));
          Log.d("FwUpdateActivity",String.format("NB: %02x%02x",value[1],value[0]));
        }
      }
      else if (BluetoothLeService.ACTION_DATA_WRITE.equals(action)) {
        int status = intent.getIntExtra(BluetoothLeService.EXTRA_STATUS,BluetoothGatt.GATT_SUCCESS);
        if (status != BluetoothGatt.GATT_SUCCESS) {
          Toast.makeText(context, "GATT error: status=" + status, Toast.LENGTH_SHORT).show();
        }

      }
    }
  };


  private void initIntentFilter() {
  	mIntentFilter = new IntentFilter();
  	mIntentFilter.addAction(BluetoothLeService.ACTION_DATA_NOTIFY);
  	mIntentFilter.addAction(BluetoothLeService.ACTION_DATA_WRITE);
  }

  public void onStart(View v) {
    if (mProgramming) {
      stopProgramming();
    } else {
      startProgramming();
    }
  }

  public void onLoad(View v) {
    if (v.getId() == R.id.btn_load_a)
      loadFile(FW_FILE_A, true);
    else
      loadFile(FW_FILE_B, true);
    updateGui();
  }

  public void onLoadCustom(View v) {
    Intent i = new Intent(this, FileActivity.class);
    i.putExtra(EXTRA_MESSAGE, FW_CUSTOM_DIRECTORY);
    startActivityForResult(i, FILE_ACTIVITY_REQ);
  }

  private void startProgramming() {
    mLog.append("Programming started\n");
    mProgramming = true;
    updateGui();

    // Prepare image notification
    byte[] buf = new byte[OAD_IMG_HDR_SIZE + 2 + 2];
    buf[0] = Conversion.loUint16(mFileImgHdr.ver);
    buf[1] = Conversion.hiUint16(mFileImgHdr.ver);
    buf[2] = Conversion.loUint16(mFileImgHdr.len);
    buf[3] = Conversion.hiUint16(mFileImgHdr.len);
    System.arraycopy(mFileImgHdr.uid, 0, buf, 4, 4);

    // Send image notification
    mCharIdentify.setValue(buf);
    mLeService.writeCharacteristic(mCharIdentify);

    // Initialize stats
    mProgInfo.reset();

    // Start the programming thread
    new Thread(new OadTask()).start();

    mTimer = new Timer();
    mTimerTask = new ProgTimerTask();
    mTimer.scheduleAtFixedRate(mTimerTask, 0, TIMER_INTERVAL);
  }

  private void stopProgramming() {
    mTimer.cancel();
    mTimer.purge();
    mTimerTask.cancel();
    mTimerTask = null;

    mProgramming = false;
    mProgressInfo.setText("");
    mProgressBar.setProgress(0);
    updateGui();

    if (mProgInfo.iBlocks == mProgInfo.nBlocks) {
      mLog.setText("Programming complete!\n");
    } else {
      mLog.append("Programming cancelled\n");
    }
  }

  private void updateGui() {
  	if (mProgramming) {
  		// Busy: stop label, progress bar, disabled file selector
  		mBtnStart.setText(R.string.cancel);
  		mBtnLoadA.setEnabled(false);
  		mBtnLoadB.setEnabled(false);
  		mBtnLoadC.setEnabled(false);
  	} else {
  		// Idle: program label, enable file selector
  		mProgressBar.setProgress(0);
  		mBtnStart.setText(R.string.start_prog);
  		if (mFileImgHdr.imgType == 'A') {
  			mBtnLoadA.setEnabled(false);
  			mBtnLoadB.setEnabled(true);
  		} else if (mFileImgHdr.imgType == 'B') {
  			mBtnLoadA.setEnabled(true);
  			mBtnLoadB.setEnabled(false);
  		}
  		mBtnLoadC.setEnabled(true);
  	}
  }

  private boolean loadFile(String filepath, boolean isAsset) {
    boolean fSuccess = false;

    // Load binary file
    try {
      // Read the file raw into a buffer
      InputStream stream;
      if (isAsset) {
        stream = getAssets().open(filepath);
      } else {
        File f = new File(filepath);
        stream = new FileInputStream(f);
      }
      stream.read(mFileBuffer, 0, mFileBuffer.length);
      stream.close();
    } catch (IOException e) {
      // Handle exceptions here
      mLog.setText("File open failed: " + filepath + "\n");
      return false;
    }

    // Show image info
    mFileImgHdr.ver = Conversion.buildUint16(mFileBuffer[5], mFileBuffer[4]);
    mFileImgHdr.len = Conversion.buildUint16(mFileBuffer[7], mFileBuffer[6]);
    mFileImgHdr.imgType = ((mFileImgHdr.ver & 1) == 1) ? 'B' : 'A';
    System.arraycopy(mFileBuffer, 8, mFileImgHdr.uid, 0, 4);
    displayImageInfo(mFileImage, mFileImgHdr);

    // Verify image types
    boolean ready = mFileImgHdr.imgType != mTargImgHdr.imgType;
    int resid = ready ? R.style.dataStyle1 : R.style.dataStyle2;
    mFileImage.setTextAppearance(this, resid);

    // Enable programming button only if image types differ
    mBtnStart.setEnabled(ready);

    // Expected duration
    displayStats();

    // Log
    mLog.setText("Image " + mFileImgHdr.imgType + " selected.\n");
    mLog.append(ready ? "Ready to program device!\n" : "Incompatible image, select alternative!\n");

    updateGui();

    return fSuccess;
  }

  private void displayImageInfo(TextView v, ImgHdr h) {
    int imgVer = (h.ver) >> 1;
    int imgSize = h.len * 4;
    String s = String.format("Type: %c Ver.: %d Size: %d", h.imgType, imgVer, imgSize);
    v.setText(Html.fromHtml(s));
  }

  private void displayStats() {
    String txt;
    int byteRate;
    int sec = mProgInfo.iTimeElapsed / 1000;
    if (sec > 0) {
      byteRate = mProgInfo.iBytes / sec;
    } else {
      byteRate = 0;
      return;
    }
    float timeEstimate;

    timeEstimate = ((float)(mFileImgHdr.len *4) / (float)mProgInfo.iBytes) * sec;

    txt = String.format("Time: %d / %d sec", sec, (int)timeEstimate);
    txt += String.format("    Bytes: %d (%d/sec)", mProgInfo.iBytes, byteRate);
    mProgressInfo.setText(txt);
  }

  private void getTargetImageInfo() {
    // Enable notification
    mLeService.setCharacteristicNotification(mCharIdentify, true);
    // Prepare data for request (try image A and B respectively, only one of
    // them will give a notification with the image info)
    int count = 0;
    int ok = 1;
    while (ok !=0 && count < 5) {
      count ++;
        ok = mLeService.writeCharacteristic(mCharIdentify, (byte) 0);
      if (ok == 0)
        ok = mLeService.writeCharacteristic(mCharIdentify, (byte) 1);
    }
  }


  private void setConnectionParameters() {
    // Make sure connection interval is long enough for OAD (Android default connection interval is 7.5 ms)
    byte[] value = { Conversion.loUint16(OAD_CONN_INTERVAL), Conversion.hiUint16(OAD_CONN_INTERVAL), Conversion.loUint16(OAD_CONN_INTERVAL),
        Conversion.hiUint16(OAD_CONN_INTERVAL), 0, 0, Conversion.loUint16(OAD_SUPERVISION_TIMEOUT), Conversion.hiUint16(OAD_SUPERVISION_TIMEOUT) };
    mCharConnReq.setValue(value);
    mLeService.writeCharacteristic(mCharConnReq);
  }


  @Override
  protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    // Check which request we're responding to
    if (requestCode == FILE_ACTIVITY_REQ) {
      // Make sure the request was successful
      if (resultCode == RESULT_OK) {
        String filename = data.getStringExtra(FileActivity.EXTRA_FILENAME);
        loadFile(filename, false);
      }
    }
  }

  /*
   * Called when a notification with the current image info has been received
   */

  private void programBlock(int block) {
  	if (!mProgramming)
  		return;
  	
    if (mProgInfo.iBlocks < mProgInfo.nBlocks) {
      mProgramming = true;
      String msg = new String();

      mProgInfo.iBlocks = (short)block;

      // Prepare block
      mOadBuffer[0] = Conversion.loUint16(mProgInfo.iBlocks);
      mOadBuffer[1] = Conversion.hiUint16(mProgInfo.iBlocks);
      System.arraycopy(mFileBuffer, mProgInfo.iBytes, mOadBuffer, 2, OAD_BLOCK_SIZE);

      // Send block
      mCharBlock.setValue(mOadBuffer);
      Log.d("FwUpdateActivity",String.format("TX Block %02x%02x",mOadBuffer[1],mOadBuffer[0]));
      boolean success = mLeService.writeCharacteristicNonBlock(mCharBlock);

      if (success) {
        // Update stats
        mProgInfo.iBlocks++;
        mProgInfo.iBytes += OAD_BLOCK_SIZE;
        mProgressBar.setProgress((mProgInfo.iBlocks * 100) / mProgInfo.nBlocks);
          if (mProgInfo.iBlocks == mProgInfo.nBlocks) {

            runOnUiThread(new Runnable() {
              public void run() {
                AlertDialog.Builder b = new AlertDialog.Builder(mThis);

                b.setMessage(R.string.oad_dialog_programming_finished);
                b.setTitle("Programming finished");
                b.setPositiveButton("OK", null);

                AlertDialog d = b.create();
                d.show();
              }
            });
          }
      } else {
         mProgramming = false;
      	 msg = "GATT writeCharacteristic failed\n";
      }
      if (!success) {
      	mLog.append(msg);
      }
    } else {
      mProgramming = false;
    }

    if (!mProgramming) {
      runOnUiThread(new Runnable() {
        public void run() {
          displayStats();
          stopProgramming();
        }
      });
    }
  }
  
	private class OadTask implements Runnable {
		@Override
		public void run() {
			while (mProgramming) {
				try {
	        Thread.sleep(SEND_INTERVAL);
        } catch (InterruptedException e) {
	        e.printStackTrace();
        }
				for (int i=0; i<BLOCKS_PER_CONNECTION & mProgramming; i++) {
					//programBlock();
				}
				if ((mProgInfo.iBlocks % 100) == 0) {
					// Display statistics each 100th block
					runOnUiThread(new Runnable() {
						public void run() {
							displayStats();
						}
					});
				}
			}
		}
	}

	private class ProgTimerTask extends TimerTask {
    @Override
    public void run() {
      mProgInfo.iTimeElapsed += TIMER_INTERVAL;
    }
  }

  private class ImgHdr {
    short ver;
    short len;
    Character imgType;
    byte[] uid = new byte[4];
  }

  private class ProgInfo {
    int iBytes = 0; // Number of bytes programmed
    short iBlocks = 0; // Number of blocks programmed
    short nBlocks = 0; // Total number of blocks
    int iTimeElapsed = 0; // Time elapsed in milliseconds

    void reset() {
      iBytes = 0;
      iBlocks = 0;
      iTimeElapsed = 0;
      nBlocks = (short) (mFileImgHdr.len / (OAD_BLOCK_SIZE / HAL_FLASH_WORD_SIZE));
    }
  }

}
