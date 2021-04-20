
/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
 * All rights reserved.</center></h2>
 *
 * This software component is licensed by ST under BSD 3-Clause license,
 * the "License"; You may not use this file except in compliance with the
 * License. You may obtain a copy of the License at:
 *                        opensource.org/licenses/BSD-3-Clause
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "stdio.h"
#include "string.h"
#include "cobs.h"
#include "stdbool.h"

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
typedef struct qCmd {
	uint8_t commnddBuff[20];
	uint8_t commandSize;
} SnniferCommand;

typedef struct qCANMsg {
	uint8_t data[8];
	CAN_RxHeaderTypeDef header;
} CANMessage;

typedef enum {
	SNIFFER_STOPPED = 0x00, SNIFFER_ACTIVE = 0x01,
} SnifferAtivityStatus;

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define osAnySignal 0x00
#define SIZE_RX 20
#define noWait 0
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
CAN_HandleTypeDef hcan1;
UART_HandleTypeDef huart1;

/* USER CODE BEGIN PV */

osThreadId receiveCommandsTaskId;
osThreadId executeCommmandtaskID;
osThreadId forwardDatagramTaskId;
osThreadId receivedDatagramTaskId;

osThreadId idleTaskId;

osMailQDef(pendingCommandsQueue, 100, SnniferCommand); // Define pendingCommandsQueue
osMailQId pendingCommandsQueue;

osMailQDef(canDatagramsQueue, 100, CANMessage);		// Define mail queue
osMailQId canDatagramsQueue;

// Peripherals ISR global variables
uint8_t rxUARTBuff[1] = { 0 };

CAN_RxHeaderTypeDef rxMessageHeader;
uint8_t rxDataReceived[8];



// Sneffer activity status variable
SnifferAtivityStatus snifferAtivityStatus = SNIFFER_STOPPED;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_CAN1_Init(void);
static void MX_USART1_UART_Init(void);
void StartDefaultTask(void const *argument);

/* USER CODE BEGIN PFP */
void bootLEDIndicator(void);

void executeCommandThread(void const*);
void rcvCommandThread(void const*);
void fordwardDatagramsThread(void const*);
void recieivedDatagramsThread(void const*);
void idleThread(void const*);

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
#define NUMBER_BLINKS 20

void bootLEDIndicator(void) {
	int blinkCounter = 0;
	while (blinkCounter < NUMBER_BLINKS) {
		HAL_GPIO_TogglePin(ORANGE_LED_GPIO_Port, ORANGE_LED_Pin);
		HAL_Delay(30);
		blinkCounter++;
	}
	HAL_GPIO_WritePin(ORANGE_LED_GPIO_Port, ORANGE_LED_Pin, GPIO_PIN_SET);
}
void substr(char *str, char *sub, int start, int len) {
	memcpy(sub, &str[start], len);
	sub[len] = '\0';
}

int toInteger(uint8_t *stringToConvert, int len) {
	int counter = len - 1;
	int exp = 1;
	int value = 0;
	while (counter >= 0) {
		value = value + (stringToConvert[counter] - '0') * exp;
		exp = exp * 10;
		counter--;
	}
	return value;
}
uint32_t sendCANMessage(uint8_t dlc, uint32_t msgID, bool isRTR,bool isStandard, uint8_t *data) {

	uint32_t TxMailbox;
	CAN_TxHeaderTypeDef pHeader;
	pHeader.DLC = dlc;

	if (isStandard) {
		pHeader.IDE = CAN_ID_STD;
		pHeader.StdId = msgID;
	} else {
		pHeader.IDE = CAN_ID_EXT;
		pHeader.ExtId = msgID;
	}
	if (isRTR) {
		pHeader.RTR = CAN_RTR_REMOTE;
	} else {
		pHeader.RTR = CAN_RTR_DATA;
	}

	HAL_CAN_AddTxMessage(&hcan1, &pHeader, data, &TxMailbox);
	return TxMailbox;
}

