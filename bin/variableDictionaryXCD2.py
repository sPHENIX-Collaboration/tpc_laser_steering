#! /usr/bin/python3

import sys

varPhiMotorCommands = {
# Variables listed below are definitions in phi_test_final.xms
'GOTO': 2,
'HOME': 1
}

varThetaLCommands = {
# Variables listed below are definitions in thetaL_test_final.xms
'GOTO': 4,
'HOME': 3
}

varThetaSCommands = {
# Variables listed below are definitions in thetaS_test_final.xms
'GOTO': 8,
'HOME': 7
}

varDoglegCommands = {
# Variables listed below are definitions in dogleg_v3_test_final.xms
'GOTO': 6,
'HOME': 5
}

varInterfaceAddresses= {
'COMMAND':'V0',
'ID':'V1',
'ARG':'V10',
'TURNS':'V11',
'STATUS':'V19',
'FPOS':'FPOS'
}

varStatusValues={
'READY':0,
'FAIL_OUT_OF_BOUNDS':1,
'FAIL_PHI_HOME':2,
'FAIL_PHI_GOTO':3,
'NEWCOMMAND':8,
'BUSY':9
}

varUniqueID={
'L0_DL0_A0': 1,
'L0_DL0_A1': 2,
'L0_DL1_A0': 3,
'L0_DL1_A1': 4,
'L0_TH_S': 5,
'L0_TH_L': 6,
'L0_PH': 7,
'L0_AT': 8,

'L1_DL0_A0': 11,
'L1_DL0_A1': 12,
'L1_DL1_A0': 13,
'L1_DL1_A1': 14,
'L1_TH_S': 15,
'L1_TH_L': 16,
'L1_PH': 17,
'L1_AT': 18,

'L2_DL0_A0': 21,
'L2_DL0_A1': 22,
'L2_DL1_A0': 23,
'L2_DL1_A1': 24,
'L2_TH_S': 25,
'L2_TH_L': 26,
'L2_PH': 27,
'L2_AT': 28,

'L3_DL0_A0': 31,
'L3_DL0_A1': 32,
'L3_DL1_A0': 33,
'L3_DL1_A1': 34,
'L3_TH_S': 35,
'L3_TH_L': 36,
'L3_PH': 37,
'L3_AT': 38,

'L4_DL0_A0': 41,
'L4_DL0_A1': 42,
'L4_DL1_A0': 43,
'L4_DL1_A1': 44,
'L4_TH_S': 45,
'L4_TH_L': 46,
'L4_PH': 47,
'L4_AT': 48,

'L5_DL0_A0': 51,
'L5_DL0_A1': 52,
'L5_DL1_A0': 53,
'L5_DL1_A1': 54,
'L5_TH_S': 55,
'L5_TH_L': 56,
'L5_PH': 57,
'L5_AT': 58,

'L6_DL0_A0': 61,
'L6_DL0_A1': 62,
'L6_DL1_A0': 63,
'L6_DL1_A1': 64,
'L6_TH_S': 65,
'L6_TH_L': 66,
'L6_PH': 67,
'L6_AT': 68,

'L7_DL0_A0': 71,
'L7_DL0_A1': 72,
'L7_DL1_A0': 73,
'L7_DL1_A1': 74,
'L7_TH_S': 75,
'L7_TH_L': 76,
'L7_PH': 77,
'L7_AT': 78
}