void setSinfferCANFilter(void) {
	/* Default filter - accept all to CAN_FIFO*/
	CAN_FilterTypeDef sFilterConfig;
	sFilterConfig.FilterBank = 0;
	sFilterConfig.FilterIdHigh = 0x00005;
	sFilterConfig.FilterBank = 0x0000;
	sFilterConfig.FilterMode = CAN_FILTERMODE_IDMASK;
	sFilterConfig.FilterScale = CAN_FILTERSCALE_32BIT;
	sFilterConfig.FilterIdHigh = 0x200 << 5;  //11-bit ID, in top bits
	sFilterConfig.FilterIdLow = 0x0000;
	sFilterConfig.FilterMaskIdHigh = 0x0000;
	sFilterConfig.FilterMaskIdLow = 0x0000;
	sFilterConfig.FilterFIFOAssignment = CAN_FILTER_FIFO0;
	sFilterConfig.FilterActivation = ENABLE;

	HAL_CAN_ConfigFilter(&hcan1, &sFilterConfig);
}

void processMessageComand(char *decodedCommand) {
	uint8_t cursor = 1;

	if (decodedCommand[cursor] == 'T') {
		cursor++;
		uint8_t messageID_str[9];
		substr((char*) decodedCommand, (char*) messageID_str, cursor, 9);

		int msgID = toInteger(messageID_str, 9);
		cursor += 9;

		uint8_t dlc_str[1];
		substr((char*) decodedCommand, (char*) dlc_str, cursor, 1);
		uint8_t dlc = atoi((char*) dlc_str);

		cursor++;
		uint8_t data[8];
		substr((char*) decodedCommand, (char*) data, cursor, 8);

		sendCANMessage(dlc, msgID, false, false, data);

	} else if (decodedCommand[cursor] == 'R') {
		cursor++;
		uint8_t messageID_str[9];
		substr((char*) decodedCommand, (char*) messageID_str, cursor, 9);

		int msgID = toInteger(messageID_str, 9);
		cursor += 9;

		uint8_t dlc_str[1];
		substr((char*) decodedCommand, (char*) dlc_str, cursor, 1);
		uint8_t dlc = toInteger(dlc_str, 1);

		sendCANMessage(dlc, msgID, true, false, 0x00);
	} else if (decodedCommand[cursor] == 't') {
		cursor++;
		uint8_t messageID_str[4];
		substr((char*) decodedCommand, (char*) messageID_str, cursor, 4);
		int msgID = toInteger(messageID_str, 4);
		cursor += 4;

		uint8_t dlc_str[1];
		substr((char*) decodedCommand, (char*) dlc_str, cursor, 1);
		uint8_t dlc = toInteger(dlc_str, 1);

		cursor++;
		uint8_t data[8];
		substr((char*) decodedCommand, (char*) data, cursor, 8);

		sendCANMessage(dlc, msgID, false, true, data);

	} else if (decodedCommand[cursor] == 'r') {
		cursor++;
		uint8_t messageID_str[4];
		substr((char*) decodedCommand, (char*) messageID_str, cursor, 4);
		int msgID = toInteger(messageID_str, 4);
		cursor += 4;

		uint8_t dlc_str[1];
		substr((char*) decodedCommand, (char*) dlc_str, cursor, 1);
		uint8_t dlc = atoi((char*) dlc_str);

		sendCANMessage(dlc, msgID, true, true, 0x00);
	}

}

void processBitRateCommand(char *decodedCommand) {

	uint8_t bitrateSrt[3];
	substr((char*) decodedCommand, (char*) bitrateSrt, 1, 3);
	int bitRate = toInteger(bitrateSrt, 3);

	bool idetified = false;

	switch (bitRate) {
	case 10:
		hcan1.Init.Prescaler = 300;
		idetified = true;
		break;
	case 20:
		hcan1.Init.Prescaler = 150;
		idetified = true;
		break;
	case 50:
		hcan1.Init.Prescaler = 60;
		idetified = true;
		break;
	case 100:
		hcan1.Init.Prescaler = 30;
		idetified = true;
		break;
	case 125:
		hcan1.Init.Prescaler = 24;
		idetified = true;
		break;
	case 250:
		hcan1.Init.Prescaler = 12;
		idetified = true;
		break;
	case 500:
		hcan1.Init.Prescaler = 6;
		idetified = true;
		break;
	}
	if (idetified) {
		HAL_CAN_DeInit(&hcan1);
		HAL_CAN_Init(&hcan1);
		setSinfferCANFilter();
		HAL_CAN_Start(&hcan1);
		if (snifferAtivityStatus != SNIFFER_STOPPED) {
			HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);
		}
	}
}
void processLoopBackModeCommand(char *decodedCommand) {

	uint8_t mode[2];
	bool idetified = false;
	substr((char*) decodedCommand, (char*) mode, 1, 2);
	if (!strcmp((char*) mode, "LB")) {
		hcan1.Init.Mode = CAN_MODE_LOOPBACK;
		idetified = true;
	} else if (!strcmp((char*) mode, "SM")) {
		hcan1.Init.Mode = CAN_MODE_SILENT;
		idetified = true;
	} else if (!strcmp((char*) mode, "NM")) {
		hcan1.Init.Mode = CAN_MODE_NORMAL;
		idetified = true;
	} else if (!strcmp((char*) mode, "SL")) {
		hcan1.Init.Mode = CAN_MODE_SILENT_LOOPBACK;
		idetified = true;
	}
	if (idetified) {
		HAL_CAN_DeInit(&hcan1);
		HAL_CAN_Init(&hcan1);
		setSinfferCANFilter();
		HAL_CAN_Start(&hcan1);
		if (snifferAtivityStatus != SNIFFER_STOPPED) {
			HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);
		}

	}
}

void processActivitySniferComand(char *decodedCommand) {

	uint8_t activityMode[3];
	substr((char*) decodedCommand, (char*) activityMode, 1, 3);

	if (!strcmp((char*) activityMode, "ON_")) {
		snifferAtivityStatus = SNIFFER_ACTIVE;
		HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);

	}

	else if (!strcmp((char*) activityMode, "OFF")) {
		HAL_CAN_DeactivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);
		snifferAtivityStatus = SNIFFER_STOPPED;

	}
}
void processRebootCommand() {
	NVIC_SystemReset();
}

void setDatagramTypeIdentifer(uint32_t ide, uint32_t rtr, uint8_t *pExitBuffer,
		uint8_t *pCursor) {
	if (ide == CAN_ID_STD) {
		if (rtr == CAN_RTR_DATA) {
			pExitBuffer[*pCursor] = 't';
		} else if (rtr == CAN_RTR_REMOTE) {
			pExitBuffer[*pCursor] = 'r';
		}
	} else if (ide == CAN_ID_EXT) {

		if (rtr == CAN_RTR_DATA) {
			pExitBuffer[*pCursor] = 'T';
		} else if (rtr == CAN_RTR_REMOTE) {
			pExitBuffer[*pCursor] = 'R';
		}
	}
	*pCursor = *pCursor + 1;
}

void setFormatedDatagramIdentifer(uint32_t idNum, uint8_t *pExitBuffer,uint8_t *pCursor, int len) {

	char *id = (char*) pvPortMalloc(sizeof(char) * (len + 1));
	int numOfDigits = 0;
	int valueToConsume = idNum;

	while (valueToConsume != 0) {
		valueToConsume /= 10;     // n = n/10
		++numOfDigits;
	}

	sprintf(id + (len - numOfDigits), "%d", (int) idNum);
	for (int eraser = 0; eraser < (len - numOfDigits); eraser++) {
		id[eraser] = '0';
	}
	strcpy((char*) pExitBuffer + *pCursor, id);
	vPortFree(id);
	*pCursor = *pCursor + len;
}

void setDatagramIdentifer(CAN_RxHeaderTypeDef receivedCANHeader,
		uint8_t *pExitBuffer, uint8_t *pCursor) {
	if (receivedCANHeader.IDE == CAN_ID_EXT) {
		setFormatedDatagramIdentifer(receivedCANHeader.ExtId, pExitBuffer,
				pCursor, 9);
	}
	if (receivedCANHeader.IDE == CAN_ID_STD) {
		setFormatedDatagramIdentifer(receivedCANHeader.StdId, pExitBuffer,
				pCursor, 4);
	}
}