varDict = {
# Variables listed below are taken from the XCD2 software manual. For more information, see https://www.nanomotion.com/wp-content/uploads/2018/05/xcd2458000-00_rev-b-fw-manual.pdf

# Tag Meanings:
# NT: No specific Tags
# FL: Variable saved to flash memory at SAVE PARAMETERS command and loaded at power up
# AX: Axis Variable
# RO: Read-only Variable
# ST: SET function is used for variable assignment

#Global Variables
'XAXIS' : 72,   # Axis Selection - Tags: NT
'TIME' : 32,    # Elapsed Time - Tags: RO, ST
'MFREQ' : 23,   # Motor Frequency - Tags: FL, AX, RO
'SPRD' : 24,    # Servo Tick length [msec] - Tags: RO, ST
'V0' : 1000,    # User Variable 1 - Tags: NT
'V1' : 1001,    # User Variable 2 - Tags: NT
'V2' : 1002,    # User Variable 3 - Tags: NT
'V3' : 1003,    # User Variable 4 - Tags: NT
'V4' : 1004,    # User Variable 5 - Tags: NT
'V5' : 1005,    # User Variable 6 - Tags: NT
'V6' : 1006,    # User Variable 7 - Tags: NT
'V7' : 1007,    # User Variable 8 - Tags: NT
'V8' : 1008,    # User Variable 9 - Tags: NT
'V9' : 1009,    # User Variable 10 - Tags: NT
'V10' : 1010,   # User Variable 11 - Tags: NT
'V11' : 1011,   # User Variable 12 - Tags: NT
'V12' : 1012,   # User Variable 13 - Tags: NT
'V13' : 1013,   # User Variable 14 - Tags: NT
'V14' : 1014,   # User Variable 15 - Tags: NT
'V15' : 1015,   # User Variable 16 - Tags: NT
'V16' : 1016,   # User Variable 17 - Tags: NT
'V17' : 1017,   # User Variable 18 - Tags: NT
'V18' : 1018,   # User Variable 19 - Tags: NT
'V19' : 1019,   # User Variable 20 - Tags: NT

# Motion Parameters
'VEL' : 1,     # Velocity - Tags: FL, AX
'ACC' : 2,     # Acceleration - Tags: FL, AX
'DEC' : 3,     # Deceleration - Tags: FL, AX
'KDEC' : 4,    # Kill Deceleration - Tags: FL, AX
'JERK' : 113,  # 3rd order motion profile. JERK = 0, 2nd order motion. Jerk >0, 3rd order motion. - Tags: FL, AX
'TPOS' : 5,    # Target Position - Tags: AX, RO

# Motion Profiler Signals
'RPOS' : 6,    # Reference Position - Tags: AX, RO
'RVEL' : 7,    # Reference Velocity - Tags: AX, RO

# Motion Signals for Sensors
'FPOS' : 9,    # Feedback Position - Tags: AX, RO, ST
'FVEL' : 10,   # Feedback Velocity - Tags: AX, RO
'PE' : 12,     # Position Error (Calculated as RPOS - FPOS) - Tags: AX, RO
'POSI' : 52,   # Position Letched on encoder index pulse - Tags: AX, RO

# Servo Loop and Drive Configuration
'KP' : 13,     # Position Loop Gain - Tags: FL, AX
'KV' : 14,     # Velocity Loop Gain - Tags: FL, AX
'KI' : 15,     # Velocity Loop Integrator Gain - Tags: FL, AX
'LI' : 16,     # Velocity Loop Integrator Limit - Tags: FL, AX
'PKI' : 64,    # Position Loop Integrator Gain - Tags: FL, AX
'PLI' : 65,    # Position Loop Integrator Limit - Tags: FL, AX
'BQA1' : 17, # BiQuad Filters Parameters - Tags: FL, AX
'BQA2' : 18, # BiQuad Filters Parameters - Tags: FL, AX
'BQB0' : 19, # BiQuad Filters Parameters - Tags: FL, AX
'BQB1' : 20, # BiQuad Filters Parameters - Tags: FL, AX
'BQB2' : 21, # BiQuad Filters Parameters - Tags: FL, AX
'BQ2A1' : 67, # BiQuad Filters Parameters - Tags: FL, AX
'BQ2A2' : 68, # BiQuad Filters Parameters - Tags: FL, AX
'BQ2B0' : 69, # BiQuad Filters Parameters - Tags: FL, AX
'BQ2B1' : 70, # BiQuad Filters Parameters - Tags: FL, AX
'BQ2B2' : 71, # BiQuad Filters Parameters - Tags: FL, AX
'ENR' : 22, # Encoder Resolution - Tags: FL, AX
'DZMIN' : 40, # Dead Zone Min - Tags: FL, AX
'DZMAX' : 41, # Dead Zone Max - Tags: FL, AX
'ZFF' : 42, # Zero Feed Forward - Tags: FL, AX
'FRP' : 43, # Friction in Positive Direction - Tags: FL, AX
'FRN' : 44, # Friction in Negative Direction - Tags: FL, AX
'DOUT' : 45, # Realtime Drive Output (% of maximal output) - Tags: AX, RO
'POSOFFS' : 95, # Position Offset - Tags: FL, AX, RO
'BLOUT' : 112, # Blackout Period [msec] - Tags: FL, AX
'DOFFS' : 43, # Drive Output Offset - Tags: FL, AX

# Safety
'DOL' : 39, # Drive Output Limit - Tags: FL, AX
'SLP' : 47, # Positive Software Limit. Disallows moves outside of bounds set here. Disables the motor if =0 and throws an error code. Set away from hard stop after homing procedure id done. - Tags: FL, AX
'SLN' : 48, # Negative Software Limit. Disallows moves outside of bounds set here. Disables the motor if =0 and throws an error code. Set away from hard stop after homing procedure id done. - Tags: FL, AX
'PEL' : 49, # Position Error Limit- Absolute value of allowed position error. If =0, PEL diabled - Tags: FL, AX
'MTL' : 51, # Motion Time Limit - max time [msec] from motion start until target position is reached. The motor is disabled if MTL is exceeded, and throws an error code. If =0, MTL is disabled. - Tags: FL, AX
'MTTMP' : 107, # Motor Temperature [Celsius] - Tags: AX, RO

# Analog Inputs
'AIN0' : 30, # Analog Input 0 - Tags: RO
'AIN1' : 31, # Analog Input 1 - Tags: RO
'AIN2' : 32, # Analog Input 2 - Tags: RO
'AIN3' : 33, # Analog Input 3 - Tags: RO
'AIN4' : 55, # Analog Input 4 - Tags: RO
'AIN5' : 56, # Analog Input 5 - Tags: RO
'AIN6' : 57, # Analog Input 6 - Tags: RO
'AIN7' : 58, # Analog Input 7 - Tags: RO
'AIN8' : 59, # Analog Input 8 - Tags: RO
'AIN9' : 60, # Analog Input 9 - Tags: RO
'AIN10' : 61, # Analog Input 10 - Tags: RO
'AIN11' : 62, # Analog Input 11 - Tags: RO

# Analog Outputs
'AOUT0' : 34, # Analog Output 0 (range: 0,4095) - Tags: RO
'AOUTSC0' : 35, # Analog Output 0 Scaled (% of Max) - Tags: NT
'AOUT1' : 36, # Analog Output 1 (range: 0,4095) - Tags: RO
'AOUTSC1' : 37, # Analog Output 1 Scaled (% of Max) - Tags: NT

# Digital Inputs/Outputs
'IO_0' : 73, # Digital IO 0. Values can be 0 or 1 - Tags: NT
'IO_1' : 74, # Digital IO 1. Values can be 0 or 1 - Tags: NT
'IO_2' : 75, # Digital IO 2. Values can be 0 or 1 - Tags: NT
'IO_3' : 76, # Digital IO 3. Values can be 0 or 1 - Tags: NT
'IO_4' : 77, # Digital IO 4. Values can be 0 or 1 - Tags: NT
'IO_5' : 78, # Digital IO 5. Values can be 0 or 1 - Tags: NT
'IO_6' : 79, # Digital IO 6. Values can be 0 or 1 - Tags: NT
'IO_7' : 80, # Digital IO 7. Values can be 0 or 1 - Tags: NT
'IO_8' : 81, # Digital IO 8. Values can be 0 or 1 - Tags: NT
'IO_9' : 82, # Digital IO 9. Values can be 0 or 1 - Tags: NT
'IO_10' : 83, # Digital IO 10. Values can be 0 or 1 - Tags: NT
'IO_11' : 84, # Digital IO 11. Values can be 0 or 1 - Tags: NT
'IO_12' : 85, # Digital IO 12. Values can be 0 or 1 - Tags: NT
'IO_13' : 86, # Digital IO 13. Values can be 0 or 1 - Tags: NT
'IO_14' : 87, # Digital IO 14. Values can be 0 or 1 - Tags: NT
'IO_15' : 88, # Digital IO 15. Values can be 0 or 1 - Tags: NT

# Flags (Accept 0 or 1 only)
'S_MOVE' : 90, # Motion is in Progress - Tags: AX, RO
'S_BUSY' : 91, # Servo Loop is Busy - Tags: AX, RO
'S_IND' : 92, # Index Position Letched - Tags: AX, RO, ST
'S_HOME' : 93, # Homing Successful - Tags: AX, RO
'S_INPOS' : 94, # In-Position Flag - Tags: AX, RO
'SSTAT' : 114, # Scope User Value - Tags: NT
'MTNPHS' : 115, # Motion Phase Variable - Tags: AX
'SERTICK' : 117, # Servo Tick Synchronization Variable - Tags: ST

# Pseudovariables
'STATUS' : 900, # Status - Tags: FL, AX
'PROGRAM_STATUS' : 901, # Program Status - Tags: NT
'SAFETY_DISABLE' : 902, # Safety Disable - Tags: FL, AX
'SAFETY_INVERSE' : 903, # Safety Inverse - Tags: FL, AX
'SAFETY_STATE' : 904, # Safety State - Tags: FL, AX
'IO_DIRECTION' : 905, # IO Direction - Tags: FL
'XMS_CHECKSUM' : 950, # XMS Checksum - Tags: RO
'XMS_LENGTH' : 951, # Length of XMS program in Controller memory - Tags: RO
'LAST_ERROR' : 960, # Returns real value of last error in the controller - Tags: AX
'AXES_NUMBER' : 981, # Number of supported axes in the system - Tags: RO
'UART0_ADDRESS' : 990, # Acces to Communication channel address - Tags: FL
'UART1_ADDRESS' : 991, # Acces to Communication channel address - Tags: FL
'IIC_ADDRESS' : 992, # Acces to Communication channel address - Tags: FL
'SPI_ADDRESS' : 993, # Acces to Communication channel address - Tags: FL
'POWERSAVE_ENABLE' : 994, # Power Save Enable; 1= enable, 0=disable - Tags: FL


}