void setDLC(uint32_t dlc, uint8_t *pExitBuffer, uint8_t *pCursor) {
	sprintf((char*) pExitBuffer + *pCursor, "%d", (int) dlc);
	*pCursor = *pCursor + 1;
}

void setData(uint8_t *data, int dlc, uint8_t *pExitBuffer, uint8_t *pCursor) {
	for (int counter = 0; counter < dlc; counter++) {
		pExitBuffer[*pCursor + counter] = data[counter];
	}
	*pCursor = *pCursor + dlc;
}

uint8_t serializeDatagram(uint8_t *pExitBuffer,CAN_RxHeaderTypeDef receivedCANHeader, uint8_t *rxData) {

	uint8_t cursor = 0;

	setDatagramTypeIdentifer(receivedCANHeader.IDE, receivedCANHeader.RTR,
			pExitBuffer, &cursor);
	setDatagramIdentifer(receivedCANHeader, pExitBuffer, &cursor);
	setDLC(receivedCANHeader.DLC, pExitBuffer, &cursor);
	if (receivedCANHeader.RTR == CAN_RTR_DATA) {
		setData(rxData, receivedCANHeader.DLC, pExitBuffer, &cursor);
	}

	return cursor;
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
	if (huart->Instance == huart1.Instance) {
		osSignalSet(receiveCommandsTaskId, osAnySignal);
	}
}


 void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan) {
  	if (HAL_CAN_GetRxMessage(&hcan1, CAN_RX_FIFO0, &rxMessageHeader,rxDataReceived) == HAL_OK) {
  		if (snifferAtivityStatus == SNIFFER_ACTIVE) {
  			osSignalSet(receivedDatagramTaskId, osAnySignal);

  		}
  	}
 }

/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void) {
	/* USER CODE BEGIN 1 */

	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */

	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* USER CODE BEGIN SysInit */

	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_CAN1_Init();
	MX_USART1_UART_Init();
	/* USER CODE BEGIN 2 */
	HAL_UART_Receive_IT(&huart1, rxUARTBuff, 1);
	setSinfferCANFilter();
	HAL_CAN_Start(&hcan1);
	if (snifferAtivityStatus != SNIFFER_STOPPED) {
		HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);
	}
	/* USER CODE END 2 */

	/* USER CODE BEGIN RTOS_MUTEX */
	/* add mutexes, ... */
	/* USER CODE END RTOS_MUTEX */

	/* USER CODE BEGIN RTOS_SEMAPHORES */
	/* add semaphores, ... */
	/* USER CODE END RTOS_SEMAPHORES */

	/* USER CODE BEGIN RTOS_TIMERS */
	/* start timers, add new ones, ... */
	/* USER CODE END RTOS_TIMERS */

	/* USER CODE BEGIN RTOS_QUEUES */
	pendingCommandsQueue = osMailCreate(osMailQ(pendingCommandsQueue), NULL); // create pendingCommandsQueue
	canDatagramsQueue = osMailCreate(osMailQ(canDatagramsQueue), NULL);
	/* USER CODE END RTOS_QUEUES */

	/* Create the thread(s) */
	/* USER CODE BEGIN RTOS_THREADS */

	osThreadDef(rcvCommandTask, rcvCommandThread, osPriorityRealtime, 0, 128);
	receiveCommandsTaskId = osThreadCreate(osThread(rcvCommandTask), NULL);

	osThreadDef(executeCommandTask, executeCommandThread, osPriorityRealtime, 0,128);
	executeCommmandtaskID = osThreadCreate(osThread(executeCommandTask), NULL);

	osThreadDef(forwardDatagramsTask, fordwardDatagramsThread, osPriorityNormal,0, 640);
	forwardDatagramTaskId = osThreadCreate(osThread(forwardDatagramsTask),NULL);

	osThreadDef(receiveDatagramsTask, recieivedDatagramsThread,osPriorityNormal, 0, 640);
	receivedDatagramTaskId = osThreadCreate(osThread(receiveDatagramsTask),NULL);

	osThreadDef(idleTask, idleThread, osPriorityIdle, 0, 128);
	idleTaskId = osThreadCreate(osThread(idleTask), NULL);

	bootLEDIndicator();

	/* USER CODE END RTOS_THREADS */

	/* Start scheduler */
	osKernelStart();

	/* We should never get here as control is now taken by the scheduler */
	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1) {
		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */
	}
	/* USER CODE END 3 */
}

/**
 * @brief System Clock Configuration
 * @retval None
 */
void SystemClock_Config(void) {
	RCC_OscInitTypeDef RCC_OscInitStruct = { 0 };
	RCC_ClkInitTypeDef RCC_ClkInitStruct = { 0 };

	/** Configure the main internal regulator output voltage
	 */
	__HAL_RCC_PWR_CLK_ENABLE();
	__HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
	/** Initializes the RCC Oscillators according to the specified parameters
	 * in the RCC_OscInitTypeDef structure.
	 */
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
	RCC_OscInitStruct.HSEState = RCC_HSE_ON;
	RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
	RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
	RCC_OscInitStruct.PLL.PLLM = 4;
	RCC_OscInitStruct.PLL.PLLN = 168;
	RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
	RCC_OscInitStruct.PLL.PLLQ = 4;
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
		Error_Handler();
	}
	/** Initializes the CPU, AHB and APB buses clocks
	 */
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
			| RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
	RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
	RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

	if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK) {
		Error_Handler();
	}
}

/**
 * @brief CAN1 Initialization Function
 * @param None
 * @retval None
 */
static void MX_CAN1_Init(void) {

	/* USER CODE BEGIN CAN1_Init 0 */

	/* USER CODE END CAN1_Init 0 */

	/* USER CODE BEGIN CAN1_Init 1 */

	/* USER CODE END CAN1_Init 1 */
	hcan1.Instance = CAN1;
	hcan1.Init.Prescaler = 12;
	hcan1.Init.Mode = CAN_MODE_NORMAL;
	hcan1.Init.SyncJumpWidth = CAN_SJW_1TQ;
	hcan1.Init.TimeSeg1 = CAN_BS1_11TQ;
	hcan1.Init.TimeSeg2 = CAN_BS2_2TQ;
	hcan1.Init.TimeTriggeredMode = DISABLE;
	hcan1.Init.AutoBusOff = DISABLE;
	hcan1.Init.AutoWakeUp = DISABLE;
	hcan1.Init.AutoRetransmission = DISABLE;
	hcan1.Init.ReceiveFifoLocked = DISABLE;
	hcan1.Init.TransmitFifoPriority = DISABLE;
	if (HAL_CAN_Init(&hcan1) != HAL_OK) {
		Error_Handler();
	}
	/* USER CODE BEGIN CAN1_Init 2 */

	/* USER CODE END CAN1_Init 2 */

}

/**
 * @brief USART1 Initialization Function
 * @param None
 * @retval None
 */
static void MX_USART1_UART_Init(void) {

	/* USER CODE BEGIN USART1_Init 0 */

	/* USER CODE END USART1_Init 0 */

	/* USER CODE BEGIN USART1_Init 1 */

	/* USER CODE END USART1_Init 1 */
	huart1.Instance = USART1;
	huart1.Init.BaudRate = 115200;
	huart1.Init.WordLength = UART_WORDLENGTH_8B;
	huart1.Init.StopBits = UART_STOPBITS_1;
	huart1.Init.Parity = UART_PARITY_NONE;
	huart1.Init.Mode = UART_MODE_TX_RX;
	huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
	huart1.Init.OverSampling = UART_OVERSAMPLING_16;
	if (HAL_UART_Init(&huart1) != HAL_OK) {
		Error_Handler();
	}
	/* USER CODE BEGIN USART1_Init 2 */

	/* USER CODE END USART1_Init 2 */

}

/**
 * @brief GPIO Initialization Function
 * @param None
 * @retval None
 */
static void MX_GPIO_Init(void) {
	GPIO_InitTypeDef GPIO_InitStruct = { 0 };

	/* GPIO Ports Clock Enable */
	__HAL_RCC_GPIOE_CLK_ENABLE();
	__HAL_RCC_GPIOH_CLK_ENABLE();
	__HAL_RCC_GPIOA_CLK_ENABLE();
	__HAL_RCC_GPIOB_CLK_ENABLE();

	/*Configure GPIO pin Output Level */
	HAL_GPIO_WritePin(GPIOE,
	PIN1_Pin | PIN2_Pin | PIN3_Pin | PIN4_Pin | PIN5_Pin | IDLE_PIN_Pin,
			GPIO_PIN_RESET);

	/*Configure GPIO pin Output Level */
	HAL_GPIO_WritePin(ORANGE_LED_GPIO_Port, ORANGE_LED_Pin, GPIO_PIN_RESET);

	/*Configure GPIO pins : PIN1_Pin PIN2_Pin PIN3_Pin PIN4_Pin
	 PIN5_Pin IDLE_PIN_Pin */
	GPIO_InitStruct.Pin = PIN1_Pin | PIN2_Pin | PIN3_Pin | PIN4_Pin | PIN5_Pin
			| IDLE_PIN_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

	/*Configure GPIO pin : BUTTON_Pin */
	GPIO_InitStruct.Pin = BUTTON_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(BUTTON_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : ORANGE_LED_Pin */
	GPIO_InitStruct.Pin = ORANGE_LED_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(ORANGE_LED_GPIO_Port, &GPIO_InitStruct);

}

/* USER CODE BEGIN 4 */
void rcvCommandThread(void const *argument) {
	uint8_t rxCommandBuff[SIZE_RX] = { 0 };
	volatile uint8_t cursor = 0;
	uint8_t rxValue[1] = { 0 };
	osEvent evt;
	while (true) {
		evt = osSignalWait(osAnySignal, 1);//osWaitForever
		if (evt.status == osEventSignal) {
			HAL_GPIO_TogglePin(PIN1_GPIO_Port, PIN1_Pin);
			rxValue[0] = rxUARTBuff[0];
			HAL_UART_Receive_IT(&huart1, rxUARTBuff, 1);
			rxCommandBuff[cursor] = rxValue[0];
			cursor++;
			if (cursor >= SIZE_RX) {
				cursor = 0;
			}
			if (rxValue[0] == 0x00) {
				SnniferCommand *pendingCmd;
				pendingCmd = osMailCAlloc(pendingCommandsQueue, 1); // osWaitForever
				if (pendingCmd != NULL) {
					strcpy((char*) pendingCmd->commnddBuff,
							(char*) rxCommandBuff);
					pendingCmd->commandSize = cursor - 1;
					osMailPut(pendingCommandsQueue, pendingCmd);
					HAL_GPIO_TogglePin(PIN2_GPIO_Port, PIN2_Pin);
					osThreadYield();
				}
				cursor = 0;
			}

		}
		else{
			osThreadYield();
		}
	}
}

void executeCommandThread(void const *argument) {
	SnniferCommand *dequedComand;
	uint8_t decodedCommand[20] = { 0 };
	osEvent evt;
	while (true) {
		evt = osMailGet(pendingCommandsQueue, 1);//osWaitForever
		if (evt.status == osEventMail) {
			dequedComand = evt.value.p;
			cobs_decode_result resutlt = cobs_decode(decodedCommand, 20,dequedComand->commnddBuff, dequedComand->commandSize);
			if (resutlt.status == COBS_DECODE_OK) {
				if (decodedCommand[0] == 'A') {
					// Change activity status
					processActivitySniferComand((char*) decodedCommand);
				}
				if (decodedCommand[0] == 'M') {
					// Send a datagram to the CAN Bus
					processMessageComand((char*) decodedCommand);
				} else if (decodedCommand[0] == 'S') {
					// Change bit rate
					processBitRateCommand((char*) decodedCommand);
				} else if (decodedCommand[0] == 'N') {
					// Change Mode CAN bus Mode
					processLoopBackModeCommand((char*) decodedCommand);
				}	// Reboot Snifer
				else if (decodedCommand[0] == 'R') {
					processRebootCommand();
				}
			}
			memset(decodedCommand, 0, sizeof(decodedCommand));
			osMailFree(pendingCommandsQueue, dequedComand);
			HAL_GPIO_TogglePin(PIN3_GPIO_Port, PIN3_Pin);
			osThreadYield();
		}
		else{
			osThreadYield();
		}
	}
}


void recieivedDatagramsThread(void const *argument) {
	//CAN_RxHeaderTypeDef rxMessageHeader;
	//uint8_t rxDataReceived[8];
	osEvent evt;
	while (true) {
		evt = osSignalWait(osAnySignal, 1);//osWaitForever
		if (evt.status == osEventSignal) {
			HAL_GPIO_TogglePin(PIN4_GPIO_Port, PIN4_Pin);
			CANMessage *msgToSend = osMailCAlloc(canDatagramsQueue, noWait);
			if (msgToSend != NULL) {
				 msgToSend->header = rxMessageHeader;
				 strcpy((char*) msgToSend->data, (char*) rxDataReceived);
				 osMailPut(canDatagramsQueue, msgToSend);
			}
			osThreadYield();
		}
		else{
			osThreadYield();
		}

	}
}

void fordwardDatagramsThread(void const *argument) {
	uint8_t serializedDatagram[24] = { 0 };
	uint8_t lenSerialized;
	uint8_t encodedDatagram[24] = { 0 };
	osEvent evt;
	CANMessage *dequeuedMsg;
	while (true) {
		evt = osMailGet(canDatagramsQueue, 1);	//osWaitForever
		if (evt.status == osEventMail) {
			dequeuedMsg = evt.value.p;
			lenSerialized = serializeDatagram(serializedDatagram,dequeuedMsg->header, dequeuedMsg->data);
			cobs_encode_result result = cobs_encode(encodedDatagram, 24,serializedDatagram, lenSerialized + 1);
			if (result.status == COBS_ENCODE_OK) {
				// Append Zero byte to delimiter frame boundary
				encodedDatagram[result.out_len + 1] = 0x00;
				HAL_UART_Transmit(&huart1, encodedDatagram, result.out_len + 1,50);
				// Toggle monitoring line to indicate a successful datagrams retransmission
				HAL_GPIO_TogglePin(PIN5_GPIO_Port, PIN5_Pin);
				memset(encodedDatagram, 0, sizeof(encodedDatagram));
			}
			osMailFree(canDatagramsQueue, dequeuedMsg);
			osThreadYield();

		}else{
			osThreadYield();
		}
	}
}

void idleThread(void const *argument) {
	while (true) {
		HAL_GPIO_TogglePin(IDLE_PIN_GPIO_Port, IDLE_PIN_Pin);
		osDelay(1);
	}
}

/* USER CODE END 4 */

/**
 * @brief  Period elapsed callback in non blocking mode
 * @note   This function is called  when TIM6 interrupt took place, inside
 * HAL_TIM_IRQHandler(). It makes a direct call to HAL_IncTick() to increment
 * a global variable "uwTick" used as application time base.
 * @param  htim : TIM handle
 * @retval None
 */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
	/* USER CODE BEGIN Callback 0 */

	/* USER CODE END Callback 0 */
	if (htim->Instance == TIM6) {
		HAL_IncTick();
	}
	/* USER CODE BEGIN Callback 1 */

	/* USER CODE END Callback 1 */
}

/**
 * @brief  This function is executed in case of error occurrence.
 * @retval None
 */
void Error_Handler(void) {
	/* USER CODE BEGIN Error_Handler_Debug */
	/* User can add his own implementation to report the HAL error return state */
	__disable_irq();
	while (1) {
	}
	/* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
